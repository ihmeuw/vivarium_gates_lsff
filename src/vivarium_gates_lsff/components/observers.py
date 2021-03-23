import pandas as pd
import itertools
import typing

from collections import Counter
from typing import Dict, List, Tuple, Iterable

from vivarium_public_health.metrics.utilities import (get_output_template, get_group_counts,
                                                      get_state_person_time, get_transition_count,
                                                      QueryString, to_years, get_age_bins)

from vivarium_gates_lsff.constants import models, results

if typing.TYPE_CHECKING:
    from vivarium.framework.engine import Builder
    from vivarium.framework.event import Event
    from vivarium.framework.population import SimulantData


class ResultsStratifier:
    """Centralized component for handling results stratification.

    This should be used as a sub-component for observers.  The observers
    can then ask this component for population subgroups and labels during
    results production and have this component manage adjustments to the
    final column labels for the subgroups.

    """

    def __init__(self, observer_name: str):
        self.name = f'{observer_name}_results_stratifier'

    def setup(self, builder: 'Builder'):
        """Perform this component's setup."""
        # The only thing you should request here are resources necessary for
        # results stratification.
        self.population_view = builder.population.get_view([
            models.VITAMIN_A_MODEL_NAME,
            'age',
            'tracked',  # Ensure we get the full population.
        ])
        pipeline_keys = ['zinc_deficiency.exposure']
        self.pipelines = {key: builder.value.get_value(key) for key in pipeline_keys}

    def group(self, population: pd.DataFrame) -> Iterable[Tuple[Tuple[str, ...], pd.DataFrame]]:
        """Takes the full population and yields stratified subgroups.

        Parameters
        ----------
        population
            The population to stratify.

        Yields
        ------
            A tuple of stratification labels and the population subgroup
            corresponding to those labels.

        """
        vit_a_pop = self.vitamin_a_population(population)
        zinc_pop = self.zinc_population(population)

        groups = itertools.product(models.VITAMIN_A_MODEL_STATES,
                                   models.ZINC_DEFICIENCY_RISK_STATES)
        for vit_a_group, zinc_group in groups:
            if population.empty:
                pop_in_group = population
            else:
                pop_in_group = population.loc[(vit_a_pop == vit_a_group)
                                              & (zinc_pop == zinc_group)]
            yield (vit_a_group, zinc_group), pop_in_group

    @staticmethod
    def update_labels(measure_data: Dict[str, float], labels: Tuple[str, ...]) -> Dict[str, float]:
        """Updates a dict of measure data with stratification labels.

        Parameters
        ----------
        measure_data
            The measure data with unstratified column names.
        labels
            The stratification labels. Yielded along with the population
            subgroup the measure data was produced from by a call to
            :obj:`ResultsStratifier.group`.

        Returns
        -------
            The measure data with column names updated with the stratification
            labels.

        """
        vit_a_group, zinc_group = labels
        measure_data = {f'{k}_VA_{vit_a_group}_ZINC_{zinc_group}': v
                        for k, v in measure_data.items()}
        return measure_data

    def vitamin_a_population(self, population: pd.DataFrame) -> pd.Series:
        pop = self.population_view.get(population.index)
        temp =  pop[models.VITAMIN_A_MODEL_NAME]
        return temp

    def zinc_population(self, population: pd.DataFrame) -> pd.Series:
        pop = self.population_view.get(population.index)
        return self.pipelines['zinc_deficiency.exposure'](pop.index).transform(
            lambda x: models.ZINC_DEFICIENCY_SUSCEPTIBLE_STATE_NAME if x=='cat2'
            else models.ZINC_DEFICIENCY_WITH_CONDITION_STATE_NAME)



class StateObserver:
    """Observes transition counts and person time for a cause."""
    configuration_defaults = {
        'metrics': {
            'disease_observer': {
                'by_age': False,
                'by_year': False,
                'by_sex': False,
            }
        }
    }

    def __init__(self, disease: str):
        self.disease = disease
        self.configuration_defaults = {
            'metrics': {f'{disease}_observer': StateObserver.configuration_defaults['metrics']['disease_observer']}
        }
        self.stratifier = ResultsStratifier(self.name)

    @property
    def name(self) -> str:
        return f'disease_observer.{self.disease}'

    @property
    def sub_components(self) -> List[ResultsStratifier]:
        return [self.stratifier]

    def setup(self, builder: 'Builder'):
        self.config = builder.configuration['metrics'][f'{self.disease}_observer'].to_dict()
        self.clock = builder.time.clock()
        self.age_bins = get_age_bins(builder)
        self.counts = Counter()
        self.person_time = Counter()

        self.states = models.STATE_MACHINE_MAP[self.disease]['states']
        self.transitions = models.STATE_MACHINE_MAP[self.disease]['transitions']

        self.previous_state_column = f'previous_{self.disease}'
        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=[self.previous_state_column])

        columns_required = ['alive', f'{self.disease}', self.previous_state_column]
        if self.config['by_age']:
            columns_required += ['age']
        if self.config['by_sex']:
            columns_required += ['sex']
        self.population_view = builder.population.get_view(columns_required)

        builder.value.register_value_modifier('metrics', self.metrics)
        # FIXME: The state table is modified before the clock advances.
        # In order to get an accurate representation of person time we need to look at
        # the state table before anything happens.
        builder.event.register_listener('time_step__prepare', self.on_time_step_prepare)
        builder.event.register_listener('collect_metrics', self.on_collect_metrics)

    def on_initialize_simulants(self, pop_data: 'SimulantData'):
        self.population_view.update(pd.Series('', index=pop_data.index, name=self.previous_state_column))

    def on_time_step_prepare(self, event: 'Event'):
        pop = self.population_view.get(event.index)
        # Ignoring the edge case where the step spans a new year.
        # Accrue all counts and time to the current year.
        for labels, pop_in_group in self.stratifier.group(pop):
            for state in self.states:
                # noinspection PyTypeChecker
                state_person_time_this_step = get_state_person_time(pop_in_group, self.config, self.disease, state,
                                                                    self.clock().year, event.step_size, self.age_bins)
                state_person_time_this_step = self.stratifier.update_labels(state_person_time_this_step, labels)
                self.person_time.update(state_person_time_this_step)

        # This enables tracking of transitions between states
        prior_state_pop = self.population_view.get(event.index)
        prior_state_pop[self.previous_state_column] = prior_state_pop[self.disease]
        self.population_view.update(prior_state_pop)

    def on_collect_metrics(self, event: 'Event'):
        pop = self.population_view.get(event.index)
        for labels, pop_in_group in self.stratifier.group(pop):
            for transition in self.transitions:
                # noinspection PyTypeChecker
                transition_counts_this_step = get_transition_count(pop_in_group, self.config, self.disease, transition,
                                                                   event.time, self.age_bins)
                transition_counts_this_step = self.stratifier.update_labels(transition_counts_this_step, labels)
                self.counts.update(transition_counts_this_step)

    def metrics(self, index: pd.Index, metrics: Dict[str, float]):
        metrics.update(self.counts)
        metrics.update(self.person_time)
        return metrics

    def __repr__(self) -> str:
        return f"StateObserver({self.disease})"



class AnemiaObserver:
    """Observes person time in the various anemia states"""
    configuration_defaults = {
        'metrics': {
            models.ANEMIA_OBSERVER: {
                'by_age': True,
                'by_year': True,
                'by_sex': True,
            }
        }
    }

    def __init__(self):
        self.configuration_defaults = {
            'metrics': { models.ANEMIA_OBSERVER:
                         AnemiaObserver.configuration_defaults['metrics'][models.ANEMIA_OBSERVER]}
        }

    @property
    def name(self) -> str:
        return models.ANEMIA_OBSERVER

    def setup(self, builder: 'Builder'):
        self.config = builder.configuration['metrics'][models.ANEMIA_OBSERVER].to_dict()
        self.clock = builder.time.clock()
        self.age_bins = get_age_bins(builder)
        self.person_time = Counter()
        self.anemia_severity = builder.value.get_value('anemia_severity')
        self.states = models.ANEMIA_SEVERITY_GROUPS

        columns_required = ['alive']
        if self.config['by_age']:
            columns_required += ['age']
        if self.config['by_sex']:
            columns_required += ['sex']
        self.population_view = builder.population.get_view(columns_required)

        builder.value.register_value_modifier('metrics', self.metrics)
        # FIXME: The state table is modified before the clock advances.
        # In order to get an accurate representation of person time we need to look at
        # the state table before anything happens.
        builder.event.register_listener('time_step__prepare', self.on_time_step_prepare)

    def on_time_step_prepare(self, event: 'Event'):
        pop = self.population_view.get(event.index)
        pop['anemia'] = self.anemia_severity(pop.index)
        # Ignoring the edge case where the step spans a new year.
        # Accrue all counts and time to the current year.
        for state in self.states:
            base_key = get_output_template(**self.config).substitute(measure=f'anemia_{state}_person_time',
                                                                     year=self.clock().year)
            base_filter = QueryString(f'alive == "alive" and anemia == "{state}"')
            # noinspection PyTypeChecker
            person_time = get_group_counts(pop, base_filter, base_key, self.config, self.age_bins,
                                           aggregate=lambda x: len(x) * to_years(event.step_size))
            self.person_time.update(person_time)

    def metrics(self, index: pd.Index, metrics: Dict[str, float]):
        metrics.update(self.person_time)
        return metrics

from collections import Counter
import typing
from typing import Dict

import pandas as pd

from vivarium_public_health.metrics.utilities import (get_output_template, get_group_counts,
                                                      QueryString, to_years, get_age_bins)

from vivarium_gates_lsff.constants import models

if typing.TYPE_CHECKING:
    from vivarium.framework.engine import Builder
    from vivarium.framework.event import Event


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

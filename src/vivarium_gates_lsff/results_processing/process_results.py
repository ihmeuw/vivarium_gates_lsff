from pathlib import Path
from typing import NamedTuple, List, Tuple

import pandas as pd
import yaml

from vivarium_gates_lsff.constants import models, results


SCENARIO_COLUMN = 'scenario'
GROUPBY_COLUMNS = [
    results.INPUT_DRAW_COLUMN,
    SCENARIO_COLUMN
]
OUTPUT_COLUMN_SORT_ORDER = [
    'year',
    'sex',
    'age',
    'scenario'
    'risk',
    'cause',
    'measure',
    'input_draw'
]


def make_measure_data(data, field_map):
    measure_data = MeasureData(
        population=get_population_data(data, field_map),
        ylls=get_by_cause_measure_data(data, 'ylls', field_map),
        ylds=get_by_cause_measure_data(data, 'ylds', field_map),
        deaths=get_by_cause_measure_data(data, 'deaths', field_map),

        # Specific to zinc and vitamin a stratification
        disease_state_person_time_diarrhea=get_state_person_time_measure_data_special(data, 'disease_state_person_time_diarrhea', field_map),
        disease_state_person_time_measles=get_state_person_time_measure_data_special(data, 'disease_state_person_time_measles', field_map),
        disease_transition_count_diarrhea=get_state_person_time_measure_data_special(data, 'disease_transition_count_diarrhea', field_map),
        disease_transition_count_measles=get_state_person_time_measure_data_special(data, 'disease_transition_count_measles', field_map),

        # disease_state_person_time=get_state_person_time_measure_data(data, 'disease_state_person_time', field_map),
        # disease_transition_count=get_transition_count_measure_data(data, 'disease_transition_count', field_map),

    )
    return measure_data


class MeasureData(NamedTuple):
    population: pd.DataFrame
    ylls: pd.DataFrame
    ylds: pd.DataFrame
    deaths: pd.DataFrame

    # Specific to zinc and vitamin a stratification
    disease_state_person_time_diarrhea: pd.DataFrame
    disease_state_person_time_measles: pd.DataFrame
    disease_transition_count_diarrhea: pd.DataFrame
    disease_transition_count_measles: pd.DataFrame

    # disease_state_person_time: pd.DataFrame
    # disease_transition_count: pd.DataFrame

    def dump(self, output_dir: Path):
        for key, df in self._asdict().items():
            df.to_hdf(output_dir / f'{key}.hdf', key=key)
            df.to_csv(output_dir / f'{key}.csv')


def read_data(path: Path, single_run: bool) -> (pd.DataFrame, List[str], Tuple[int, int]):
    data = pd.read_hdf(path)
    # noinspection PyUnresolvedReferences
    data = (data
            .drop(columns=data.columns.intersection(results.THROWAWAY_COLUMNS))
            .reset_index(drop=True)
            .rename(columns={results.OUTPUT_SCENARIO_COLUMN: SCENARIO_COLUMN})
            )
    if single_run:
        data[results.INPUT_DRAW_COLUMN] = 0
        data[results.RANDOM_SEED_COLUMN] = 0
        data[SCENARIO_COLUMN] = 'baseline'
        keyspace = {results.INPUT_DRAW_COLUMN: [0],
                    results.RANDOM_SEED_COLUMN: [0],
                    results.OUTPUT_SCENARIO_COLUMN: ['baseline']}
    else:
        data[results.INPUT_DRAW_COLUMN] = data[results.INPUT_DRAW_COLUMN].astype(int)
        data[results.RANDOM_SEED_COLUMN] = data[results.RANDOM_SEED_COLUMN].astype(int)
        with (path.parent / 'keyspace.yaml').open() as f:
            keyspace = yaml.full_load(f)
    years = read_model_spec_for_start_end(path.parent)
    return data, keyspace, years


def read_model_spec_for_start_end(path: Path) -> Tuple[int, int]:
    with (path / 'model_specification.yaml').open() as f:
        spec = yaml.full_load(f)
    time_cfg = spec['configuration']['time']
    return (time_cfg['start']['year'], time_cfg['end']['year'])


def filter_out_incomplete(data, keyspace):
    output = []
    for draw in keyspace[results.INPUT_DRAW_COLUMN]:
        # For each draw, gather all random seeds completed for all scenarios.
        random_seeds = set(keyspace[results.RANDOM_SEED_COLUMN])
        draw_data = data.loc[data[results.INPUT_DRAW_COLUMN] == draw]
        for scenario in keyspace[results.OUTPUT_SCENARIO_COLUMN]:
            seeds_in_data = draw_data.loc[data[SCENARIO_COLUMN] == scenario,
                                          results.RANDOM_SEED_COLUMN].unique()
            random_seeds = random_seeds.intersection(seeds_in_data)
        draw_data = draw_data.loc[draw_data[results.RANDOM_SEED_COLUMN].isin(random_seeds)]
        output.append(draw_data)
    return pd.concat(output, ignore_index=True).reset_index(drop=True)


def aggregate_over_seed(data, field_map):
    non_count_columns = []
    for non_count_template in results.NON_COUNT_TEMPLATES:
        non_count_columns += results.RESULT_COLUMNS(field_map, non_count_template)
    count_columns = [c for c in data.columns if c not in non_count_columns + GROUPBY_COLUMNS]

    # non_count_data = data[non_count_columns + GROUPBY_COLUMNS].groupby(GROUPBY_COLUMNS).mean()
    count_data = data[count_columns + GROUPBY_COLUMNS].groupby(GROUPBY_COLUMNS).sum()
    return pd.concat([
        count_data,
        # non_count_data
    ], axis=1).reset_index()


def pivot_data(data):
    return (data
            .set_index(GROUPBY_COLUMNS)
            .stack()
            .reset_index()
            .rename(columns={f'level_{len(GROUPBY_COLUMNS)}': 'process', 0: 'value'}))


def sort_data(data):
    sort_order = [c for c in OUTPUT_COLUMN_SORT_ORDER if c in data.columns]
    other_cols = [c for c in data.columns if c not in sort_order]
    data = data[sort_order + other_cols].sort_values(sort_order)
    return data.reset_index(drop=True)


def split_processing_column(data):
    # TODO the required splitting here is dependant on what types of stratification exist in the model
    data['process'], data['age'] = data.process.str.split('_in_age_group_').str
    data['process'], data['sex'] = data.process.str.split('_among_').str
    data['year'] = data.process.str.split('_in_').str[-1]
    data['measure'] = data.process.str.split('_in_').str[:-1].apply(lambda x: '_in_'.join(x))
    return data.drop(columns='process')


def get_population_data(data, field_map):
    total_pop = pivot_data(data[[results.TOTAL_POPULATION_COLUMN]
                                + results.RESULT_COLUMNS(field_map, 'population')
                                + GROUPBY_COLUMNS])
    total_pop = total_pop.rename(columns={'process': 'measure'})
    return sort_data(total_pop)


def get_measure_data(data, measure, field_map):
    data = pivot_data(data[results.RESULT_COLUMNS(field_map, measure) + GROUPBY_COLUMNS])
    data = split_processing_column(data)
    return sort_data(data)


def get_by_cause_measure_data(data, measure, field_map):
    data = get_measure_data(data, measure, field_map)
    data['measure'], data['cause'] = data.measure.str.split('_due_to_').str
    return sort_data(data)


def get_state_person_time_measure_data(data, measure, field_map):
    data = get_measure_data(data, measure, field_map)
    data['measure'], data['cause'] = 'state_person_time', data.measure.str.split('_person_time').str[0]
    return sort_data(data)


def get_transition_count_measure_data(data, measure, field_map):
    data = get_measure_data(data, measure, field_map)
    data['cause'] = data['measure'].str.split('_event_count').str[0]
    data['measure'] = 'transition_count'
    return sort_data(data)


# Specific to zinc and vitamin a stratification
def get_state_person_time_measure_data_special(data, measure, field_map):
    data = get_measure_data(data, measure, field_map)
    data = split_age_column(data, ('diarrhea' in measure))
    data['measure'], data['cause'] = 'state_person_time', data.measure.str.split('_person_time').str[0]
    return sort_data(data)


def get_transition_count_measure_data_special(data, measure, field_map):
    data = get_measure_data(data, measure, field_map)
    data = split_age_column(data, ('diarrhea' in measure))
    data['cause'] = data['measure'].str.split('_event_count').str[0]
    data['measure'] = 'transition_count'
    return sort_data(data)


def split_age_column(data, has_zinc):
    data['age'], data['vitamin_a_category'] = data.age.str.split('_VA_').str
    if has_zinc:
        data['vitamin_a_category'], data['zinc_category'] = data.vitamin_a_category.str.split('_ZINC_').str
    return data


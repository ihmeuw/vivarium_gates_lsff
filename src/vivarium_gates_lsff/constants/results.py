import itertools

from vivarium_gates_lsff.constants import models

#################################
# Results columns and variables #
#################################

TOTAL_POPULATION_COLUMN = 'total_population'
TOTAL_YLDS_COLUMN = 'years_lived_with_disability'
TOTAL_YLLS_COLUMN = 'years_of_life_lost'

# Columns from parallel runs
INPUT_DRAW_COLUMN = 'input_draw'
RANDOM_SEED_COLUMN = 'random_seed'
OUTPUT_SCENARIO_COLUMN = 'branch_name.scenario'

STANDARD_COLUMNS = {
    'total_population': TOTAL_POPULATION_COLUMN,
    'total_ylls': TOTAL_YLLS_COLUMN,
    'total_ylds': TOTAL_YLDS_COLUMN,
}

THROWAWAY_COLUMNS = []

TOTAL_POPULATION_COLUMN_TEMPLATE = 'total_population_{POP_STATE}'
DEATH_COLUMN_TEMPLATE = 'death_due_to_{CAUSE_OF_DEATH}_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
YLLS_COLUMN_TEMPLATE = 'ylls_due_to_{CAUSE_OF_DEATH}_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
YLDS_COLUMN_TEMPLATE = 'ylds_due_to_{CAUSE_OF_DISABILITY}_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
PERSON_TIME_COLUMN_TEMPLATE = 'person_time_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
DISEASE_STATE_PERSON_TIME_COLUMN_TEMPLATE = '{DISEASE_STATE}_person_time_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'
DISEASE_TRANSITION_COUNT_COLUMN_TEMPLATE = '{DISEASE_TRANSITION}_event_count_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}'

DISEASE_STATE_PERSON_TIME_COLUMN_TEMPLATE_DIARRHEA = '{DISEASE_STATE_DIARRHEA}_person_time_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}_VA_{STRATIFICATION_STATE_VITAMIN_A}_ZINC_{STRATIFICATION_STATE_ZINC}'
DISEASE_STATE_PERSON_TIME_COLUMN_TEMPLATE_MEASLES = '{DISEASE_STATE_MEASLES}_person_time_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}_VA_{STRATIFICATION_STATE_VITAMIN_A}'
DISEASE_TRANSITION_COUNT_COLUMN_TEMPLATE_DIARRHEA = '{DISEASE_TRANSITION_DIARRHEA}_event_count_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}_VA_{STRATIFICATION_STATE_VITAMIN_A}_ZINC_{STRATIFICATION_STATE_ZINC}'
DISEASE_TRANSITION_COUNT_COLUMN_TEMPLATE_MEASLES = '{DISEASE_TRANSITION_MEASLES}_event_count_in_{YEAR}_among_{SEX}_in_age_group_{AGE_GROUP}_VA_{STRATIFICATION_STATE_VITAMIN_A}'

COLUMN_TEMPLATES = {
    'population': TOTAL_POPULATION_COLUMN_TEMPLATE,
    'deaths': DEATH_COLUMN_TEMPLATE,
    'ylls': YLLS_COLUMN_TEMPLATE,
    'ylds': YLDS_COLUMN_TEMPLATE,

    'disease_state_person_time_diarrhea': DISEASE_STATE_PERSON_TIME_COLUMN_TEMPLATE_DIARRHEA,
    'disease_state_person_time_measles': DISEASE_STATE_PERSON_TIME_COLUMN_TEMPLATE_MEASLES,
    'disease_transition_count_diarrhea': DISEASE_TRANSITION_COUNT_COLUMN_TEMPLATE_DIARRHEA,
    'disease_transition_count_measles': DISEASE_TRANSITION_COUNT_COLUMN_TEMPLATE_MEASLES,
    
    # 'disease_state_person_time': DISEASE_STATE_PERSON_TIME_COLUMN_TEMPLATE,
    # 'disease_transition_count': DISEASE_TRANSITION_COUNT_COLUMN_TEMPLATE,
}

NON_COUNT_TEMPLATES = [
]

STRATIFICATION_STATES_VITAMIN_A = models.VITAMIN_A_MODEL_STATES

STRATIFICATION_STATES_ZINC = models.ZINC_DEFICIENCY_RISK_STATES


POP_STATES = ('living', 'dead', 'tracked', 'untracked')
SEXES = ('male', 'female')
YEARS = tuple(range(2020, 2024))
AGE_GROUPS = ('early_neonatal', 'late_neonatal', 'post_neonatal', '1_to_4')
# TODO - add causes of death
CAUSES_OF_DEATH = (
    'other_causes',
    models.DIARRHEA_WITH_CONDITION_STATE_NAME,
    models.MEASLES_WITH_CONDITION_STATE_NAME
    
)
# TODO - add causes of disability
CAUSES_OF_DISABILITY = (
    models.DIARRHEA_WITH_CONDITION_STATE_NAME,
    models.MEASLES_WITH_CONDITION_STATE_NAME
)

TEMPLATE_FIELD_MAP = {
    'POP_STATE': POP_STATES,
    'YEAR': YEARS,
    'SEX': SEXES,
    'AGE_GROUP': AGE_GROUPS,
    'CAUSE_OF_DEATH': CAUSES_OF_DEATH,
    'CAUSE_OF_DISABILITY': CAUSES_OF_DISABILITY,
    'DISEASE_STATE': models.STATES,
    'DISEASE_STATE_DIARRHEA': models.DIARRHEA_MODEL_STATES,
    'DISEASE_STATE_MEASLES': models.MEASLES_MODEL_STATES,
    'DISEASE_TRANSITION': models.TRANSITIONS,
    'DISEASE_TRANSITION_DIARRHEA': models.DIARRHEA_MODEL_TRANSITIONS,
    'DISEASE_TRANSITION_MEASLES': models.MEASLES_MODEL_TRANSITIONS,
    'STRATIFICATION_STATE_VITAMIN_A': STRATIFICATION_STATES_VITAMIN_A,
    'STRATIFICATION_STATE_ZINC': STRATIFICATION_STATES_ZINC
}


def RESULT_COLUMNS(field_map, kind='all'):
    if kind not in COLUMN_TEMPLATES and kind != 'all':
        raise ValueError(f'Unknown result column type {kind}')
    columns = []
    if kind == 'all':
        for k in COLUMN_TEMPLATES:
            columns += RESULT_COLUMNS(k)
        columns = list(STANDARD_COLUMNS.values()) + columns
    else:
        template = COLUMN_TEMPLATES[kind]
        filtered_field_map = {field: values
                              for field, values in field_map.items() if f'{{{field}}}' in template}
        fields, value_groups = filtered_field_map.keys(), itertools.product(*filtered_field_map.values())
        for value_group in value_groups:
            columns.append(template.format(**{field: value for field, value in zip(fields, value_group)}))
    return columns


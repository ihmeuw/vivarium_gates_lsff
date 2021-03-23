"""Loads, standardizes and validates input data for the simulation.

Abstract the extract and transform pieces of the artifact ETL.
The intent here is to provide a uniform interface around this portion
of artifact creation. The value of this interface shows up when more
complicated data needs are part of the project. See the BEP project
for an example.

`BEP <https://github.com/ihmeuw/vivarium_gates_bep/blob/master/src/vivarium_gates_bep/data/loader.py>`_

.. admonition::

   No logging is done here. Logging is done in vivarium inputs itself and forwarded.
"""
from typing import Dict, NamedTuple, Callable
import pandas as pd

from gbd_mapping import causes, covariates, risk_factors, sequelae
from vivarium.framework.artifact import EntityKey
from vivarium_gbd_access import gbd
from vivarium_inputs import globals as vi_globals, interface, extract, utilities as vi_utils, utility_data
from vivarium_inputs.mapping_extension import alternative_risk_factors

from vivarium_gates_lsff import paths
from vivarium_gates_lsff.constants import data_keys, data_values


def map_loader_funcs(keys: NamedTuple) -> Dict[str, Callable]:
    mapper = {
        'restrictions': load_metadata,
        'categories': load_metadata,
        'distribution': load_metadata,
    }
    return {k : mapper.get(k.split('.')[-1], load_standard_data) for k in keys}


def get_data(lookup_key: str, location: str) -> pd.DataFrame:
    """Retrieves data from an appropriate source.

    Parameters
    ----------
    lookup_key
        The key that will eventually get put in the artifact with
        the requested data.
    location
        The location to get data for.

    Returns
    -------
        The requested data.

    """
    mapping = {
        data_keys.POPULATION.LOCATION: load_population_location,
        data_keys.POPULATION.STRUCTURE: load_population_structure,
        data_keys.POPULATION.AGE_BINS: load_age_bins,
        data_keys.POPULATION.DEMOGRAPHY: load_demographic_dimensions,
        data_keys.POPULATION.TMRLE: load_theoretical_minimum_risk_life_expectancy,
        data_keys.POPULATION.ACMR: load_standard_data,
        data_keys.COVARIATES.COVARIATE_LIVE_BIRTHS_BY_SEX: load_standard_data,
    }
    mapping.update(map_loader_funcs(data_keys.DIARRHEA))
    mapping.update(map_loader_funcs(data_keys.MEASLES))
    mapping.update(map_loader_funcs(data_keys.NEURAL_TUBE_DEFECTS))
    mapping.update(map_loader_funcs(data_keys.LBWSG))
    mapping.update(map_loader_funcs(data_keys.VITAMIN_A))
    mapping.update(map_loader_funcs(data_keys.ZINC))
    mapping.update({
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_EXPOSURE: load_standard_data,
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_EXPOSURE_SD: load_standard_data,
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_NO_ANEMIA_IRON_RESPONSIVE_PROPORTION: load_no_anemia_iron_responsive_proportion,
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_MILD_ANEMIA_IRON_RESPONSIVE_PROPORTION: load_iron_responsive_proportion,
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_MODERATE_ANEMIA_IRON_RESPONSIVE_PROPORTION: load_iron_responsive_proportion,
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_SEVERE_ANEMIA_IRON_RESPONSIVE_PROPORTION: load_iron_responsive_proportion,
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_MILD_ANEMIA_DISABILITY_WEIGHT: load_iron_deficiency_dw,
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_MODERATE_ANEMIA_DISABILITY_WEIGHT: load_iron_deficiency_dw,
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_SEVERE_ANEMIA_DISABILITY_WEIGHT: load_iron_deficiency_dw,
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_RESTRICTIONS: load_metadata,
    })
    mapping.update(map_loader_funcs(data_keys.CSMR_AFFECTEDBY_LBWSG))
    return mapping[lookup_key](lookup_key, location)

def load_population_location(key: str, location: str) -> str:
    if key != data_keys.POPULATION.LOCATION:
        raise ValueError(f'Unrecognized key {key}')
    return location

    
def load_population_structure(key: str, location: str) -> pd.DataFrame:
    return interface.get_population_structure(location)


def load_age_bins(key: str, location: str) -> pd.DataFrame:
    return interface.get_age_bins()


def load_demographic_dimensions(key: str, location: str) -> pd.DataFrame:
    return interface.get_demographic_dimensions(location)


def load_theoretical_minimum_risk_life_expectancy(key: str, location: str) -> pd.DataFrame:
    return interface.get_theoretical_minimum_risk_life_expectancy()


def load_standard_data(key: str, location: str) -> pd.DataFrame:
    key = EntityKey(key)
    entity = get_entity(key)
    return interface.get_measure(entity, key.measure, location)


def load_metadata(key: str, location: str):
    key = EntityKey(key)
    entity = get_entity(key)
    entity_metadata = entity[key.measure]
    if hasattr(entity_metadata, 'to_dict'):
        entity_metadata = entity_metadata.to_dict()
    return entity_metadata


# Project-specific data functions here

def load_iron_deficiency_dw(key: str, location: str):
    sequela_map = {
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_MILD_ANEMIA_DISABILITY_WEIGHT:
            'sequela.mild_iron_deficiency_anemia.disability_weight',
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_MODERATE_ANEMIA_DISABILITY_WEIGHT:
            'sequela.moderate_iron_deficiency_anemia.disability_weight',
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_SEVERE_ANEMIA_DISABILITY_WEIGHT:
            'sequela.severe_iron_deficiency_anemia.disability_weight',
    }
    data_key = sequela_map[key]
    return load_standard_data(data_key, location)


def load_no_anemia_iron_responsive_proportion(key: str, location: str):
    responsive_ids, non_responsive_ids = [], []
    for responsive, non_responsive in data_values.ANEMIA_SEQUELAE_ID_MAP.values():
        responsive_ids.extend(responsive)
        non_responsive_ids.extend(non_responsive)

    responsive_sequelae = [s for s in sequelae if s.gbd_id in responsive_ids]
    non_responsive_sequelae = [s for s in sequelae if s.gbd_id in non_responsive_ids]

    all_prevalence = []
    iron_responsive_prevalence = []
    for sequela in responsive_sequelae:
        try:
            prevalence = interface.get_measure(sequela, 'prevalence', location)
        except (extract.DataDoesNotExistError, extract.DataAbnormalError):
            continue
        all_prevalence.append(prevalence)
        iron_responsive_prevalence.append(prevalence)
    for sequela in non_responsive_sequelae:
        try:
            prevalence = interface.get_measure(sequela, 'prevalence', location)
        except (extract.DataDoesNotExistError, extract.DataAbnormalError):
            continue
        all_prevalence.append(prevalence)
    all_prevalence = sum(all_prevalence)
    iron_responsive_prevalence = sum(iron_responsive_prevalence)
    non_responsive_prevalence = all_prevalence - iron_responsive_prevalence

    other_anemias_prevalence = interface.get_measure(causes.hemoglobinopathies_and_hemolytic_anemias,
                                                     'prevalence', location)
    hiv_prevalence = interface.get_measure(causes.hiv_aids, 'prevalence', location)
    malaria_prevalence = interface.get_measure(causes.malaria, 'prevalence', location)
    reverse_causal_prevalence = other_anemias_prevalence + hiv_prevalence + malaria_prevalence

    proportion = (1 - all_prevalence
                  - (reverse_causal_prevalence - non_responsive_prevalence)/(1 - all_prevalence)).fillna(0)
    return proportion


def load_iron_responsive_proportion(key: str, location: str):
    sequela_map = {
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_MILD_ANEMIA_IRON_RESPONSIVE_PROPORTION:
            data_values.ANEMIA_SEQUELAE_ID_MAP['mild'],
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_MODERATE_ANEMIA_IRON_RESPONSIVE_PROPORTION:
            data_values.ANEMIA_SEQUELAE_ID_MAP['moderate'],
        data_keys.IRON_DEFICIENCY.IRON_DEFICIENCY_SEVERE_ANEMIA_IRON_RESPONSIVE_PROPORTION:
            data_values.ANEMIA_SEQUELAE_ID_MAP['severe'],
    }
    responsive_ids, non_responsive_ids = sequela_map[key]

    responsive_prevalence = []
    for s_id in responsive_ids:
        sequela = [s for s in sequelae if s.gbd_id == s_id]
        if sequela:
            sequela = sequela.pop()
        else:
            continue
        try:
            prevalence = interface.get_measure(sequela, 'prevalence', location)
        except (extract.DataDoesNotExistError, extract.DataAbnormalError):
            continue
        responsive_prevalence.append(prevalence)
    responsive_prevalence = sum(responsive_prevalence)

    non_responsive_prevalence = []
    for s_id in non_responsive_ids:
        sequela = [s for s in sequelae if s.gbd_id == s_id]
        if sequela:
            sequela = sequela.pop()
        else:
            continue
        try:
            prevalence = interface.get_measure(sequela, 'prevalence', location)
        except (extract.DataDoesNotExistError, extract.DataAbnormalError):
            continue
        non_responsive_prevalence.append(prevalence)
    non_responsive_prevalence = sum(non_responsive_prevalence)

    return (responsive_prevalence / (responsive_prevalence + non_responsive_prevalence)).fillna(0)


def get_entity(key: str):
    # Map of entity types to their gbd mappings.
    type_map = {
        'cause': causes,
        'covariate': covariates,
        'risk_factor': risk_factors,
        'alternative_risk_factor': alternative_risk_factors,
        'sequela': sequelae
    }
    key = EntityKey(key)
    return type_map[key.type][key.name]

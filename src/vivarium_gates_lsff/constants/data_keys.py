from typing import NamedTuple

from vivarium_public_health.utilities import TargetString


#############
# Data Keys #
#############

METADATA_LOCATIONS = 'metadata.locations'


class __Population(NamedTuple):
    LOCATION: str = 'population.location'
    STRUCTURE: str = 'population.structure'
    AGE_BINS: str = 'population.age_bins'
    DEMOGRAPHY: str = 'population.demographic_dimensions'
    TMRLE: str = 'population.theoretical_minimum_risk_life_expectancy'
    ACMR: str = 'cause.all_causes.cause_specific_mortality_rate'

    @property
    def name(self):
        return 'population'

    @property
    def log_name(self):
        return 'population'

POPULATION = __Population()


class __COVARIATES(NamedTuple):
    COVARIATE_LIVE_BIRTHS_BY_SEX: TargetString = TargetString('covariate.live_births_by_sex.estimate')

    @property
    def name(self):
        return 'covariates'

    @property
    def log_name(self):
        return self.name

COVARIATES = __COVARIATES()


class __DIARRHEA(NamedTuple):
    DIARRHEA_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.diarrheal_diseases.cause_specific_mortality_rate')
    DIARRHEA_PREVALENCE: TargetString = TargetString('cause.diarrheal_diseases.prevalence')
    DIARRHEA_INCIDENCE_RATE: TargetString = TargetString('cause.diarrheal_diseases.incidence_rate')
    DIARRHEA_REMISSION_RATE: TargetString = TargetString('cause.diarrheal_diseases.remission_rate')
    DIARRHEA_EXCESS_MORTALITY_RATE: TargetString = TargetString('cause.diarrheal_diseases.excess_mortality_rate')
    DIARRHEA_DISABILITY_WEIGHT: TargetString = TargetString('cause.diarrheal_diseases.disability_weight')
    DIARRHEA_RESTRICTIONS: TargetString = TargetString('cause.diarrheal_diseases.restrictions')

    @property
    def name(self):
        return 'diarrheal_diseases'

    @property
    def log_name(self):
        return self.name

DIARRHEA = __DIARRHEA()


class __MEASLES(NamedTuple):
    MEASLES_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.measles.cause_specific_mortality_rate')
    MEASLES_PREVALENCE: TargetString = TargetString('cause.measles.prevalence')
    MEASLES_INCIDENCE_RATE: TargetString = TargetString('cause.measles.incidence_rate')
    MEASLES_EXCESS_MORTALITY_RATE: TargetString = TargetString('cause.measles.excess_mortality_rate')
    MEASLES_DISABILITY_WEIGHT: TargetString = TargetString('cause.measles.disability_weight')
    MEASLES_RESTRICTIONS: TargetString = TargetString('cause.measles.restrictions')

    @property
    def name(self):
        return 'measles'

    @property
    def log_name(self):
        return self.name

MEASLES = __MEASLES()


class __NEURAL_TUBE_DEFECTS(NamedTuple):
    NEURAL_TUBE_DEFECTS_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.neural_tube_defects.cause_specific_mortality_rate')
    NEURAL_TUBE_DEFECTS_PREVALENCE: TargetString = TargetString('cause.neural_tube_defects.prevalence')
    NEURAL_TUBE_DEFECTS_BIRTH_PREVALENCE: TargetString = TargetString('cause.neural_tube_defects.birth_prevalence')
    NEURAL_TUBE_DEFECTS_EXCESS_MORTALITY_RATE: TargetString = TargetString('cause.neural_tube_defects.excess_mortality_rate')
    NEURAL_TUBE_DEFECTS_DISABILITY_WEIGHT: TargetString = TargetString('cause.neural_tube_defects.disability_weight')
    NEURAL_TUBE_DEFECTS_RESTRICTIONS: TargetString = TargetString('cause.neural_tube_defects.restrictions')

    @property
    def name(self):
        return 'neural_tube_defects'

    @property
    def log_name(self):
        return self.name

NEURAL_TUBE_DEFECTS = __NEURAL_TUBE_DEFECTS()


class __LBWSG(NamedTuple):
    LBWSG_DISTRIBUTION: TargetString = TargetString('risk_factor.low_birth_weight_and_short_gestation.distribution')
    LBWSG_CATEGORIES: TargetString = TargetString('risk_factor.low_birth_weight_and_short_gestation.categories')
    LBWSG_EXPOSURE: TargetString = TargetString('risk_factor.low_birth_weight_and_short_gestation.exposure')
    LBWSG_RELATIVE_RISK: TargetString = TargetString('risk_factor.low_birth_weight_and_short_gestation.relative_risk')
    LBWSG_PAF: TargetString = TargetString('risk_factor.low_birth_weight_and_short_gestation.population_attributable_fraction')

    @property
    def name(self):
        return 'low_birthweight_short_gestation'

    @property
    def log_name(self):
        return self.name

LBWSG = __LBWSG()


# Note: no mortality associated with vitamin A deficiency in this model
class __VITAMIN_A(NamedTuple):
    VITAMIN_A_DEFICIENCY_CATEGORIES: TargetString = TargetString('risk_factor.vitamin_a_deficiency.categories')
    VITAMIN_A_DEFICIENCY_EXPOSURE: TargetString = TargetString('risk_factor.vitamin_a_deficiency.exposure')
    VITAMIN_A_DEFICIENCY_RELATIVE_RISK: TargetString = TargetString('risk_factor.vitamin_a_deficiency.relative_risk')
    VITAMIN_A_DEFICIENCY_PAF: TargetString = TargetString('risk_factor.vitamin_a_deficiency.population_attributable_fraction')
    VITAMIN_A_DEFICIENCY_DISTRIBUTION: TargetString = TargetString('risk_factor.vitamin_a_deficiency.distribution')
    VITAMIN_A_DEFICIENCY_RESTRICTIONS: TargetString = TargetString('risk_factor.vitamin_a_deficiency.restrictions')
    VITAMIN_A_DEFICIENCY_DISABILITY_WEIGHT: TargetString = TargetString('cause.vitamin_a_deficiency.disability_weight')

    @property
    def name(self):
        return 'vitamin_a'

    @property
    def log_name(self):
        return self.name

VITAMIN_A = __VITAMIN_A()


class __IRON_DEFICIENCY(NamedTuple):
    IRON_DEFICIENCY_EXPOSURE: TargetString = TargetString('risk_factor.iron_deficiency.exposure')
    IRON_DEFICIENCY_EXPOSURE_SD: TargetString = TargetString('risk_factor.iron_deficiency.exposure_standard_deviation')
    IRON_DEFICIENCY_NO_ANEMIA_IRON_RESPONSIVE_PROPORTION: TargetString = TargetString('risk_factor.iron_deficiency.no_anemia_iron_responsive_proportion')
    IRON_DEFICIENCY_MILD_ANEMIA_IRON_RESPONSIVE_PROPORTION: TargetString = TargetString('risk_factor.iron_deficiency.mild_anemia_iron_responsive_proportion')
    IRON_DEFICIENCY_MODERATE_ANEMIA_IRON_RESPONSIVE_PROPORTION: TargetString = TargetString('risk_factor.iron_deficiency.moderate_anemia_iron_responsive_proportion')
    IRON_DEFICIENCY_SEVERE_ANEMIA_IRON_RESPONSIVE_PROPORTION: TargetString = TargetString('risk_factor.iron_deficiency.severe_anemia_iron_responsive_proportion')
    IRON_DEFICIENCY_MILD_ANEMIA_DISABILITY_WEIGHT: TargetString = TargetString('risk_factor.iron_deficiency.mild_anemia_disability_weight')
    IRON_DEFICIENCY_MODERATE_ANEMIA_DISABILITY_WEIGHT: TargetString = TargetString('risk_factor.iron_deficiency.moderate_anemia_disability_weight')
    IRON_DEFICIENCY_SEVERE_ANEMIA_DISABILITY_WEIGHT: TargetString = TargetString('risk_factor.iron_deficiency.severe_anemia_disability_weight')
    IRON_DEFICIENCY_RESTRICTIONS: TargetString = TargetString('risk_factor.iron_deficiency.restrictions')

    @property
    def name(self):
        return 'iron_deficiency'

    @property
    def log_name(self):
        return self.name

IRON_DEFICIENCY = __IRON_DEFICIENCY()


# Cause specific mortality rates for causes affected by LBWSG but not included as a Disease Model
class __CSMR_AFFECTEDBY_LBWSG(NamedTuple):
    URI_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.upper_respiratory_infections.cause_specific_mortality_rate')
    OTITIS_MEDIA_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.otitis_media.cause_specific_mortality_rate')
    MENINGITIS_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.meningitis.cause_specific_mortality_rate')
    ENCEPHALITIS_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.encephalitis.cause_specific_mortality_rate')
    NEONATAL_PRETERM_BIRTH_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.neonatal_preterm_birth.cause_specific_mortality_rate')
    NEONATAL_ENCEPHALOPATHY_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.neonatal_encephalopathy_due_to_birth_asphyxia_and_trauma.cause_specific_mortality_rate')
    NEONATAL_SEPSIS_AND_OTHER_NEONATAL_INFECTIONS_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.neonatal_sepsis_and_other_neonatal_infections.cause_specific_mortality_rate')
    HEMOLYTIC_DISEASE_AND_OTHER_NEONATAL_JAUNDICE_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.hemolytic_disease_and_other_neonatal_jaundice.cause_specific_mortality_rate')
    OTHER_NEONATAL_DISORDERS_CAUSE_SPECIFIC_MORTALITY_RATE: TargetString = TargetString('cause.other_neonatal_disorders.cause_specific_mortality_rate')

    @property
    def name(self):
        return 'affected_by_lbwsg_not_modeled'

    @property
    def log_name(self):
        return self.name

CSMR_AFFECTEDBY_LBWSG = __CSMR_AFFECTEDBY_LBWSG()


class __ZINC(NamedTuple):
    ZINC_DEFICIENCY_CATEGORIES: TargetString = TargetString('risk_factor.zinc_deficiency.categories')
    ZINC_DEFICIENCY_EXPOSURE: TargetString = TargetString('risk_factor.zinc_deficiency.exposure')
    ZINC_DEFICIENCY_RELATIVE_RISK: TargetString = TargetString('risk_factor.zinc_deficiency.relative_risk')
    ZINC_DEFICIENCY_PAF: TargetString = TargetString('risk_factor.zinc_deficiency.population_attributable_fraction')
    ZINC_DEFICIENCY_DISTRIBUTION: TargetString = TargetString('risk_factor.zinc_deficiency.distribution')
    ZINC_DEFICIENCY_RESTRICTIONS: TargetString = TargetString('risk_factor.zinc_deficiency.restrictions')

    @property
    def name(self):
        return 'zinc'

    @property
    def log_name(self):
        return self.name

ZINC = __ZINC()


MAKE_ARTIFACT_KEY_GROUPS = [
    POPULATION,
    COVARIATES,
    DIARRHEA,
    MEASLES,
    NEURAL_TUBE_DEFECTS,
    LBWSG,
    VITAMIN_A,
    IRON_DEFICIENCY,
    CSMR_AFFECTEDBY_LBWSG,
    ZINC,
]

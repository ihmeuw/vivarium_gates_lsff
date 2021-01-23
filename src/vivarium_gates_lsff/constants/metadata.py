from typing import NamedTuple


####################
# Project metadata #
####################

PROJECT_NAME = 'vivarium_gates_lsff'
CLUSTER_PROJECT = 'proj_cost_effect'

CLUSTER_QUEUE = 'all.q'
MAKE_ARTIFACT_MEM = '10G'
MAKE_ARTIFACT_CPU = '1'
MAKE_ARTIFACT_RUNTIME = '3:00:00'
MAKE_ARTIFACT_SLEEP = 10


class __Locations(NamedTuple):
    TANZANIA: str = 'United Republic of Tanzania'
    UGANDA: str = 'Uganda'

LOCATIONS = __Locations()

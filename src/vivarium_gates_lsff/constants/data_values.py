from typing import NamedTuple


class __HEMOGLOBIN_DISTRIBUTION(NamedTuple):
    WEIGHT_GAMMA: float = 0.4
    WEIGHT_GUMBEL: float = 0.6
    EXPOSURE_MAX: float = 220.


HEMOGLOBIN_DISTRIBUTION = __HEMOGLOBIN_DISTRIBUTION()


ANEMIA_SEQUELAE_ID_MAP = {
    'mild': (
        # responsive
        [
            144,
            172,
            177,
            182,
            206,
            240,
            438,
            442,
            525,
            537,
            1004,
            1008,
            1012,
            1016,
            1020,
            1024,
            1028,
            1032,
            1106,
            1361,
            1373,
            1385,
            1397,
            1409,
            1421,
            1433,
            1445,
            4952,
            4955,
            4976,
            4985,
            4988,
            5009,
            5225,
            5228,
            5249,
            5252,
            5273,
            5276,
            5393,
            5567,
            5579,
            5627,
            5648,
            5651,
            5654,
            5678,
            5699,
            5702,
            7202,
            7214,
            22989,
            22990,
            22991,
            22992,
            22993,
            23030,
            23034,
            23038,
            23042,
            23046        ],
        # non_responsive
        [
            531,
            645,
            648,
            651,
            654,
            1057,
            1061,
            1065,
            1069,
            1079,
            1089,
            1099,
            1120,
            5018,
            5027,
            5036,
            5051,
            5063,
            5075,
            5087,
            5099,
            5111,
            5123,
            5606,
            5705,
        ]
    ),
    'moderate': (
        # responsive
        [145,
         173,
         178,
         183,
         207,
         241,
         439,
         443,
         526,
         538,
         1005,
         1009,
         1013,
         1017,
         1021,
         1025,
         1029,
         1033,
         1107,
         1364,
         1376,
         1388,
         1400,
         1412,
         1424,
         1436,
         1448,
         4958,
         4961,
         4979,
         4991,
         4994,
         5012,
         5219,
         5222,
         5243,
         5246,
         5267,
         5270,
         5396,
         5570,
         5582,
         5630,
         5657,
         5660,
         5663,
         5681,
         5708,
         5711,
         5714,
         7205,
         7217,
         22999,
         23000,
         23001,
         23002,
         23003,
         23031,
         23035,
         23039,
         23043,
         23047],
        # non_responsive
        [532,
         646,
         649,
         652,
         655,
         1058,
         1062,
         1066,
         1070,
         1080,
         1090,
         1100,
         1121,
         5021,
         5030,
         5039,
         5054,
         5066,
         5078,
         5090,
         5102,
         5114,
         5126,
         5609]
    ),
    'severe': (
        # responsive
        [146,
         174,
         179,
         184,
         208,
         242,
         440,
         444,
         527,
         539,
         1006,
         1010,
         1014,
         1018,
         1022,
         1026,
         1030,
         1034,
         1108,
         1367,
         1379,
         1391,
         1403,
         1415,
         1427,
         1439,
         1451,
         4964,
         4967,
         4982,
         4997,
         5000,
         5015,
         5213,
         5216,
         5237,
         5240,
         5261,
         5264,
         5399,
         5573,
         5585,
         5633,
         5666,
         5669,
         5672,
         5717,
         5720,
         5723,
         5684,
         7208,
         7220,
         23009,
         23010,
         23011,
         23012,
         23013,
         23032,
         23036,
         23040,
         23044,
         23048],
        # non_responsive
        [5129,
         533,
         1059,
         1060,
         1063,
         1064,
         1067,
         1068,
         1071,
         1074,
         1075,
         1077,
         1081,
         1083,
         1085,
         1087,
         1091,
         1093,
         1095,
         1097,
         1101,
         1122,
         647,
         650,
         653,
         656,
         5024,
         5033,
         5042,
         5057,
         5069,
         5081,
         5093,
         5612,
         5105,
         5117]
    )
}

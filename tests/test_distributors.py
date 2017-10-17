import unittest

import pandas as pd
from pandas.testing import assert_frame_equal
# import numpy as np

from petri_dish.distributors import DirectedDistributor


class DistributorTestCase(unittest.TestCase):
    def setUp(self):
        self.test_subjects = pd.DataFrame(
            {
                'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'market_id': [1, 1, 2, 3, 2, 1, 3, 2, 1, 2],
                'has_server_skill': [True, True, False, True, True, True, False, False, True, False],
                'num_app_accessed': [9, 1, 3, 2, 6, 23, 0, 3, 9, 2],
                'treatment_group': [-1, 0, None, None, 0, None, 0, None, None, None]
            }
        )
        self.test_directed_distributor = DirectedDistributor(
            [-1, 0],  # treatment_group_ids,
            'treatment_group',  # treatment_assignment_col,
            ['market_id'],  # balancing_features,
            ['has_server_skill'],  # discrete_features,
            ['num_app_accessed']  # continuous_features
        )
        self.test_assignments = pd.DataFrame(
            {
                'level_0': [1, 1, 2, 2, 3, 3],
                'level_1': [-1, 0, -1, 0, -1, 0],
                'treatment_group': [1.0, 1.0, 0.0, 1.0, 0.0, 1.0]
            }
        )

    def test_get_current_assignments_returns_assignments_count_successfully(self):
        expected = self.test_assignments
        actual = self.test_directed_distributor._get_current_assignments(self.test_subjects)
        assert_frame_equal(expected, actual.reset_index())

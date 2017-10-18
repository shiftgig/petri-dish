import unittest

import pandas as pd
from pandas.testing import assert_series_equal
import numpy as np

from petri_dish.distributors import DirectedDistributor


class DistributorTestCase(unittest.TestCase):
    def setUp(self):
        # Set up a random seed for the processes that involve randomization
        np.random.seed(10)
        self.test_subjects = pd.DataFrame(
            {
                'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'market_id': [1, 1, 2, 3, 2, 1, 3, 2, 1, 2],
                'has_server_skill': [True, True, False, True, True, True, False, False, True, False],
                'num_app_accessed': [9, 1, 3, 2, 6, 23, 0, 3, 9, 2],
                'treatment_group': [-1, 0, None, None, 0, None, 0, None, None, None]
            }
        )
        self.candidate_test_subjects_data = pd.DataFrame(
            {
                'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'market_id': [1, 1, 2, 3, 2, 1, 3, 2, 1, 2],
                'has_server_skill': [True, True, False, True, True, True, False, False, True, False],
                'num_app_accessed': [9, 1, 3, 2, 6, 23, 0, 3, 9, 2],
                'treatment_group': [-1.0, 0.0, -1.0, -1.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0]
            }
        )
        self.test_directed_distributor = DirectedDistributor(
            [-1, 0],               # treatment_group_ids,
            'treatment_group',     # treatment_assignment_col,
            ['market_id'],         # balancing_features,
            ['has_server_skill'],  # discrete_features,
            ['num_app_accessed']   # continuous_features
        )
        test_assignments_index = pd.MultiIndex.from_product(
            [[1, 2, 3]] + [[-1, 0]],
            names=(['market_id', 'treatment_group'])
        )
        test_assignments_index = test_assignments_index.map(tuple)
        test_assignments = self.test_subjects.groupby(['market_id'])['treatment_group'].value_counts()
        self.test_assignment_balance = test_assignments.reindex(test_assignments_index).fillna(0).sort_index()

    def test_get_current_assignment_balance_returns_assignments_count_successfully(self):
        expected = self.test_assignment_balance
        actual = self.test_directed_distributor.get_current_assignment_balance(self.test_subjects)
        assert_series_equal(expected, actual)

    def test_get_current_assignment_balance_returns_series_type(self):
        result = self.test_directed_distributor.get_current_assignment_balance(self.test_subjects)
        self.assertTrue(isinstance(result, pd.Series))

    def test_generate_candidate_assignments_returns_correct_assignments(self):
        expected = self.candidate_test_subjects_data['treatment_group']
        result = self.test_directed_distributor.generate_candidate_assignments(
            self.test_subjects,
            self.test_assignment_balance
        )
        actual = result[0]['treatment_group']
        assert_series_equal(expected, actual)

    def test_generate_candidate_assignments_returns_tuple(self):
        result = self.test_directed_distributor.generate_candidate_assignments(
            self.test_subjects,
            self.test_assignment_balance
        )
        self.assertTrue(isinstance(result, tuple))

    def test_calculate_min_p_value_distribution_independence_returns_expected_p_value(self):
        expected = 0.80239520915240781
        actual = self.test_directed_distributor.calculate_min_p_value_distribution_independence(
            self.candidate_test_subjects_data
        )
        self.assertEqual(expected, actual)

    @unittest.skip("Not implemented")
    def test_assign_group_returns_successfully(self):
        result = self.test_directed_distributor.assign_group(self.test_subjects)
        print(result)

    @unittest.skip("Not implemented")
    def test_assign_group_copies_input_data_by_value(self):
        pass

    @unittest.skip("Not implemented")
    def test_assign_group_returns_tuple(self):
        pass

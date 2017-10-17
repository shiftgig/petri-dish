
from abc import ABCMeta, abstractmethod
import pandas as pd

from stat_tools import chi_squared, ttest


class AbstractBaseDistributor(object):
    __metaclass__ = ABCMeta

    def __init__(self, treatment_group_ids):
        self.treatment_group_ids = treatment_group_ids

    @abstractmethod
    def assign_group(self, subjects):
        """
        Assigns each of the experimentation subjects (without a previous assignment) to a treatment group
        (control is also considered a treatment group here, with no treatment applied).

        Parameters
        ----------
        subjects: pandas DataFrame | table with all experimentation subjects, assigned and unassigned. With features.

        Returns
        -------
        selected_assignments: pandas dataFrame | table with all experimentation subjects assigned to a treatment group.
        max_min_p: float | the min p_value for the selected assignments for all the subjects features.
        """
        pass


# Stochastic Distributor object | uses law of large numbers principle
class StochasticDistributor(AbstractBaseDistributor):
    """
    The assignment method for this subclass is stochastic and generally should be used when the law
    of large numbers is observable for each group, namely, when there is a large quantity of experimentation
    subjects on each group.
    """
    def assign_group(self, subjects):
        # TODO: implement
        pass


# Directed Distributor object | directs the distributions based on subject's characteristics
class DirectedDistributor(AbstractBaseDistributor):
    """
    The assignment method for this subclass is directed. This means that an experimentation subject will be
    assigned to a treatment group based on the total balance of the system in terms of the subject's characteristics.
    This method should be generally used when a small number of subjects per treatment group is expected, and therefore,
    where the law of large numbers isn't observable.
    """
    random_attempts = 1000

    def __init__(
        self,
        treatment_group_ids,
        treatment_assignment_col,
        balancing_features,
        discrete_features,
        continuous_features
    ):
        AbstractBaseDistributor.__init__(self, treatment_group_ids)
        self.treatment_assignment_col = treatment_assignment_col
        self.balancing_features = balancing_features
        self.discrete_features = discrete_features
        self.continuous_features = continuous_features

    def assign_group(self, subjects):
        # copy originall dataframe since we are going to change them
        subjects_copy = subjects.copy()

        # get the count of each treatment in each of the blocking bins
        current_assignments_balance = self.get_current_assignment_balance(subjects_copy)

        max_min_p = 0
        # Try several randomized assignments (with guaranteed balance across blocking variables) and choose the assignment
        for randomization in range(self.random_attempts):

            # Generate candidate assignments
            (candidate_subjects_copy, candidate_assignments_balance) = self.generate_candidate_assignments(
                subjects_copy,
                current_assignments_balance
            )

            # Test the distribution quality of those assignments
            min_p_value = self.calculate_min_p_value_distribution_independence(candidate_subjects_copy)

            # Keep current trial if the distribution is better (evenly across treatment groups) than the previous one
            if min_p_value > max_min_p:
                selected_assignments = candidate_subjects_copy
                max_min_p = min_p_value

        return selected_assignments, max_min_p

    def get_current_assignment_balance(self, subjects_df, count_nulls=False):

        # Get a multi index that includes all combination of blocking variables and treatments
        joint_index = pd.MultiIndex.from_product(
            [subjects_df[col].unique() for col in self.balancing_features] + [self.treatment_group_ids],
            names=(self.balancing_features + [self.treatment_assignment_col])
        )
        joint_block = joint_index.map(tuple)

        # Remove nulls if not counting
        if not count_nulls:
            subjects_df = subjects_df.dropna(subset=[self.treatment_assignment_col])

        if subjects_df.empty:
            counts = pd.Series(0, index=joint_index, dtype=float, name=self.treatment_assignment_col)
        else:
            # Count the number of occurences of each value in each bin
            counts = subjects_df.groupby(self.balancing_features)[self.treatment_assignment_col].value_counts()
            # And in missing bins
            counts = counts.reindex(joint_block).fillna(0)

        return counts.sort_index()

    def generate_candidate_assignments(self, subjects, assignments_balance):
        """
        Generates candidate assignments for all the unassigned test subjects using the pre-existing assignments
        and the balancing features.
        """
        candidate_subjects_assignments = subjects.copy()
        candidate_assignments_balance = assignments_balance.copy()

        # for each unassigned row
        for ind, subject in candidate_subjects_assignments[candidate_subjects_assignments[
            self.treatment_assignment_col].isnull()
        ].iterrows():
            # determine which bin of the blocking variables the subject belongs to
            block_index = tuple(subject.loc[self.balancing_features])
            # choose a random assignment balanced across within the bin
            assignment = (
                candidate_assignments_balance
                .loc[block_index]   # Get the number of assignments to each treatment for the bin
                .sample(frac=1)
                .argmin()
            )
            candidate_subjects_assignments.loc[ind, self.treatment_assignment_col] = assignment
            candidate_assignments_balance.loc[block_index + (assignment,)] += 1

        return (candidate_subjects_assignments, candidate_assignments_balance)

    def calculate_min_p_value_distribution_independence(self, candidate_subjects_data):
        """
        Calculates minimum p-value for any discrete (categorical) and continous variable across treatments.

        Ideally the distribution of each feature across treatment groups should not be independent,
        thus statistically we want the p-value to be high.

        (low p-value indicating lower confidence interval to reject null hypothesis of
        independence in the distribution).
        """
        min_p = 1

        # p-values for discrete balancing variables
        for cat in self.balancing_features + self.discrete_features:
            p = chi_squared(
                candidate_subjects_data[cat],
                candidate_subjects_data[self.treatment_assignment_col]
            )
            min_p = min(min_p, p)

        # p-values for continuous balancing variables
        for t_ind1 in range(len(self.treatment_group_ids)):

            treatment1_slice = candidate_subjects_data[
                candidate_subjects_data[self.treatment_assignment_col] == self.treatment_group_ids[t_ind1]
            ]

            for t_ind2 in range(t_ind1 + 1, len(self.treatment_group_ids)):

                treatment2_slice = candidate_subjects_data[candidate_subjects_data[
                    self.treatment_assignment_col] == self.treatment_group_ids[t_ind2]
                ]

                for col in self.continuous_features:
                    if (treatment1_slice[col].notnull().sum() > 1) and (treatment2_slice[col].notnull().sum > 1):
                        p = ttest(treatment1_slice[col], treatment2_slice[col])
                        min_p = min(min_p, p)

        return min_p

    def set_random_attempts(self, attempts):
        self.random_attempts = attempts

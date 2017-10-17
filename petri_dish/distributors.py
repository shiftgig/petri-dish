
from abc import ABCMeta
import numpy as np


# Distributor object | abstract class
#   properties
#       treatment groups (including control group) [number of groups or actual group number]
class AbstractBaseDistributor(object):
    __metaclass__ = ABCMeta

    def __init__(self, treatment_groups):
        treatment_groups = treatment_groups


# Stochastic Distributor object | uses law of large numbers principle
class StochasticDistributor(AbstractBaseDistributor):
    """
    The assignment method for this subclass is stochastic and generally should be used when the law
    of large numbers is observable for each group, namely, when there is a large quantity of experimentation
    subjects on each group.
    """
    def assign_group(self, subjects):
        """
        Assigns each of the experimentation subjects to a treatment group (control is also considered a treatment
        group here, with no treatment applied).

        Parameters
        ----------
        subjects: pandas DataFrame | table of experimentation subjects

        Returns
        -------
        group_assignment: pandas Series | a series with all the assignments with same height as the subjects table.
        """
        pass


# Directed Distributor object | directs the distributions based on subject's characteristics
class DirectedDistributor(AbstractBaseDistributor):
    """
    The assignment method for this subclass is directed. This means that an experimentation subject will be
    assigned to a group based on the total balance of the system in terms of the subject's characteristics. This
    method should be generally used when a small number of subjects per treatment group is expected, and therefore,
    where the law of large numbers isn't observable.
    """
    random_attempts = 5000

    def __init__(self, treatment_groups, pre_assigned_subjects):
        AbstractBaseDistributor.__init__(self, treatment_groups)
        self.pre_assigned_subjects = pre_assigned_subjects

    def assign_group(
        self,
        subjects,
        blocking_vars,
        discrete_variables,
        continuous_variables,
    ):
        """
        Assigns each of the new experimentation subjects to a treatment group (control is also considered a treatment
        group here, with no treatment applied).

        Parameters
        ----------
        subjects
        blocking_vars
        discrete_variables
        continuous_variables

        Returns
        -------
        group_assignment: pandas Series | a series with all the assignments with same height as the subjects table.
        """
        # copy originall dataframe since we are going to change them
        subjects_df = subjects.copy()

        # get the count of each treatment in each of the blocking bins
        current_balance = count_values_in_bins(subjects_df, block_vars, treatment_col, values=treatments)
        current_balance = current_balance.sort_index()

        # Try several randomized assignments (with guaranteed balance across blocking variables) and choose the assignment
        # for which the balancing variables are most equally distributed across treatments
        max_min_p = 0
        for randomization in range(num_attempts):
            # initiallize to randomization of treatment assignments and balance
            possible_treatment = subjects_df.copy()
            possible_balance = current_balance.copy()

            # for each unassigned row
            for ind, subject in possible_treatment[possible_treatment[treatment_col].isnull()].iterrows():
                # determine which bin of the blocking variables the subject belongs to
                block_index = tuple(subject.loc[block_vars])
                # choose a random assignment balanced across within the bin
                assignment = (
                    possible_balance
                    .loc[block_index]   # Get the number of assignments to each treatment for the bin
                    .sample(frac=1)
                    .argmin()
                )
                possible_treatment.loc[ind, treatment_col] = assignment
                possible_balance.loc[block_index + (assignment,)] += 1

            # Determine how different the distribution of each balancing variable is across treatment groups
            # We want them to be the same, thus statistically we want the p value to be high.
            # We will assess this by the minimum p value for any balancing variable across treatments
            min_p = 1

            # Assess p-values for categorical balancing variables
            for cat in block_vars + cat_vars:
                _, p, _ = chi_squared(possible_treatment[cat], possible_treatment[treatment_col])
                min_p = min(min_p, p)

            # Assess p-values for continuous balancing variables
            for t_ind1 in range(len(treatments)):
                treatment1_slice = possible_treatment[possible_treatment[treatment_col] == treatments[t_ind1]]
                for t_ind2 in range(t_ind1 + 1, len(treatments)):
                    treatment2_slice = possible_treatment[possible_treatment[treatment_col] == treatments[t_ind2]]
                    for col in cont_vars:
                        if (treatment1_slice[col].notnull().sum() > 1) and (treatment2_slice[col].notnull().sum > 1):
                            _, p = ttest(treatment1_slice[col], treatment2_slice[col])
                            min_p = min(min_p, p)

            # Keep current trial if it has a higher min_p value
            if min_p > max_min_p:
                selected_assignments = possible_treatment
                max_min_p = min_p
        return selected_assignments, max_min_p

    def set_random_attempts(self, attempts):
        self.random_attempts = attempts


from abc import ABCMeta


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
    def assign_group(self, subjects, treatment_col):
        """
        Assigns each of the experimentation subjects to a treatment group (control is also considered a treatment
        group here, with no treatment applied).

        Parameters
        ----------
        subjects: pandas DataFrame | table of experimentation subjects
        treatment_col: string | the key name for the column used to indicate the tratment group membrship.
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

    def assign_group(
        self,
        subjects,
        treatment_col,
        blocking_vars,
        discrete_variables,
        continuous_variables,
    ):
        """
        Assigns each of the experimentation subjects to a treatment group (control is also considered a treatment
        group here, with no treatment applied).

        Parameters
        ----------
        subjects
        treatment_col
        blocking_vars
        discrete_variables
        continuous_variables
        """
        pass

    def set_random_attempts(self, attempts):
        self.random_attempts = attempts



# Distributor object | abstract class
#   properties
#       treatment groups (including control group) [number of groups or actual group number]
class Distributor(object):
    def __init__(self, treatment_groups):
        treatment_groups = treatment_groups


# Stochastic Distributor object | uses law of large numbers principle
class StochasticDistributor(Distributor):
    def assign_group(self, subjects, treatment_col):
        pass


# Directed Distributor object | directs the distributions based on subject's characteristics
class DirectedDistributor(Distributor):
    random_attempts = 5000

    def assign_group(
        self,
        subjects,
        treatment_col,
        blocking_vars,
        discrete_variables,
        continuous_variables,
    ):
        pass

    def set_random_attempts(self, attempts):
        self.random_attempts = attempts

import pandas as pd
import scipy as sp


def chi_squared(series1, series2):
    """
    Applies a chi squared statistic to test the null hypothesis that two categorical Series are independently
    distributed.
    Parameters
    ----------
    series1: pandas Series | The first series of category-like values.
    series2: pandas Series | The second series of category-like values
    Returns
    ----------
    chi2: float | The chi squared test statistic
    p: float | The p-value of the t-test
    dof: int | degrees-of-freedom
    """
    joint_distribution = pd.crosstab(series1.astype(str), series2.astype(str))
    chi2, p, dof, _ = sp.stats.chi2_contingency(joint_distribution)
    return p


def ttest(series1, series2, equal_var=False):
    """
    Applies a ttest to test the null hypothesis that two Series of continuous values have equal mean.
    Parameters
    ----------
    series1: pandas Series | The first series of category-like values.
    series2: pandas Series | The second series of category-like values
    equal_var: bool | whether or not to assume equal variance in calculating the t-test
    Returns
    ----------
    t: float | The t-statistic
    p: float | The p-value of the t-test
    """
    t, p = sp.stats.ttest_ind(series1.values, series2.values, equal_var=equal_var, nan_policy='omit')
    return p

import numpy as np


def demand_shock(
    base_demand,
    shock_std=0.05,
    active=True
):
    """
    Applies a stochastic demand shock.

    Parameters
    ----------
    base_demand : float
        Baseline market demand.
    shock_std : float
        Standard deviation of demand shock.
    active : bool
        Whether shocks are enabled.

    Returns
    -------
    shocked_demand : float
        Adjusted market demand.
    """

    if not active:
        return base_demand

    shock = np.random.normal(loc=0.0, scale=shock_std)
    shocked_demand = base_demand * (1 + shock)

    return max(shocked_demand, 0.0)


def cost_shock(
    marginal_cost,
    shock_std=0.03,
    active=True
):
    """
    Applies a stochastic cost shock.

    Parameters
    ----------
    marginal_cost : float
        Baseline marginal cost.
    shock_std : float
        Standard deviation of cost shock.
    active : bool
        Whether shocks are enabled.

    Returns
    -------
    shocked_cost : float
        Adjusted marginal cost.
    """

    if not active:
        return marginal_cost

    shock = np.random.normal(loc=0.0, scale=shock_std)
    shocked_cost = marginal_cost * (1 + shock)

    return max(shocked_cost, 0.0)

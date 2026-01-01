import numpy as np


def compute_demand(
    prices,
    innovation,
    base_demand=1000,
    price_elasticity=1.5,
    innovation_weight=0.3
):
    """
    Computes firm-level demand and market shares in a competitive market.

    Parameters
    ----------
    prices : np.ndarray
        Array of firm prices.
    innovation : np.ndarray
        Array of cumulative innovation levels.
    base_demand : float
        Total market demand.
    price_elasticity : float
        Sensitivity of demand to price differences.
    innovation_weight : float
        Weight of innovation in consumer preference.

    Returns
    -------
    firm_demand : np.ndarray
        Quantity demanded for each firm.
    market_share : np.ndarray
        Market share of each firm.
    """

    n_firms = len(prices)

    # Normalize innovation to avoid scale dominance
    if np.sum(innovation) > 0:
        norm_innovation = innovation / np.max(innovation)
    else:
        norm_innovation = np.zeros(n_firms)

    # Consumer utility (lower price + higher innovation = higher utility)
    utility = (
        -price_elasticity * prices
        + innovation_weight * norm_innovation
    )

    # Softmax choice model for market share
    exp_utility = np.exp(utility - np.max(utility))
    market_share = exp_utility / np.sum(exp_utility)

    # Allocate total demand
    firm_demand = base_demand * market_share

    return firm_demand, market_share

def compute_cost(
    quantity,
    marginal_cost=20.0,
    innovation_spend=0.0,
    fixed_cost=0.0,
):
    """
    Computes total production cost for a firm.

    Parameters
    ----------
    quantity : float
        Quantity produced / sold by the firm.
    marginal_cost : float
        Cost per unit of output.
    innovation_spend : float
        Investment in innovation (R&D).
    fixed_cost : float
        Fixed operating cost (optional).

    Returns
    -------
    total_cost : float
        Total cost incurred by the firm.
    """

    variable_cost = marginal_cost * quantity
    total_cost = variable_cost + innovation_spend + fixed_cost

    return total_cost

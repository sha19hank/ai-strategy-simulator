def industry_pressure(
    rivalry=0.5,
    threat_of_entry=0.3,
    substitutes=0.3,
    complements=0.2
):
    """
    Computes an industry-level competitive pressure index.

    Parameters
    ----------
    rivalry : float
        Intensity of competition among incumbents (0–1).
    threat_of_entry : float
        Ease of new firms entering the market (0–1).
    substitutes : float
        Availability of substitute products (0–1).
    complements : float
        Strength of complementary goods (0–1).

    Returns
    -------
    pressure : float
        Net industry pressure affecting firm profitability.
    """

    pressure = (
        rivalry
        + threat_of_entry
        + substitutes
        - complements
    )

    return max(pressure, 0.0)


def apply_strategy_pressure(
    profit,
    pressure,
    sensitivity=0.1
):
    """
    Adjusts firm profit based on industry pressure.

    Parameters
    ----------
    profit : float
        Firm's raw economic profit.
    pressure : float
        Industry pressure index.
    sensitivity : float
        Strength of pressure impact.

    Returns
    -------
    adjusted_profit : float
        Profit after strategic pressure.
    """

    adjusted_profit = profit * (1 - sensitivity * pressure)
    return adjusted_profit

import numpy as np


def innovation_effect(
    cumulative_innovation,
    max_effect=0.3,
    diminishing_returns=True
):
    """
    Computes the productivity / demand advantage gained from innovation.

    Parameters
    ----------
    cumulative_innovation : float or np.ndarray
        Total accumulated innovation investment of a firm.
    max_effect : float
        Maximum possible innovation advantage.
    diminishing_returns : bool
        Whether innovation exhibits diminishing returns.

    Returns
    -------
    effect : float or np.ndarray
        Innovation multiplier applied to demand or cost.
    """

    if diminishing_returns:
        # Log-based diminishing returns
        effect = max_effect * np.log1p(cumulative_innovation)
    else:
        # Linear effect (not recommended, but provided for experimentation)
        effect = max_effect * cumulative_innovation

    return effect

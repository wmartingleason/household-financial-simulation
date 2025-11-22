"""
Configuration file for backend risk engine.

Contains stochastic model parameters estimated from SIPP data.
These parameters define the income volatility model used in Monte Carlo simulations.
"""

# Stochastic income model parameters
MODEL_PARAMS = {
    'lambda': .273,                # Rate of Poisson jumps
    'jump_median_pct': 0.232,      # Median percentage jump in income
    'jump_q25': 0.115,             # 25th percentile of jump sizes
    'jump_q75': 0.545,             # 75th percentile of jump sizes
    'prob_upward': 0.5,            # Probability that income jump is upward (50%)
}

# Default simulation parameters
DEFAULT_N_SIMULATIONS = 10000

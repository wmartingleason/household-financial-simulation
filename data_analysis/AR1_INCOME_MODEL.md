# AR(1) Income Model Documentation

## Overview

This module implements an AR(1) model with household-specific mean reversion for modeling income dynamics in financial risk simulations. The model estimates parameters from SIPP household income data and generates realistic income trajectories that preserve both within-household volatility and cross-sectional heterogeneity.

## Model Specification

The income process for household i follows:

```
log(Y_{it}) = μ_i + ρ(log(Y_{i,t-1}) - μ_i) + ε_{it}
```

where:
- **Y_{it}**: Household i's income at time t
- **μ_i**: Household-specific long-run mean (equilibrium log income)
- **ρ**: Persistence parameter (0 < ρ < 1)
- **ε_{it}**: i.i.d. normal shocks with variance σ²

### Household-Specific Means

Each household reverts to its own equilibrium μ_i, which is approximated by the household's initial income. This ensures that the cross-sectional income distribution remains stable over time, avoiding unrealistic convergence to a single population mean.

## Parameter Estimation

### Method

Parameters are estimated using within-household fixed effects to separate cross-sectional heterogeneity from time-series dynamics:

1. For each household, calculate the household-specific mean: μ_i = mean(log(Y_{it}))
2. Demean the data: y*_{it} = log(Y_{it}) - μ_i
3. Estimate ρ from demeaned data: ρ_i = Cov(y*_{it}, y*_{i,t-1}) / Var(y*_{i,t-1})
4. Calculate residual standard deviation: σ_i
5. Aggregate across households using median: ρ = median(ρ_i), σ = median(σ_i)

This approach avoids the bias that arises from pooling data across households with different equilibrium income levels.

### Estimated Parameters (SIPP 2021-2024)

From 673 households:

| Parameter | Value | Interpretation |
|-----------|-------|----------------|
| ρ | 0.892 | Autocorrelation coefficient |
| σ | 0.108 | Standard deviation of monthly shocks |
| Half-life | 6.1 months | Time for shock to decay to 50% |

## Implementation

### Basic Usage

```python
from src.ar1_model import AR1Model

# Estimate parameters from data
params = AR1Model.estimate_ar1_parameters(raw_data)

# Simulate income trajectory
initial_income = 5000  # serves as household equilibrium
trajectory = AR1Model.simulate_trajectory(
    initial_income=initial_income,
    n_months=24,
    params=params,
    seed=42
)
```

### Integration with Risk Engine

```python
from src.risk_engine import RiskEngine

risk_engine = RiskEngine(
    initial_fund=10000,
    monthly_expenses=3000,
    initial_income=5000,
    n_months=24,
    n_simulations=1000
)

risk_metrics = risk_engine.run_risk_assessment(params)
```

## Model Properties

### Stationarity

With ρ < 1, the process is mean-reverting and stationary around each household's equilibrium:

- Unconditional mean: E[log(Y_{it})] = μ_i
- Unconditional variance: Var[log(Y_{it})] = σ²/(1-ρ²) ≈ 0.057
- Autocorrelation at lag k: Corr[log(Y_{it}), log(Y_{i,t-k})] = ρ^k

## Validation Results

### Coefficient of Variation

Comparison between real SIPP data (664 households) and simulated data (1000 trajectories, 48 months):

| Statistic | Real Data | Simulated |
|-----------|-----------|-----------|
| Median CV | 0.203 | 0.178 |
| Mean CV | 0.283 | 0.183 |
| 25th percentile | 0.088 | 0.152 |
| 75th percentile | 0.393 | 0.210 |

The simulated median CV matches real data at 88%. The difference is partly due to the continuous nature of the AR(1) process versus discrete income changes observed in panel data (approximately 27% of months show no change). The  stationarity of the panel data is caused by unreported changes in some cases, and actual stability of income in others.

### Income Dynamics

The model reproduces realistic income persistence:

- Real data median autocorrelation: 0.875
- Model parameter ρ: 0.892

## Mathematical Details

### Derivation of Variance Formula

For the stationary distribution:

```
Var[log(Y_{it})] = Var[ρ log(Y_{i,t-1}) + ε_{it}]
                 = ρ² Var[log(Y_{it})] + σ²
```

Solving for the unconditional variance:

```
Var[log(Y_{it})] = σ² / (1 - ρ²)
```

### Shock Persistence

A shock ε_{it} affects future income according to:

```
∂log(Y_{i,t+k})/∂ε_{it} = ρ^k
```

With ρ = 0.892:
- After 1 month: 89% of shock remains
- After 6 months: 50% of shock remains
- After 12 months: 25% of shock remains

### Limitations

- Does not model permanent structural changes (career transitions, disabilities)
- Assumes symmetric shocks (no skewness)
- No discrete jump component for rare large events
- Homogeneous dynamics (all households share same ρ and σ)

## Files

- `src/ar1_model.py`: Core implementation
- `src/simulation.py`: Integration with simulation framework
- `test_variance_preservation.py`: Validation script for cross-sectional variance
- `AR1_INCOME_MODEL.md`: This documentation

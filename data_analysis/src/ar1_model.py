"""
AR(1) model with household-specific mean reversion for income dynamics.

Model specification:
    log(Y_{it}) = μ_i + ρ(log(Y_{i,t-1}) - μ_i) + ε_{it}

where μ_i is household i's equilibrium (approximated by initial income),
ρ is the persistence parameter, and ε_{it} ~ N(0, σ²).
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional


class AR1Model:
    """AR(1) model with household-specific mean reversion."""

    @staticmethod
    def estimate_ar1_parameters(raw_data: pd.DataFrame) -> Dict[str, float]:
        """
        Estimate AR(1) parameters using within-household fixed effects.

        For each household, we estimate the AR(1) process on demeaned data
        to separate cross-sectional heterogeneity from time-series dynamics.

        Args:
            raw_data: Raw household income data with columns SSUID, SHHADID, THTOTINC

        Returns:
            Dictionary with model parameters (rho, mu, sigma, initial_income_median, etc.)
        """
        household_rhos = []
        household_sigmas = []
        household_means = []
        all_residuals = []

        for (ssuid, shhadid), group in raw_data.groupby(['SSUID', 'SHHADID']):
            income = group['THTOTINC'].values
            income_nonzero = income[income > 0]

            if len(income_nonzero) < 6:
                continue

            log_income = np.log(income_nonzero)
            mu_i = np.mean(log_income)
            household_means.append(mu_i)

            log_income_demeaned = log_income - mu_i
            y_t = log_income_demeaned[1:]
            y_t_lag = log_income_demeaned[:-1]

            if len(y_t) >= 3 and np.var(y_t_lag) > 1e-6:
                rho_i = np.cov(y_t, y_t_lag)[0, 1] / np.var(y_t_lag)
                rho_i = max(0.0, min(rho_i, 0.99))
                household_rhos.append(rho_i)

                residuals = y_t - rho_i * y_t_lag
                household_sigmas.append(np.std(residuals))
                all_residuals.extend(residuals)

        rho = np.median(household_rhos) if household_rhos else 0.7
        sigma = np.median(household_sigmas) if household_sigmas else 0.15
        mu = np.median(household_means) if household_means else 8.5

        print(f"\n  Within-household estimation:")
        print(f"  Households: {len(household_rhos)}")
        print(f"  ρ median: {np.median(household_rhos):.4f}, mean: {np.mean(household_rhos):.4f}")
        print(f"  σ median: {np.median(household_sigmas):.4f}, mean: {np.mean(household_sigmas):.4f}")

        all_incomes = []
        for (ssuid, shhadid), group in raw_data.groupby(['SSUID', 'SHHADID']):
            income = group['THTOTINC'].values
            income_nonzero = income[income > 0]
            all_incomes.extend(income_nonzero)

        all_incomes = np.array(all_incomes)

        params = {
            'rho': rho,
            'mu': mu,
            'sigma': sigma,
            'initial_income_median': np.median(all_incomes) if len(all_incomes) > 0 else 5000,
            'initial_income_std': np.std(np.log(all_incomes)) if len(all_incomes) > 0 else 0.5,
            'n_households': len(household_rhos),
            'n_residuals': len(all_residuals),
        }

        print(f"\nAR(1) Model Parameters:")
        print(f"  ρ (persistence): {params['rho']:.6f}")
        print(f"  σ (shock std): {params['sigma']:.6f}")
        print(f"  Half-life: {-np.log(2) / np.log(params['rho']):.2f} months" if params['rho'] > 0 else "  N/A")

        var_unconditional = params['sigma']**2 / (1 - params['rho']**2) if params['rho'] < 0.99 else np.inf
        print(f"  Unconditional var(log Y): {var_unconditional:.6f}")

        return params

    @staticmethod
    def simulate_trajectory(
        initial_income: float,
        n_months: int,
        params: Dict[str, float],
        seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Simulate income trajectory with household-specific mean reversion.

        Args:
            initial_income: Starting income (serves as household equilibrium)
            n_months: Number of months to simulate
            params: Model parameters (rho, sigma)
            seed: Random seed for reproducibility

        Returns:
            Array of simulated income values
        """
        if seed is not None:
            np.random.seed(seed)

        log_income = np.zeros(n_months)
        log_income[0] = np.log(initial_income)
        mu_household = log_income[0]

        for t in range(1, n_months):
            shock = np.random.normal(0, params['sigma'])
            log_income[t] = mu_household + params['rho'] * (log_income[t-1] - mu_household) + shock

        income = np.exp(log_income)
        income = np.maximum(income, 100)

        return income

    @staticmethod
    def validate_model(
        raw_data: pd.DataFrame,
        n_simulations: int = 1000,
        n_months: int = 24
    ) -> Tuple[Dict[str, float], np.ndarray]:
        """
        Estimate parameters and run validation simulations.

        Args:
            raw_data: Raw household income data
            n_simulations: Number of trajectories to simulate
            n_months: Number of months per trajectory

        Returns:
            Tuple of (parameters dict, simulated trajectories array)
        """
        params = AR1Model.estimate_ar1_parameters(raw_data)

        simulated_trajectories = []
        for i in range(n_simulations):
            log_initial = np.log(params['initial_income_median']) + np.random.normal(0, params['initial_income_std'])
            initial = np.exp(log_initial)
            trajectory = AR1Model.simulate_trajectory(initial, n_months, params, seed=i)
            simulated_trajectories.append(trajectory)

        return params, np.array(simulated_trajectories)

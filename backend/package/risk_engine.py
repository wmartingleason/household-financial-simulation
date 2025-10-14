"""
Risk engine for evaluating household bankruptcy risk via Monte Carlo simulation.
"""

import numpy as np
from typing import Dict, Optional


class RiskEngine:
    """
    Evaluates bankruptcy risk using Monte Carlo simulation of income trajectories.

    Calculates the probability of going into debt given household parameters and
    a stochastic income model.
    """

    @staticmethod
    def simulate_trajectory(
        initial_income: float,
        n_months: int,
        params: Dict[str, float],
        seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Simulate income trajectory with stochastic jumps.

        Uses a compound Poisson process where income jump sizes are lognormally distributed.

        Args:
            initial_income: Starting monthly income
            n_months: Number of months to simulate
            params: Model parameters dictionary containing:
                - lambda: Rate of jumps
                - jump_median_pct: Median percentage jump size
                - jump_q25: 25th percentile of jump sizes
                - jump_q75: 75th percentile of jump sizes
                - prob_upward: Probability that a jump is upward
            seed: Random seed for reproducibility

        Returns:
            Array of simulated income values over n_months
        """
        if seed is not None:
            np.random.seed(seed)

        income = np.zeros(n_months)
        income[0] = initial_income

        # Jump size parameters (lognormal distribution)
        mu = np.log(params['jump_median_pct'])
        iqr_ratio = params['jump_q75'] / params['jump_q25'] if params['jump_q25'] > 0 else 2
        sigma = np.log(iqr_ratio) / 1.35
        sigma = max(0.1, min(sigma, 1.0))  # Bound sigma to reasonable range
        household_lambda = params['lambda']

        for t in range(1, n_months):
            if np.random.random() < household_lambda:
                # Jump occurs
                jump_pct = np.random.lognormal(mu, sigma)
                jump_pct = min(jump_pct, 2.0)  # Cap at 200% change

                if np.random.random() < params['prob_upward']:
                    income[t] = income[t-1] * (1 + jump_pct)
                else:
                    income[t] = income[t-1] * max(0.01, 1 - jump_pct)

                income[t] = max(100, income[t])  # Floor at $100
            else:
                # No jump, income stays constant
                income[t] = income[t-1]

        return income

    def calculate_bankruptcy_risk(
        self,
        initial_fund: float,
        monthly_expenses: float,
        initial_income: float,
        n_months: int,
        n_simulations: int,
        params: Dict[str, float],
        seed: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate bankruptcy risk using Monte Carlo simulation.

        Args:
            initial_fund: Starting savings amount
            monthly_expenses: Fixed monthly spending
            initial_income: Starting monthly income
            n_months: Simulation duration in months
            n_simulations: Number of Monte Carlo trials
            params: Income model parameters (see simulate_trajectory for details)
            seed: Random seed for reproducibility

        Returns:
            Dictionary with risk metrics:
                - debt_probability: Fraction of simulations ending in debt
                - mean_min_balance: Average minimum balance across simulations
                - mean_final_balance: Average final balance across simulations
                - median_min_balance: Median minimum balance
                - median_final_balance: Median final balance
        """
        if seed is not None:
            np.random.seed(seed)

        debt_trials = 0
        min_balances = []
        final_balances = []

        for i in range(n_simulations):
            # Generate income trajectory for this simulation
            income_trajectory = self.simulate_trajectory(
                initial_income, n_months, params, seed=i if seed else None
            )

            # Simulate savings evolution
            balance = initial_fund
            monthly_balances = [balance]

            for month_income in income_trajectory:
                monthly_savings = month_income - monthly_expenses
                balance += monthly_savings
                monthly_balances.append(balance)

                if balance < 0:
                    debt_trials += 1
                    break 

            min_balances.append(min(monthly_balances))
            final_balances.append(balance)

        debt_probability = debt_trials / n_simulations

        return {
            'debt_probability': debt_probability,
            'mean_min_balance': float(np.mean(min_balances)),
            'mean_final_balance': float(np.mean(final_balances)),
            'median_min_balance': float(np.median(min_balances)),
            'median_final_balance': float(np.median(final_balances))
        }

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
        available_credit: float,
        interest_rate: float,
        n_months: int,
        n_simulations: int,
        params: Dict[str, float],
        seed: Optional[int] = None,
        n_sample_paths: int = 100
    ) -> Dict:
        """
        Calculate financial outcomes using Monte Carlo simulation.
        
        Args:
            initial_fund: Starting savings amount
            monthly_expenses: Fixed monthly spending
            initial_income: Starting monthly income
            available_credit: Credit limit (currently unused)
            interest_rate: Interest rate on debt (currently unused)
            n_months: Simulation duration in months
            n_simulations: Number of Monte Carlo trials
            params: Income model parameters (see simulate_trajectory for details)
            seed: Random seed for reproducibility
            n_sample_paths: Number of full paths to return for visualization (default 100)
            
        Returns:
            Dictionary with simulation results
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Storage for all simulations
        all_paths = np.zeros((n_simulations, n_months + 1))  # +1 for initial state
        terminal_values = []
        min_balances = []
        ever_negative = []
        months_to_negative = []  # For those who go negative
        
        # Sample indices for paths to return in full
        sample_indices = np.random.choice(n_simulations, min(n_sample_paths, n_simulations), replace=False)
        sample_paths = []
        
        for i in range(n_simulations):
            # Generate income trajectory for this simulation
            income_trajectory = self.simulate_trajectory(
                initial_income, n_months, params, seed=i if seed else None
            )
            
            # Simulate savings evolution (NO early termination)
            balance = initial_fund
            monthly_balances = [balance]
            went_negative = False
            first_negative_month = None
            
            for month_idx, month_income in enumerate(income_trajectory):
                monthly_savings = month_income - monthly_expenses
                balance += monthly_savings
                monthly_balances.append(balance)

                # Track first time going negative
                if balance < 0 and not went_negative:
                    went_negative = True
                    first_negative_month = month_idx + 1
            
            # Store results
            all_paths[i] = monthly_balances
            terminal_values.append(balance)
            min_balances.append(min(monthly_balances))
            ever_negative.append(went_negative)
            if went_negative:
                months_to_negative.append(first_negative_month)
            
            # Save full path if in sample
            if i in sample_indices:
                sample_paths.append(monthly_balances)

            # Debt accrues interest
            if balance < 0:
                balance *= 1 + (interest_rate) / 12
        
        # Calculate aggregate statistics across all simulations at each time point
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        aggregate_stats = {
            'months': list(range(n_months + 1)),
            'mean': all_paths.mean(axis=0).tolist(),
        }
        
        for p in percentiles:
            aggregate_stats[f'p{p}'] = np.percentile(all_paths, p, axis=0).tolist()
        
        # Calculate terminal statistics
        terminal_array = np.array(terminal_values)
        terminal_stats = {
            'mean': float(terminal_array.mean()),
            'median': float(np.median(terminal_array)),
            'std': float(terminal_array.std()),
        }
        
        for p in percentiles:
            terminal_stats[f'p{p}'] = float(np.percentile(terminal_array, p))
        
        # Calculate derived statistics
        negative_terminal_count = sum(1 for v in terminal_values if v < 0)
        ever_negative_count = sum(ever_negative)
        
        statistics = {
            'terminalStats': terminal_stats,
            'negativeTerminalPct': (negative_terminal_count / n_simulations) * 100,
            'everNegativePct': (ever_negative_count / n_simulations) * 100,
            'medianMinBalance': float(np.median(min_balances)),
            'meanMinBalance': float(np.mean(min_balances)),
        }
        
        # Add median months to negative (only for those who went negative)
        if months_to_negative:
            statistics['medianMonthsToNegative'] = float(np.median(months_to_negative))
        else:
            statistics['medianMonthsToNegative'] = None
        
        # Calculate survival curve (probability of remaining positive at each month)
        probability_positive_by_month = []
        for month in range(n_months + 1):
            positive_count = sum(1 for path in all_paths if path[month] >= 0)
            probability_positive_by_month.append((positive_count / n_simulations) * 100)
        
        # Risk metrics
        risk_metrics = {
            'probabilityPositiveByMonth': probability_positive_by_month,
            'emergencyFundMonths': initial_fund / monthly_expenses if monthly_expenses > 0 else float('inf'),
            'monthlyNetIncome': initial_income - monthly_expenses
        }
        
        return {
            'samplePaths': sample_paths,
            'terminalValues': terminal_values,
            'aggregateStats': aggregate_stats,
            'statistics': statistics,
            'riskMetrics': risk_metrics,
            'metadata': {
                'nSimulations': n_simulations,
                'nMonths': n_months,
                'nSamplePaths': len(sample_paths),
                'initialFund': initial_fund,
                'monthlyExpenses': monthly_expenses,
                'initialIncome': initial_income
            }
        }
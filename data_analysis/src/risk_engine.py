"""
Risk engine for evaluating household financial strategies.
"""

import numpy as np
from typing import Dict, Optional
from data_analysis.src.simulation import Simulation


class RiskEngine:
    """
    Evaluates savings strategies against income volatility using Monte Carlo simulation.
    
    Calculates the probability of going into debt under different spending scenarios.
    """
    
    def __init__(
        self, 
        initial_fund: float,
        monthly_expenses: float,
        initial_income = None,
        n_months: int = 24,
        n_simulations: int = 1000,
    ):
        """
        Initialize the risk engine.
        
        Args:
            initial_fund: Starting savings amount
            monthly_expenses: Fixed monthly spending
            n_months: Simulation duration in months
            n_simulations: Number of trials
        """
        self.initial_fund = initial_fund
        self.monthly_expenses = monthly_expenses
        self.initial_income = initial_income
        self.n_months = n_months
        self.n_simulations = n_simulations
        self.simulation = Simulation()
    
    def run_risk_assessment(
        self, 
        params: Dict[str, float],
        seed: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Run Monte Carlo simulation to assess debt risk.
        
        Args:
            params: Income model parameters from Simulation.estimate_model_parameters
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary with risk metrics
        """
        if seed is not None:
            np.random.seed(seed)
        
        debt_trials = 0
        min_balances = []
        final_balances = []
        
        for i in range(self.n_simulations):
            # Generate income trajectory
            
            initial_income = self.initial_income or params['initial_income_median'] * np.random.lognormal(0, 0.5)
            income_trajectory = self.simulation.simulate_trajectory(
                initial_income, self.n_months, params, seed=i if seed else None
            )
            
            # Simulate savings evolution
            balance = self.initial_fund
            monthly_balances = [balance]
            
            for month_income in income_trajectory:
                monthly_savings = month_income - self.monthly_expenses
                balance += monthly_savings
                monthly_balances.append(balance)
                
                if balance < 0:
                    debt_trials += 1
                    break
            
            min_balances.append(min(monthly_balances))
            final_balances.append(balance)
        
        debt_probability = debt_trials / self.n_simulations
        
        return {
            'debt_probability': debt_probability,
            'mean_min_balance': np.mean(min_balances),
            'mean_final_balance': np.mean(final_balances),
            'median_min_balance': np.median(min_balances),
            'median_final_balance': np.median(final_balances)
        }
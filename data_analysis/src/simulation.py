"""
Simulation module for income trajectory modeling and validation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class Simulation:
    """
    Simulates household income trajectories based on estimated parameters.
    
    This class handles parameter estimation from real data, trajectory simulation,
    and validation against empirical distributions.
    """
    
    @staticmethod
    def estimate_model_parameters(
        household_stats_full: pd.DataFrame, 
        income_analysis: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Extract model parameters from household statistics.
        
        Args:
            household_stats_full: Full household statistics DataFrame
            income_analysis: Income-dependent analysis DataFrame
            
        Returns:
            Dictionary of model parameters
        """
        # Winsorize extreme jumps at 99th percentile to remove outliers
        jump_sizes = household_stats_full['mean_nonzero_pct_change'].dropna()
        jump_sizes_winsorized = np.clip(jump_sizes, 0, jump_sizes.quantile(0.99))
        
        params = {
            # Jump frequency
            'lambda': 1 - household_stats_full['frac_zero_change'].median(),
            
            # Jump size: use MEDIAN not mean to avoid outlier influence
            'jump_median_pct': household_stats_full['mean_nonzero_pct_change'].median(),
            
            # For lognormal: use IQR to estimate scale parameter robustly
            'jump_q25': household_stats_full['mean_nonzero_pct_change'].quantile(0.25),
            'jump_q75': household_stats_full['mean_nonzero_pct_change'].quantile(0.75),
            
            # Jump direction
            'prob_upward': 0.5,
            
            # Initial income (also use median)
            'initial_income_median': income_analysis['mean_income'].median(),
            'initial_income_iqr': (income_analysis['mean_income'].quantile(0.75) - 
                                   income_analysis['mean_income'].quantile(0.25)),
        }
        
        return params
    
    @staticmethod
    def simulate_trajectory(
        initial_income: float, 
        n_months: int, 
        params: Dict[str, float], 
        seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Simulate income trajectory with household-specific lambda drawn from distribution.
        
        Args:
            initial_income: Starting income level
            n_months: Number of months to simulate
            params: Model parameters dictionary
            seed: Random seed for reproducibility
            
        Returns:
            Array of simulated income values
        """
        if seed is not None:
            np.random.seed(seed)
        
        income = np.zeros(n_months)
        income[0] = initial_income
        
        # Each household draws its own jump frequency from a Beta distribution
        # Beta(α, β) with mean = α/(α+β), variance = αβ/((α+β)²(α+β+1))
        # Target: mean ≈ 0.09, but with right skew (most near 0, some higher)
        household_lambda = np.random.beta(2, 20)
        
        # Jump size parameters
        mu = np.log(params['jump_median_pct'])
        iqr_ratio = params['jump_q75'] / params['jump_q25'] if params['jump_q25'] > 0 else 2
        sigma = np.log(iqr_ratio) / 1.35
        sigma = max(0.1, min(sigma, 1.0))
        
        for t in range(1, n_months):
            if np.random.random() < household_lambda:
                jump_pct = np.random.lognormal(mu, sigma)
                jump_pct = min(jump_pct, 2.0)
                
                if np.random.random() < params['prob_upward']:
                    income[t] = income[t-1] * (1 + jump_pct)
                else:
                    income[t] = income[t-1] * max(0.01, 1 - jump_pct)
                
                income[t] = max(100, income[t])
            else:
                income[t] = income[t-1]
        
        return income
    
    def run_simulations(
        self, 
        n_simulations: int, 
        n_months: int, 
        params: Dict[str, float]
    ) -> np.ndarray:
        """
        Run multiple income trajectory simulations.
        
        Args:
            n_simulations: Number of trajectories to simulate
            n_months: Number of months per trajectory
            params: Model parameters dictionary
            
        Returns:
            Array of shape (n_simulations, n_months)
        """
        simulated_trajectories = []
        
        for i in range(n_simulations):
            initial = params['initial_income_median'] * np.random.lognormal(0, 0.5)
            trajectory = self.simulate_trajectory(initial, n_months, params, seed=i)
            simulated_trajectories.append(trajectory)
        
        return np.array(simulated_trajectories)
    
    @staticmethod
    def calc_validation_stats(trajectory: np.ndarray) -> Optional[Dict[str, float]]:
        """
        Calculate validation statistics for a single trajectory.
        
        Args:
            trajectory: Simulated income trajectory
            
        Returns:
            Dictionary of statistics, or None if insufficient data
        """
        if len(trajectory) < 2:
            return None
        
        trajectory_nonzero = trajectory[trajectory > 0]
        if len(trajectory_nonzero) < 2:
            return None
        
        changes = np.diff(trajectory_nonzero)
        pct_changes = changes / trajectory_nonzero[:-1]
        
        return {
            'cv': np.std(trajectory_nonzero) / np.mean(trajectory_nonzero),
            'frac_zero_change': (changes == 0).mean(),
            'mean_nonzero_pct_change': np.mean(np.abs(pct_changes[changes != 0])) if (changes != 0).any() else 0,
            'jump_freq': (changes != 0).mean()
        }
    
    def compute_simulation_statistics(
        self, 
        simulated_trajectories: np.ndarray
    ) -> pd.DataFrame:
        """
        Compute statistics for all simulated trajectories.
        
        Args:
            simulated_trajectories: Array of simulated trajectories
            
        Returns:
            DataFrame with statistics for each trajectory
        """
        simulated_stats = [self.calc_validation_stats(traj) for traj in simulated_trajectories]
        simulated_stats = [s for s in simulated_stats if s is not None]
        
        return pd.DataFrame(simulated_stats)
    
    def validate_model(
        self,
        household_stats_full: pd.DataFrame,
        income_analysis: pd.DataFrame,
        n_simulations: int = 1000,
        n_months: int = 24
    ) -> tuple[Dict[str, float], pd.DataFrame, np.ndarray]:
        """
        Complete validation pipeline: estimate parameters, simulate, and compute statistics.
        
        Args:
            household_stats_full: Full household statistics from real data
            income_analysis: Income analysis from real data
            n_simulations: Number of trajectories to simulate
            n_months: Number of months per trajectory
            
        Returns:
            Tuple of (params, simulated_stats_df, simulated_trajectories)
        """
        # Estimate parameters
        params = self.estimate_model_parameters(household_stats_full, income_analysis)
        
        print("\nModel Parameters:")
        for key, value in params.items():
            print(f"{key}: {value:.3f}")
        
        # Run simulations
        simulated_trajectories = self.run_simulations(n_simulations, n_months, params)
        
        # Compute statistics
        simulated_df = self.compute_simulation_statistics(simulated_trajectories)
        
        # Print validation summary
        metrics = ['cv', 'frac_zero_change', 'mean_nonzero_pct_change', 'jump_freq']
        
        print("\nValidation: Real vs Simulated Statistics")
        print("\nReal Data:")
        print(household_stats_full[metrics].describe())
        print("\nSimulated Data:")
        print(simulated_df[metrics].describe())
        
        return params, simulated_df, simulated_trajectories
"""
Simulation module for income trajectory modeling and validation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .ar1_model import AR1Model


class Simulation:
    """
    Simulates household income trajectories based on estimated parameters.
    
    This class handles parameter estimation from real data, trajectory simulation,
    and validation against empirical distributions.
    """
    
    @staticmethod
    def estimate_model_parameters(
        raw_data: pd.DataFrame,
        household_stats_full: Optional[pd.DataFrame] = None,
        income_analysis: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """
        Estimate AR(1) model parameters from household income data.

        Args:
            raw_data: Raw household income data with columns SSUID, SHHADID, THTOTINC
            household_stats_full: Optional, not used
            income_analysis: Optional, not used

        Returns:
            Dictionary of model parameters (rho, sigma, mu, etc.)
        """
        params = AR1Model.estimate_ar1_parameters(raw_data)
        return params
    
    @staticmethod
    def simulate_trajectory(
        initial_income: float,
        n_months: int,
        params: Dict[str, float],
        seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Simulate income trajectory using AR(1) model with mean reversion.

        Args:
            initial_income: Starting income level
            n_months: Number of months to simulate
            params: Model parameters (rho, mu, sigma)
            seed: Random seed for reproducibility

        Returns:
            Array of simulated income values
        """
        return AR1Model.simulate_trajectory(initial_income, n_months, params, seed)
    
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
        Calculate validation statistics for a single trajectory using Statistics.calc_household_stats.

        Args:
            trajectory: Simulated income trajectory

        Returns:
            Dictionary of statistics, or None if insufficient data
        """
        if len(trajectory) < 2:
            return None

        # Import Statistics class (local import to avoid circular dependency)
        from src.statistics import Statistics

        # Convert trajectory to DataFrame format expected by calc_household_stats
        trajectory_df = pd.DataFrame({
            'THTOTINC': trajectory
        })

        # Calculate statistics using the same method as for real data
        stats_series = Statistics.calc_household_stats(trajectory_df)

        # Convert to dictionary, excluding n_months
        stats_dict = stats_series.to_dict()
        if 'n_months' in stats_dict:
            del stats_dict['n_months']

        # Add mean_nonzero_pct_change for backward compatibility with existing code
        trajectory_nonzero = trajectory[trajectory > 0]
        if len(trajectory_nonzero) >= 2:
            changes = np.diff(trajectory_nonzero)
            pct_changes = changes / trajectory_nonzero[:-1]
            stats_dict['mean_nonzero_pct_change'] = np.mean(np.abs(pct_changes[changes != 0])) if (changes != 0).any() else 0
            stats_dict['frac_zero_change'] = (changes == 0).mean()
        else:
            stats_dict['mean_nonzero_pct_change'] = np.nan
            stats_dict['frac_zero_change'] = np.nan

        return stats_dict
    
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
        raw_data: pd.DataFrame,
        household_stats_full: pd.DataFrame,
        income_analysis: Optional[pd.DataFrame] = None,
        n_simulations: int = 1000,
        n_months: int = 24
    ) -> tuple[Dict[str, float], pd.DataFrame, np.ndarray]:
        """
        Complete validation pipeline: estimate parameters, simulate, and compute statistics.

        Args:
            raw_data: Raw household income data (used for robust parameter estimation)
            household_stats_full: Full household statistics from real data (used for validation comparison)
            income_analysis: Income analysis from real data (optional, for backward compatibility)
            n_simulations: Number of trajectories to simulate
            n_months: Number of months per trajectory

        Returns:
            Tuple of (params, simulated_stats_df, simulated_trajectories)
        """
        # Estimate parameters using raw data
        params = self.estimate_model_parameters(raw_data, household_stats_full, income_analysis)
        
        print("\nModel Parameters:")
        for key, value in params.items():
            print(f"{key}: {value:.3f}")
        
        # Run simulations
        simulated_trajectories = self.run_simulations(n_simulations, n_months, params)
        
        # Compute statistics
        simulated_df = self.compute_simulation_statistics(simulated_trajectories)
        
        # Print validation summary with expanded metrics
        metrics = [
            'cv',
            'frac_zero_change',
            'mean_nonzero_pct_change',
            'jump_freq',
            'skewness',
            'kurtosis',
            'autocorrelation',
            'frac_large_jumps_25pct',
            'frac_large_jumps_50pct'
        ]

        # Define custom aggregation functions including median
        agg_funcs = ['count', 'mean', 'std', 'min', 'median', '25%', '50%', '75%', 'max']

        print("\nValidation: Real vs Simulated Statistics")
        print("\nReal Data:")
        real_desc = household_stats_full[metrics].agg(['count', 'mean', 'std', 'min',
                                                        lambda x: x.quantile(0.25),
                                                        lambda x: x.quantile(0.5),  # median
                                                        lambda x: x.quantile(0.75),
                                                        'max'])
        real_desc.index = ['count', 'mean', 'std', 'min', '25%', 'median', '75%', 'max']
        print(real_desc)

        print("\nSimulated Data:")
        sim_desc = simulated_df[metrics].agg(['count', 'mean', 'std', 'min',
                                               lambda x: x.quantile(0.25),
                                               lambda x: x.quantile(0.5),  # median
                                               lambda x: x.quantile(0.75),
                                               'max'])
        sim_desc.index = ['count', 'mean', 'std', 'min', '25%', 'median', '75%', 'max']
        print(sim_desc)

        return params, simulated_df, simulated_trajectories
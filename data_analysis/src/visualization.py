"""
Visualization module for household income volatility analysis.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional


class Visualization:
    """
    Creates visualizations for household income volatility analysis.
    
    This class provides methods for generating all plots used in the analysis
    pipeline, including distributions, relationships, and validation comparisons.
    """
    
    @staticmethod
    def plot_volatility_distributions(
        household_stats: pd.DataFrame,
        save_path: Optional[str] = 'income_volatility_exploration.png'
    ) -> None:
        """
        Plot histograms of CV and jump frequency distributions.
        
        Args:
            household_stats: DataFrame with cv and jump_freq columns
            save_path: Path to save figure, or None to skip saving
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram 1: Coefficient of Variation
        axes[0].hist(household_stats['cv'], bins=50, edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('Coefficient of Variation (CV)', fontsize=12)
        axes[0].set_ylabel('Number of Households', fontsize=12)
        axes[0].set_title('Distribution of Income Volatility\n(CV = σ/μ)', fontsize=14)
        axes[0].axvline(household_stats['cv'].median(), color='red', linestyle='--', 
                        linewidth=2, label=f'Median = {household_stats["cv"].median():.2f}')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)
        
        # Histogram 2: Frequency of Large Jumps
        axes[1].hist(household_stats['jump_freq'], bins=50, edgecolor='black', alpha=0.7)
        axes[1].set_xlabel('Frequency of Large Jumps (≥30%)', fontsize=12)
        axes[1].set_ylabel('Number of Households', fontsize=12)
        axes[1].set_title('Distribution of Large Jump Frequency\n(Drops or Spikes ≥30%)', fontsize=14)
        axes[1].axvline(household_stats['jump_freq'].median(), color='red', linestyle='--', 
                        linewidth=2, label=f'Median = {household_stats["jump_freq"].median():.2f}')
        axes[1].legend()
        axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        # Print summary statistics
        print("Summary Statistics:")
        print(f"Total households analyzed: {len(household_stats)}")
        print(f"\nCoefficient of Variation:")
        print(household_stats['cv'].describe())
        print(f"\nLarge Jump Frequency:")
        print(household_stats['jump_freq'].describe())
    
    @staticmethod
    def plot_variance_relationships(household_stats_full: pd.DataFrame) -> None:
        """
        Plot relationships between variance and persistence/change magnitude.
        
        Args:
            household_stats_full: DataFrame with acf_lag1, median_abs_change, cv columns
        """
        # Analyze high-variance, low-jump households
        high_var_low_jump = household_stats_full[
            (household_stats_full['cv'] > household_stats_full['cv'].quantile(0.75)) &
            (household_stats_full['jump_freq'] < household_stats_full['jump_freq'].quantile(0.25))
        ]
        
        print("\nHigh Variance + Low Jump households:")
        print(f"Count: {len(high_var_low_jump)}")
        print("\nCharacteristics:")
        print(high_var_low_jump[['median_abs_change', 'acf_lag1', 'trend_component']].describe())
        
        # Scatter plots
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        axes[0].scatter(household_stats_full['acf_lag1'], household_stats_full['cv'], 
                        alpha=0.5, s=20)
        axes[0].set_xlabel('Autocorrelation (lag 1)', fontsize=12)
        axes[0].set_ylabel('Coefficient of Variation', fontsize=12)
        axes[0].set_title('Variance vs. Persistence', fontsize=14)
        axes[0].grid(alpha=0.3)
        
        axes[1].scatter(household_stats_full['median_abs_change'], household_stats_full['cv'], 
                        alpha=0.5, s=20)
        axes[1].set_xlabel('Median Absolute % Change', fontsize=12)
        axes[1].set_ylabel('Coefficient of Variation', fontsize=12)
        axes[1].set_title('Variance vs. Typical Change Size', fontsize=14)
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_change_characteristics(household_stats_full: pd.DataFrame) -> None:
        """
        Plot income stickiness and change magnitude distributions.
        
        Args:
            household_stats_full: DataFrame with frac_zero_change and 
                                  mean_nonzero_pct_change columns
        """
        print("\nChange Distribution Analysis:")
        print(household_stats_full[['frac_zero_change', 'frac_small_change', 
                                    'frac_large_change', 'mean_nonzero_pct_change']].describe())
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        axes[0].hist(household_stats_full['frac_zero_change'], bins=50, 
                     edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('Fraction of Months with Zero Change', fontsize=12)
        axes[0].set_ylabel('Number of Households', fontsize=12)
        axes[0].set_title('Income Stickiness Distribution', fontsize=14)
        axes[0].axvline(household_stats_full['frac_zero_change'].median(), 
                        color='red', linestyle='--', linewidth=2,
                        label=f'Median = {household_stats_full["frac_zero_change"].median():.2f}')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)
        
        # Conditional on change happening, what's the percentage magnitude?
        axes[1].hist(household_stats_full['mean_nonzero_pct_change'].dropna(), bins=50, 
                     edgecolor='black', alpha=0.7)
        axes[1].set_xlabel('Mean % Change When Change Occurs', fontsize=12)
        axes[1].set_ylabel('Number of Households', fontsize=12)
        axes[1].set_title('Size of Changes (% terms, Excluding Zeros)', fontsize=14)
        axes[1].axvline(household_stats_full['mean_nonzero_pct_change'].median(), 
                        color='red', linestyle='--', linewidth=2,
                        label=f'Median = {household_stats_full["mean_nonzero_pct_change"].median():.2%}')
        axes[1].legend()
        axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_income_dependence(income_analysis: pd.DataFrame) -> None:
        """
        Plot relationships between income level and jump characteristics.
        
        Args:
            income_analysis: DataFrame with mean_income, jump_freq, mean_jump_size_pct,
                            and income_quintile columns
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Jump frequency vs income
        axes[0, 0].scatter(income_analysis['mean_income'], income_analysis['jump_freq'], 
                           alpha=0.3, s=20)
        axes[0, 0].set_xlabel('Mean Income Level', fontsize=12)
        axes[0, 0].set_ylabel('Jump Frequency', fontsize=12)
        axes[0, 0].set_title('Jump Frequency vs Income Level', fontsize=14)
        axes[0, 0].set_xscale('log')
        axes[0, 0].grid(alpha=0.3)
        
        # Jump size vs income
        axes[0, 1].scatter(income_analysis['mean_income'], income_analysis['mean_jump_size_pct'], 
                           alpha=0.3, s=20)
        axes[0, 1].set_xlabel('Mean Income Level', fontsize=12)
        axes[0, 1].set_ylabel('Mean Jump Size (%)', fontsize=12)
        axes[0, 1].set_title('Jump Magnitude vs Income Level', fontsize=14)
        axes[0, 1].set_xscale('log')
        axes[0, 1].set_yscale('log')
        axes[0, 1].grid(alpha=0.3)
        
        # Boxplots by quintile  
        income_analysis.boxplot(column='jump_freq', by='income_quintile', ax=axes[1, 0])
        axes[1, 0].set_xlabel('Income Quintile', fontsize=12)
        axes[1, 0].set_ylabel('Jump Frequency', fontsize=12)
        axes[1, 0].set_title('Jump Frequency by Income Quintile', fontsize=14)
        axes[1, 0].get_figure().suptitle('')  # Remove default title
        
        income_analysis.boxplot(column='mean_jump_size_pct', by='income_quintile', ax=axes[1, 1])
        axes[1, 1].set_xlabel('Income Quintile', fontsize=12)
        axes[1, 1].set_ylabel('Mean Jump Size (%)', fontsize=12)
        axes[1, 1].set_title('Jump Size by Income Quintile', fontsize=14)
        axes[1, 1].get_figure().suptitle('')
        
        plt.tight_layout()
        plt.show()
        
        # Summary statistics by quintile
        print("\nJump characteristics by income quintile:")
        print(income_analysis.groupby('income_quintile')[
            ['jump_freq', 'mean_jump_size_pct', 'mean_upward_jump', 'mean_downward_jump']
        ].mean())
    
    @staticmethod
    def plot_validation_comparison(
        household_stats_full: pd.DataFrame,
        simulated_df: pd.DataFrame
    ) -> None:
        """
        Compare real data distributions with simulated data.
        
        Args:
            household_stats_full: Real household statistics
            simulated_df: Simulated household statistics
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        metrics = ['cv', 'frac_zero_change', 'mean_nonzero_pct_change', 'jump_freq']
        titles = ['Coefficient of Variation', 'Fraction Zero Change', 
                  'Mean Jump Size (%)', 'Jump Frequency']
        
        for idx, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[idx // 2, idx % 2]
            
            # Real data
            ax.hist(household_stats_full[metric].dropna(), bins=30, alpha=0.5, 
                    label='Real Data', density=True, edgecolor='black')
            
            # Simulated data
            ax.hist(simulated_df[metric].dropna(), bins=30, alpha=0.5, 
                    label='Simulated', density=True, edgecolor='black')
            
            ax.set_xlabel(title, fontsize=12)
            ax.set_ylabel('Density', fontsize=12)
            ax.set_title(f'{title}: Real vs Simulated', fontsize=14)
            ax.legend()
            ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_trajectory_comparison(
        df: pd.DataFrame,
        simulated_trajectories: np.ndarray,
        n_samples: int = 30,
        min_months: int = 30
    ) -> None:
        """
        Plot sample trajectories from real data vs simulated data.
        
        Args:
            df: Real household data (sorted by SSUID, SHHADID, YEAR, MONTHCODE)
            simulated_trajectories: Array of simulated trajectories (n_sims, n_months)
            n_samples: Number of sample trajectories to plot
            min_months: Minimum months required for real households
        """
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Extract real trajectories - filter to households with enough data
        household_lengths = df.groupby(['SSUID', 'SHHADID']).size()
        valid_households = household_lengths[household_lengths > min_months].index.tolist()
        
        n_samples_actual = min(n_samples, len(valid_households))
        sampled_households = [valid_households[i] for i in np.random.choice(len(valid_households), size=n_samples_actual, replace=False)]
        
        real_trajectories = []
        for ssuid, shhadid in sampled_households:
            hh_data = df[(df['SSUID'] == ssuid) & (df['SHHADID'] == shhadid)].sort_values(['YEAR', 'MONTHCODE'])
            income = hh_data['THTOTINC'].values
            income_nonzero = income[income > 0]
            if len(income_nonzero) >= 2:
                real_trajectories.append(income_nonzero)
        
        # Calculate median trajectory for real data
        max_len = max(len(t) for t in real_trajectories)
        padded_real = np.full((len(real_trajectories), max_len), np.nan)
        for i, traj in enumerate(real_trajectories):
            padded_real[i, :len(traj)] = traj
        real_median = np.nanmedian(padded_real, axis=0)
        
        # Plot real trajectories
        for traj in real_trajectories:
            axes[0].plot(range(len(traj)), traj, alpha=0.4, color='steelblue', linewidth=1)
        axes[0].plot(range(len(real_median)), real_median, color='darkblue', 
                    linewidth=2.5, label='Median', zorder=100)
        axes[0].set_xlabel('Month', fontsize=12)
        axes[0].set_ylabel('Income (log scale)', fontsize=12)
        axes[0].set_title(f'Real Household Trajectories (n={len(real_trajectories)})', fontsize=14)
        axes[0].set_yscale('log')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        
        # Sample and plot simulated trajectories
        n_sim_samples = min(n_samples, simulated_trajectories.shape[0])
        sampled_indices = np.random.choice(
            simulated_trajectories.shape[0], 
            size=n_sim_samples, 
            replace=False
        )
        sampled_sim = simulated_trajectories[sampled_indices]
        
        # Calculate median trajectory for simulated data
        sim_median = np.median(sampled_sim, axis=0)
        
        # Plot simulated trajectories
        for traj in sampled_sim:
            axes[1].plot(range(len(traj)), traj, alpha=0.4, color='coral', linewidth=1)
        axes[1].plot(range(len(sim_median)), sim_median, color='darkred', 
                    linewidth=2.5, label='Median', zorder=100)
        axes[1].set_xlabel('Month', fontsize=12)
        axes[1].set_ylabel('Income (log scale)', fontsize=12)
        axes[1].set_title(f'Simulated Trajectories (n={n_sim_samples})', fontsize=14)
        axes[1].set_yscale('log')
        axes[1].legend()
        axes[1].grid(alpha=0.3)
        
        # Synchronize axes for comparison
        # Get combined y-limits
        all_incomes = np.concatenate([np.concatenate(real_trajectories), sampled_sim.flatten()])
        y_min, y_max = all_incomes.min() * 0.8, all_incomes.max() * 1.2
        
        # Set same limits for both plots
        axes[0].set_xlim(0, simulated_trajectories.shape[1])
        axes[1].set_xlim(0, simulated_trajectories.shape[1])
        axes[0].set_ylim(y_min, y_max)
        axes[1].set_ylim(y_min, y_max)
        
        plt.tight_layout()
        plt.show()
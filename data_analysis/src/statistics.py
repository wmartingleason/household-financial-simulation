"""
Statistical calculations for household income volatility analysis.
"""

import pandas as pd
import numpy as np
from config.config import LARGE_JUMP_THRESHOLD, SMALL_CHANGE_THRESHOLD


class Statistics:
    """
    Computes statistical measures of income volatility for household data.
    
    This class provides methods to calculate various volatility metrics
    from household income time series data.
    """
    
    @staticmethod
    def calc_household_stats(group: pd.DataFrame) -> pd.Series:
        """
        Calculate basic volatility statistics for a household.
        
        Args:
            group: DataFrame for a single household (from groupby)
            
        Returns:
            Series with variance, cv, jump_freq, n_months
        """
        income = group['THTOTINC'].values
        
        # Filter out zeros and NaNs for percentage change calculation
        income_nonzero = income[income > 0]
        
        if len(income_nonzero) < 2:
            return pd.Series({  
                'variance': np.nan,
                'cv': np.nan,
                'jump_freq': np.nan,
                'n_months': len(income)
            })
        
        # Variance and CV
        variance = np.var(income_nonzero)
        cv = np.std(income_nonzero) / np.mean(income_nonzero)
        
        # Calculate percentage changes
        pct_changes = np.diff(income_nonzero) / income_nonzero[:-1]
        
        # Count large jumps (absolute change >= 30%)
        large_jumps = np.abs(pct_changes) >= LARGE_JUMP_THRESHOLD
        jump_freq = large_jumps.sum() / len(pct_changes) if len(pct_changes) > 0 else 0
        
        return pd.Series({
            'variance': variance,
            'cv': cv,
            'jump_freq': jump_freq,
            'n_months': len(income)
        })
    
    @staticmethod
    def decompose_variance_sources(group: pd.DataFrame) -> pd.Series:
        """
        Decompose variance into trend, change magnitude, and persistence components.
        
        Args:
            group: DataFrame for a single household (from groupby)
            
        Returns:
            Series with trend_component, median_abs_change, max_abs_change, acf_lag1
        """
        income = group['THTOTINC'].values
        income_nonzero = income[income > 0]
        
        if len(income_nonzero) < 3:
            return pd.Series({
                'trend_component': np.nan,
                'median_abs_change': np.nan,
                'max_abs_change': np.nan,
                'acf_lag1': np.nan
            })
        
        # Linear trend strength
        x = np.arange(len(income_nonzero))
        trend = np.polyfit(x, income_nonzero, 1)[0]  # Slope
        trend_component = abs(trend) * len(income_nonzero) / np.mean(income_nonzero)
        
        # Typical change magnitude
        pct_changes = np.diff(income_nonzero) / income_nonzero[:-1]
        median_abs_change = np.median(np.abs(pct_changes))
        max_abs_change = np.max(np.abs(pct_changes))
        
        # Autocorrelation
        if len(income_nonzero) > 1:
            acf_lag1 = np.corrcoef(income_nonzero[:-1], income_nonzero[1:])[0, 1]
        else:
            acf_lag1 = np.nan
        
        return pd.Series({
            'trend_component': trend_component,
            'median_abs_change': median_abs_change,
            'max_abs_change': max_abs_change,
            'acf_lag1': acf_lag1
        })
    
    @staticmethod
    def analyze_change_distribution(group: pd.DataFrame) -> pd.Series:
        """
        Analyze the distribution of income changes.
        
        Args:
            group: DataFrame for a single household (from groupby)
            
        Returns:
            Series with frac_zero_change, frac_small_change, frac_large_change, 
            mean_nonzero_pct_change
        """
        income = group['THTOTINC'].values
        income_nonzero = income[income > 0]
        
        if len(income_nonzero) < 2:
            return pd.Series({
                'frac_zero_change': np.nan,
                'frac_small_change': np.nan,
                'frac_large_change': np.nan,
                'mean_nonzero_pct_change': np.nan
            })
        
        changes = np.diff(income_nonzero)
        pct_changes = changes / income_nonzero[:-1]
        
        # Categorize changes
        frac_zero = (changes == 0).mean()
        frac_small = (np.abs(pct_changes) < SMALL_CHANGE_THRESHOLD).mean()
        frac_large = (np.abs(pct_changes) >= LARGE_JUMP_THRESHOLD).mean()
        
        # For non-zero changes, what's the typical percentage magnitude?
        nonzero_pct_changes = pct_changes[changes != 0]
        mean_nonzero_pct = np.mean(np.abs(nonzero_pct_changes)) if len(nonzero_pct_changes) > 0 else 0
        
        return pd.Series({
            'frac_zero_change': frac_zero,
            'frac_small_change': frac_small,
            'frac_large_change': frac_large,
            'mean_nonzero_pct_change': mean_nonzero_pct
        })
    
    @staticmethod
    def income_dependent_analysis(group: pd.DataFrame) -> pd.Series:
        """
        Analyze jump characteristics including income level and directional asymmetry.
        
        Args:
            group: DataFrame for a single household (from groupby)
            
        Returns:
            Series with mean_income, jump_freq, mean_jump_size_pct, 
            mean_upward_jump, mean_downward_jump
        """
        income = group['THTOTINC'].values
        income_nonzero = income[income > 0]
        
        if len(income_nonzero) < 2:
            return pd.Series({
                'mean_income': np.nan,
                'jump_freq': np.nan,
                'mean_jump_size_pct': np.nan,
                'mean_upward_jump': np.nan,
                'mean_downward_jump': np.nan
            })
        
        changes = np.diff(income_nonzero)
        pct_changes = changes / income_nonzero[:-1]
        
        # Jump detection (change != 0)
        jumps = changes != 0
        jump_freq = jumps.mean()
        
        # When jumps happen, what's the magnitude?
        if jumps.sum() > 0:
            jump_sizes = np.abs(pct_changes[jumps])
            mean_jump_pct = np.mean(jump_sizes)
            
            # Separate up vs down
            upward_jumps = pct_changes[jumps & (changes > 0)]
            downward_jumps = pct_changes[jumps & (changes < 0)]
            
            mean_upward = np.mean(upward_jumps) if len(upward_jumps) > 0 else 0
            mean_downward = np.mean(np.abs(downward_jumps)) if len(downward_jumps) > 0 else 0
        else:
            mean_jump_pct = 0
            mean_upward = 0
            mean_downward = 0
        
        return pd.Series({
            'mean_income': np.mean(income_nonzero),
            'jump_freq': jump_freq,
            'mean_jump_size_pct': mean_jump_pct,
            'mean_upward_jump': mean_upward,
            'mean_downward_jump': mean_downward
        })
    
    def compute_household_stats(self, df: pd.DataFrame, min_months: int = 6) -> pd.DataFrame:
        """
        Compute basic household statistics with filtering.
        
        Args:
            df: Input DataFrame with household data
            min_months: Minimum number of months required
            
        Returns:
            DataFrame with household statistics
        """
        household_stats = df.groupby(['SSUID', 'SHHADID']).apply(self.calc_household_stats).reset_index()
        
        # Filter to households with sufficient observations
        household_stats = household_stats[household_stats['n_months'] >= min_months]
        
        # Remove any remaining NaNs
        household_stats = household_stats.dropna(subset=['cv', 'jump_freq'])
        
        return household_stats
    
    def compute_variance_decomposition(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute variance decomposition for all households.
        
        Args:
            df: Input DataFrame with household data
            
        Returns:
            DataFrame with decomposition results
        """
        return df.groupby(['SSUID', 'SHHADID']).apply(self.decompose_variance_sources).reset_index()
    
    def compute_change_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute change distribution statistics for all households.
        
        Args:
            df: Input DataFrame with household data
            
        Returns:
            DataFrame with change distribution statistics
        """
        return df.groupby(['SSUID', 'SHHADID']).apply(self.analyze_change_distribution).reset_index()
    
    def compute_income_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute income-dependent analysis for all households.
        
        Args:
            df: Input DataFrame with household data
            
        Returns:
            DataFrame with income analysis results, including income_quintile
        """
        income_analysis = df.groupby(['SSUID', 'SHHADID']).apply(self.income_dependent_analysis).reset_index()
        income_analysis = income_analysis.dropna()
        
        # Bin by income level
        income_analysis['income_quintile'] = pd.qcut(
            income_analysis['mean_income'], 
            q=5, 
            labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
        )
        
        return income_analysis
    
    def compute_full_household_stats(self, df: pd.DataFrame, min_months: int = 6) -> pd.DataFrame:
        """
        Compute complete household statistics by merging all analyses.
        
        This creates the household_stats_full DataFrame used for visualization
        and parameter estimation.
        
        Args:
            df: Input DataFrame with household data
            min_months: Minimum number of months required
            
        Returns:
            DataFrame with all household statistics merged
        """
        # Compute base stats with filtering
        household_stats = self.compute_household_stats(df, min_months)
        
        # Compute additional analyses
        decomp = self.compute_variance_decomposition(df)
        change_dist = self.compute_change_distribution(df)
        
        # Merge all together
        household_stats_full = household_stats.merge(decomp, on='SSUID', how='inner')
        household_stats_full = household_stats_full.merge(change_dist, on='SSUID', how='inner')
        
        # Remove any NaNs from the new columns
        household_stats_full = household_stats_full.dropna(subset=['acf_lag1', 'median_abs_change'])
        
        return household_stats_full
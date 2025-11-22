import pandas as pd
from typing import List, Optional
from config.config import HOUSEHOLD_COLS


class DataLoader:
    """Loads household income data from CSV files."""
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize the data loader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
    
    def load_years(self, years: List[int], nrows: Optional[int] = None) -> pd.DataFrame:
        """
        Load and concatenate data from multiple years.
        
        Args:
            years: List of years to load
            nrows: Number of rows to read per file (for testing)
            
        Returns:
            Concatenated DataFrame with added YEAR column
        """
        dfs = []
        for year in years:
            df_year = pd.read_csv(
                f'{self.data_dir}/pu{year}.csv',
                sep='|',
                usecols=HOUSEHOLD_COLS,
                nrows=nrows
            )
            df_year['YEAR'] = year
            dfs.append(df_year)
        
        return pd.concat(dfs, ignore_index=True)
    
    def sort_by_household_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sort by household and time.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Sorted DataFrame
        """
        return df.sort_values(['SSUID', 'YEAR', 'MONTHCODE'])
    
    def filter_to_primary_panel(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Keep only one panel per household (the one with most observations).
        
        This handles cases where households appear in multiple survey panels,
        which would create artificially long time series.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with only one panel per household
        """
        # Count observations per household-panel combination
        panel_counts = df.groupby(['SSUID', 'SHHADID', 'SPANEL']).size().reset_index(name='count')
        
        # For each household, keep the panel with most observations
        idx_max = panel_counts.groupby(['SSUID', 'SHHADID'])['count'].idxmax()
        primary_panels = panel_counts.loc[idx_max, ['SSUID', 'SHHADID', 'SPANEL']]
        
        # Merge to filter
        df_filtered = df.merge(primary_panels, on=['SSUID', 'SHHADID', 'SPANEL'], how='inner')
        
        n_removed = len(df) - len(df_filtered)
        print(f"Filtered to primary panels: removed {n_removed} observations from duplicate panels")
        
        return df_filtered
    
    def deduplicate_months(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Keep only one observation per household per calendar month.
        
        SIPP data contains person-level records, so the same household-month
        can appear multiple times. This keeps the first occurrence.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with one row per household per month
        """
        n_before = len(df)
        
        # Sort to ensure consistent ordering, then keep first of each month
        df_sorted = df.sort_values(['SSUID', 'SHHADID', 'YEAR', 'MONTHCODE', 'SWAVE'])
        df_dedup = df_sorted.drop_duplicates(
            subset=['SSUID', 'SHHADID', 'YEAR', 'MONTHCODE'], 
            keep='first'
        )
        
        n_removed = n_before - len(df_dedup)
        print(f"Deduplicated months: removed {n_removed} duplicate person-level observations")
        print(f"  {n_before} rows -> {len(df_dedup)} rows")
        
        return df_dedup
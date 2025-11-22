"""
Main orchestration script for household income volatility analysis.

This script coordinates the data loading, statistical analysis, simulation,
and visualization pipeline.
"""

from config.config import YEARS, DATA_DIR, MIN_MONTHS, NROWS
from src.data_loader import DataLoader
from src.statistics import Statistics
from src.simulation import Simulation
from src.visualization import Visualization
from src.risk_engine import RiskEngine


def main():
    """Run the complete household income volatility analysis pipeline."""
    
    print("=" * 60)
    print("HOUSEHOLD INCOME VOLATILITY ANALYSIS")
    print("=" * 60)
    
    print("\nLoading data...")
    loader = DataLoader(DATA_DIR)
    df = loader.load_years(YEARS, nrows=NROWS)
    
    df = loader.sort_by_household_time(df)
    print(f"Loaded {len(df)} records for {df['SSUID'].nunique()} households")
    df = loader.filter_to_primary_panel(df)
    df = loader.deduplicate_months(df)
    
    print("\nComputing statistical measures...")
    stats = Statistics()

    household_stats = stats.compute_household_stats(df, min_months=MIN_MONTHS)
    household_stats_full = household_stats  # Alias for backward compatibility

    income_analysis = stats.compute_income_analysis(df)

    print(f"Analyzed {len(household_stats)} households with sufficient data")
    
    # print("\n[3/6] Generating visualizations...")
    viz = Visualization()
    
    # viz.plot_volatility_distributions(household_stats)
    
    # viz.plot_variance_relationships(household_stats_full)
    
    # viz.plot_change_characteristics(household_stats_full)
    
    # viz.plot_income_dependence(income_analysis)
    
    print("\nEstimating model parameters and running simulations...")
    sim = Simulation()

    params, simulated_df, simulated_trajectories = sim.validate_model(
        raw_data=df,
        household_stats_full=household_stats_full,
        income_analysis=income_analysis,
        n_simulations=1000,
        n_months=48
    )
        
    print("\nGenerating validation plots...")
    viz.plot_validation_comparison(household_stats_full, simulated_df)
    
    print("\nGenerating trajectory comparison...")
    viz.plot_trajectory_comparison(df, simulated_trajectories, n_samples=50)
    
    print("\nRunning risk engine analysis...")
    risk_engine = RiskEngine(
        initial_fund=10000,
        monthly_expenses=3000,
        initial_income=6000,
        n_months=24,
        n_simulations=1000
    )
    
    risk_metrics = risk_engine.run_risk_assessment(params, seed=42)
    
    print(f"\nRisk Assessment Results:")
    print(f"Debt probability: {risk_metrics['debt_probability']:.3f}")
    print(f"Mean minimum balance: ${risk_metrics['mean_min_balance']:,.0f}")
    print(f"Mean final balance: ${risk_metrics['mean_final_balance']:,.0f}")


if __name__ == "__main__":
    main()
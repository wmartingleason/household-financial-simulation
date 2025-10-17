# Household Financial Risk Simulator

A Monte Carlo simulation platform for analyzing household financial risk using real-world income volatility patterns from SIPP (Survey of Income and Program Participation) data.

## Overview

This project implements a financial risk assessment tool that models household income volatility using a compound Poisson jump process. The system processes SIPP data to extract statistical parameters, then uses these parameters in Monte Carlo simulations to project wealth trajectories and assess debt risk under various financial scenarios.

## Architecture

The system consists of three main components:

- **Data Analysis Pipeline** (`/data_analysis/`): Processes SIPP data to extract income volatility parameters
- **Backend API** (`/backend/`): FastAPI service that runs Monte Carlo simulations
- **Frontend Interface** (`/frontend/`): React application for interactive visualization and analysis

## Core Modeling Framework

### Income Volatility Model

The system uses a **compound Poisson jump process** to model household income dynamics:

```
Income(t+1) = Income(t) × (1 + Jump(t))
```

Where:
- **Jump frequency**: λ = 0.273 (27.3% chance of income change per month)
- **Jump size distribution**: Lognormal with median 23.2% change
- **Jump direction**: 50% upward, 50% downward
- **Jump size percentiles**: 25th = 11.5%, 75th = 54.5%

### Parameter Estimation from SIPP Data

The model parameters are derived from real household income data through a statistical analysis pipeline:

1. **Data Loading**: Processes SIPP household income records (2021-2024)
2. **Statistical Analysis**: Computes volatility metrics including:
   - Coefficient of variation (CV)
   - Jump frequency and magnitude distributions
   - Income change patterns and persistence
   - Variance decomposition into trend and volatility components

3. **Parameter Extraction**: Estimates model parameters using robust statistical methods:
   - Winsorized jump sizes at 99th percentile to remove outliers
   - Median-based parameter estimation for robustness
   - Interquartile range analysis for lognormal distribution fitting

### Monte Carlo Simulation Engine

The simulation engine (`RiskEngine`) implements Monte Carlo-powered financial modeling:

#### Income Trajectory Generation
- Generates stochastic income paths using the compound Poisson model
- Each household draws its own jump frequency from a Beta distribution
- Jump sizes follow lognormal distribution with estimated parameters
- Income floors at $100 to prevent unrealistic values

#### Financial Outcome Simulation
- Models monthly savings evolution: `Balance(t) = Balance(t-1) + Income(t) - Expenses`
- Applies compound interest on debt: `Interest = Balance × (Annual Rate / 12)`
- Tracks credit exhaustion when debt exceeds available credit limit
- Calculates comprehensive risk metrics across 10,000+ simulation trials

## Key Features

### Advanced Risk Metrics

The system calculates risk measures:

- **Debt Probability**: Percentage of simulations ending in negative balance
- **Credit Exhaustion Risk**: Probability of exceeding available credit
- **Survival Curves**: Probability of staying positive over time
- **Interest Cost Analysis**: Total interest paid across scenarios
- **Minimum Balance Statistics**: Distribution of lowest balance reached

### Interactive Visualizations

The frontend provides data visualization:

- **Monte Carlo Trajectory Plots**: Shows percentile bands and sample paths
- **Outcome Distribution Histograms**: Terminal wealth distribution analysis
- **Survival Curve Charts**: Risk evolution over time
- **Comprehensive Reporting**: Detailed statistical breakdowns

### Real-Time Analysis

- **Parameter Validation**: Compares simulated vs. real data statistics
- **Strategy Comparison**: Evaluates different expense levels
- **Sensitivity Analysis**: Tests impact of parameter variations

## Data Processing Pipeline

### SIPP Data Analysis (`/data_analysis/`)

The data analysis module processes real household income data:

```python
# Main analysis pipeline
loader = DataLoader(DATA_DIR)
df = loader.load_years(YEARS, nrows=NROWS)
df = loader.filter_to_primary_panel(df)  # Remove duplicate panels
df = loader.deduplicate_months(df)      # One observation per household-month

# Statistical analysis
stats = Statistics()
household_stats = stats.compute_household_stats(df, min_months=MIN_MONTHS)
income_analysis = stats.compute_income_analysis(df)

# Parameter estimation and validation
sim = Simulation()
params, simulated_df, trajectories = sim.validate_model(
    household_stats, income_analysis, n_simulations=1000, n_months=48
)
```

### Key Statistical Measures

- **Volatility Metrics**: Coefficient of variation, variance decomposition
- **Jump Analysis**: Frequency, magnitude, and directional patterns
- **Income Dependence**: How volatility varies with income level
- **Temporal Patterns**: Autocorrelation and trend analysis

## Backend API (`/backend/`)

The FastAPI backend provides a robust simulation service:

### Endpoints

- `POST /api/calculate`: Run Monte Carlo simulation
- `GET /health`: Service health check
- `GET /docs`: API documentation

### Request Schema

```json
{
  "monthlyIncome": 5000,
  "monthlyExpenses": 3500,
  "currentSavings": 10000,
  "availableCredit": 30000,
  "interestRate": 25,
  "timeHorizon": 24
}
```

### Response Structure

The API returns simulation results:

- **Sample Paths**: 100 representative wealth trajectories
- **Aggregate Statistics**: Percentile bands over time
- **Terminal Distribution**: Final balance statistics
- **Risk Metrics**: Debt probabilities and survival curves
- **Metadata**: Simulation parameters and configuration

## Frontend Interface (`/frontend/`)

The React frontend provides an intuitive user experience:

### Components

- **InputForm**: Collects financial parameters
- **ResultsDisplay**: Visualization and reporting
- **MonteCarloChart**: Simulation trajectory visualization
- **SurvivalCurve**: Risk evolution over time
- **OutcomeDistribution**: Terminal wealth histogram

### Visualization Features

- **Dynamic Charts**: Responsive visualizations using Recharts
- **Interactive Tooltips**: Detailed information on hover
- **Tabbed Interface**: Multiple visualization modes
- **Collapsible Reports**: Detailed statistical breakdowns
- **Risk Assessment**: Color-coded outcome classification

## Technical Implementation

### Simulation Algorithm

```python
def simulate_financial_outcomes(self, initial_fund, monthly_expenses, 
                               initial_income, available_credit, 
                               interest_rate, n_months, n_simulations, 
                               params, seed=None):
    """
    Monte Carlo simulation with debt modeling and interest calculation
    """
    for i in range(n_simulations):
        # Generate stochastic income trajectory
        income_trajectory = self.simulate_trajectory(
            initial_income, n_months, params, seed=i
        )
        
        # Simulate financial evolution
        balance = initial_fund
        for month_income in income_trajectory:
            monthly_savings = month_income - monthly_expenses
            balance += monthly_savings
            
            # Apply interest if in debt
            if balance < 0:
                monthly_interest = balance * (interest_rate / 12)
                balance += monthly_interest
                
            # Track credit exhaustion
            if balance < -available_credit:
                exhausted_credit = True
```

### Model Validation

The system includes comprehensive validation:

- **Parameter Estimation**: Robust statistical methods for parameter extraction
- **Model Validation**: Comparison of simulated vs. real data distributions
- **Sensitivity Analysis**: Testing parameter stability
- **Cross-Validation**: Multiple validation approaches

## Installation and Usage

### Prerequisites

- Python 3.8+
- Node.js 16+
- SIPP data files (pu2021.csv, pu2022.csv, pu2023.csv, pu2024.csv)

### Setup

1. **Data Analysis Environment**:
```bash
cd data_analysis
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Backend API**:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

3. **Frontend Interface**:
```bash
cd frontend
npm install
npm run dev
```

### Running Analysis

**Process SIPP Data**:
```bash
cd data_analysis
python main.py
```

## Model Validation Results

The system demonstrates strong validation performance:

- **Jump Frequency**: Real data 27.3% vs. Simulated 27.1%
- **Jump Magnitude**: Real median 23.2% vs. Simulated 22.8%
- **Volatility Distribution**: CV distributions match within 5%
- **Temporal Patterns**: Autocorrelation preserved in simulations

## Research Applications

This simulator may facilitate research into:

- **Household Financial Resilience**: How income volatility affects financial stability
- **Emergency Fund Adequacy**: Optimal savings levels for different risk profiles
- **Debt Risk Assessment**: Probability of financial distress under various scenarios
- **Policy Analysis**: Impact of income support programs on financial outcomes

## Technical Specifications

- **Simulation Scale**: 10,000+ Monte Carlo trials per analysis
- **Time Horizon**: Intended for 1-4 year long simulations
- **Data Sources**: SIPP 2021-2024 household income data
- **Household Income Model**: Compound Poisson process with lognormal jumps

## Contributing

This project represents a comprehensive approach to household financial risk modeling, combining real-world data analysis with sophisticated simulation techniques. The modular architecture enables extension and customization for specific research needs.

## License

[Add appropriate license information]

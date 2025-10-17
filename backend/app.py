"""
FastAPI backend for household financial simulation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from risk_engine import RiskEngine
from config import MODEL_PARAMS, DEFAULT_N_SIMULATIONS
from mangum import Mangum

app = FastAPI(title="Household Financial Simulation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://wmartingleason.com",
        "https://wmartingleason.com",
        "https://www.wmartingleason.com",
        "http://localhost:5173",
        "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class RiskRequest(BaseModel):
    monthlyIncome: float = Field(..., gt=0, description="Current monthly income")
    monthlyExpenses: float = Field(..., ge=0, description="Monthly expenses")
    currentSavings: float = Field(..., ge=0, description="Current savings")
    availableCredit: float = Field(..., ge=0, description="Available credit")
    interestRate: float = Field(..., ge=0, description="Interest rate")
    timeHorizon: int = Field(..., gt=0, le=240, description="Time horizon in months")

# Nested response schemas
class AggregateStats(BaseModel):
    months: List[int]
    mean: List[float]
    p5: List[float]
    p10: List[float]
    p25: List[float]
    p50: List[float]
    p75: List[float]
    p90: List[float]
    p95: List[float]

class TerminalStats(BaseModel):
    mean: float
    median: float
    std: float
    p5: float
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float
    p95: float

class Statistics(BaseModel):
    terminalStats: TerminalStats
    negativeTerminalPct: float
    everNegativePct: float
    creditExhaustionPct: float
    medianMinBalance: float
    meanMinBalance: float
    medianInterestPaid: float
    meanInterestPaid: float
    medianMonthsToNegative: Optional[float]

class RiskMetrics(BaseModel):
    probabilityPositiveByMonth: List[float]
    probabilityAboveCreditByMonth: List[float]
    emergencyFundMonths: float
    monthlyNetIncome: float

class Metadata(BaseModel):
    nSimulations: int
    nMonths: int
    nSamplePaths: int
    initialFund: float
    monthlyExpenses: float
    initialIncome: float
    availableCredit: float
    interestRate: float

# Main response schema
class RiskResponse(BaseModel):
    samplePaths: List[List[float]]
    terminalValues: List[float]
    aggregateStats: AggregateStats
    statistics: Statistics
    riskMetrics: RiskMetrics
    metadata: Metadata

@app.post("/api/calculate", response_model=RiskResponse)
def simulate_financial_outcomes(request: RiskRequest):
    """
    Calculate financial outcomes using Monte Carlo simulation.
    Returns comprehensive simulation data including trajectories, statistics, and risk metrics.
    """
    try:
        engine = RiskEngine()
        
        # Run the simulation
        results = engine.simulate_financial_outcomes(
            initial_fund=request.currentSavings,
            initial_income=request.monthlyIncome,
            monthly_expenses=request.monthlyExpenses,
            available_credit=request.availableCredit,
            interest_rate=request.interestRate / 100,
            n_months=request.timeHorizon,
            n_simulations=DEFAULT_N_SIMULATIONS,
            params=MODEL_PARAMS,
            seed=42,
            n_sample_paths=100
        )
        
        aggregate_stats = AggregateStats(**results['aggregateStats'])
        
        terminal_stats = TerminalStats(**results['statistics']['terminalStats'])
        statistics = Statistics(
            terminalStats=terminal_stats,
            negativeTerminalPct=results['statistics']['negativeTerminalPct'],
            everNegativePct=results['statistics']['everNegativePct'],
            creditExhaustionPct=results['statistics']['creditExhaustionPct'],
            medianMinBalance=results['statistics']['medianMinBalance'],
            meanMinBalance=results['statistics']['meanMinBalance'],
            medianInterestPaid=results['statistics']['medianInterestPaid'],
            meanInterestPaid=results['statistics']['meanInterestPaid'],
            medianMonthsToNegative=results['statistics']['medianMonthsToNegative']
        )
        
        risk_metrics = RiskMetrics(**results['riskMetrics'])
        metadata = Metadata(**results['metadata'])
        
        return RiskResponse(
            samplePaths=results['samplePaths'],
            terminalValues=results['terminalValues'],
            aggregateStats=aggregate_stats,
            statistics=statistics,
            riskMetrics=risk_metrics,
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )

@app.get("/")
def root():
    return {"message": "Financial Simulation API", "endpoints": ["/api/calculate", "/health", "/docs"]}

@app.get("/health")
def health_check():
    """Health check for deployment monitoring."""
    return {"status": "healthy"}

handler = Mangum(app)
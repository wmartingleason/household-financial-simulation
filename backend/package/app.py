"""
FastAPI backend for bankruptcy risk calculation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from risk_engine import RiskEngine
from config import MODEL_PARAMS, DEFAULT_N_SIMULATIONS

app = FastAPI(title="Bankruptcy Risk API")

# Enable CORS so React can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://wmartingleason.com",
        "https://wmartingleason.com",
        "https://www.wmartingleason.com"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class RiskRequest(BaseModel):
    monthlyIncome: float = Field(..., gt=0, description="Current monthly income")
    monthlyExpenses: float = Field(..., ge=0, description="Monthly expenses")
    currentSavings: float = Field(..., ge=0, description="Current savings")
    timeHorizon: int = Field(..., gt=0, le=240, description="Time horizon in months")

# Response schema
class RiskResponse(BaseModel):
    bankruptcyRisk: float
    iterations: int
    monthlyIncome: float
    monthlyExpenses: float
    currentSavings: float
    timeHorizon: int
    meanMinBalance: Optional[float] = None
    meanFinalBalance: Optional[float] = None
    medianMinBalance: Optional[float] = None
    medianFinalBalance: Optional[float] = None


@app.post("/api/calculate", response_model=RiskResponse)
def calculate_bankruptcy_risk(request: RiskRequest):
    """
    Calculate bankruptcy risk using Monte Carlo simulation.
    
    Returns the probability of going into debt within the specified time horizon.
    """
    try:
        # Initialize the risk engine
        engine = RiskEngine()
        
        # Run the simulation
        results = engine.calculate_bankruptcy_risk(
            initial_fund=request.currentSavings,
            monthly_expenses=request.monthlyExpenses,
            initial_income=request.monthlyIncome,
            n_months=request.timeHorizon,
            n_simulations=DEFAULT_N_SIMULATIONS,
            params=MODEL_PARAMS,
            seed=42
        )
        
        # Convert debt_probability to percentage
        bankruptcy_risk_pct = results['debt_probability'] * 100
        
        return RiskResponse(
            bankruptcyRisk=bankruptcy_risk_pct,
            iterations=DEFAULT_N_SIMULATIONS,
            monthlyIncome=request.monthlyIncome,
            monthlyExpenses=request.monthlyExpenses,
            currentSavings=request.currentSavings,
            timeHorizon=request.timeHorizon,
            meanMinBalance=results['mean_min_balance'],
            meanFinalBalance=results['mean_final_balance'],
            medianMinBalance=results['median_min_balance'],
            medianFinalBalance=results['median_final_balance']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Simulation failed: {str(e)}"
        )

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "message": "Bankruptcy Risk API is running",
        "docs": "Visit /docs for interactive API documentation"
    }

@app.get("/health")
def health_check():
    """Health check for deployment monitoring."""
    return {"status": "healthy"}

handler = Mangum(app)
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from backend.engine.elasticity import ElasticityEngine
from backend.engine.waterfall import WaterfallEngine
from backend.engine.simulator import ScenarioSimulator
from agent.pricing_agent import PricingOrchestratorAgent

app = FastAPI(
    title="UP PRICING INTELLIGENCE™ - Executive Cockpit",
    version="1.0.0"
)

agent = PricingOrchestratorAgent()

class SimulationRequest(BaseModel):
    sku: str
    price_change_pct: float
    segment: Optional[str] = "ALL"

@app.get("/api/portfolio")
def get_portfolio():
    return agent.generate_portfolio_opportunity_map()

@app.get("/api/waterfall/{sku}")
def get_waterfall(sku: str):
    return WaterfallEngine.generate_waterfall(sku)

@app.get("/api/elasticity/{sku}")
def get_elasticity(sku: str, segment: Optional[str] = "ALL"):
    return ElasticityEngine.calculate_from_transactions(
        transactions_df=None, sku=sku, segment=None if segment == "ALL" else segment
    )

@app.post("/api/simulate")
def run_simulation(req: SimulationRequest):
    return ScenarioSimulator.run_simulation(
        sku=req.sku,
        price_change_pct=req.price_change_pct,
        segment=None if req.segment == "ALL" else req.segment
    )

@app.get("/api/diagnose/{sku}")
def diagnose_sku(sku: str):
    return agent.analyze_sku(sku)

# Main Dashboard View
@app.get("/", response_class=HTMLResponse)
def index():
    # Return complete responsive SPA Dashboard
    with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("dashboard.app:app", host="127.0.0.1", port=8000, reload=True)

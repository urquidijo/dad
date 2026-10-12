"""
UP PRICING INTELLIGENCE™ - Pricing Orchestrator Agent
Strategic AI Consultant leveraging Value-Based Pricing, Guardrails, and Econometric Tools.
"""

import json
from typing import Dict, Any, List
from backend.engine.elasticity import ElasticityEngine
from backend.engine.waterfall import WaterfallEngine
from backend.engine.simulator import ScenarioSimulator

class PricingOrchestratorAgent:
    """
    Antigravity AI Pricing Consultant.
    Orchestrates mathematical pricing tools, applies strategic business guardrails,
    and formulates executive pricing recommendations.
    """

    SYSTEM_ROLE = """
    Eres el Senior Pricing Consultant de UP PRICING INTELLIGENCE™.
    Tus principios de decisión son:
    1. Value-Based Pricing sobre Cost-Plus.
    2. Proteger el margen de bolsillo (Pocket Margin) identificando fugas de descuentos.
    3. Respetar estrictamente los Guardrails de margen mínimo (> 20%).
    4. Rechazar reducciones de precio lineales que no demuestren ganancia neta mediante elasticidad.
    """

    def __init__(self):
        self.catalog = [
            "SKU-BEV-001",
            "SKU-SNK-002",
            "SKU-DAI-003",
            "SKU-ORG-004",
            "SKU-CLE-005"
        ]

    def analyze_sku(self, sku: str) -> Dict[str, Any]:
        """
        Executes a comprehensive 360° pricing diagnostic for a single SKU:
        Elasticity + Price Waterfall + Opportunity Identification.
        """
        sku_clean = sku.strip().upper()
        waterfall = WaterfallEngine.generate_waterfall(sku_clean)
        elasticity = ElasticityEngine.calculate_from_transactions(None, sku_clean)

        # Strategic Analysis
        coeff = elasticity["elasticity_coefficient"]
        pocket_margin_pct = waterfall["metrics"]["pocket_margin_percent"]
        top_leak = waterfall["metrics"]["top_margin_leak"]

        if abs(coeff) < 0.8:
            strategic_verdict = "OPORTUNIDAD DE CAPTURA DE VALOR (ALZA DE PRECIO RECOMENDADA)"
            recommended_action = (
                f"El producto es inelástico ({coeff:.2f}). Se recomienda un aumento de precio entre +4% y +8%. "
                f"Adicionalmente, auditar y recortar '{top_leak}' para recuperar margen de bolsillo."
            )
            opportunity_score = 92
        elif abs(coeff) > 1.4:
            strategic_verdict = "ALTO RIESGO DE COMMODITIZACIÓN (OPTIMIZACIÓN DE FUGAS)"
            recommended_action = (
                f"Producto elástico ({coeff:.2f}). No subir precios de lista. La palanca de rentabilidad es "
                f"reestructurar '{top_leak}' y exigir contraprestación de volumen a distribuidores."
            )
            opportunity_score = 68
        else:
            strategic_verdict = "ZONA DE EQUILIBRIO COMPETITIVO"
            recommended_action = (
                f"Elasticidad moderada ({coeff:.2f}). Mantener precio y enfocar en promociones paquetizadas."
            )
            opportunity_score = 75

        return {
            "sku": sku_clean,
            "product_name": waterfall["product_name"],
            "waterfall_summary": waterfall["metrics"],
            "elasticity_summary": elasticity,
            "strategic_verdict": strategic_verdict,
            "opportunity_score": opportunity_score,
            "executive_recommendation": recommended_action
        }

    def evaluate_price_change(self, sku: str, price_change_pct: float, segment: str = "ALL") -> Dict[str, Any]:
        """
        Simulates scenario and returns executive consultant justification.
        """
        sim = ScenarioSimulator.run_simulation(sku, price_change_pct, segment)
        return {
            "simulation_result": sim,
            "consultant_verdict": sim["guardrail_status"],
            "rationale": sim["strategic_rationale"]
        }

    def generate_portfolio_opportunity_map(self) -> List[Dict[str, Any]]:
        """
        Generates the Executive Opportunity Matrix across all SKUs.
        """
        results = []
        for sku in self.catalog:
            results.append(self.analyze_sku(sku))
        results.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return results

if __name__ == "__main__":
    agent = PricingOrchestratorAgent()
    print("=" * 60)
    print("UP PRICING INTELLIGENCE™ - Portfolio Opportunity Diagnostic")
    print("=" * 60)
    report = agent.generate_portfolio_opportunity_map()
    for item in report:
        print(f"\n[{item['sku']}] {item['product_name']}")
        print(f"  Score: {item['opportunity_score']} | Veredicto: {item['strategic_verdict']}")
        print(f"  Margen Bolsillo: {item['waterfall_summary']['pocket_margin_percent']}% | Elasticidad: {item['elasticity_summary']['elasticity_coefficient']}")
        print(f"  Consejo: {item['executive_recommendation']}")

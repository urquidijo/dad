from typing import Dict, Any, Optional
from backend.engine.elasticity import ElasticityEngine
from backend.engine.waterfall import WaterfallEngine

class ScenarioSimulator:
    """
    Simulates What-If pricing changes and enforces Strategic Pricing Guardrails.
    """

    BASELINE_VOLUMES = {
        "SKU-BEV-001": 25000,
        "SKU-SNK-002": 14000,
        "SKU-DAI-003": 11000,
        "SKU-ORG-004": 6500,
        "SKU-CLE-005": 16000
    }

    @classmethod
    def run_simulation(
        cls,
        sku: str,
        price_change_pct: float,
        segment: Optional[str] = None
    ) -> Dict[str, Any]:
        sku_clean = sku.strip().upper()
        waterfall = WaterfallEngine.generate_waterfall(sku_clean)
        elasticity_data = ElasticityEngine.calculate_from_transactions(
            transactions_df=None, sku=sku_clean, segment=segment
        )

        base_pocket_price = waterfall["metrics"]["pocket_price"]
        cogs = waterfall["metrics"]["cogs"]
        base_volume = cls.BASELINE_VOLUMES.get(sku_clean, 10000)
        elasticity = elasticity_data["elasticity_coefficient"]

        # 1. Baseline Calculations
        base_revenue = base_pocket_price * base_volume
        base_profit = (base_pocket_price - cogs) * base_volume
        base_margin_pct = (base_profit / base_revenue * 100) if base_revenue > 0 else 0

        # 2. Projected Metrics with Price Change
        new_pocket_price = base_pocket_price * (1 + price_change_pct / 100.0)
        demand_change_pct = elasticity * price_change_pct
        new_volume = max(0, int(round(base_volume * (1 + demand_change_pct / 100.0))))

        new_revenue = new_pocket_price * new_volume
        new_profit = (new_pocket_price - cogs) * new_volume
        new_margin_pct = ((new_pocket_price - cogs) / new_pocket_price * 100) if new_pocket_price > 0 else 0

        revenue_delta = new_revenue - base_revenue
        profit_delta = new_profit - base_profit

        # 3. Guardrail Evaluations
        min_margin_guardrail = 20.0
        guardrail_status = "APPROVED"
        guardrail_flags = []
        strategic_rationale = ""

        if new_margin_pct < min_margin_guardrail:
            guardrail_status = "REJECTED"
            guardrail_flags.append(
                f"Fallo de Guardrail de Margen: El margen proyectado ({new_margin_pct:.1f}%) está por debajo del umbral mínimo corporativo ({min_margin_guardrail}%)."
            )

        if profit_delta < 0 and price_change_pct < 0:
            guardrail_status = "REJECTED"
            guardrail_flags.append(
                f"Destrucción de Beneficio: La reducción de precio de {price_change_pct}% no genera suficiente elasticidad para compensar la erosión de margen (Pérdida neta: ${abs(profit_delta):,.2f})."
            )

        if price_change_pct > 15.0 and abs(elasticity) > 1.2:
            if guardrail_status != "REJECTED":
                guardrail_status = "WARNING"
            guardrail_flags.append(
                f"Riesgo de Churn Masivo: Subida abrupta en producto elástico ({elasticity:.2f}) provocará una caída de demanda estimada del {abs(demand_change_pct):.1f}%."
            )

        # 4. Strategic Rationale
        if guardrail_status == "APPROVED":
            if profit_delta > 0:
                strategic_rationale = (
                    f"Aprobado por el Pricing Engine: Un ajuste de {price_change_pct:+.1f}% incrementa el beneficio neto en "
                    f"${profit_delta:,.2f} (+{(profit_delta/base_profit*100):.1f}%). El producto presenta elasticidad favorable ({elasticity:.2f})."
                )
            else:
                strategic_rationale = "Aprobado: El ajuste se mantiene dentro de los límites de tolerancia operativa y política comercial."
        elif guardrail_status == "WARNING":
            strategic_rationale = (
                f"Aprobado con Advertencias: Beneficio proyectado favorable (${profit_delta:+,.2f}), pero monitorear cuota de mercado ante fuga de volumen (-{abs(demand_change_pct):.1f}%)."
            )
        else:
            strategic_rationale = (
                f"Propuesta RECHAZADA por los Guardrails Corporativos: " + " ".join(guardrail_flags)
            )

        return {
            "sku": sku_clean,
            "product_name": waterfall["product_name"],
            "segment": segment or "TODOS",
            "price_change_pct": price_change_pct,
            "elasticity_coefficient": elasticity,
            "guardrail_status": guardrail_status,
            "guardrail_flags": guardrail_flags,
            "strategic_rationale": strategic_rationale,
            "baseline": {
                "pocket_price": round(base_pocket_price, 2),
                "volume": base_volume,
                "revenue": round(base_revenue, 2),
                "profit": round(base_profit, 2),
                "margin_pct": round(base_margin_pct, 2)
            },
            "projected": {
                "pocket_price": round(new_pocket_price, 2),
                "volume": new_volume,
                "demand_change_pct": round(demand_change_pct, 2),
                "revenue": round(new_revenue, 2),
                "profit": round(new_profit, 2),
                "margin_pct": round(new_margin_pct, 2),
                "revenue_delta": round(revenue_delta, 2),
                "profit_delta": round(profit_delta, 2)
            }
        }

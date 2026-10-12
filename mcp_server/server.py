"""
UP PRICING INTELLIGENCE™ - Model Context Protocol (MCP) Server
Exposes Pricing Intelligence mathematical engines as MCP tools for Antigravity Agents.
"""

from mcp.server.fastmcp import FastMCP
from backend.engine.elasticity import ElasticityEngine
from backend.engine.waterfall import WaterfallEngine
from backend.engine.simulator import ScenarioSimulator

# Initialize FastMCP Server
mcp = FastMCP("up-pricing-intelligence")

@mcp.tool()
def calculate_elasticity(sku: str, segment: str = "ALL") -> dict:
    """
    Calcula el coeficiente econométrico de elasticidad precio-demanda (PED),
    el R² de ajuste, nivel de confianza y la recomendación estratégica de pricing.
    
    Args:
        sku: Código único del producto (ej: 'SKU-BEV-001', 'SKU-SNK-002', 'SKU-ORG-004').
        segment: Segmento de cliente opcional ('MASS_RETAIL', 'CONVENIENCE', 'WHOLESALE', 'ECOMMERCE', 'ALL').
    """
    segment_param = None if segment == "ALL" else segment
    return ElasticityEngine.calculate_from_transactions(
        transactions_df=None, sku=sku, segment=segment_param
    )

@mcp.tool()
def generate_price_waterfall(sku: str) -> dict:
    """
    Genera el desglose completo de la Cascada de Precios (Price Waterfall),
    identificando el Precio de Lista, descuentos en factura, fugas fuera de factura
    (rebates, subsidios), Precio de Bolsillo (Pocket Price) y Margen de Bolsillo.
    
    Args:
        sku: Código único del producto (ej: 'SKU-BEV-001', 'SKU-SNK-002', 'SKU-ORG-004').
    """
    return WaterfallEngine.generate_waterfall(sku)

@mcp.tool()
def run_what_if_scenario(sku: str, price_change_percentage: float, segment: str = "ALL") -> dict:
    """
    Simula un escenario 'What-If' con un cambio porcentual de precio,
    proyectando el impacto en demanda, ingresos brutos y beneficio neto,
    y evaluando los Guardrails estratégicos (margen mínimo, prevención de pérdidas).
    
    Args:
        sku: Código único del producto (ej: 'SKU-BEV-001', 'SKU-SNK-002', 'SKU-ORG-004').
        price_change_percentage: Porcentaje de ajuste de precio (ej: 5.0 para +5%, -3.5 para -3.5%).
        segment: Segmento de cliente a evaluar ('ALL', 'MASS_RETAIL', 'CONVENIENCE', etc.).
    """
    segment_param = None if segment == "ALL" else segment
    return ScenarioSimulator.run_simulation(
        sku=sku, price_change_pct=price_change_percentage, segment=segment_param
    )

if __name__ == "__main__":
    mcp.run()

from typing import Dict, Any

class WaterfallEngine:
    """
    Price Waterfall & Margin Leakage Engine.
    Breaks down List Price to Pocket Price and Pocket Margin:
    List Price
      - Standard Discount
    = Invoice Price
      - Cash / Early Payment Discount
      - Promotional Allowance
      - Annual Rebate
    = Pocket Price
      - COGS (Base Cost)
    = Pocket Margin (Absolute & Percentage)
    """

    DEFAULT_CATALOG = {
        "SKU-BEV-001": {
            "name": "Bebida Energética Ultra 500ml",
            "list_price": 3.50,
            "standard_discount": 0.35,
            "cash_discount": 0.10,
            "promotional_allowance": 0.20,
            "annual_rebate": 0.15,
            "base_cost": 1.20,
            "min_margin_percent": 20.0
        },
        "SKU-SNK-002": {
            "name": "Snack Premium Frutos Secos 150g",
            "list_price": 5.00,
            "standard_discount": 0.50,
            "cash_discount": 0.15,
            "promotional_allowance": 0.30,
            "annual_rebate": 0.25,
            "base_cost": 2.10,
            "min_margin_percent": 25.0
        },
        "SKU-DAI-003": {
            "name": "Yogurt Griego Artesanal 1L",
            "list_price": 4.20,
            "standard_discount": 0.40,
            "cash_discount": 0.10,
            "promotional_allowance": 0.25,
            "annual_rebate": 0.20,
            "base_cost": 1.80,
            "min_margin_percent": 18.0
        },
        "SKU-ORG-004": {
            "name": "Café Especialidad Orgánico 250g",
            "list_price": 9.00,
            "standard_discount": 0.90,
            "cash_discount": 0.20,
            "promotional_allowance": 0.40,
            "annual_rebate": 0.50,
            "base_cost": 3.50,
            "min_margin_percent": 30.0
        },
        "SKU-CLE-005": {
            "name": "Detergente Eco Líquido 3L",
            "list_price": 8.50,
            "standard_discount": 0.85,
            "cash_discount": 0.25,
            "promotional_allowance": 0.50,
            "annual_rebate": 0.40,
            "base_cost": 4.00,
            "min_margin_percent": 15.0
        }
    }

    @classmethod
    def generate_waterfall(cls, sku: str) -> Dict[str, Any]:
        sku_clean = sku.strip().upper()
        item = cls.DEFAULT_CATALOG.get(sku_clean)
        if not item:
            # Default template for unknown SKU
            item = {
                "name": f"Producto Genérico ({sku})",
                "list_price": 10.00,
                "standard_discount": 1.00,
                "cash_discount": 0.30,
                "promotional_allowance": 0.50,
                "annual_rebate": 0.40,
                "base_cost": 4.50,
                "min_margin_percent": 20.0
            }

        list_price = float(item["list_price"])
        std_discount = float(item["standard_discount"])
        invoice_price = list_price - std_discount

        cash_disc = float(item["cash_discount"])
        promo_allowance = float(item["promotional_allowance"])
        annual_rebate = float(item["annual_rebate"])
        off_invoice_leak = cash_disc + promo_allowance + annual_rebate

        pocket_price = invoice_price - off_invoice_leak
        base_cost = float(item["base_cost"])
        pocket_margin = pocket_price - base_cost
        pocket_margin_pct = (pocket_margin / pocket_price * 100) if pocket_price > 0 else 0

        # Identification of primary leakage point
        leakages = [
            ("Descuento Estándar de Factura", std_discount),
            ("Descuento Pronto Pago", cash_disc),
            ("Apoyo Promocional (Trade Spend)", promo_allowance),
            ("Rebates Anuales por Volumen", annual_rebate),
        ]
        leakages.sort(key=lambda x: x[1], reverse=True)
        top_leak_name, top_leak_val = leakages[0]

        return {
            "sku": sku_clean,
            "product_name": item["name"],
            "steps": [
                {"label": "Precio de Lista (MSRP)", "amount": round(list_price, 2), "type": "base"},
                {"label": "Descuento en Factura", "amount": round(-std_discount, 2), "type": "deduction"},
                {"label": "Precio de Factura", "amount": round(invoice_price, 2), "type": "subtotal"},
                {"label": "Descuento Pronto Pago", "amount": round(-cash_disc, 2), "type": "deduction"},
                {"label": "Subsidio Promocional", "amount": round(-promo_allowance, 2), "type": "deduction"},
                {"label": "Rebate Anual Fuera de Factura", "amount": round(-annual_rebate, 2), "type": "deduction"},
                {"label": "Precio de Bolsillo (Pocket Price)", "amount": round(pocket_price, 2), "type": "subtotal"},
                {"label": "Costo de Mercancía (COGS)", "amount": round(-base_cost, 2), "type": "cost"},
                {"label": "Margen de Bolsillo (Pocket Margin)", "amount": round(pocket_margin, 2), "type": "final_profit"}
            ],
            "metrics": {
                "list_price": round(list_price, 2),
                "invoice_price": round(invoice_price, 2),
                "pocket_price": round(pocket_price, 2),
                "cogs": round(base_cost, 2),
                "pocket_margin": round(pocket_margin, 2),
                "pocket_margin_percent": round(pocket_margin_pct, 2),
                "total_discount_leakage": round(list_price - pocket_price, 2),
                "top_margin_leak": f"{top_leak_name} (${top_leak_val:.2f} por unidad)"
            }
        }

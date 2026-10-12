-- =============================================================================
-- UP PRICING INTELLIGENCE™ - Seed Data for Retail Pricing
-- =============================================================================

-- 1. Insert Segments
INSERT INTO customer_segments (segment_code, segment_name, description, price_sensitivity_rating) VALUES
('MASS_RETAIL', 'Supermercados & Mass Retail', 'Cadenas de supermercados con alta rotación y alta sensibilidad a precio', 'HIGH'),
('CONVENIENCE', 'Tiendas de Conveniencia / Express', 'Puntos de venta de paso con baja sensibilidad a precio y mayor margen', 'LOW'),
('WHOLESALE', 'Mayoristas / Distribuidores', 'Volúmenes masivos con negociación agresiva de rebajas y descuentos', 'HIGH'),
('ECOMMERCE', 'Canal Digital Directo (DTC)', 'Consumidores directos con comportamiento elástico influenciado por promociones', 'MEDIUM')
ON CONFLICT (segment_code) DO NOTHING;

-- 2. Insert Products
INSERT INTO products (sku, name, category, base_cost, list_price, min_margin_percent, current_inventory) VALUES
('SKU-BEV-001', 'Bebida Energética Ultra 500ml', 'Bebidas', 1.20, 3.50, 20.00, 15000),
('SKU-SNK-002', 'Snack Premium Frutos Secos 150g', 'Snacks', 2.10, 5.00, 25.00, 8500),
('SKU-DAI-003', 'Yogurt Griego Artesanal 1L', 'Lácteos', 1.80, 4.20, 18.00, 6200),
('SKU-ORG-004', 'Café Especialidad Orgánico 250g', 'Gourmet', 3.50, 9.00, 30.00, 4100),
('SKU-CLE-005', 'Detergente Eco Líquido 3L', 'Hogar', 4.00, 8.50, 15.00, 9300)
ON CONFLICT (sku) DO NOTHING;

-- 3. Initial Price Waterfalls
INSERT INTO pricing_waterfalls (product_id, list_price, standard_discount, invoice_price, cash_discount, promotional_allowance, annual_rebate, pocket_price, unit_cogs, pocket_margin, pocket_margin_percent) VALUES
(1, 3.50, 0.35, 3.15, 0.10, 0.20, 0.15, 2.70, 1.20, 1.50, 42.86),
(2, 5.00, 0.50, 4.50, 0.15, 0.30, 0.25, 3.80, 2.10, 1.70, 34.00),
(3, 4.20, 0.40, 3.80, 0.10, 0.25, 0.20, 3.25, 1.80, 1.45, 34.52),
(4, 9.00, 0.90, 8.10, 0.20, 0.40, 0.50, 7.00, 3.50, 3.50, 38.89),
(5, 8.50, 0.85, 7.65, 0.25, 0.50, 0.40, 6.50, 4.00, 2.50, 29.41);

-- 4. Initial Elasticity Benchmarks
INSERT INTO elasticity_metrics (product_id, segment_id, elasticity_coefficient, r_squared, confidence_level, interpretation, recommendation) VALUES
(1, 1, -1.850, 0.9120, 95.0, 'Elástica', 'Sensible al precio. Subir precios reducirá ingresos netos; optimizar descuentos promocionales.'),
(2, 2, -0.620, 0.8840, 95.0, 'Inelástica', 'Oportunidad de aumento de precio (+4% a +7%) sin pérdida significativa de demanda.'),
(3, 1, -1.350, 0.8650, 90.0, 'Elástica', 'Mantener precio competitivo y defender márgenes eliminando fugas de rebajas trimestrales.'),
(4, 4, -0.450, 0.9310, 99.0, 'Altamente Inelástica', 'Poder de fijación de precios alto (Value-Based Pricing). Margen expansible.'),
(5, 3, -2.100, 0.8990, 95.0, 'Muy Elástica', 'Commodity. Reducir costos base antes de cualquier intento de ajuste de precio.');

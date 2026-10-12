-- =============================================================================
-- UP PRICING INTELLIGENCE™ - Database Schema (PostgreSQL)
-- =============================================================================

-- Drop tables if needed
DROP TABLE IF EXISTS simulation_scenarios CASCADE;
DROP TABLE IF EXISTS pricing_waterfalls CASCADE;
DROP TABLE IF EXISTS elasticity_metrics CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customer_segments CASCADE;

-- 1. Customer Segments (e.g. Retail, B2B Enterprise, Wholesale, Premium)
CREATE TABLE customer_segments (
    id SERIAL PRIMARY KEY,
    segment_code VARCHAR(50) UNIQUE NOT NULL,
    segment_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_sensitivity_rating VARCHAR(20) DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Products / SKUs
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    base_cost NUMERIC(12, 2) NOT NULL,           -- Cost of Goods Sold (COGS)
    list_price NUMERIC(12, 2) NOT NULL,          -- Manufacturer Suggested Retail Price / List Price
    min_margin_percent NUMERIC(5, 2) DEFAULT 15.00, -- Hard guardrail: min profit margin %
    current_inventory INT DEFAULT 1000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Historical Retail Transactions
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) NOT NULL,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    segment_id INT NOT NULL REFERENCES customer_segments(id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    unit_list_price NUMERIC(12, 2) NOT NULL,
    unit_invoice_price NUMERIC(12, 2) NOT NULL,    -- Price on invoice after contractual discounts
    promotional_discount NUMERIC(12, 2) DEFAULT 0.00, -- Seasonal / promo discount
    rebate_amount NUMERIC(12, 2) DEFAULT 0.00,       -- End-of-quarter rebates
    unit_cogs NUMERIC(12, 2) NOT NULL,             -- Unit cost at transaction time
    pocket_price NUMERIC(12, 2) NOT NULL,          -- Real cash realized after all discounts/rebates
    pocket_margin NUMERIC(12, 2) NOT NULL,         -- pocket_price - unit_cogs
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Calculated Elasticity Metrics
CREATE TABLE elasticity_metrics (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    segment_id INT REFERENCES customer_segments(id) ON DELETE SET NULL,
    elasticity_coefficient NUMERIC(6, 3) NOT NULL, -- e.g. -1.45 (elastic), -0.75 (inelastic)
    r_squared NUMERIC(5, 4),                      -- Goodness of fit (0 to 1)
    confidence_level NUMERIC(5, 2) DEFAULT 95.0,
    interpretation VARCHAR(50) NOT NULL,          -- Inelastic, Unitary, Elastic
    recommendation TEXT,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Price Waterfall Breakdown (Per SKU)
CREATE TABLE pricing_waterfalls (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    list_price NUMERIC(12, 2) NOT NULL,
    standard_discount NUMERIC(12, 2) DEFAULT 0.00,
    invoice_price NUMERIC(12, 2) NOT NULL,
    cash_discount NUMERIC(12, 2) DEFAULT 0.00,
    promotional_allowance NUMERIC(12, 2) DEFAULT 0.00,
    annual_rebate NUMERIC(12, 2) DEFAULT 0.00,
    pocket_price NUMERIC(12, 2) NOT NULL,
    unit_cogs NUMERIC(12, 2) NOT NULL,
    pocket_margin NUMERIC(12, 2) NOT NULL,
    pocket_margin_percent NUMERIC(6, 2) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Scenario Simulation Logs (Audit & Agent Memory)
CREATE TABLE simulation_scenarios (
    id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(150) NOT NULL,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price_change_pct NUMERIC(6, 2) NOT NULL,       -- e.g. +5.0% or -3.0%
    projected_demand_change_pct NUMERIC(6, 2) NOT NULL,
    projected_volume INT NOT NULL,
    projected_revenue NUMERIC(14, 2) NOT NULL,
    projected_profit NUMERIC(14, 2) NOT NULL,
    margin_percent NUMERIC(6, 2) NOT NULL,
    guardrail_status VARCHAR(20) NOT NULL,         -- APPROVED, REJECTED, WARNING
    strategic_rationale TEXT,                      -- AI Agent decision argument
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices for performance
CREATE INDEX idx_transactions_product ON transactions(product_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_products_sku ON products(sku);

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Numeric, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    id = Column(Integer, primary_key=True, index=True)
    segment_code = Column(String(50), unique=True, nullable=False)
    segment_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price_sensitivity_rating = Column(String(20), default="MEDIUM")
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="segment")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    base_cost = Column(Numeric(12, 2), nullable=False)
    list_price = Column(Numeric(12, 2), nullable=False)
    min_margin_percent = Column(Numeric(5, 2), default=15.00)
    current_inventory = Column(Integer, default=1000)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="product")
    waterfall = relationship("PricingWaterfall", uselist=False, back_populates="product")
    elasticity_metrics = relationship("ElasticityMetric", back_populates="product")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    segment_id = Column(Integer, ForeignKey("customer_segments.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_list_price = Column(Numeric(12, 2), nullable=False)
    unit_invoice_price = Column(Numeric(12, 2), nullable=False)
    promotional_discount = Column(Numeric(12, 2), default=0.00)
    rebate_amount = Column(Numeric(12, 2), default=0.00)
    unit_cogs = Column(Numeric(12, 2), nullable=False)
    pocket_price = Column(Numeric(12, 2), nullable=False)
    pocket_margin = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="transactions")
    segment = relationship("CustomerSegment", back_populates="transactions")


class ElasticityMetric(Base):
    __tablename__ = "elasticity_metrics"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    segment_id = Column(Integer, ForeignKey("customer_segments.id", ondelete="SET NULL"), nullable=True)
    elasticity_coefficient = Column(Numeric(6, 3), nullable=False)
    r_squared = Column(Numeric(5, 4), nullable=True)
    confidence_level = Column(Numeric(5, 2), default=95.0)
    interpretation = Column(String(50), nullable=False)
    recommendation = Column(Text, nullable=True)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="elasticity_metrics")


class PricingWaterfall(Base):
    __tablename__ = "pricing_waterfalls"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, unique=True)
    list_price = Column(Numeric(12, 2), nullable=False)
    standard_discount = Column(Numeric(12, 2), default=0.00)
    invoice_price = Column(Numeric(12, 2), nullable=False)
    cash_discount = Column(Numeric(12, 2), default=0.00)
    promotional_allowance = Column(Numeric(12, 2), default=0.00)
    annual_rebate = Column(Numeric(12, 2), default=0.00)
    pocket_price = Column(Numeric(12, 2), nullable=False)
    unit_cogs = Column(Numeric(12, 2), nullable=False)
    pocket_margin = Column(Numeric(12, 2), nullable=False)
    pocket_margin_percent = Column(Numeric(6, 2), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="waterfall")


class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(150), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price_change_pct = Column(Numeric(6, 2), nullable=False)
    projected_demand_change_pct = Column(Numeric(6, 2), nullable=False)
    projected_volume = Column(Integer, nullable=False)
    projected_revenue = Column(Numeric(14, 2), nullable=False)
    projected_profit = Column(Numeric(14, 2), nullable=False)
    margin_percent = Column(Numeric(6, 2), nullable=False)
    guardrail_status = Column(String(20), nullable=False)
    strategic_rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

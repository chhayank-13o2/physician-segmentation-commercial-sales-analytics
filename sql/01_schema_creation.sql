-- ============================================================================
-- 01_schema_creation.sql
-- ============================================================================
-- Business Context:
-- This script creates the foundational star schema for the physician segmentation
-- and commercial sales analytics project. The schema consists of dimension
-- tables (Physician, Product, Territory, Sales Rep, Date) and a central fact
-- table (Prescriptions).
-- ============================================================================

-- Dimension: Physician
-- Stores demographic and professional information about physicians.
CREATE TABLE dim_physician (
    physician_id VARCHAR(10) PRIMARY KEY,
    npi VARCHAR(10) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    specialty VARCHAR(50),
    territory_id VARCHAR(10),
    city VARCHAR(50),
    state VARCHAR(2),
    years_in_practice INTEGER,
    medical_school VARCHAR(100)
);

-- Dimension: Product
-- Contains details about the pharmaceutical products being prescribed.
CREATE TABLE dim_product (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(50),
    generic_name VARCHAR(50),
    product_type VARCHAR(10), -- e.g., 'Brand' or 'Generic'
    therapeutic_area VARCHAR(50),
    launch_date DATE,
    average_price_per_rx DECIMAL(10,2)
);

-- Dimension: Territory
-- Represents the geographical sales territories.
CREATE TABLE dim_territory (
    territory_id VARCHAR(10) PRIMARY KEY,
    territory_name VARCHAR(50),
    region VARCHAR(20),
    district VARCHAR(50),
    state_coverage VARCHAR(100)
);

-- Dimension: Sales Rep
-- Information about the sales representatives assigned to territories.
CREATE TABLE dim_sales_rep (
    rep_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    territory_id VARCHAR(10) REFERENCES dim_territory(territory_id),
    hire_date DATE,
    experience_years INTEGER,
    email VARCHAR(100)
);

-- Dimension: Date
-- A standard date dimension table covering 2023-01-01 to 2024-12-31.
CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- Populate Date Dimension (PostgreSQL specific generate_series)
INSERT INTO dim_date
SELECT
    datum AS date_id,
    EXTRACT(YEAR FROM datum) AS year,
    EXTRACT(QUARTER FROM datum) AS quarter,
    EXTRACT(MONTH FROM datum) AS month,
    EXTRACT(DAY FROM datum) AS day_of_month,
    EXTRACT(ISODOW FROM datum) AS day_of_week,
    CASE WHEN EXTRACT(ISODOW FROM datum) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM
    generate_series('2023-01-01'::DATE, '2024-12-31'::DATE, '1 day'::interval) AS datum;


-- Fact: Prescriptions
-- Records individual prescription transactions (TRx) and new prescriptions (NRx).
CREATE TABLE fact_prescriptions (
    rx_id VARCHAR(20) PRIMARY KEY,
    physician_id VARCHAR(10) REFERENCES dim_physician(physician_id),
    product_id VARCHAR(10) REFERENCES dim_product(product_id),
    rx_date DATE REFERENCES dim_date(date_id),
    trx_quantity INTEGER,
    nrx_quantity INTEGER,
    rx_type VARCHAR(10), -- e.g., 'New', 'Refill'
    payer_type VARCHAR(20) -- e.g., 'Commercial', 'Medicare', 'Medicaid'
);

-- ============================================================================
-- Index Creation
-- ============================================================================
-- Indexes on foreign keys and frequently queried columns to improve read performance.

CREATE INDEX idx_fact_rx_physician ON fact_prescriptions(physician_id);
CREATE INDEX idx_fact_rx_product ON fact_prescriptions(product_id);
CREATE INDEX idx_fact_rx_date ON fact_prescriptions(rx_date);

CREATE INDEX idx_dim_physician_territory ON dim_physician(territory_id);
CREATE INDEX idx_dim_physician_specialty ON dim_physician(specialty);

CREATE INDEX idx_dim_sales_rep_territory ON dim_sales_rep(territory_id);

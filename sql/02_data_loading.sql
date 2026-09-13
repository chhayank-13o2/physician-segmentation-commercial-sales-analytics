-- ============================================================================
-- 02_data_loading.sql
-- ============================================================================
-- Business Context:
-- This script provides PostgreSQL COPY commands to bulk load data from CSV
-- files into the respective dimension and fact tables. It assumes the CSV files
-- are located in an accessible directory and formatted appropriately.
-- ============================================================================

-- Set variables and configurations for bulk loading
-- Increase maintenance_work_mem to speed up index updates during bulk load
-- (Run this outside a transaction block if possible, or adapt for session)
SET maintenance_work_mem = '1GB';
-- Ensure date format matches CSV, assuming YYYY-MM-DD
SET DateStyle TO 'ISO, MDY';

-- TRUNCATE existing data if running a full reload (optional, comment out if incremental)
-- CASCADE will also truncate dependent tables
-- TRUNCATE TABLE dim_physician CASCADE;
-- TRUNCATE TABLE dim_product CASCADE;
-- TRUNCATE TABLE dim_territory CASCADE;
-- TRUNCATE TABLE dim_sales_rep CASCADE;
-- TRUNCATE TABLE fact_prescriptions CASCADE;

-- Load dim_territory
-- Load this first as other tables reference it
/*
COPY dim_territory (territory_id, territory_name, region, district, state_coverage)
FROM '/path/to/data/territory.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '');
*/

-- Load dim_product
/*
COPY dim_product (product_id, product_name, generic_name, product_type, therapeutic_area, launch_date, average_price_per_rx)
FROM '/path/to/data/product.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '');
*/

-- Load dim_physician
-- Depends on dim_territory (optional but logical dependency)
/*
COPY dim_physician (physician_id, npi, first_name, last_name, specialty, territory_id, city, state, years_in_practice, medical_school)
FROM '/path/to/data/physician.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '');
*/

-- Load dim_sales_rep
-- Depends on dim_territory
/*
COPY dim_sales_rep (rep_id, first_name, last_name, territory_id, hire_date, experience_years, email)
FROM '/path/to/data/sales_rep.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '');
*/

-- Load fact_prescriptions
-- Huge table, load last. Depends on all dimensions.
/*
COPY fact_prescriptions (rx_id, physician_id, product_id, rx_date, trx_quantity, nrx_quantity, rx_type, payer_type)
FROM '/path/to/data/prescriptions.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '');
*/

-- Reset maintenance_work_mem after loading
SET maintenance_work_mem TO DEFAULT;

-- Analyze tables to update statistics for the query planner
-- ANALYZE dim_territory;
-- ANALYZE dim_product;
-- ANALYZE dim_physician;
-- ANALYZE dim_sales_rep;
-- ANALYZE fact_prescriptions;

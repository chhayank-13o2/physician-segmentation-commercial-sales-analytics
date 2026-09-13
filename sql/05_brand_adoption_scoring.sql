-- ============================================================================
-- 05_brand_adoption_scoring.sql
-- ============================================================================
-- Business Context:
-- Analyzes brand preference and adoption behavior among physicians.
-- - Brand vs generic split by specialty
-- - Brand adoption rate by territory
-- - Monthly brand adoption trend
-- - High-value brand adopters
-- - Brand adoption cohort analysis
-- ============================================================================

-- 1. Brand vs generic split by specialty (2024)
CREATE OR REPLACE VIEW vw_specialty_brand_split AS
SELECT
    dp.specialty,
    SUM(CASE WHEN dprod.product_type = 'Brand' THEN fp.trx_quantity ELSE 0 END) AS brand_trx,
    SUM(CASE WHEN dprod.product_type = 'Generic' THEN fp.trx_quantity ELSE 0 END) AS generic_trx,
    SUM(fp.trx_quantity) AS total_trx,
    SUM(CASE WHEN dprod.product_type = 'Brand' THEN fp.trx_quantity ELSE 0 END)::DECIMAL / NULLIF(SUM(fp.trx_quantity), 0) AS brand_share
FROM fact_prescriptions fp
JOIN dim_physician dp ON fp.physician_id = dp.physician_id
JOIN dim_product dprod ON fp.product_id = dprod.product_id
WHERE EXTRACT(YEAR FROM fp.rx_date) = 2024
GROUP BY dp.specialty;

-- 2. Brand adoption rate by territory (2024)
CREATE OR REPLACE VIEW vw_territory_brand_adoption AS
SELECT
    dt.territory_name,
    SUM(CASE WHEN dprod.product_type = 'Brand' THEN fp.trx_quantity ELSE 0 END) AS brand_trx,
    SUM(fp.trx_quantity) AS total_trx,
    SUM(CASE WHEN dprod.product_type = 'Brand' THEN fp.trx_quantity ELSE 0 END)::DECIMAL / NULLIF(SUM(fp.trx_quantity), 0) AS brand_adoption_rate
FROM fact_prescriptions fp
JOIN dim_physician dp ON fp.physician_id = dp.physician_id
JOIN dim_territory dt ON dp.territory_id = dt.territory_id
JOIN dim_product dprod ON fp.product_id = dprod.product_id
WHERE EXTRACT(YEAR FROM fp.rx_date) = 2024
GROUP BY dt.territory_name;


-- 3. Monthly brand adoption trend (Global)
CREATE OR REPLACE VIEW vw_monthly_brand_trend AS
SELECT
    DATE_TRUNC('month', fp.rx_date) AS month_start,
    SUM(CASE WHEN dprod.product_type = 'Brand' THEN fp.trx_quantity ELSE 0 END) AS brand_trx,
    SUM(fp.trx_quantity) AS total_trx,
    SUM(CASE WHEN dprod.product_type = 'Brand' THEN fp.trx_quantity ELSE 0 END)::DECIMAL / NULLIF(SUM(fp.trx_quantity), 0) AS brand_share
FROM fact_prescriptions fp
JOIN dim_product dprod ON fp.product_id = dprod.product_id
GROUP BY DATE_TRUNC('month', fp.rx_date)
ORDER BY month_start;


-- 4. High-value brand adopters (>50% brand share AND high volume / Decile 7+)
CREATE OR REPLACE VIEW vw_high_value_brand_adopters AS
SELECT
    vd.physician_id,
    dp.first_name,
    dp.last_name,
    dp.specialty,
    vd.metric_value AS volume_2024,
    bad.metric_value AS brand_share_2024
FROM vw_volume_decile vd
JOIN vw_brand_adoption_decile bad ON vd.physician_id = bad.physician_id
JOIN dim_physician dp ON vd.physician_id = dp.physician_id
WHERE vd.decile >= 7        -- High volume constraint
  AND bad.metric_value > 0.50; -- >50% Brand share


-- 5. Brand adoption cohort analysis (by first time they prescribed brand)
CREATE OR REPLACE VIEW vw_brand_adoption_cohort AS
WITH first_brand_rx AS (
    SELECT
        fp.physician_id,
        MIN(DATE_TRUNC('month', fp.rx_date)) AS cohort_month
    FROM fact_prescriptions fp
    JOIN dim_product dprod ON fp.product_id = dprod.product_id
    WHERE dprod.product_type = 'Brand'
    GROUP BY fp.physician_id
)
SELECT
    cohort_month,
    COUNT(DISTINCT physician_id) AS new_brand_prescribers
FROM first_brand_rx
GROUP BY cohort_month
ORDER BY cohort_month;

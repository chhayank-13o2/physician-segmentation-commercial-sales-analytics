-- ============================================================================
-- 04_market_growth_analysis.sql
-- ============================================================================
-- Business Context:
-- Contains views and queries for analyzing market dynamics:
-- - Territory-level YoY growth
-- - Specialty market trends
-- - Product-level QoQ growth
-- - Market share by product
-- - Rolling 3-month avg TRx by territory
-- ============================================================================

-- 1. Territory-level YoY growth rates
CREATE OR REPLACE VIEW vw_territory_yoy_growth AS
WITH territory_yearly AS (
    SELECT
        dp.territory_id,
        dt.territory_name,
        SUM(CASE WHEN EXTRACT(YEAR FROM fp.rx_date) = 2023 THEN fp.trx_quantity ELSE 0 END) AS vol_2023,
        SUM(CASE WHEN EXTRACT(YEAR FROM fp.rx_date) = 2024 THEN fp.trx_quantity ELSE 0 END) AS vol_2024
    FROM fact_prescriptions fp
    JOIN dim_physician dp ON fp.physician_id = dp.physician_id
    JOIN dim_territory dt ON dp.territory_id = dt.territory_id
    GROUP BY dp.territory_id, dt.territory_name
)
SELECT
    territory_id,
    territory_name,
    vol_2023,
    vol_2024,
    CASE
        WHEN vol_2023 = 0 THEN NULL
        ELSE ((vol_2024 - vol_2023)::DECIMAL / vol_2023)
    END AS yoy_growth_rate
FROM territory_yearly;

-- 2. Specialty-level market trends
CREATE OR REPLACE VIEW vw_specialty_market_trends AS
SELECT
    dp.specialty,
    EXTRACT(YEAR FROM fp.rx_date) AS rx_year,
    EXTRACT(MONTH FROM fp.rx_date) AS rx_month,
    SUM(fp.trx_quantity) AS total_trx
FROM fact_prescriptions fp
JOIN dim_physician dp ON fp.physician_id = dp.physician_id
GROUP BY dp.specialty, EXTRACT(YEAR FROM fp.rx_date), EXTRACT(MONTH FROM fp.rx_date)
ORDER BY rx_year DESC, rx_month DESC, total_trx DESC;

-- 3. Product-level quarter-over-quarter growth
CREATE OR REPLACE VIEW vw_product_qoq_growth AS
WITH product_quarterly AS (
    SELECT
        dp.product_name,
        d.year,
        d.quarter,
        SUM(fp.trx_quantity) AS quarter_trx
    FROM fact_prescriptions fp
    JOIN dim_product dp ON fp.product_id = dp.product_id
    JOIN dim_date d ON fp.rx_date = d.date_id
    GROUP BY dp.product_name, d.year, d.quarter
),
lagged_quarterly AS (
    SELECT
        product_name,
        year,
        quarter,
        quarter_trx,
        LAG(quarter_trx) OVER (PARTITION BY product_name ORDER BY year, quarter) AS prev_quarter_trx
    FROM product_quarterly
)
SELECT
    product_name,
    year,
    quarter,
    quarter_trx,
    prev_quarter_trx,
    CASE
        WHEN prev_quarter_trx = 0 THEN NULL
        ELSE ((quarter_trx - prev_quarter_trx)::DECIMAL / prev_quarter_trx)
    END AS qoq_growth_rate
FROM lagged_quarterly;

-- 4. Market share by product (TRx share) in 2024
CREATE OR REPLACE VIEW vw_product_market_share AS
WITH total_market AS (
    SELECT SUM(trx_quantity) AS overall_total_trx
    FROM fact_prescriptions
    WHERE EXTRACT(YEAR FROM rx_date) = 2024
),
product_market AS (
    SELECT
        dp.product_name,
        SUM(fp.trx_quantity) AS product_trx
    FROM fact_prescriptions fp
    JOIN dim_product dp ON fp.product_id = dp.product_id
    WHERE EXTRACT(YEAR FROM fp.rx_date) = 2024
    GROUP BY dp.product_name
)
SELECT
    pm.product_name,
    pm.product_trx,
    tm.overall_total_trx,
    (pm.product_trx::DECIMAL / tm.overall_total_trx) AS market_share_pct
FROM product_market pm
CROSS JOIN total_market tm;


-- 5. Rolling 3-month average TRx by territory
CREATE OR REPLACE VIEW vw_territory_rolling_3m_avg AS
WITH monthly_territory_vol AS (
    SELECT
        dp.territory_id,
        DATE_TRUNC('month', fp.rx_date) AS rx_month,
        SUM(fp.trx_quantity) AS monthly_trx
    FROM fact_prescriptions fp
    JOIN dim_physician dp ON fp.physician_id = dp.physician_id
    GROUP BY dp.territory_id, DATE_TRUNC('month', fp.rx_date)
)
SELECT
    territory_id,
    rx_month,
    monthly_trx,
    AVG(monthly_trx) OVER (
        PARTITION BY territory_id
        ORDER BY rx_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_3m_avg_trx
FROM monthly_territory_vol;

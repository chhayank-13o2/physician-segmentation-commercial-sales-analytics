-- ============================================================================
-- 03_decile_segmentation.sql
-- ============================================================================
-- Business Context:
-- Creates 3 decile views for scoring physicians.
-- 1. Volume Decile: Trailing 12-month (2024) TRx volume.
-- 2. Growth Decile: Year-over-Year (2024 vs 2023) TRx growth rate.
-- 3. Brand Adoption Decile: Share of Brand TRx / Total TRx in 2024.
-- Decile 10 = Highest performance/metric, Decile 1 = Lowest.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Volume Decile (vw_volume_decile)
-- Rank physicians by trailing 12-month total TRx (2024 data)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_volume_decile AS
WITH phy_volume_2024 AS (
    SELECT
        physician_id,
        SUM(trx_quantity) AS total_trx_2024
    FROM fact_prescriptions
    WHERE EXTRACT(YEAR FROM rx_date) = 2024
    GROUP BY physician_id
)
SELECT
    physician_id,
    COALESCE(total_trx_2024, 0) AS metric_value,
    NTILE(10) OVER (ORDER BY COALESCE(total_trx_2024, 0) ASC) AS decile
FROM phy_volume_2024;


-- ----------------------------------------------------------------------------
-- 2. Growth Decile (vw_growth_decile)
-- Rank by YoY TRx growth rate (2024 vs 2023)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_growth_decile AS
WITH yearly_trx AS (
    SELECT
        physician_id,
        SUM(CASE WHEN EXTRACT(YEAR FROM rx_date) = 2023 THEN trx_quantity ELSE 0 END) AS trx_2023,
        SUM(CASE WHEN EXTRACT(YEAR FROM rx_date) = 2024 THEN trx_quantity ELSE 0 END) AS trx_2024
    FROM fact_prescriptions
    WHERE EXTRACT(YEAR FROM rx_date) IN (2023, 2024)
    GROUP BY physician_id
),
growth_calc AS (
    SELECT
        physician_id,
        trx_2023,
        trx_2024,
        -- Handle division by zero and new prescribers
        CASE
            WHEN trx_2023 = 0 AND trx_2024 > 0 THEN 999.99 -- Maximum growth proxy
            WHEN trx_2023 = 0 AND trx_2024 = 0 THEN 0
            ELSE ((trx_2024 - trx_2023)::DECIMAL / trx_2023)
        END AS yoy_growth_rate
    FROM yearly_trx
)
SELECT
    physician_id,
    yoy_growth_rate AS metric_value,
    NTILE(10) OVER (ORDER BY yoy_growth_rate ASC) AS decile
FROM growth_calc;


-- ----------------------------------------------------------------------------
-- 3. Brand Adoption Decile (vw_brand_adoption_decile)
-- Rank by brand share (brand TRx / total TRx) in 2024
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_brand_adoption_decile AS
WITH phy_brand_mix AS (
    SELECT
        fp.physician_id,
        SUM(fp.trx_quantity) AS total_trx_2024,
        SUM(CASE WHEN dp.product_type = 'Brand' THEN fp.trx_quantity ELSE 0 END) AS brand_trx_2024
    FROM fact_prescriptions fp
    JOIN dim_product dp ON fp.product_id = dp.product_id
    WHERE EXTRACT(YEAR FROM fp.rx_date) = 2024
    GROUP BY fp.physician_id
),
brand_share_calc AS (
    SELECT
        physician_id,
        total_trx_2024,
        brand_trx_2024,
        CASE
            WHEN total_trx_2024 = 0 THEN 0
            ELSE (brand_trx_2024::DECIMAL / total_trx_2024)
        END AS brand_share
    FROM phy_brand_mix
)
SELECT
    physician_id,
    brand_share AS metric_value,
    NTILE(10) OVER (ORDER BY brand_share ASC) AS decile
FROM brand_share_calc;

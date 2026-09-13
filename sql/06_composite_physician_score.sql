-- ============================================================================
-- 06_composite_physician_score.sql
-- ============================================================================
-- Business Context:
-- Calculates a combined physician score based on weighting the 3 deciles:
-- Composite = (0.40 * Volume) + (0.30 * Growth) + (0.30 * Brand Adoption)
-- Then segments physicians into tiers:
-- Platinum (Top 10%), Gold (10-25%), Silver (25-50%), Bronze (Bottom 50%)
-- ============================================================================

CREATE OR REPLACE VIEW vw_physician_composite_score AS
WITH combined_deciles AS (
    SELECT
        p.physician_id,
        p.first_name,
        p.last_name,
        p.specialty,
        p.territory_id,
        COALESCE(vd.decile, 1) AS volume_decile,
        COALESCE(gd.decile, 1) AS growth_decile,
        COALESCE(bd.decile, 1) AS brand_decile
    FROM dim_physician p
    LEFT JOIN vw_volume_decile vd ON p.physician_id = vd.physician_id
    LEFT JOIN vw_growth_decile gd ON p.physician_id = gd.physician_id
    LEFT JOIN vw_brand_adoption_decile bd ON p.physician_id = bd.physician_id
),
scored_physicians AS (
    SELECT
        *,
        (0.40 * volume_decile) + (0.30 * growth_decile) + (0.30 * brand_decile) AS composite_score
    FROM combined_deciles
),
ranked_physicians AS (
    SELECT
        *,
        PERCENT_RANK() OVER (ORDER BY composite_score DESC) AS pct_rank
    FROM scored_physicians
)
SELECT
    physician_id,
    first_name || ' ' || last_name AS physician_name,
    specialty,
    territory_id,
    volume_decile,
    growth_decile,
    brand_decile,
    ROUND(composite_score::NUMERIC, 2) AS composite_score,
    CASE
        WHEN pct_rank <= 0.10 THEN 'Platinum'
        WHEN pct_rank <= 0.25 THEN 'Gold'
        WHEN pct_rank <= 0.50 THEN 'Silver'
        ELSE 'Bronze'
    END AS tier
FROM ranked_physicians;

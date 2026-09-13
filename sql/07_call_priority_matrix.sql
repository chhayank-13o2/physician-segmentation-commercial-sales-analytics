-- ============================================================================
-- 07_call_priority_matrix.sql
-- ============================================================================
-- Business Context:
-- Constructs a 2x2 Call Priority Matrix for sales reps to optimize reach:
-- Volume Axis: High (Decile >= 7), Low (Decile < 7)
-- Opportunity Axis: Avg(Growth Decile, Brand Decile) -> High (>= 6), Low (< 6)
--
-- Matrix Assignments:
-- Priority A - Protect (High Vol, High Opp) -> Weekly call
-- Priority B - Grow    (Low Vol,  High Opp) -> Bi-weekly call
-- Priority C - Retain  (High Vol, Low Opp)  -> Monthly call
-- Priority D - Monitor (Low Vol,  Low Opp)  -> Quarterly call
-- ============================================================================

-- 1. Assign Priority Bucket (vw_call_priority_matrix)
CREATE OR REPLACE VIEW vw_call_priority_matrix AS
WITH matrix_calc AS (
    SELECT
        pcs.physician_id,
        pcs.physician_name,
        pcs.specialty,
        pcs.territory_id,
        pcs.composite_score,
        pcs.tier,
        pcs.volume_decile,
        ((pcs.growth_decile + pcs.brand_decile) / 2.0) AS opportunity_score
    FROM vw_physician_composite_score pcs
)
SELECT
    physician_id,
    physician_name,
    specialty,
    territory_id,
    volume_decile,
    opportunity_score,
    composite_score,
    tier,
    CASE
        WHEN volume_decile >= 7 AND opportunity_score >= 6 THEN 'Priority A - Protect'
        WHEN volume_decile < 7  AND opportunity_score >= 6 THEN 'Priority B - Grow'
        WHEN volume_decile >= 7 AND opportunity_score < 6  THEN 'Priority C - Retain'
        ELSE 'Priority D - Monitor'
    END AS priority_bucket,
    CASE
        WHEN volume_decile >= 7 AND opportunity_score >= 6 THEN 'Weekly'
        WHEN volume_decile < 7  AND opportunity_score >= 6 THEN 'Bi-weekly'
        WHEN volume_decile >= 7 AND opportunity_score < 6  THEN 'Monthly'
        ELSE 'Quarterly'
    END AS recommended_call_frequency
FROM matrix_calc;

-- 2. Summary: Count and Avg Composite Score per Priority Bucket per Territory
-- (Can be executed as a query rather than a view if desired, shown here as a view for persistence)
CREATE OR REPLACE VIEW vw_priority_summary_by_territory AS
SELECT
    territory_id,
    priority_bucket,
    COUNT(*) AS physician_count,
    ROUND(AVG(composite_score), 2) AS avg_composite_score
FROM vw_call_priority_matrix
GROUP BY territory_id, priority_bucket
ORDER BY territory_id, priority_bucket;


-- 3. Top 50 physicians to call this week (Priority A, ordered by composite score)
-- This is a sample query that reps can run
CREATE OR REPLACE VIEW vw_top_50_call_list AS
SELECT
    physician_id,
    physician_name,
    specialty,
    territory_id,
    priority_bucket,
    composite_score,
    recommended_call_frequency
FROM vw_call_priority_matrix
WHERE priority_bucket = 'Priority A - Protect'
ORDER BY composite_score DESC
LIMIT 50;

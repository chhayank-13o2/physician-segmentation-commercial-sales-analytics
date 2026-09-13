# Methodology

## Segmentation Approach

### Why Decile-Based Segmentation is the Pharma Industry Standard
In pharmaceutical sales and marketing, resources (sales representative time, marketing budgets) are constrained, while the target audience (physicians) is large. Decile-based segmentation is the industry standard because it provides a clear, actionable, and relative ranking of physicians based on their prescribing value. Unlike absolute thresholds, deciles ensure that the top tier always represents the top 10% of the universe, automatically adjusting for market size and general prescribing trends.

### Comparison with Other Methods (k-means, RFM)
- **k-means Clustering**: While mathematically sophisticated, k-means can create segments that are difficult to explain to sales reps. Deciles are intuitive (10 is better than 1) and easy to operationalize.
- **RFM (Recency, Frequency, Monetary)**: More suited for retail or e-commerce. In pharma, a physician's overall volume and brand loyalty are more predictive of future value than the recency of their last script.

### Three-Axis Model: Volume, Growth, Brand Adoption
Our segmentation utilizes a three-dimensional approach to capture a holistic view of a physician's value:
1. **Volume**: The total size of the physician's practice in the therapeutic area.
2. **Growth**: The trajectory of their prescribing (are they expanding their practice or slowing down?).
3. **Brand Adoption**: Their propensity to prescribe our specific brand over generics or competitors.

## Decile Scoring Methodology

### Volume Decile
- **Metric**: Trailing 12-month Total Prescriptions (TRx) within the therapeutic class.
- **Methodology**: Physicians are ranked by TRx volume. The universe is divided into 10 equal groups using the `NTILE(10)` window function. Decile 10 represents the top 10% of prescribers.

### Growth Decile
- **Metric**: Year-over-Year (YoY) TRx growth rate (Current 12 months vs. Previous 12 months).
- **Methodology**: YoY growth % is calculated. Physicians are ranked by this percentage and divided into deciles. 
- **Handling Edge Cases**: Physicians with no previous year data (new prescribers) are excluded from the growth calculation and assigned a default median score to prevent skewing.

### Brand Adoption Decile
- **Metric**: Brand Share Percentage (Brand TRx / Total TRx in class).
- **Methodology**: Physicians are ranked by their brand share and divided into deciles using `NTILE(10)`.

## Composite Scoring

To arrive at a single metric for tiering, a composite score is calculated using a weighted average of the three deciles.

### Weight Rationale
- **Volume (40%)**: The most critical factor; a small share of a large prescriber is often worth more than a large share of a small prescriber.
- **Growth (30%)**: Important for identifying future high-value targets.
- **Brand Adoption (30%)**: Reflects the physician's receptivity to our specific messaging and product.

*Formula*: `(Volume_Decile * 0.40) + (Growth_Decile * 0.30) + (Brand_Decile * 0.30)`

### Tier Definitions
Based on the composite score ranking, physicians are assigned to tiers:
- **Platinum**: Top 10% (Highest priority, key opinion leaders, massive volume).
- **Gold**: 10-25% (High value, significant growth potential).
- **Silver**: 25-50% (Moderate value, maintenance targets).
- **Bronze**: 50-100% (Low value, opportunistic or non-personal promotion only).

## Call Priority Matrix

### 2×2 Matrix Design Rationale
The Call Priority Matrix maps Volume (Y-axis, High/Low) against Brand Adoption/Growth (X-axis, High/Low) to create actionable call plans for sales representatives.

| | High Brand/Growth | Low Brand/Growth |
|---|---|---|
| **High Volume** | **Priority A** (Defend & Grow) | **Priority B** (Convert & Expand) |
| **Low Volume** | **Priority C** (Maintain) | **Priority D** (Monitor / Do Not Call) |

### Call Frequency Allocation
- **Priority A**: Weekly calls. These are the most valuable customers and require constant engagement to defend market share.
- **Priority B**: Bi-weekly calls. High potential for conversion; significant effort should be spent educating these physicians.
- **Priority C**: Monthly calls. Maintenance level; ensure they have necessary samples and materials.
- **Priority D**: Quarterly or no calls. Rely on non-personal promotion (email, direct mail) for efficiency.

### Expected ROI Impact
By shifting representative effort away from Priority D physicians toward Priority A and B, the sales force maximizes the return on time invested, expecting a higher conversion rate and revenue lift per call.

## Limitations & Assumptions

- **Synthetic Data Caveats**: This analysis uses generated data; actual market dynamics may present more skewed distributions (e.g., the 80/20 rule is often more extreme in real pharma data).
- **Seasonal Adjustment Considerations**: The current model uses trailing 12-month data, which smooths out seasonality. For shorter-term metrics, seasonal adjustments would be required.
- **Data Freshness Requirements**: In a production environment, prescription data (often sourced from IQVIA or Symphony Health) has a lag of 1-4 weeks. The model assumes data is updated monthly.

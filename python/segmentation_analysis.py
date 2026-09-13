"""
Physician Segmentation Analysis
================================
Calculates per-physician metrics (volume, YoY growth, brand adoption),
assigns decile scores, composite rankings, and tier classifications.

Reads from: ../data/raw/physicians.csv, prescriptions.csv, products.csv
Outputs to:  ../data/raw/physician_segments.csv
"""
import os
import pandas as pd
import numpy as np


def analyze_segmentation() -> None:
    """
    Performs decile-based segmentation analysis on physician prescription data.
    
    Three-axis scoring:
      - Volume Decile: Trailing 12-month total TRx (2024)
      - Growth Decile: YoY TRx growth rate (2024 vs 2023)
      - Brand Adoption Decile: Brand TRx share percentage
    
    Composite Score = 0.40 * Volume + 0.30 * Growth + 0.30 * Brand Adoption
    """
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'raw')

    # --- Load Data ---
    print("Loading data...")
    physicians = pd.read_csv(os.path.join(data_dir, 'physicians.csv'))
    prescriptions = pd.read_csv(os.path.join(data_dir, 'prescriptions.csv'))
    products = pd.read_csv(os.path.join(data_dir, 'products.csv'))

    # Parse dates and join product info
    prescriptions['rx_date'] = pd.to_datetime(prescriptions['rx_date'])
    prescriptions = prescriptions.merge(
        products[['product_id', 'product_type']], on='product_id', how='left'
    )

    # --- Split by Year ---
    rx_2024 = prescriptions[prescriptions['rx_date'].dt.year == 2024]
    rx_2023 = prescriptions[prescriptions['rx_date'].dt.year == 2023]

    # --- Volume: Total TRx in 2024 ---
    trx_2024 = (
        rx_2024.groupby('physician_id')['trx_quantity']
        .sum()
        .reset_index(name='total_trx_2024')
    )
    trx_2023 = (
        rx_2023.groupby('physician_id')['trx_quantity']
        .sum()
        .reset_index(name='total_trx_2023')
    )

    # --- Growth: YoY TRx Growth Rate ---
    growth_df = pd.merge(trx_2024, trx_2023, on='physician_id', how='left').fillna(0)
    growth_df['yoy_growth_pct'] = np.where(
        growth_df['total_trx_2023'] > 0,
        (growth_df['total_trx_2024'] - growth_df['total_trx_2023'])
        / growth_df['total_trx_2023'] * 100,
        0
    )

    # --- Brand Adoption: Brand TRx / Total TRx in 2024 ---
    brand_rx = (
        rx_2024[rx_2024['product_type'] == 'Brand']
        .groupby('physician_id')['trx_quantity']
        .sum()
        .reset_index(name='brand_trx')
    )
    brand_df = pd.merge(trx_2024, brand_rx, on='physician_id', how='left').fillna(0)
    brand_df['brand_share_pct'] = np.where(
        brand_df['total_trx_2024'] > 0,
        brand_df['brand_trx'] / brand_df['total_trx_2024'] * 100,
        0
    )

    # --- Merge All Metrics onto Physicians ---
    df = physicians.copy()
    df = df.merge(
        growth_df[['physician_id', 'total_trx_2024', 'total_trx_2023', 'yoy_growth_pct']],
        on='physician_id', how='left'
    ).fillna(0)
    df = df.merge(
        brand_df[['physician_id', 'brand_trx', 'brand_share_pct']],
        on='physician_id', how='left'
    ).fillna(0)

    # --- Assign Deciles (1 = lowest, 10 = highest) ---
    print("Assigning decile scores...")
    df['volume_decile'] = pd.qcut(
        df['total_trx_2024'].rank(method='first'), 10, labels=False
    ) + 1
    df['growth_decile'] = pd.qcut(
        df['yoy_growth_pct'].rank(method='first'), 10, labels=False
    ) + 1
    df['brand_decile'] = pd.qcut(
        df['brand_share_pct'].rank(method='first'), 10, labels=False
    ) + 1

    # --- Composite Score ---
    df['composite_score'] = (
        0.40 * df['volume_decile']
        + 0.30 * df['growth_decile']
        + 0.30 * df['brand_decile']
    )

    # --- Tier Assignment ---
    def assign_tier(score: float) -> str:
        percentile = df['composite_score'].rank(pct=True)
        return ''  # placeholder

    # Use percentile-based tiers
    df['score_pctile'] = df['composite_score'].rank(pct=True)
    conditions = [
        df['score_pctile'] >= 0.90,
        df['score_pctile'] >= 0.75,
        df['score_pctile'] >= 0.50,
    ]
    choices = ['Platinum', 'Gold', 'Silver']
    df['tier'] = np.select(conditions, choices, default='Bronze')
    df.drop(columns=['score_pctile'], inplace=True)

    # --- Save Output ---
    out_path = os.path.join(data_dir, 'physician_segments.csv')
    df.to_csv(out_path, index=False)
    print(f"\nSegmentation saved to: {out_path}")
    print(f"Total physicians segmented: {len(df)}")

    # --- Summary Statistics ---
    print("\n" + "=" * 60)
    print("SEGMENTATION SUMMARY")
    print("=" * 60)

    print("\n--- Volume Decile Distribution ---")
    print(df['volume_decile'].value_counts().sort_index().to_string())

    print("\n--- Tier Distribution ---")
    tier_summary = df.groupby('tier').agg(
        count=('physician_id', 'count'),
        avg_trx=('total_trx_2024', 'mean'),
        avg_composite=('composite_score', 'mean')
    ).round(1)
    print(tier_summary.to_string())

    print("\n--- Top 10 Physicians by Composite Score ---")
    top10 = df.nlargest(10, 'composite_score')[
        ['physician_id', 'first_name', 'last_name', 'specialty',
         'volume_decile', 'growth_decile', 'brand_decile',
         'composite_score', 'tier']
    ]
    print(top10.to_string(index=False))


if __name__ == '__main__':
    analyze_segmentation()

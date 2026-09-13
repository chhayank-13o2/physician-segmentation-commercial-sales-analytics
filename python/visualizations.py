"""
Publication-Quality Visualizations for GitHub README
=====================================================
Generates 6 professional charts from the segmentation and territory data.

Outputs saved to: python/outputs/
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def get_paths():
    """Returns standard data and output directory paths."""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'raw')
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
    os.makedirs(out_dir, exist_ok=True)
    return data_dir, out_dir


def chart_decile_distribution(df: pd.DataFrame, out_dir: str) -> None:
    """Bar chart: physician count per volume decile."""
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    counts = df['volume_decile'].value_counts().sort_index()
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, 10))
    ax.bar(counts.index, counts.values, color=colors, edgecolor='white', linewidth=0.5)
    for i, v in enumerate(counts.values):
        ax.text(counts.index[i], v + 5, str(v), ha='center', fontweight='bold', fontsize=11)
    ax.set_title('Physician Distribution by Volume Decile', fontsize=18, fontweight='bold', pad=15)
    ax.set_xlabel('Volume Decile (1=Lowest, 10=Highest)', fontsize=13)
    ax.set_ylabel('Number of Physicians', fontsize=13)
    ax.set_xticks(range(1, 11))
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'decile_distribution.png'))
    plt.close()
    print("  [OK] decile_distribution.png")


def chart_priority_matrix(df: pd.DataFrame, out_dir: str) -> None:
    """Scatter plot: 2x2 call priority matrix quadrant chart."""
    df = df.copy()
    df['opportunity_score'] = (df['growth_decile'] + df['brand_decile']) / 2

    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)

    colors = {'A': '#e74c3c', 'B': '#f39c12', 'C': '#3498db', 'D': '#bdc3c7'}
    labels = {'A': 'A – Protect (Weekly)', 'B': 'B – Grow (Bi-weekly)',
              'C': 'C – Retain (Monthly)', 'D': 'D – Monitor (Quarterly)'}

    for bucket_key in ['D', 'C', 'B', 'A']:
        mask = df['priority_bucket'].str.startswith(bucket_key)
        ax.scatter(
            df.loc[mask, 'volume_decile'] + np.random.normal(0, 0.12, mask.sum()),
            df.loc[mask, 'opportunity_score'] + np.random.normal(0, 0.12, mask.sum()),
            c=colors[bucket_key], label=labels[bucket_key], alpha=0.6, s=30, edgecolor='white', linewidth=0.3
        )

    ax.axvline(x=6.5, color='#2c3e50', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.axhline(y=5.5, color='#2c3e50', linestyle='--', linewidth=1.5, alpha=0.7)

    ax.text(8.5, 9.5, 'A: PROTECT', fontsize=14, fontweight='bold', color='#e74c3c', alpha=0.6, ha='center')
    ax.text(3.5, 9.5, 'B: GROW', fontsize=14, fontweight='bold', color='#f39c12', alpha=0.6, ha='center')
    ax.text(8.5, 1.5, 'C: RETAIN', fontsize=14, fontweight='bold', color='#3498db', alpha=0.6, ha='center')
    ax.text(3.5, 1.5, 'D: MONITOR', fontsize=14, fontweight='bold', color='#bdc3c7', alpha=0.6, ha='center')

    ax.set_title('Physician Call Priority Matrix', fontsize=18, fontweight='bold', pad=15)
    ax.set_xlabel('Volume Decile →', fontsize=13)
    ax.set_ylabel('Opportunity Score →', fontsize=13)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 11)
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'priority_matrix_quadrant.png'))
    plt.close()
    print("  [OK] priority_matrix_quadrant.png")


def chart_territory_comparison(out_dir: str, data_dir: str) -> None:
    """Horizontal bar chart: top 15 territories by TRx."""
    terr_path = os.path.join(data_dir, 'territory_performance.csv')
    if not os.path.exists(terr_path):
        print("  ⚠ territory_performance.csv not found, skipping")
        return

    tdf = pd.read_csv(terr_path).head(15)

    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    if 'region' in tdf.columns:
        region_colors = {'Northeast': '#e74c3c', 'Southeast': '#3498db',
                         'Midwest': '#2ecc71', 'West': '#f39c12'}
        bar_colors = tdf['region'].map(region_colors).fillna('#95a5a6')
    else:
        bar_colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(tdf)))

    display_labels = tdf['territory_name'] if 'territory_name' in tdf.columns else tdf['territory_id']
    y_pos = range(len(tdf) - 1, -1, -1)

    ax.barh(y_pos, tdf['total_trx'].values, color=bar_colors, edgecolor='white', height=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(display_labels)

    for i, v in enumerate(tdf['total_trx'].values):
        ax.text(v + 50, y_pos[i], f'{v:,.0f}', va='center', fontsize=9)

    ax.set_title('Top 15 Territories by Total TRx (2024)', fontsize=18, fontweight='bold', pad=15)
    ax.set_xlabel('Total Prescriptions (TRx)', fontsize=13)

    if 'region' in tdf.columns:
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=c, label=r) for r, c in
                           {'Northeast': '#e74c3c', 'Southeast': '#3498db',
                            'Midwest': '#2ecc71', 'West': '#f39c12'}.items()]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'territory_comparison.png'))
    plt.close()
    print("  [OK] territory_comparison.png")


def chart_brand_adoption_trend(data_dir: str, out_dir: str) -> None:
    """Line chart: monthly brand share % over 24 months from actual data."""
    rx_path = os.path.join(data_dir, 'prescriptions.csv')
    products_path = os.path.join(data_dir, 'products.csv')

    prescriptions = pd.read_csv(rx_path)
    products = pd.read_csv(products_path)
    prescriptions['rx_date'] = pd.to_datetime(prescriptions['rx_date'])
    prescriptions = prescriptions.merge(products[['product_id', 'product_type']], on='product_id', how='left')

    prescriptions['month'] = prescriptions['rx_date'].dt.to_period('M')
    monthly = prescriptions.groupby(['month', 'product_type'])['trx_quantity'].sum().unstack(fill_value=0)
    monthly['brand_share_pct'] = monthly.get('Brand', 0) / monthly.sum(axis=1) * 100
    monthly = monthly.reset_index()
    monthly['month'] = monthly['month'].dt.to_timestamp()

    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.plot(monthly['month'], monthly['brand_share_pct'], marker='o', color='#2ecc71',
            linewidth=2.5, markersize=6, label='Brand Share %')
    z = np.polyfit(range(len(monthly)), monthly['brand_share_pct'], 1)
    p = np.poly1d(z)
    ax.plot(monthly['month'], p(range(len(monthly))), '--', color='#95a5a6',
            linewidth=1.5, label=f'Trend (slope: {z[0]:.2f}%/mo)')

    ax.fill_between(monthly['month'], monthly['brand_share_pct'], alpha=0.1, color='#2ecc71')
    ax.set_title('Brand Adoption Trend (24 Months)', fontsize=18, fontweight='bold', pad=15)
    ax.set_xlabel('Month', fontsize=13)
    ax.set_ylabel('Brand Share %', fontsize=13)
    ax.legend(fontsize=11)
    plt.xticks(rotation=45)
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'brand_adoption_trend.png'))
    plt.close()
    print("  [OK] brand_adoption_trend.png")


def chart_specialty_mix(df: pd.DataFrame, out_dir: str) -> None:
    """Donut chart: TRx distribution by top 8 specialties."""
    spec_trx = df.groupby('specialty')['total_trx_2024'].sum().nlargest(8)

    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    colors = sns.color_palette('Set2', 8)
    wedges, texts, autotexts = ax.pie(
        spec_trx, labels=spec_trx.index, autopct='%1.1f%%',
        colors=colors, wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
        pctdistance=0.8, textprops={'fontsize': 11}
    )
    for t in autotexts:
        t.set_fontweight('bold')
    ax.set_title('TRx Distribution by Specialty', fontsize=18, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'specialty_mix.png'))
    plt.close()
    print("  [OK] specialty_mix.png")


def chart_composite_score_distribution(df: pd.DataFrame, out_dir: str) -> None:
    """Histogram: composite score distribution colored by tier."""
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)

    tier_colors = {'Bronze': '#cd7f32', 'Silver': '#c0c0c0', 'Gold': '#ffd700', 'Platinum': '#e5e4e2'}
    for tier in ['Bronze', 'Silver', 'Gold', 'Platinum']:
        subset = df[df['tier'] == tier]
        ax.hist(subset['composite_score'], bins=20, alpha=0.7,
                color=tier_colors[tier], label=tier, edgecolor='white')

    ax.set_title('Composite Score Distribution by Tier', fontsize=18, fontweight='bold', pad=15)
    ax.set_xlabel('Composite Score', fontsize=13)
    ax.set_ylabel('Number of Physicians', fontsize=13)
    ax.legend(fontsize=11)
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'composite_score_distribution.png'))
    plt.close()
    print("  [OK] composite_score_distribution.png")


def create_all_visualizations() -> None:
    """Generate all 6 publication-quality charts."""
    data_dir, out_dir = get_paths()
    sns.set_style('whitegrid')

    seg_path = os.path.join(data_dir, 'physician_segments.csv')
    if not os.path.exists(seg_path):
        print(f"ERROR: {seg_path} not found. Run segmentation_analysis.py first.")
        return

    df = pd.read_csv(seg_path)
    print("Generating visualizations...")

    chart_decile_distribution(df, out_dir)
    chart_specialty_mix(df, out_dir)
    chart_composite_score_distribution(df, out_dir)
    chart_brand_adoption_trend(data_dir, out_dir)

    # These need call_priority / territory data
    if 'priority_bucket' in df.columns:
        chart_priority_matrix(df, out_dir)
    else:
        print("  [WARN] priority_bucket column missing, skipping priority matrix chart")

    chart_territory_comparison(out_dir, data_dir)

    print(f"\nAll charts saved to: {out_dir}")


if __name__ == '__main__':
    create_all_visualizations()

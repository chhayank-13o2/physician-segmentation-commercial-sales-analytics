"""
Territory Performance Analytics
================================
Computes territory-level KPIs by aggregating physician segmentation data.

Reads from: ../data/raw/physician_segments.csv, call_priority_list.csv,
            prescriptions.csv, products.csv, territories.csv
Outputs to:  ../data/raw/territory_performance.csv
"""
import os
import pandas as pd
import numpy as np


def analyze_territory_performance() -> None:
    """
    Computes territory-level KPIs and ranks territories by total TRx.
    """
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'raw')

    # Load data
    call_path = os.path.join(data_dir, 'call_priority_list.csv')
    seg_path = os.path.join(data_dir, 'physician_segments.csv')
    territories_path = os.path.join(data_dir, 'territories.csv')
    prescriptions_path = os.path.join(data_dir, 'prescriptions.csv')

    # Use call_priority_list if available, else segments
    if os.path.exists(call_path):
        df = pd.read_csv(call_path)
    elif os.path.exists(seg_path):
        df = pd.read_csv(seg_path)
    else:
        print("Required CSVs not found. Run segmentation_analysis.py first.")
        return

    territories = pd.read_csv(territories_path) if os.path.exists(territories_path) else None

    # Load prescriptions for NRx data
    prescriptions = pd.read_csv(prescriptions_path)
    prescriptions['rx_date'] = pd.to_datetime(prescriptions['rx_date'])
    rx_2024 = prescriptions[prescriptions['rx_date'].dt.year == 2024]

    nrx_by_phys = rx_2024.groupby('physician_id')['nrx_quantity'].sum().reset_index(name='total_nrx')
    df = df.merge(nrx_by_phys, on='physician_id', how='left').fillna(0)

    # KPIs per territory
    territory_stats = []

    for terr, group in df.groupby('territory_id'):
        total_trx = group['total_trx_2024'].sum()
        total_nrx = group['total_nrx'].sum()
        physician_count = len(group)
        avg_trx = total_trx / physician_count if physician_count else 0
        yoy_growth = group['yoy_growth_pct'].mean()
        brand_share = group['brand_share_pct'].mean()
        top_spec = group['specialty'].mode().iloc[0] if not group['specialty'].empty else 'Unknown'

        has_priority = 'priority_bucket' in group.columns
        pri_a = len(group[group['priority_bucket'].str.startswith('A')]) if has_priority else 0
        pri_b = len(group[group['priority_bucket'].str.startswith('B')]) if has_priority else 0

        territory_stats.append({
            'territory_id': terr,
            'total_trx': total_trx,
            'total_nrx': total_nrx,
            'physician_count': physician_count,
            'avg_trx_per_physician': round(avg_trx, 1),
            'yoy_growth_rate': round(yoy_growth, 2),
            'brand_share_pct': round(brand_share, 2),
            'top_specialty': top_spec,
            'priority_a_count': pri_a,
            'priority_b_count': pri_b
        })

    tdf = pd.DataFrame(territory_stats)
    total_market_trx = tdf['total_trx'].sum()
    tdf['market_share'] = round(tdf['total_trx'] / total_market_trx * 100, 2) if total_market_trx else 0

    # Add region from territories table
    if territories is not None:
        tdf = tdf.merge(territories[['territory_id', 'region', 'territory_name']], on='territory_id', how='left')

    tdf = tdf.sort_values('total_trx', ascending=False).reset_index(drop=True)
    tdf['rank'] = range(1, len(tdf) + 1)

    out_path = os.path.join(data_dir, 'territory_performance.csv')
    tdf.to_csv(out_path, index=False)
    print(f"Territory performance saved to: {out_path}")
    print(f"Total territories: {len(tdf)}")

    print("\n--- Top 10 Territories ---")
    print(tdf.head(10)[['rank', 'territory_id', 'total_trx', 'physician_count',
                         'yoy_growth_rate', 'brand_share_pct', 'market_share']].to_string(index=False))

    print("\n--- Bottom 10 Territories ---")
    print(tdf.tail(10)[['rank', 'territory_id', 'total_trx', 'physician_count',
                          'yoy_growth_rate', 'brand_share_pct', 'market_share']].to_string(index=False))


if __name__ == '__main__':
    analyze_territory_performance()

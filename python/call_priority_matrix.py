"""
Call Priority Matrix.
Generates priority segmentation, visualizes it, and builds territory call lists.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def build_call_priority_matrix() -> None:
    """
    Builds the 2x2 priority matrix and territory call lists.
    """
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    out_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(out_dir, exist_ok=True)
    
    seg_path = os.path.join(data_dir, 'physician_segments.csv')
    if not os.path.exists(seg_path):
        print(f"Segmentation file not found: {seg_path}")
        return
        
    df = pd.read_csv(seg_path)
    df['opportunity_score'] = (df['growth_decile'] + df['brand_decile']) / 2
    
    def get_priority(row: pd.Series) -> str:
        high_vol = row['volume_decile'] >= 7
        high_opp = row['opportunity_score'] >= 6
        
        if high_vol and high_opp:
            return 'A (Protect - Weekly)'
        elif not high_vol and high_opp:
            return 'B (Grow - Bi-weekly)'
        elif high_vol and not high_opp:
            return 'C (Retain - Monthly)'
        else:
            return 'D (Monitor - Quarterly)'
            
    df['priority_bucket'] = df.apply(get_priority, axis=1)
    
    plt.figure(figsize=(12, 8), dpi=300)
    sns.set_style('whitegrid')
    
    color_map = {
        'A (Protect - Weekly)': 'red',
        'B (Grow - Bi-weekly)': 'orange',
        'C (Retain - Monthly)': 'blue',
        'D (Monitor - Quarterly)': 'gray'
    }
    
    sns.scatterplot(
        data=df, 
        x='volume_decile', 
        y='opportunity_score', 
        hue='priority_bucket', 
        palette=color_map,
        alpha=0.7
    )
    
    plt.axvline(x=6.5, color='black', linestyle='--')
    plt.axhline(y=5.5, color='black', linestyle='--')
    
    plt.text(8.5, 8, 'A: Protect', fontsize=12, fontweight='bold', alpha=0.5)
    plt.text(3, 8, 'B: Grow', fontsize=12, fontweight='bold', alpha=0.5)
    plt.text(8.5, 3, 'C: Retain', fontsize=12, fontweight='bold', alpha=0.5)
    plt.text(3, 3, 'D: Monitor', fontsize=12, fontweight='bold', alpha=0.5)
    
    plt.title('Physician Call Priority Matrix', fontsize=16)
    plt.xlabel('Volume Decile', fontsize=12)
    plt.ylabel('Opportunity Score', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'call_priority_matrix.png'))
    plt.close()
    
    summary = df.groupby('priority_bucket').agg(
        count=('physician_id', 'count'),
        avg_composite=('composite_score', 'mean'),
        avg_trx=('total_trx_2024', 'mean')
    ).reset_index()
    print("--- Priority Summary ---")
    print(summary)
    
    df['rank_in_terr'] = df.groupby('territory_id')['composite_score'].rank(ascending=False, method='first')
    call_list = df.sort_values(['territory_id', 'rank_in_terr'])
    call_list.to_csv(os.path.join(data_dir, 'call_priority_list.csv'), index=False)
    df.to_csv(seg_path, index=False)

if __name__ == '__main__':
    build_call_priority_matrix()

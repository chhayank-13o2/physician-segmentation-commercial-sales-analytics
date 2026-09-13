"""
Generate Professional Excel Deliverables
=========================================
Builds:
1. excel/physician_segmentation_workbook.xlsx
2. excel/territory_scorecard.xlsx

Features:
- Professional styling, corporate color palette (navy/slate/teal)
- Formatted tables with auto-filters
- Number formatting (currency, percentages, integer commas)
- Conditional formatting (color scales, highlighters)
- Summary cross-tabs and rollups
"""
import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule


def create_excel_deliverables():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'raw')
    excel_dir = os.path.join(base_dir, 'excel')
    os.makedirs(excel_dir, exist_ok=True)

    print("Loading data for Excel workbooks...")
    df_phys = pd.read_csv(os.path.join(data_dir, 'physician_segments.csv'))
    df_terr = pd.read_csv(os.path.join(data_dir, 'territory_performance.csv'))
    df_reps = pd.read_csv(os.path.join(data_dir, 'sales_reps.csv'))

    # Styles
    navy_header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    teal_header_fill = PatternFill(start_color="008080", end_color="008080", fill_type="solid")
    accent_fill = PatternFill(start_color="E8EEF5", end_color="E8EEF5", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=11)
    thin_border = Border(
        left=Side(style='thin', color='D3D3D3'),
        right=Side(style='thin', color='D3D3D3'),
        top=Side(style='thin', color='D3D3D3'),
        bottom=Side(style='thin', color='D3D3D3')
    )

    # -------------------------------------------------------------
    # WORKBOOK 1: physician_segmentation_workbook.xlsx
    # -------------------------------------------------------------
    wb1_path = os.path.join(excel_dir, 'physician_segmentation_workbook.xlsx')
    wb1 = openpyxl.Workbook()

    # --- Sheet 1: Physician Segments ---
    ws1 = wb1.active
    ws1.title = "Physician Segments"
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1.merge_cells("A1:K1")
    title_cell = ws1["A1"]
    title_cell.value = "PHYSICIAN SEGMENTATION & DECILE SCORING MODEL (2,200 HCPs)"
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    title_cell.fill = navy_header_fill
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 35

    cols_to_export = [
        'physician_id', 'first_name', 'last_name', 'specialty', 'territory_id',
        'total_trx_2024', 'yoy_growth_pct', 'brand_share_pct',
        'volume_decile', 'composite_score', 'tier', 'priority_bucket'
    ]
    headers = [
        'Physician ID', 'First Name', 'Last Name', 'Specialty', 'Territory',
        '2024 TRx', 'YoY Growth %', 'Brand Share %',
        'Volume Decile', 'Composite Score', 'Tier', 'Call Priority'
    ]

    ws1.append([]) # row 2 empty
    ws1.append(headers) # row 3 headers
    ws1.row_dimensions[3].height = 25

    for col_idx, cell in enumerate(ws1[3], 1):
        cell.font = header_font
        cell.fill = navy_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row_data in df_phys[cols_to_export].itertuples(index=False):
        ws1.append(list(row_data))

    # Number formatting & borders
    for row in ws1.iter_rows(min_row=4, max_row=ws1.max_row, min_col=1, max_col=len(headers)):
        for col_idx, cell in enumerate(row, 1):
            cell.font = regular_font
            cell.border = thin_border
            if col_idx == 6: # TRx
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right")
            elif col_idx in (7, 8): # Growth, Brand Share
                cell.number_format = '0.0%'
                cell.value = cell.value / 100.0 if cell.value else 0
                cell.alignment = Alignment(horizontal="right")
            elif col_idx in (9, 10): # Decile, Composite
                cell.number_format = '0.0'
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in (11, 12): # Tier, Priority
                cell.alignment = Alignment(horizontal="center")

    # Conditional Formatting on Composite Score (Column J)
    color_scale = ColorScaleRule(start_type='min', start_color='F8696B',
                                 mid_type='percentile', mid_value=50, mid_color='FFEB84',
                                 end_type='max', end_color='63BE7B')
    ws1.conditional_formatting.add(f"J4:J{ws1.max_row}", color_scale)

    # Auto-filter
    ws1.auto_filter.ref = f"A3:L{ws1.max_row}"

    # Auto-adjust column width
    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # --- Sheet 2: Decile x Specialty Cross-Tab ---
    ws2 = wb1.create_sheet(title="Decile x Specialty Pivot")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:M1")
    ws2["A1"].value = "PHYSICIAN COUNT BY SPECIALTY & VOLUME DECILE"
    ws2["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    ws2["A1"].fill = teal_header_fill
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 30

    pivot_df = pd.crosstab(df_phys['specialty'], df_phys['volume_decile'], margins=True, margins_name="Total")
    ws2.append([])

    pivot_headers = ['Specialty'] + [f"Decile {i}" for i in range(1, 11)] + ['Total HCPs']
    ws2.append(pivot_headers)
    ws2.row_dimensions[3].height = 24

    for cell in ws2[3]:
        cell.font = header_font
        cell.fill = teal_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for spec, row_vals in pivot_df.iterrows():
        row_list = [spec] + [int(v) for v in row_vals]
        ws2.append(row_list)

    for row in ws2.iter_rows(min_row=4, max_row=ws2.max_row, min_col=1, max_col=12):
        is_total_row = (row[0].value == "Total")
        for cell in row:
            cell.font = bold_font if is_total_row else regular_font
            cell.border = thin_border
            if isinstance(cell.value, (int, float)):
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right")

    for col in ws2.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws2.column_dimensions[col_letter].width = max(max_len + 3, 11)

    # --- Sheet 3: Call Priority Matrix (Action Plan) ---
    ws3 = wb1.create_sheet(title="Call Priority Matrix")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("A1:J1")
    ws3["A1"].value = "TARGET CALL LIST: PRIORITY A & B PHYSICIANS (HIGH POTENTIAL)"
    ws3["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    ws3["A1"].fill = navy_header_fill
    ws3["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws3.row_dimensions[1].height = 30

    df_priority_targets = df_phys[df_phys['priority_bucket'].str.startswith(('A', 'B'))].sort_values('composite_score', ascending=False)
    p_cols = ['physician_id', 'first_name', 'last_name', 'specialty', 'territory_id', 'total_trx_2024', 'composite_score', 'tier', 'priority_bucket']
    p_headers = ['HCP ID', 'First Name', 'Last Name', 'Specialty', 'Territory', '2024 TRx', 'Score', 'Tier', 'Priority Status', 'Contact Completed?']

    ws3.append([])
    ws3.append(p_headers)
    ws3.row_dimensions[3].height = 24
    for cell in ws3[3]:
        cell.font = header_font
        cell.fill = navy_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row_data in df_priority_targets[p_cols].itertuples(index=False):
        ws3.append(list(row_data) + ['[ ]'])

    for row in ws3.iter_rows(min_row=4, max_row=ws3.max_row, min_col=1, max_col=10):
        for col_idx, cell in enumerate(row, 1):
            cell.font = regular_font
            cell.border = thin_border
            if col_idx == 6:
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right")
            elif col_idx == 7:
                cell.number_format = '0.0'
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in (8, 9, 10):
                cell.alignment = Alignment(horizontal="center")

    ws3.auto_filter.ref = f"A3:J{ws3.max_row}"
    for col in ws3.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws3.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb1.save(wb1_path)
    print(f"  [OK] Saved: {wb1_path}")

    # -------------------------------------------------------------
    # WORKBOOK 2: territory_scorecard.xlsx
    # -------------------------------------------------------------
    wb2_path = os.path.join(excel_dir, 'territory_scorecard.xlsx')
    wb2 = openpyxl.Workbook()

    ws_terr = wb2.active
    ws_terr.title = "Territory Scorecard"
    ws_terr.views.sheetView[0].showGridLines = True

    # Title
    ws_terr.merge_cells("A1:L1")
    ws_terr["A1"].value = "COMMERCIAL SALES PERFORMANCE SCORECARD - ALL 40 TERRITORIES"
    ws_terr["A1"].font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    ws_terr["A1"].fill = navy_header_fill
    ws_terr["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws_terr.row_dimensions[1].height = 35

    # Merge rep info
    df_terr_full = df_terr.merge(
        df_reps[['territory_id', 'first_name', 'last_name']],
        on='territory_id', how='left'
    )
    df_terr_full['rep_name'] = df_terr_full['first_name'] + ' ' + df_terr_full['last_name']

    t_cols = [
        'rank', 'territory_id', 'territory_name', 'region', 'rep_name',
        'physician_count', 'total_trx', 'total_nrx', 'market_share',
        'brand_share_pct', 'yoy_growth_rate', 'priority_a_count'
    ]
    t_headers = [
        'Rank', 'Territory ID', 'Territory Name', 'Region', 'Sales Representative',
        'HCP Universe', 'Total TRx', 'Total NRx', 'Market Share %',
        'Brand Share %', 'YoY Growth %', 'Priority A HCPs'
    ]

    ws_terr.append([])
    ws_terr.append(t_headers)
    ws_terr.row_dimensions[3].height = 25

    for cell in ws_terr[3]:
        cell.font = header_font
        cell.fill = navy_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row_data in df_terr_full[t_cols].itertuples(index=False):
        ws_terr.append(list(row_data))

    for row in ws_terr.iter_rows(min_row=4, max_row=ws_terr.max_row, min_col=1, max_col=12):
        for col_idx, cell in enumerate(row, 1):
            cell.font = regular_font
            cell.border = thin_border
            if col_idx in (1, 6, 12): # Rank, Count, Priority A
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in (7, 8): # TRx, NRx
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right")
            elif col_idx in (9, 10, 11): # Shares, Growth
                cell.number_format = '0.0%'
                cell.value = cell.value / 100.0 if cell.value else 0
                cell.alignment = Alignment(horizontal="right")

    # Conditional formatting on Market Share % (Col I)
    color_scale_terr = ColorScaleRule(start_type='min', start_color='F8696B',
                                      mid_type='percentile', mid_value=50, mid_color='FFEB84',
                                      end_type='max', end_color='63BE7B')
    ws_terr.conditional_formatting.add(f"I4:I{ws_terr.max_row}", color_scale_terr)
    ws_terr.auto_filter.ref = f"A3:L{ws_terr.max_row}"

    for col in ws_terr.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_terr.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # --- Sheet 2: Regional Rollup ---
    ws_reg = wb2.create_sheet(title="Regional Summary")
    ws_reg.views.sheetView[0].showGridLines = True

    ws_reg.merge_cells("A1:G1")
    ws_reg["A1"].value = "REGIONAL PERFORMANCE ROLLUP"
    ws_reg["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    ws_reg["A1"].fill = teal_header_fill
    ws_reg["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws_reg.row_dimensions[1].height = 30

    reg_summary = df_terr_full.groupby('region').agg(
        territory_count=('territory_id', 'count'),
        hcp_count=('physician_count', 'sum'),
        total_trx=('total_trx', 'sum'),
        total_nrx=('total_nrx', 'sum'),
        avg_brand_share=('brand_share_pct', 'mean'),
        avg_growth=('yoy_growth_rate', 'mean')
    ).reset_index()

    reg_headers = ['Region', 'Territories', 'Total HCPs', 'Total TRx', 'Total NRx', 'Avg Brand Share %', 'Avg YoY Growth %']
    ws_reg.append([])
    ws_reg.append(reg_headers)
    ws_reg.row_dimensions[3].height = 24

    for cell in ws_reg[3]:
        cell.font = header_font
        cell.fill = teal_header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row_data in reg_summary.itertuples(index=False):
        ws_reg.append(list(row_data))

    for row in ws_reg.iter_rows(min_row=4, max_row=ws_reg.max_row, min_col=1, max_col=7):
        for col_idx, cell in enumerate(row, 1):
            cell.font = regular_font
            cell.border = thin_border
            if col_idx in (2, 3):
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in (4, 5):
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right")
            elif col_idx in (6, 7):
                cell.number_format = '0.0%'
                cell.value = cell.value / 100.0 if cell.value else 0
                cell.alignment = Alignment(horizontal="right")

    for col in ws_reg.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_reg.column_dimensions[col_letter].width = max(max_len + 4, 14)

    wb2.save(wb2_path)
    print(f"  [OK] Saved: {wb2_path}")


if __name__ == '__main__':
    create_excel_deliverables()

# Power BI Setup Guide

This step-by-step guide walks you through building the Physician Segmentation & Commercial Sales Analytics dashboard in Power BI.

## Step 1: Import CSVs
1. Open Power BI Desktop.
2. Click **Get Data** -> **Text/CSV**.
3. Navigate to the `data/processed/` folder (or `data/raw/` depending on your pipeline output).
4. Import the following files one by one:
   - `dim_physician.csv`
   - `dim_product.csv`
   - `dim_territory.csv`
   - `dim_sales_rep.csv`
   - `dim_date.csv`
   - `fact_prescriptions.csv`
   - `physician_segmentation.csv`
5. Click **Transform Data** to open Power Query Editor. Ensure data types are correct (e.g., `date_id` as Date, `revenue` as Decimal Number, `physician_id` as Whole Number). Click **Close & Apply**.

*Screenshot Placeholder: Power Query Editor showing imported tables and data types.*

## Step 2: Set Up Data Model Relationships
1. Navigate to the **Model View** (diagram icon on the left panel).
2. Arrange your tables in a Star Schema format, with `fact_prescriptions` in the center.
3. Create the following relationships by dragging and dropping the fields:
   - `dim_physician[physician_id]` to `fact_prescriptions[physician_id]` (1:Many)
   - `dim_product[product_id]` to `fact_prescriptions[product_id]` (1:Many)
   - `dim_date[date_id]` to `fact_prescriptions[date_id]` (1:Many)
   - `dim_territory[territory_id]` to `dim_physician[territory_id]` (1:Many)
   - `dim_physician[physician_id]` to `physician_segmentation[physician_id]` (1:1, set Cross filter direction to "Both").

*Screenshot Placeholder: Power BI Model View showing the Star Schema relationships.*

## Step 3: Create Calculated Columns (Optional)
If your date table doesn't already have them, create useful date hierarchies.
1. Go to **Data View**. Select `dim_date`.
2. Click **New Column** and add formulas if needed (e.g., `YearMonth = FORMAT('dim_date'[date_id], "YYYY-MM")`).
*(Note: Most of this should be handled in the data generation/SQL phase, but can be done here if necessary).*

## Step 4: Create DAX Measures
1. Create a dedicated Measure Table (Home -> Enter Data -> name it `_Measures`).
2. Right-click the new table and select **New Measure**.
3. Copy and paste the DAX formulas from `powerbi/data_model.md` one by one (e.g., `Total TRx`, `YoY Growth %`, `Brand Share %`, `Physician Count by Tier`).
4. Format the measures appropriately (e.g., set `YoY Growth %` to Percentage with 1 decimal place, `Total Revenue` to Currency).

*Screenshot Placeholder: The Fields pane showing the `_Measures` table populated with calculator icons.*

## Step 5: Build Each Dashboard Page

### Page 1: Executive Summary
1. Add KPI Cards at the top for `Total TRx`, `Total Revenue`, and `YoY Growth %`.
2. Add a Line Chart: X-axis = `dim_date[YearMonth]`, Y-axis = `Total TRx` and `Total NRx`.
3. Add a Filled Map: Location = `dim_territory[territory_name]`, Tooltips = `Total Revenue`.

### Page 2: Physician Segmentation
1. Add a Donut Chart: Legend = `physician_segmentation[tier]`, Values = `Physician Count by Tier`.
2. Add a Stacked Column Chart: X-axis = `physician_segmentation[volume_decile]`, Y-axis = `Total TRx`.
3. Add a Matrix: Rows = `physician_segmentation[tier]`, Values = `Total TRx`, `Avg TRx per Physician`, `Brand Share %`.

### Page 3: Territory Performance
1. Add a Clustered Bar Chart: Y-axis = `dim_territory[region]`, X-axis = `Total TRx`.
2. Add a Table: Columns = `dim_sales_rep[first_name]`, `dim_sales_rep[last_name]`, `Total TRx`, `YoY Growth %`.

### Page 4: Call Priority Matrix
1. Add a Scatter Chart: X-axis = `Brand Share %`, Y-axis = `Total TRx`, Legend = `physician_segmentation[call_priority]`, Details = `dim_physician[physician_id]`.
2. Add a Table below for the Call List: `physician_id`, `first_name`, `last_name`, `specialty`, `tier`, `call_priority`.

*Screenshot Placeholder: Final layout of the Call Priority Matrix page.*

## Step 6: Apply Formatting and Theme
1. Go to **View** -> **Themes** -> **Browse for themes**.
2. Select the `PharmaTheme.json` file created earlier.
3. Standardize visual borders, shadows, and title fonts across all pages.
4. Add a consistent header navigation bar to switch between pages using buttons.

## Step 7: Set up Drill-through and Filters
1. **Filters**: Add Slicers to every page for `dim_date[Year]`, `dim_territory[Region]`, and `dim_physician[specialty]`. Sync them across pages if desired.
2. **Drill-through**: Create a hidden "Physician Profile" page. Drag `dim_physician[physician_id]` into the "Drill-through" well on this page. Now, from Page 2 or 4, users can right-click a physician and select "Drill through -> Physician Profile" to see detailed metrics.

*Screenshot Placeholder: Demonstration of the right-click drill-through functionality.*

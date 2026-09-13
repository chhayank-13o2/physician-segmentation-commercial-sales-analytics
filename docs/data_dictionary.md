# Data Dictionary

## Dimension Tables

### `dim_physician`
Stores detailed information about prescribing physicians.

| Column Name | Data Type | Description | Example Value | Nullable? | Notes |
|---|---|---|---|---|---|
| physician_id | INT | Unique identifier for each physician | 10001 | No | Primary Key |
| first_name | VARCHAR(50) | Physician's first name | John | No | |
| last_name | VARCHAR(50) | Physician's last name | Doe | No | |
| specialty | VARCHAR(100) | Primary medical specialty | Cardiology | No | |
| npi_number | VARCHAR(10) | National Provider Identifier | 1234567890 | No | Unique identifier |
| address | VARCHAR(255) | Practice address | 123 Main St | No | |
| city | VARCHAR(100) | Practice city | New York | No | |
| state | VARCHAR(2) | Practice state | NY | No | |
| zip_code | VARCHAR(10) | Practice ZIP code | 10001 | No | |
| territory_id | INT | Identifier for the assigned sales territory | 101 | No | Foreign Key to `dim_territory` |

### `dim_product`
Stores information about the pharmaceutical products.

| Column Name | Data Type | Description | Example Value | Nullable? | Notes |
|---|---|---|---|---|---|
| product_id | INT | Unique identifier for each product | 201 | No | Primary Key |
| product_name | VARCHAR(100) | Name of the pharmaceutical product | WonderDrug | No | |
| brand_name | VARCHAR(100) | Brand name of the product | WonderBrand | Yes | |
| manufacturer | VARCHAR(100) | Company manufacturing the product | PharmaCorp | No | |
| therapeutic_class | VARCHAR(100) | Classification of the product | Beta-blocker | No | |
| is_brand | BOOLEAN | Indicates if the product is a brand (True) or generic (False) | True | No | |

### `dim_territory`
Stores geographic sales territory definitions.

| Column Name | Data Type | Description | Example Value | Nullable? | Notes |
|---|---|---|---|---|---|
| territory_id | INT | Unique identifier for the territory | 101 | No | Primary Key |
| territory_name | VARCHAR(100) | Name of the territory | Northeast - NY | No | |
| region | VARCHAR(50) | Region containing the territory | Northeast | No | |
| district | VARCHAR(50) | District containing the territory | New York Metro | No | |

### `dim_sales_rep`
Stores information about the sales representatives.

| Column Name | Data Type | Description | Example Value | Nullable? | Notes |
|---|---|---|---|---|---|
| rep_id | INT | Unique identifier for the sales rep | 501 | No | Primary Key |
| first_name | VARCHAR(50) | Sales Rep's first name | Alice | No | |
| last_name | VARCHAR(50) | Sales Rep's last name | Smith | No | |
| email | VARCHAR(100) | Sales Rep's email address | alice.smith@pharma.com | No | |
| phone | VARCHAR(20) | Sales Rep's phone number | 555-0100 | Yes | |
| territory_id | INT | Identifier for the assigned territory | 101 | No | Foreign Key to `dim_territory` |
| hire_date | DATE | Date the rep was hired | 2021-05-15 | No | |

## Fact Tables

### `fact_prescriptions`
Stores prescription level transactional data.

| Column Name | Data Type | Description | Example Value | Nullable? | Notes |
|---|---|---|---|---|---|
| prescription_id | BIGINT | Unique identifier for the prescription event | 90001001 | No | Primary Key |
| date_id | DATE | Date the prescription was written | 2023-10-01 | No | Foreign Key to `dim_date` |
| physician_id | INT | Identifier of the prescribing physician | 10001 | No | Foreign Key to `dim_physician` |
| product_id | INT | Identifier of the prescribed product | 201 | No | Foreign Key to `dim_product` |
| trx_count | INT | Total Prescriptions (TRx) count | 5 | No | |
| nrx_count | INT | New Prescriptions (NRx) count | 2 | No | |
| quantity | INT | Quantity of pills/units prescribed | 30 | No | |
| revenue | DECIMAL(10,2) | Estimated revenue from the prescription | 150.00 | No | |

## Derived / Aggregate Tables

### `physician_segmentation`
Stores calculated deciles, scores, and tiers for each physician.

| Column Name | Data Type | Description | Example Value | Nullable? | Notes |
|---|---|---|---|---|---|
| physician_id | INT | Identifier of the physician | 10001 | No | Primary Key |
| volume_decile | INT | Decile ranking based on total TRx (1-10, 10 is highest) | 9 | No | |
| growth_decile | INT | Decile ranking based on YoY TRx growth (1-10) | 8 | No | |
| brand_decile | INT | Decile ranking based on brand share % (1-10) | 10 | No | |
| composite_score | DECIMAL(5,2) | Weighted score (40% Vol, 30% Growth, 30% Brand) | 8.80 | No | |
| tier | VARCHAR(20) | Segmentation tier (Platinum, Gold, Silver, Bronze) | Platinum | No | |
| call_priority | VARCHAR(10) | Assigned call priority (A, B, C, D) | A | No | Derived from matrix |

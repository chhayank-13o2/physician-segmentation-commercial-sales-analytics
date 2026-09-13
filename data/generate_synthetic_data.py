import os
import random
import uuid
import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
from faker import Faker

def main():
    np.random.seed(42)
    random.seed(42)
    fake = Faker()
    Faker.seed(42)

    raw_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    
    print("Generating Products...")
    products = [
        {"product_id": "PRD-001", "product_name": "Lipitor", "generic_name": "atorvastatin", "product_type": "Brand", "therapeutic_area": "Cardiovascular", "launch_date": "1997-01-01", "average_price_per_rx": 200.0},
        {"product_id": "PRD-002", "product_name": "Crestor", "generic_name": "rosuvastatin", "product_type": "Brand", "therapeutic_area": "Cardiovascular", "launch_date": "2003-08-12", "average_price_per_rx": 220.0},
        {"product_id": "PRD-003", "product_name": "Norvasc", "generic_name": "amlodipine", "product_type": "Brand", "therapeutic_area": "Cardiovascular", "launch_date": "1992-07-31", "average_price_per_rx": 150.0},
        {"product_id": "PRD-004", "product_name": "Plavix", "generic_name": "clopidogrel", "product_type": "Brand", "therapeutic_area": "Cardiovascular", "launch_date": "1997-11-17", "average_price_per_rx": 180.0},
        {"product_id": "PRD-005", "product_name": "Eliquis", "generic_name": "apixaban", "product_type": "Brand", "therapeutic_area": "Cardiovascular", "launch_date": "2012-12-28", "average_price_per_rx": 450.0},
        {"product_id": "PRD-006", "product_name": "Entresto", "generic_name": "sacubitril/valsartan", "product_type": "Brand", "therapeutic_area": "Cardiovascular", "launch_date": "2015-07-07", "average_price_per_rx": 550.0},
        {"product_id": "PRD-007", "product_name": "atorvastatin", "generic_name": "atorvastatin", "product_type": "Generic", "therapeutic_area": "Cardiovascular", "launch_date": "2011-11-30", "average_price_per_rx": 15.0},
        {"product_id": "PRD-008", "product_name": "rosuvastatin", "generic_name": "rosuvastatin", "product_type": "Generic", "therapeutic_area": "Cardiovascular", "launch_date": "2016-04-29", "average_price_per_rx": 20.0},
        {"product_id": "PRD-009", "product_name": "amlodipine", "generic_name": "amlodipine", "product_type": "Generic", "therapeutic_area": "Cardiovascular", "launch_date": "2007-03-23", "average_price_per_rx": 10.0},
        {"product_id": "PRD-010", "product_name": "lisinopril", "generic_name": "lisinopril", "product_type": "Generic", "therapeutic_area": "Cardiovascular", "launch_date": "2002-07-01", "average_price_per_rx": 8.0},
        {"product_id": "PRD-011", "product_name": "metoprolol", "generic_name": "metoprolol", "product_type": "Generic", "therapeutic_area": "Cardiovascular", "launch_date": "2006-07-31", "average_price_per_rx": 12.0},
        {"product_id": "PRD-012", "product_name": "losartan", "generic_name": "losartan", "product_type": "Generic", "therapeutic_area": "Cardiovascular", "launch_date": "2010-04-06", "average_price_per_rx": 14.0},
    ]
    df_products = pd.DataFrame(products)
    df_products.to_csv(os.path.join(raw_dir, 'products.csv'), index=False)

    print("Generating Territories...")
    regions = ["Northeast", "Southeast", "Midwest", "West"]
    territories = []
    states = ["NY", "CA", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
    for i in range(1, 41):
        territories.append({
            "territory_id": f"T-{i:03d}",
            "territory_name": f"Territory {i}",
            "region": np.random.choice(regions),
            "district": f"District {i // 10 + 1}",
            "state_coverage": np.random.choice(states)
        })
    df_territories = pd.DataFrame(territories)
    df_territories.to_csv(os.path.join(raw_dir, 'territories.csv'), index=False)

    print("Generating Sales Reps...")
    reps = []
    for i in range(1, 41):
        reps.append({
            "rep_id": f"R-{i:03d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "territory_id": f"T-{i:03d}",
            "hire_date": fake.date_between(start_date='-10y', end_date='today'),
            "experience_years": np.random.randint(1, 15),
            "email": fake.email()
        })
    df_reps = pd.DataFrame(reps)
    df_reps.to_csv(os.path.join(raw_dir, 'sales_reps.csv'), index=False)

    print("Generating Physicians...")
    specialties = ["Cardiology", "Internal Medicine", "Family Practice", "Endocrinology", "Nephrology", "Neurology", "Pulmonology", "Gastroenterology", "Rheumatology", "Hematology", "Oncology", "Geriatrics", "Emergency Medicine", "Hospitalist", "General Practice"]
    specialty_probs = [0.12, 0.20, 0.18, 0.05, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.05, 0.04, 0.05, 0.04, 0.03]
    
    physicians = []
    for i in range(1, 2201):
        physicians.append({
            "physician_id": f"PH-{i:04d}",
            "npi": fake.numerify(text="##########"),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "specialty": np.random.choice(specialties, p=specialty_probs),
            "territory_id": f"T-{np.random.randint(1, 41):03d}",
            "city": fake.city(),
            "state": fake.state_abbr(),
            "years_in_practice": np.random.randint(1, 41),
            "medical_school": fake.company() + " Medical School"
        })
    df_physicians = pd.DataFrame(physicians)
    df_physicians.to_csv(os.path.join(raw_dir, 'physicians.csv'), index=False)

    print("Generating Prescriptions (~250k)...")
    
    # Generate dates
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2024, 12, 31)
    date_range = (end_date - start_date).days
    
    # Pareto distribution for physician rx volume
    # alpha around 1.16 gives ~80/20 rule
    volumes = np.random.pareto(1.16, 2200)
    volumes = volumes / np.sum(volumes) * 250000
    volumes = volumes.astype(int)
    
    prescriptions = []
    rx_counter = 1
    
    for idx, physician in enumerate(physicians):
        vol = volumes[idx]
        if vol <= 0:
            continue
            
        phys_spec = physician['specialty']
        # Higher affinity for Cardiologists
        if phys_spec == 'Cardiology':
            brand_prob = 0.45
            vol_multiplier = 1.2
        elif phys_spec in ['Internal Medicine', 'Family Practice']:
            brand_prob = 0.35
            vol_multiplier = 1.0
        else:
            brand_prob = 0.25
            vol_multiplier = 0.8
            
        vol = int(vol * vol_multiplier)
        
        for _ in range(vol):
            # Select product
            is_brand = np.random.random() < brand_prob
            if is_brand:
                prod = np.random.choice(products[:6])
            else:
                prod = np.random.choice(products[6:])
                
            # Date with seasonal variation (less in Q1, more in Q4)
            random_days = np.random.randint(0, date_range)
            rx_date = start_date + timedelta(days=random_days)
            month = rx_date.month
            
            # Simple rejection sampling for seasonality
            prob = 1.0
            if month in [1, 2, 3]: prob = 0.9
            elif month in [10, 11, 12]: prob = 1.1
            
            if np.random.random() > prob:
                rx_date = rx_date + timedelta(days=np.random.randint(-30, 30))
                # Adjust if out of bounds
                if rx_date < start_date: rx_date = start_date
                if rx_date > end_date: rx_date = end_date
                
            rx_type = np.random.choice(['New', 'Refill'], p=[0.3, 0.7])
            trx = np.random.randint(1, 4)
            nrx = np.random.randint(1, trx + 1) if rx_type == 'New' else 0
            
            prescriptions.append({
                "rx_id": f"RX-{rx_counter:07d}",
                "physician_id": physician['physician_id'],
                "product_id": prod['product_id'],
                "rx_date": rx_date.strftime("%Y-%m-%d"),
                "trx_quantity": trx,
                "nrx_quantity": nrx,
                "rx_type": rx_type,
                "payer_type": np.random.choice(["Commercial", "Medicare", "Medicaid", "Cash"], p=[0.5, 0.3, 0.15, 0.05])
            })
            rx_counter += 1
            
    df_prescriptions = pd.DataFrame(prescriptions)
    df_prescriptions.to_csv(os.path.join(raw_dir, 'prescriptions.csv'), index=False)

    print("\nSummary Statistics:")
    print(f"Products: {len(df_products)}")
    print(f"Territories: {len(df_territories)}")
    print(f"Sales Reps: {len(df_reps)}")
    print(f"Physicians: {len(df_physicians)}")
    print(f"Prescriptions: {len(df_prescriptions)}")

if __name__ == "__main__":
    main()

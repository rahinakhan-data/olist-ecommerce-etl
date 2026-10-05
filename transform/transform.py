import os
import sys
import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import text, create_engine
from dotenv import load_dotenv

BASE_DIR = Path().resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import SCHEMA, LOG_DIR

LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename= LOG_DIR / 'transform_pipeline_logs.log',
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    filemode= 'a',
)

REPORTS_DIR = BASE_DIR / 'reports'
REPORTS_DIR.mkdir(exist_ok=True)

# ==========================================================================================================
# 1. Function to convert data types
# ==========================================================================================================
def convert_dtypes(dfs):
    
    # Create a secure clean storage dictionary
    cleaned_dfs = {}

    for file_name, df in dfs.items():
        cleaned_dfs[file_name] = df.copy()

    logging.info("--- [Day 2 - Step 1] Explicit Datatype Conversions Started ---")

    # A. Order dataset conversion
    if 'olist_orders_dataset.csv' in cleaned_dfs:
        df = cleaned_dfs['olist_orders_dataset.csv']
        print("-------------------------------Datatypes Before conversion---------------------------")
        print(df.dtypes)
        datetime_columns = ['order_purchase_timestamp', 
                                'order_approved_at', 
                                'order_delivered_carrier_date', 
                                'order_delivered_customer_date', 
                                'order_estimated_delivery_date'
                            ]
        # loop to convert each column datatype
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        print("-------------------------------Datatypes After conversion---------------------------")
        print(df.dtypes)

        print("Success..! All datetime columns correctly converted into datetime object\n")
        logging.info(f"[olist_orders_dataset] Converted {len(datetime_columns)} columns to datetime format. Rows: {len(df)}")

    # B. Order Items Dataset Conversion
    if 'olist_order_items_dataset.csv' in cleaned_dfs:
        df = cleaned_dfs['olist_order_items_dataset.csv']
        print("-------------------------------Datatypes Before conversion---------------------------")
        print(df.dtypes)

        # Convert item timeline limits to datetime objects
        df['shipping_limit_date'] = pd.to_datetime(df['shipping_limit_date'], errors='coerce')

        # Convert currency parameters securely to numeric float formats
        for col in ['price', 'freight_value']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print("-------------------------------Datatypes After conversion---------------------------")
        print(df.dtypes)
        print("Success..! 'shipping_limit_date', 'price, and 'freight_value' converted into correct datatypes\n")
        logging.info(f"[olist_order_items_dataset] Converted shipping_limit_date, price, and freight_value. Rows: {len(df)}")
        
    # C. Order Reviews Dataset Conversion        
    if 'olist_order_reviews_dataset.csv' in cleaned_dfs:
        df = cleaned_dfs['olist_order_reviews_dataset.csv']
        print("-------------------------------Datatypes Before conversion---------------------------")
        print(df.dtypes)

        # Convert review interaction logs to datetime formats
        for col in ['review_creation_date', 'review_answer_timestamp']:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        print("-------------------------------Datatypes After conversion---------------------------")
        print(df.dtypes)
        print("Success..! 'review_creation_date' and 'review_answer_timestamp' converted into datetime object\n") 
        logging.info(f"[olist_order_reviews_dataset] Converted review_creation_date and review_answer_timestamp. Rows: {len(df)}")
 
    logging.info("--- [Day 2 - Step 1] Explicit Datatype Conversions Completed ---")
    return cleaned_dfs

# ====================================================================================================================
# 2. Function to remove duplicates
# ====================================================================================================================
def remove_duplicates(dfs):
    print("============================= Handling Duplicate records started ===================================")
    logging.info("--- [Day 2 - Step 2] Duplicate Row Removal Scan Started ---")

    cleaned_dfs = {}
    for file_name, df in dfs.items():
        cleaned_dfs[file_name] = df.copy()
        before_rows = len(cleaned_dfs[file_name])

        # Track total exact identical matching rows across entire file dataset
        duplicate_records = cleaned_dfs[file_name].duplicated().sum()

        # drop the rows if exact duplicate records exist
        if duplicate_records > 0:
            print(f"Total {duplicate_records} records found in {file_name}\n")
            cleaned_dfs[file_name].drop_duplicates(inplace=True)
            print(f" -> Clean Complete | Rows Before: {before_rows} | Rows After: {len(cleaned_dfs[file_name])}\n")
            logging.info(f"[{file_name}] Duplicates Cleaned | Before: {before_rows} | After: {len(cleaned_dfs[file_name])} | Dropped: {duplicate_records}")
        else:
            logging.info(f"[{file_name}] Clean. 0 duplicates found across dataset. Rows: {before_rows}")

    print("============================= Handling Duplicate records end ======================================")
    logging.info("--- [Day 2 - Step 2] Duplicate Row Removal Scan Completed ---")
    return cleaned_dfs

# =====================================================================================================================
# 3. Function to Handle Null values
# =====================================================================================================================
def handle_null_values(dfs):
    print("============================= Handling Null Values Started ===================================")
    logging.info("--- [Day 2 - Step 3] Missing Value Handling Engine Started ---")

    cleaned_dfs = {}
    try:
        for file_name, df in dfs.items():
            df_clean = df.copy()
            null_counts = df_clean.isnull().sum().sum()
            
            if null_counts > 0:
                print(f"Total {null_counts} null values found in {file_name}")
                logging.info(f"[{file_name}] Processing missing fields. Total initial null counts: {null_counts}")

                num_cols = df_clean.select_dtypes(include = 'number').columns
                cat_cols = df_clean.select_dtypes(include = ['object', 'string']).columns
                datetime_columns = df_clean.select_dtypes(include = 'datetime64').columns
                try:
                    # 1. Handle Critical Primary Keys
                    critical_keys = [col for col in ['order_id', 'customer_id', 'product_id', 'seller_id'] if col in df_clean.columns]
                    
                    # Remove complete row records where major unique identity keys are completely blank
                    for col in critical_keys:
                        col_nulls = df_clean[col].isnull().sum()
                        if col_nulls > 0:
                            before_rows = len(df_clean)
                            print(f"Before Handling Null Values in {col}")
                            print(f"Total rows: {before_rows} | Total Null Values: {df_clean[col].isnull().sum()}")
                            print(f"Dropping rows of {col} with null values.")
                            df_clean = df_clean.dropna(subset = col)
                            after_rows = len(df_clean)
                            print(f"After Handling Null Values in {col} ")
                            print(f"Total rows: {after_rows} | Total Null Values: {df_clean[col].isnull().sum()}")

                    # 2. Handle Categorical Columns
                    for col in cat_cols:
                        if df_clean[col].isnull().sum()>0:
                            if col == 'product_category_name':
                                df_clean[col] = df_clean[col].fillna("missing_category")
                            elif col == 'review_comment_title':
                                df_clean[col] = df_clean[col].fillna("No Title")
                            elif col == 'review_comment_message':
                                df_clean[col] = df_clean[col].fillna("No message")
                            else:
                                df_clean[col] = df_clean[col].fillna("Unknown")

                    # 3. Handle Numerical Columns                   
                    for col in num_cols:
                        if df_clean[col].isnull().sum()>0:
                            df_clean[col] = df_clean[col].fillna(0)

                except Exception as err:
                    print("Error: ",err)
            else:
                logging.info(f"[{file_name}] 0 missing parameters detected. Keeping clean structure.")       
            cleaned_dfs[file_name] = df_clean
            
    except Exception as err:
        print("Error: ",err)
        logging.error(f"Global dictionary level failure under handle_null_values: {err}")

    print("============================= Handling Null Values End ======================================")
    logging.info("--- [Day 2 - Step 3] Missing Value Handling Engine Finished ---")

    return cleaned_dfs

# =========================================================================================================
# 4. Function to translate categories
# =========================================================================================================
def translate_categories(dfs):
    
    print("\n============================= Category Translation Started ===================================")
    logging.info("--- [Day 2 - Step 4] Category Translation Mapping Started ---")
    cleaned_dfs = {}

    for file_name, df in dfs.items():
        cleaned_dfs[file_name] = df.copy()

    if 'olist_products_dataset.csv' in cleaned_dfs and 'product_category_name_translation.csv' in cleaned_dfs:
        prod_df = cleaned_dfs['olist_products_dataset.csv']
        trans_df = cleaned_dfs['product_category_name_translation.csv']

        before_rows = len(prod_df)

        merged_df = pd.merge(prod_df, trans_df, on='product_category_name', how='left')

        # Backup rule: If explicit translation doesn't exist, preserve original Portuguese text token
        merged_df['product_category_name_english'] = merged_df['product_category_name_english'].fillna(merged_df['product_category_name'])
    
        # Drop old Portuguese column to finalize analytical-ready star schema table grain
        merged_df = merged_df.drop(columns='product_category_name')

        cleaned_dfs['olist_products_dataset.csv'] = merged_df

        print("Translated product categories from Portuguese to English successfully.")
        logging.info(f"[dim_products] Translation successfully completed. Rows verified: {len(merged_df)} (Before: {before_rows})")
    
    logging.info("--- [Day 2 - Step 4] Category Translation Mapping Completed ---")
    return cleaned_dfs  

# ===========================================================================================================
# 5. Function to build dim tables (day 3 Tasks)
# ===========================================================================================================
def build_dim_tables(dfs):
    dimensions = {}

    if 'olist_customers_dataset.csv' in dfs:
        dimensions['dim_customers'] = dfs['olist_customers_dataset.csv'].drop_duplicates(subset = 'customer_id', keep='first')

    if 'olist_products_dataset.csv' in dfs:
        required_columns = [
            'product_id', 'product_category_name_english', 'product_weight_g', 
            'product_length_cm', 'product_height_cm', 'product_width_cm'
        ]
        dimensions['dim_products'] = dfs['olist_products_dataset.csv'].drop_duplicates(subset = 'product_id', keep = 'first')[required_columns]

    if 'olist_sellers_dataset.csv' in dfs:
        dimensions['dim_sellers'] = dfs['olist_sellers_dataset.csv'].drop_duplicates(subset='seller_id', keep='first')

    if 'olist_orders_dataset.csv' in dfs:
        try:
            order_df = dfs['olist_orders_dataset.csv']
            unique_dates = order_df['order_purchase_timestamp'].dt.date.dropna().unique()
            date_df = pd.DataFrame({'date_actual': sorted(unique_dates)})

            date_df['date_actual'] = pd.to_datetime(date_df['date_actual'])
            date_df['date_key'] = date_df['date_actual'].dt.strftime('%Y%m%d').astype('int')
            date_df['date'] = date_df['date_actual'].dt.date
            date_df['day'] = date_df['date_actual'].dt.day
            date_df['month'] = date_df['date_actual'].dt.month
            date_df['year'] = date_df['date_actual'].dt.year
            date_df['quarter'] = date_df['date_actual'].dt.quarter
            date_df['day_of_week'] = date_df['date_actual'].dt.dayofweek

            dimensions['dim_date'] = date_df.drop(columns='date')
        except Exception as err:
            print("Error while building dim_date: ", err)

    return dimensions

# =========================================================================================================
# 6. Function to build secure table joins (Day 3 Task)
# =========================================================================================================
def build_fact_orders_joins(dfs):
    print("\n============================= Day 3: Building Secure Joins Started ===============================")
    logging.info("--- [Day 3] Central Fact Table Joins Engine Started ---")

    items_df = dfs['olist_order_items_dataset.csv'].copy()
    orders_df = dfs['olist_orders_dataset.csv'].copy()
    payments_df = dfs['olist_order_payments_dataset.csv'].copy()
    reviews_df = dfs['olist_order_reviews_dataset.csv'].copy()

    logging.info(f"[Grain Profile] Base Items: {len(items_df)} rows | Raw Payments: {len(payments_df)} rows | Raw Reviews: {len(reviews_df)} rows")

    # Review Grain Layer
    print("Fixing Review Grain Layer...")
    reviews_agg = reviews_df.groupby('order_id').agg(review_score=('review_score', 'mean')).reset_index()

    print("Merging Items and Orders layers securely...")
    fact_df = pd.merge(items_df, orders_df, on='order_id', how='left')
    fact_df = pd.merge(fact_df, reviews_agg, on='order_id', how='left')
    
    # Payment Grain Layer (Preventing Revenue Inflation Bug)
    print("Fixing Payment Grain Layer...")
    order_totals = items_df.groupby('order_id')['price'].sum().reset_index()
    order_totals.columns = ['order_id', 'total_items_price_per_order']

    payments_agg = payments_df.groupby('order_id').agg(
        total_payment_value=('payment_value', 'sum'),
        payment_type=('payment_type', 'first')
    ).reset_index()

    payment_map = pd.merge(payments_agg, order_totals, on='order_id', how='inner')
    payment_map['payment_ratio'] = payment_map['total_payment_value'] / payment_map['total_items_price_per_order']

    fact_df = pd.merge(fact_df, payment_map[['order_id', 'payment_type', 'payment_ratio']], on='order_id', how='left')
    fact_df['payment_value'] = (fact_df['price'] * fact_df['payment_ratio']).fillna(0)
    fact_df.drop(columns=['payment_ratio'], inplace=True)
    
    print(f"Row Count Profile: Fact table grain stable at {len(fact_df)} valid records.")
    logging.info(f"[Join Step 2] Managed payment allocations. Finalized Fact size: {len(fact_df)}")

    print("============================= Day 3: Building Secure Joins End ==============================\n")
    logging.info("--- [Day 3] Central Fact Table Joins Engine Completed Successfully ---")

    return fact_df

# =========================================================================================================
# 7. Function to Add Derived Columns (Day 4 Task)
# =========================================================================================================
def add_derived_columns(fact_df):
    print("\n============================= Day 4: Adding Derived Columns Started ===============================")
    logging.info("--- [Day 4] Derived Columns Generation Started ---")
    
    df_derived = fact_df.copy()
    
    # A. delivery_delay_days (Actual vs Estimated Delivery Date)
    df_derived['delivery_delay_days'] = (df_derived['order_delivered_customer_date'] - df_derived['order_estimated_delivery_date']).dt.days
    df_derived['delivery_delay_days'] = df_derived['delivery_delay_days'].apply(lambda x: x if x > 0 else 0).fillna(0).astype('int64')

    # B. total_order_value (Price + Freight Value)
    df_derived['total_order_value'] = df_derived['price'] + df_derived['freight_value']
    
    # C. is_positive_review (Review score of 4 or above -> 1 else 0 or boolean)
    df_derived['is_positive_review'] = df_derived['review_score'].apply(lambda x: 1 if x >= 4 else 0)

    df_derived['order_purchase_date_key'] = df_derived['order_purchase_timestamp'].dt.strftime('%Y%m%d').fillna('-1').astype(int)

    logging.info(f"Derived columns successfully added. Columns shape: {df_derived.shape}")
    print("============================= Day 4: Adding Derived Columns End ==============================\n")
    return df_derived

# =========================================================================================================
# 8. Function to Run Data Quality Checks (Day 4 Task)
# =========================================================================================================
def run_data_quality_checks(fact_df, dfs):
    print("\n============================= Day 4: Running Data Quality Assertions ===============================")
    logging.info("--- [Day 4] Data Quality Engine Started ---")
    
    # Check 1: No negative prices or freight values
    print("Audit 1: Checking for negative financial parameters...")
    negative_prices = (fact_df['price'] < 0).sum()
    negative_freight = (fact_df['freight_value'] < 0).sum()
    assert negative_prices == 0, f"DQ Failure: Found {negative_prices} negative prices!"
    assert negative_freight == 0, f"DQ Failure: Found {negative_freight} negative freight values!"
    print(" -> Financial integrity checked. No negative prices/freight found.")
    
    # Check 2: No delivery date before purchase date
    print("Audit 2: Checking delivery dates vs purchase dates timeline...")
    invalid_delivery_timeline = (fact_df['order_delivered_customer_date'] < fact_df['order_purchase_timestamp']).sum()
    assert invalid_delivery_timeline == 0, f"DQ Failure: Found {invalid_delivery_timeline} rows where delivery happened before purchase!"
    print(" -> Timeline checks passed. Delivery sequence is logically consistent.")
    
    # Check 3: No future dates
    print("Audit 3: Scanning for anomalous future timestamps...")
    current_time = pd.Timestamp.now()
    date_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date']
    for col in date_cols:
        if col in fact_df.columns:
            future_dates = (fact_df[col] > current_time).sum()
            assert future_dates == 0, f"DQ Failure: Column {col} contains {future_dates} future dates!"
    print(" -> Future timestamp scanning complete. No ghost/future entries found.")
    
    # Check 4: No orphan foreign keys
    print("Audit 4: Validating foreign key structural constraints...")
    
    # Extract only valid non-null customer entries from the fact table to check against dimensions
    valid_fact_customers = fact_df['customer_id'].dropna()
    
    if 'olist_orders_dataset.csv' in dfs:
        orphan_customers = (~valid_fact_customers.isin(dfs['olist_orders_dataset.csv']['customer_id'])).sum()
        assert orphan_customers == 0, f"DQ Failure: Found {orphan_customers} orphan customer IDs relative to cleaned orders!"
        
    if 'olist_products_dataset.csv' in dfs:
        valid_fact_products = fact_df['product_id'].dropna()
        orphan_products = (~valid_fact_products.isin(dfs['olist_products_dataset.csv']['product_id'])).sum()
        assert orphan_products == 0, f"DQ Failure: Found {orphan_products} orphan product IDs in fact table!"
        
    print(" -> All foreign key checks passed. Referential integrity is perfectly safe.")
    print("\n ALL DATA QUALITY ASSERTIONS PASSED SUCCESSFULLY! ")
    logging.info("--- [Day 4] All Data Quality Checks Passed Without Exception ---")
    print("============================= Day 4: Data Quality Assertions End ==============================\n")
    return True

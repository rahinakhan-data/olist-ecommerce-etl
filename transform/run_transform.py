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
from transform import (convert_dtypes, remove_duplicates, 
                        handle_null_values, translate_categories, build_dim_tables, 
                        build_fact_orders_joins, add_derived_columns, run_data_quality_checks, 
                    )
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok= True)

REPORTS_DIR = BASE_DIR / 'reports'
REPORTS_DIR.mkdir(exist_ok= True)

load_dotenv(dotenv_path=BASE_DIR / '.env')

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename= LOG_DIR / 'transform_pipeline_logs.log',
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    filemode= 'a',
)

# =====================================================================================================
# 1. Function to fetch records from database staging tables
# =====================================================================================================
def fetch_records():
    print("Records fetching started from database")
    logging.info("--- [Extraction Step] Fetching Data From Staging Schema Started ---")

    file_names = list(SCHEMA.keys())
    dfs = {}

    for file_name in file_names:
        clean_table_name = f"raw_{file_name.replace('.csv', '').replace('_dataset', '')}"
        try:
            fetch_query = f"SELECT * FROM staging.{clean_table_name}"
            dfs[file_name] = pd.read_sql(fetch_query, con=engine)

            print(f"Success..! {len(dfs[file_name])} records fetched from 'staging.{clean_table_name}'")
            logging.info(f"Successfully fetched staging.{clean_table_name} | Row Count: {len(dfs[file_name])}")

        except Exception as err:
            print("Error occurs during fetching data from database: ", err)
            logging.error(f"Error fetching staging.{clean_table_name}: {err}")  

    logging.info("--- [Extraction Step] Fetching Data Completed ---")
    return dfs

# =========================================================================================================
# 9. Function to Load Data to Warehouse Schema & Generate DQ Report (Day 5 Task)
# =========================================================================================================
def load_to_analytics_and_report(fact_df, dimensions, raw_dfs, cleaned_dfs):
    print("\n============================= Day 5: Wrap Up & Loading Started ===============================")
    logging.info("--- [Day 5] Load Layer & Data Quality Report Generation Started ---")
    
    try:
        # A. Create warehouse schema if it does not exist
        print("Creating warehouse schema if not exists...")
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS warehouse;"))
            conn.commit()
            
        # B. Publish all Dimension Tables to the warehouse schema
        print("Publishing Dimension Tables to database 'warehouse' schema...")
        for dim_name, dim_df in dimensions.items():
            dim_df.to_sql(name=dim_name, con=engine, schema='warehouse', if_exists='replace', index=False)
            print(f" ✓ Successfully loaded WAREHOUSE.{dim_name} table.")
            logging.info(f"[Load Step] Loaded warehouse.{dim_name} | Rows: {len(dim_df)}")

        # C. Load Central Fact Table to the warehouse schema
        print("Loading central 'fact_orders' into 'warehouse' schema...")
        fact_df.to_sql(name='fact_orders', con=engine, schema='warehouse', if_exists='replace', index=False)
        print("Success..! Final Star Schema completely published.")
        logging.info(f"[Load Step] Loaded warehouse.fact_orders | Rows: {len(fact_df)}")
        
    except Exception as err:
        print("Error while loading tables: ", err)
        logging.error(f"Failed to execute Day 5 Loading operations: {err}")
        raise err

    # D. DQ CSV Profiler summary mapping logic
    print("\nGenerating comprehensive Data Quality Report...")
    report_records = []
    
    for file_name in raw_dfs.keys():
        raw_rows = len(raw_dfs[file_name])
        clean_rows = len(cleaned_dfs[file_name]) if file_name in cleaned_dfs else "N/A"
        report_records.append({
            "Dataset_Name": file_name, 
            "Raw_Row_Count": raw_rows, 
            "Cleaned_Row_Count": clean_rows,
            "Total Rows Dropped": raw_rows - clean_rows
        })        
    
    dq_report_df = pd.DataFrame(report_records)
    report_output_path = REPORTS_DIR / 'data_quality_report.csv'
    dq_report_df.to_csv(report_output_path, index=False)
    
    print(f"Data Quality Report successfully saved at: {report_output_path}")
    print("\n--- Summary Visual Profile ---")
    print(dq_report_df.to_string(index=False))
    
    print("============================= Day 5: Wrap Up & Loading End ==============================\n")
    logging.info("--- [Day 5] Pipeline Completed. Data Quality Report Generated Successfully ---")


if __name__ == "__main__":
    logging.info("==================== WEEK 2 TRANSFORM ENGINE RUN STARTED ====================")

    # 1. Fetch Data
    dfs = fetch_records()
    
    # 2. Day 2 Task Functions
    cleaned_dfs = convert_dtypes(dfs)
    cleaned_dfs = remove_duplicates(cleaned_dfs)
    cleaned_dfs = handle_null_values(cleaned_dfs)
    cleaned_dfs = translate_categories(cleaned_dfs)

    # 3. Day 3 Step: Build Dimensions & Secure Joins
    dimensions = build_dim_tables(cleaned_dfs) # FIXED: Added execution layers to capture dimensions
    final_fact_orders = build_fact_orders_joins(cleaned_dfs)

    # 4. Day 4 Steps: Add metrics & Run Validations
    final_fact_orders = add_derived_columns(final_fact_orders)
    dq_passed = run_data_quality_checks(final_fact_orders, cleaned_dfs)

    # 5. Day 5 Load Engine Execution Check Map
    load_to_analytics_and_report(final_fact_orders, dimensions, dfs, cleaned_dfs)
    
    logging.info("==================== WEEK 2 TRANSFORM ENGINE RUN SUCCESSFUL ====================")
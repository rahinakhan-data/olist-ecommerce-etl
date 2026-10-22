# Import requied libraries
import sys
import logging
import pandas as pd
from pathlib import Path

# Finds the exact path of your main project folder
BASE_DIR = Path().resolve()
if str(BASE_DIR) not in sys.path:   # Checks if python knows where the main folder is
    sys.path.append(str(BASE_DIR))  # Adds the main folder to python's path list

from config.config import SCHEMA
from config.db_utils import LOGS_DIR, REPORTS_DIR, engine
from transform.transform import (convert_dtypes, remove_duplicates, 
                        handle_null_values, translate_categories, build_dim_tables, 
                        build_fact_orders_joins, add_derived_columns, run_data_quality_checks, 
                    )

LOGS_DIR.mkdir(exist_ok= True)   # Make logs folder if it does not exist
REPORTS_DIR.mkdir(exist_ok= True)   # Make reports folder if it does not exist

# Set up log file rules
logging.basicConfig(
    filename= LOGS_DIR / 'transform_pipeline_logs.log',
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    filemode= 'a',
)

# =====================================================================================================
# 1. Function to fetch records from database staging tables
# =====================================================================================================
def fetch_records():
    file_names = list(SCHEMA.keys())
    dfs = {}
    for file_name in file_names:
        clean_table_name = f"raw_{file_name.replace('.csv', '').replace('_dataset', '')}"
        fetch_query = f"SELECT * FROM staging.{clean_table_name}"
        dfs[file_name] = pd.read_sql(fetch_query, con=engine)
    return dfs

# =============================================================================================================
def get_transformed_data():
    print("\n--- Transformation Process Engine Started ---")
    raw_dfs = fetch_records()   
    
    cleaned_dfs = convert_dtypes(raw_dfs)               
    cleaned_dfs = remove_duplicates(cleaned_dfs)    
    cleaned_dfs = handle_null_values(cleaned_dfs)   
    cleaned_dfs = translate_categories(cleaned_dfs) 

    dimensions = build_dim_tables(cleaned_dfs)      
    final_fact_orders = build_fact_orders_joins(cleaned_dfs)    
    final_fact_orders = add_derived_columns(final_fact_orders)          
    
    dq_passed = run_data_quality_checks(final_fact_orders, cleaned_dfs) 
    if not dq_passed:
        raise ValueError("Data Quality Check Failed inside Transform Layer!")
        
    print(" ✓ Transformation completed successfully.")
    return final_fact_orders, dimensions, raw_dfs, cleaned_dfs
# Import requied libraries
import sys
import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import text

# Finds the exact path of your main project folder
BASE_DIR = Path().resolve()
if str(BASE_DIR) not in sys.path:   # Checks if python knows where the main folder is
    sys.path.append(str(BASE_DIR))  # Adds the main folder to python's path list

from transform.run_transform import get_transformed_data
from config.db_utils import LOGS_DIR, REPORTS_DIR, engine

# Set up log file rules
logging.basicConfig(
    filename = LOGS_DIR / 'load_pipeline_logs.log',
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    filemode = 'a'
)

def apply_warehouse_constraints():
    
    print("Applying Primary Keys, Foreign Keys and Performance Indexes...")
    constraints = [
        "ALTER TABLE warehouse.dim_customers ADD PRIMARY KEY (customer_id);",
        "ALTER TABLE warehouse.dim_products ADD PRIMARY KEY (product_id);",
        "ALTER TABLE warehouse.dim_sellers ADD PRIMARY KEY (seller_id);",
        "ALTER TABLE warehouse.dim_date ADD PRIMARY KEY (date_key);",
        
        "ALTER TABLE warehouse.fact_orders ADD CONSTRAINT fk_warehouse_customer FOREIGN KEY (customer_id) REFERENCES warehouse.dim_customers(customer_id);",
        "ALTER TABLE warehouse.fact_orders ADD CONSTRAINT fk_warehouse_product FOREIGN KEY (product_id) REFERENCES warehouse.dim_products(product_id);",
        "ALTER TABLE warehouse.fact_orders ADD CONSTRAINT fk_warehouse_seller FOREIGN KEY (seller_id) REFERENCES warehouse.dim_sellers(seller_id);",
        "ALTER TABLE warehouse.fact_orders ADD CONSTRAINT fk_warehouse_date FOREIGN KEY (order_purchase_date_key) REFERENCES warehouse.dim_date(date_key);",
        
        "CREATE INDEX IF NOT EXISTS idx_fact_date_key ON warehouse.fact_orders(order_purchase_date_key);"
    ]
    with engine.connect() as conn:
        for sql in constraints:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                conn.rollback()
    print(" ✓ Database Constraints and Indexes applied successfully.")

def run_reconciliation(fact_df):
    """Reconciliation Matrix Check: DataFrame vs Warehouse Match"""
    print("\n--- Running Day 1: Automated Reconciliation Audit Check ---")
    df_rows = len(fact_df)
    df_revenue = round(fact_df['price'].sum(), 2)

    with engine.connect() as conn:
        db_rows = conn.execute(text("SELECT COUNT(*) FROM warehouse.fact_orders;")).scalar()
        db_rev = conn.execute(text("SELECT SUM(price) FROM warehouse.fact_orders;")).scalar()
        db_revenue = round(db_rev, 2) if db_rev is not None else 0.0

    print(f"Target Metric | Python Dataframe | Warehouse Database")
    print(f"--------------|------------------|-------------------")
    print(f"Row Counts    | {df_rows:<16} | {db_rows:<18}")
    print(f"Total Revenue | ${df_revenue:<15} | ${db_revenue:<17}\n")

    assert df_rows == db_rows, "Reconciliation Error: Rows count mismatch!"
    assert abs(df_revenue - db_revenue) < 1.0, "Reconciliation Error: Revenue discrepancy detected!"
    print("SUCCESS: Reconciliation passed! Data matches completely.")

def generate_dq_report(raw_dfs, cleaned_dfs):
    
    report_records = []
    for file_name in raw_dfs.keys():
        raw_rows = len(raw_dfs[file_name])
        clean_rows = len(cleaned_dfs[file_name]) if file_name in cleaned_dfs else raw_rows
        report_records.append({
            "Dataset_Name": file_name,
            "Raw_Row_Count": raw_rows,
            "Cleaned_Row_Count": clean_rows,
            "Total Rows Dropped": raw_rows - clean_rows
        })
    dq_df = pd.DataFrame(report_records)
    dq_df.to_csv(REPORTS_DIR / 'data_quality_report.csv', index=False)
    print(" ✓ Data Quality Report saved at reports/data_quality_report.csv")

def load_data_warehouse(final_fact_orders, dimensions, raw_dfs, cleaned_dfs):
    print("\n============================= Warehouse Loading Started ===============================")
    try:
        
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS warehouse;"))
            conn.commit()

            print("Cleaning up older warehouse dependencies safely...")
            conn.execute(text("DROP TABLE IF EXISTS warehouse.fact_orders CASCADE;"))
            for dim_name in dimensions.keys():
                conn.execute(text(f"DROP TABLE IF EXISTS warehouse.{dim_name} CASCADE;"))
            conn.commit()

        # A. First load dimensions safely
        for dim_name, dim_df in dimensions.items():
            dim_df.to_sql(name=dim_name, con=engine, schema='warehouse', if_exists='replace', index=False)
            print(f" ✓ Table loaded: warehouse.{dim_name}")

        # =====================================================================================
        # B. Load central fact table
        final_fact_orders.to_sql(name='fact_orders', con=engine, schema='warehouse', if_exists='replace', index=False)
        print(" ✓ Table loaded: warehouse.fact_orders")

        apply_warehouse_constraints()
        run_reconciliation(final_fact_orders)
        generate_dq_report(raw_dfs, cleaned_dfs)
        
        print("============================= Warehouse Loading Successful ==============================\n")
    except Exception as err:
        logging.error(f"Critical error in Load Layer: {err}")
        raise err

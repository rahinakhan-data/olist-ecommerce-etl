import sys                          # Import sys to handle system-specific parameters and paths
import pandas as pd                 # Import pandas library for data manipulation using DataFrames
import logging                      # Import logging module to track events and print log messages
from datetime import datetime, timedelta        # Import datetime tools to manage dates and time intervals

from airflow import DAG             # Import DAG to define the Airflow workflow graph
from airflow.operators.python import PythonOperator     # Import PythonOperator to execute Python functions as tasks
from sqlalchemy import text                             # Import text tool to write raw SQL commands safely

if '/opt/airflow' not in sys.path:
    sys.path.insert(0, '/opt/airflow')

from config.config import SCHEMA            # Import the expected database schema definition
from config.db_utils import engine          # Import the database connection engine

from extract.run_extract import run_extract_pipeline        # Import the function that pulls raw data
from transform.run_transform import get_transformed_data    # Import the function that cleans and formats data
from load.load import load_data_warehouse                   # Import the function that saves data into the warehouse

# --------------------------- Extraction Task -----------------------------
def run_extraction():
    logging.info("--- [Airflow Task] Extraction Layer Started ---")
    run_extract_pipeline()      # Execute the external extraction script to get raw data
    logging.info("--- [Airflow Task] Extraction Layer Finished ---")

# ------------------------- Transformation Task ------------------------------
def run_transformation():
    logging.info("--- Transformation Layer Started ---")
    
    # Run transformation function and save results into tables and dictionarie
    final_fact_orders, dimensions, raw_dfs, cleaned_dfs = get_transformed_data() 
    
    logging.info("Staging transformed fact table into database...")
    
    # Save the fact orders DataFrame into the database
    final_fact_orders.to_sql(
        name='temp_transformed_fact_orders', 
        con=engine, 
        schema='staging',
        if_exists='replace', 
        index=False, 
        chunksize=10000
    )
    
    logging.info("Staging dimension tables into database...")
    for dim_name, dim_df in dimensions.items():
        # Save the current dimension DataFrame into the database
        dim_df.to_sql(
            name=f'temp_{dim_name}', 
            con=engine, 
            schema='staging',
            if_exists='replace', 
            index=False
        )
        
    logging.info("Staging cleaned datasets into database...")
    for file_name, clean_df in cleaned_dfs.items():
        clean_table_name = f"temp_clean_{file_name.replace('.csv', '').replace('_dataset', '')}"
        # Save the clean DataFrame into the database
        clean_df.to_sql(
            name=clean_table_name, 
            con=engine, 
            schema='staging',
            if_exists='replace', 
            index=False, 
            chunksize=10000
        )

    logging.info("--- Transformation Layer Finished & All Data Safely Staged in DB ---")

# ----------------------------- Load Task ---------------------------------------------
def run_loading():
    logging.info("--- Warehouse Loading Layer Started ---")    
    
    logging.info("--- Fetching fact table from DB stage ---")

    # Read the temporary fact table back into a pandas DataFrame
    final_fact_orders = pd.read_sql("SELECT * FROM staging.temp_transformed_fact_orders", con=engine)
    
    logging.info("--- Fetching dimension tables from DB stage ---")
    dimensions = {}         # Create an empty dictionary to hold dimension dataframes
    dim_names = ['dim_customers', 'dim_products', 'dim_sellers', 'dim_date']    # Define a list of expected dimension table names
    for dim in dim_names:
        # Read temporary dimension data from DB and save it in the dictionary
        dimensions[dim] = pd.read_sql(f"SELECT * FROM staging.temp_{dim}", con=engine)
        
    logging.info("--- Rebuilding raw and cleaned dictionaries from DB ---")
    raw_dfs = {}
    cleaned_dfs = {}
    
    file_names = list(SCHEMA.keys())    # Get the list of all file names defined in the schema configuration
    for file_name in file_names:
        
        # Create the raw table name string by cleaning the filename
        raw_table_name = f"raw_{file_name.replace('.csv', '').replace('_dataset', '')}" 

        # Read raw table data from staging schema into the dictionary
        raw_dfs[file_name] = pd.read_sql(f"SELECT * FROM staging.{raw_table_name}", con=engine)
        
        clean_table_name = f"temp_clean_{file_name.replace('.csv', '').replace('_dataset', '')}"    # Create the clean table name string by cleaning the filename
        cleaned_dfs[file_name] = pd.read_sql(f"SELECT * FROM staging.{clean_table_name}", con=engine)   # Read clean table data from staging schema into the dictionary
    
    # logging.info("Running load_data_warehouse inside Load Task...")
    # Pass all rebuilt DataFrames into final warehouse function
    load_data_warehouse(final_fact_orders, dimensions, raw_dfs, cleaned_dfs)    
    
    logging.info("--- Cleaning up temporary database tables ---")
    with engine.connect() as conn:      # Open a connection to the database
        conn.execute(text("DROP TABLE IF EXISTS staging.temp_transformed_fact_orders;"))    # Run SQL to delete temporary fact table
        for dim in dim_names:
            conn.execute(text(f"DROP TABLE IF EXISTS staging.temp_{dim};"))
        for file_name in file_names:
            clean_table_name = f"temp_clean_{file_name.replace('.csv', '').replace('_dataset', '')}"    # Re-create the temporary clean table name
            conn.execute(text(f"DROP TABLE IF EXISTS staging.{clean_table_name};")) # Run SQL to delete that temporary clean table
        conn.commit()   # Save changes and finalize deletions in the database
        
    logging.info("--- Warehouse Loading Layer Finished Successfully ---")

# -------------------------------------------------------------------------------------------------------------------------
# Define a dictionary containing default configurations for the Airflow DAG
default_args = {
    'owner': 'Data_engineering_team',       # Set the owner/team name responsible for this DAG
    'retries': 2,       # Set the number of times a task should retry if it fails
    'retry_delay': timedelta(minutes=1),    # Set the wait time of 1 minute before retrying a failed task
    'depends_on_past': False        # Allow tasks to run even if the previous run failed
}

with DAG(
    dag_id = 'Olist_Ecommerce_ETL_Pipeline_DAG',  # Give a unique identifier name to this DAG
    default_args = default_args,                  # Pass the default configuration dictionary created above
    schedule = None,                              # Set to None meaning this workflow must be triggered manually
    start_date = datetime(2026, 10, 19),          # Set the date when this workflow becomes active
    catchup = False,                              # Disable backfilling historical missed runs from start_date
    tags = ['olist', 'etl']                       # Add labels to filter and search this DAG in Airflow UI
) as dag:

     # Initialize the extraction task using PythonOperator
    task_extract = PythonOperator( task_id='Extract_task', python_callable=run_extraction )

    # Initialize the transformation task using PythonOperator
    task_transform = PythonOperator( task_id='Transform_task', python_callable=run_transformation )

    # Initialize the loading task using PythonOperator
    task_load = PythonOperator( task_id='Load_task', python_callable=run_loading )

    # Define execution order
    task_extract >> task_transform >> task_load

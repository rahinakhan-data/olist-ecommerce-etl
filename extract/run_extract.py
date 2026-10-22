import sys
import logging
from pathlib import Path
from sqlalchemy import text

# Finds the exact path of your main project folder
BASE_DIR = Path().resolve()
if str(BASE_DIR) not in sys.path:   # Checks if python knows where the main folder is
    sys.path.append(str(BASE_DIR))  # Adds the main folder to python's path list

from extract.extract import extract_records, data_profiling
from config.config import SCHEMA
from config.db_utils import REPORTS_DIR, engine

def run_extract_pipeline():
    print("End-to-End ETL Pipeline Running...") # Show start message to screen
    logging.info("================ Extraction RUN STARTED ================") # start message to save on logs
    try:
        # open a live connection to Docker database
        with engine.connect() as conn:
            print("Connection established to database") # Show success message on screen when connection is established
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging")) # run SQL to build a schema named 'staging' when it is missing
            conn.commit()
            print("Staging schema verified and ready in Docker Postgres.")
            logging.info("Database connection established and staging schema verified.") # write the success message in log file

        # Week 1: Day-2 
        file_names = list(SCHEMA.keys())
        extracted_dfs = {} # create an empty dict to hold data tables temporarily
        
        for file_name in file_names: # pick up each file name one by one
            df = extract_records(file_name)
            if df is not None:
                extracted_dfs[file_name] = df
        # Week 1: Day 3
        report_path = REPORTS_DIR / 'raw_data_profile_report.md'
        data_profiling(extracted_dfs, report_path)

        # LOAD INTO STAGING DATABASE
        print("\nLoading raw data directly into staging schema...")
        for file_name, df in extracted_dfs.items():

            # Clean up the file name to make a clean database table name
            table_name = f"raw_{file_name.replace('.csv', '').replace('_dataset', '')}"

            print(f"{len(df)} records are started to loading in staging.{table_name}")

            # command to push the entire data table to database
            df.to_sql(
                name = table_name, # traget database table name
                con = engine,
                schema = 'staging',
                index = False, # do not upload standard pandas index number as a column
                if_exists = 'replace', # completely wipe out older tables if they already exist
                method = 'multi', # insert rows in batches to speed up the process
                chunksize = 10000 # batch of 10000 rows should be insrted at a time
            )
            print(f"{len(df)} records are successfully inserted into staging.{table_name}")
            logging.info(f"{len(df)} records are successfully inserted into staging.{table_name}")
        print("\n Pipeline successfully executed end-to-end!")
        logging.info("================ Extraction ETL RUN SUCCESSFUL ================")

    except Exception as err: # if anything break, jump down here
        print("Database connection is not established", err)
        logging.error(f"Critical execution failure observed {err}")



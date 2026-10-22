# import required libraries
import time
import sys
import logging
from pathlib import Path

# Finds the exact path of your main project folder
BASE_DIR = Path().resolve()
if str(BASE_DIR) not in sys.path:   # Checks if python knows where the main folder is
    sys.path.append(str(BASE_DIR))  # Adds the main folder to python's path list

# Import the main pipeline steps
from extract.run_extract import run_extract_pipeline
from transform.run_transform import get_transformed_data
from load.load import load_data_warehouse

def run_complete_pipeline():
    # Print and log the start of the entire automation process
    print("---------------------------- Complete Pipeline Run Start ----------------------------")
    logging.info("---------------------------- Pipeline run in one click ---------------------------")
    
    # save the exact start time
    start_time = time.time()
    try:
        # Step 1: Run the extraction layer
        run_extract_pipeline()

        # Step 2: Clean, join, and prepare all raw data into fresh dimensions and fact tables
        final_fact_orders, dimensions, raw_dfs, cleaned_dfs = get_transformed_data() 

        # Step 3 : Run the load layer
        load_data_warehouse(final_fact_orders, dimensions, raw_dfs, cleaned_dfs)

        # Save the end time
        end_time = time.time()

        print(f"Successfully pipeline run in {end_time - start_time}")
    except Exception as err:
        # Catch any system or database errors
        print("Error: ",err)

    # Print and log the successful completion 
    print("------------------------ Complete Pipeline Run End ------------------------------")
    logging.info("--------------------------- Complete Pipeline Run End ---------------------------")

if __name__ == "__main__":
    # Trigger the master one-click automation function when running the file
    run_complete_pipeline()

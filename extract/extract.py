# import required libraries and modules
import sys
import time
import logging
import pandas as pd
from pathlib import Path

# define root directory
BASE_DIR = Path().resolve()
if str(BASE_DIR) not in sys.path: # Checks if python knows where the main folder is
    sys.path.append(str(BASE_DIR)) # Adds the main folder to python's path list

from config.config import DATA_DIR, LOG_DIR, SCHEMA

# Gets a list of all CSV file names from config
file_names = list(SCHEMA.keys())

# Creates the logs folder automatically if it is missing
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename= LOG_DIR / 'extract_pipeline_logs.log', # Sets the name and location of the log text file
    level= logging.INFO, # to save both normal notes and errors
    format= "%(asctime)s - %(levelname)s - %(message)s", # Sets the design of log messages with date and time
    filemode= 'a' # Keeps old logs and adds new messages at the bottom ('a' = append)
)

def extract_records(file_name):
    file_path = DATA_DIR / file_name # Combines data folder path with the CSV file name

    logging.info(f"Extraction started from '{file_name}'") # Writes a note in the log file that reading has started
    start_time = time.time() # Saves the exact start time before reading the file
    try:
        if not file_path.exists(): # Checks if the CSV file is missing
            raise FileNotFoundError(f"File not found at {file_path}") # Stops the code if the file is not there

        # load into df
        df = pd.read_csv(file_path, dtype=SCHEMA[file_name]) # Reads the CSV data into python with the correct column types
        rows = len(df) # Counts the total number of data rows 

        end_time = time.time() # Saves the exact finish time after reading the file
        duration = end_time - start_time

        print(f"{rows} records successfully extracted from '{file_name}' in {duration:.2f}s")
        logging.info(f"Extraction succeed from '{file_name}' | Rows: {rows} | Time Taken: {duration:.2f}s")   
        return df     # Sends the loaded data table back to the program

    except Exception as err:
        print(f"Error found during extraction {err}") # Prints the error message on screen
        logging.error(f"Error occurs during extraction") # Saves an error note inside the log file
        return None # Returns nothing because the file failed to load

#============================================================================
# Day 3: Data Profiling
#=============================================================================
# Starts a function to check data quality and make a report
def  data_profiling(extracted_dfs, report_path):
    print("Data Profiling Started")
    logging.info(f"Data Profiling Started")

    profile_results = {} # Creates an empty dictionary to hold the results of all tables

    for name, df in extracted_dfs.items():  # Loops through each table using its name and data
        total_rows = df.shape[0] # Finds the total number of rows in the table
        total_cols = df.shape[1] # Finds the total number of columns in the table
        duplicate_counts = df.duplicated().sum() # Counts how many rows are exact copies of each other
        null_counts = df.isnull().sum() # Counts how many empty or missing values are in each column
        null_percentage = (df.isnull().mean()*100).round(2) # Calculates the percentage of missing values rounded to 2 numbers
        """
        null_df = pd.DataFrame({
            'null_counts' : null_counts,
            'null_percentage' : null_percentage
        }).reset_index().rename(columns={'index' : 'column_name'})

        """

        null_df = pd.DataFrame({
            'null_counts' : null_counts,
            'null_percentage' : null_percentage
        })
        null_df = null_df.reset_index()
        null_df.columns = ['column_name', 'null_counts','null_percentage' ]

        numeric_cols = df.select_dtypes(include = 'number').columns # Finds all numeical columns
        filtered_numeric_cols = [c for c in numeric_cols if 'zip_code' not in c and 'id' not in c] # Filters out IDs and zip codes from number analysis

        statistics_df = None # Sets the math summary table to empty by default
        if len(filtered_numeric_cols) >0: # Checks if the table has any valid number columns left
            statistics_df = df[filtered_numeric_cols].describe().loc[['min','mean','max']].round(2) # Finds the minimum, average, and maximum values of numbers

        profile_results[name] = {
            'total_rows' : total_rows,
            'total_cols' : total_cols,
            'duplicate_counts' : duplicate_counts,
            'null_table': null_df,
            'statistics_table' : statistics_df
        }

    print("Writing All Metrics into Report")

    report_content = "# Raw Data Profile Report \n"
    report_content += "---\n\n"

    for name, value in profile_results.items():
        report_content += f"Table : `{name}`\n\n"
        report_content += f"Total Rows: {value['total_rows']} \n"
        report_content += f"Total Columns: {value['total_cols']} \n"
        report_content += f"Duplicate Records: {value['duplicate_counts']} \n"

        report_content += "Null Values Summary\n"
        report_content += value['null_table'].to_markdown(index = False) + "\n\n"

        report_content += "Descriptive Statistics Summary\n"
        if value['statistics_table'] is not None:
            report_content += value['statistics_table'].to_markdown() + "\n\n"
        else:
            report_content += "No numerical columns available for summary.\n\n"

        report_content += "\n\n"

    with open(report_path, 'w', encoding="utf-8") as file:
        file.write(report_content)
        print(f"Report successfully saved at {report_path}")

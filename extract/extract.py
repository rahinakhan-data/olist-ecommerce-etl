# import required libraries and modules
import sys
import time
import logging
import pandas as pd
from pathlib import Path

# define root directory
BASE_DIR = Path().resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.config import BASE_DIR, DATA_DIR, LOG_DIR, SCHEMA

file_names = list(SCHEMA.keys())

LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename= LOG_DIR / 'extract_pipeline_logs.log',
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    filemode= 'a'
)

def extract_records(file_name):
    file_path = DATA_DIR / file_name

    logging.info(f"Extraction started from '{file_name}'")
    start_time = time.time()
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found at {file_path}")

        # load into df
        df = pd.read_csv(file_path, dtype=SCHEMA[file_name])
        rows = len(df)

        end_time = time.time()
        duration = end_time - start_time

        print(f"{rows} records successfully extracted from '{file_name}' in {duration:.2f}s")
        logging.info(f"Extraction succeed from '{file_name}' | Rows: {rows} | Time Taken: {duration:.2f}s")   
        return df     

    except Exception as err:
        print(f"Error found during extraction {err}")
        logging.error(f"Error occurs during extraction")
        return None

extracted_dfs = {}
for file_name in file_names:
    df = extract_records(file_name)
    if df is not None:
        extracted_dfs[file_name] = df
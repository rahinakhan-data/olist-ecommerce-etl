# Import requied libraries
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 1. System path setup so Python can find project folders easily
# Docker
DATA_DIR = Path('/opt/airflow/data')
LOGS_DIR = Path('/opt/airflow/logs')
REPORTS_DIR = Path('/opt/airflow/reports')

# 3. Load secret database configuration details from the hidden .env file
ENV_FILE_PATH = Path('/opt/airflow/.env')
load_dotenv(dotenv_path=ENV_FILE_PATH)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 4. Combine credentials into a URL and build the active PostgreSQL engine link
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)


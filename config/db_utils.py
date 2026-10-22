# Import requied libraries
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 1. System path setup so Python can find project folders easily
BASE_DIR = Path().resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# 2. Define path variables and automatically create folders if they are missing
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok = True)

LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok = True)

REPORTS_DIR = BASE_DIR /'reports'
REPORTS_DIR.mkdir(exist_ok = True)

# 3. Load secret database configuration details from the hidden .env file
load_dotenv(dotenv_path = BASE_DIR / '.env')

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 4. Combine credentials into a URL and build the active PostgreSQL engine link
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)


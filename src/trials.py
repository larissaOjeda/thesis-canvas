from dap.integration.database import DatabaseConnection
from dotenv import load_dotenv
import os

load_dotenv() 
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

db_connection = DatabaseConnection(DATABASE_URL)
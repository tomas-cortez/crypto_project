import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL")
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS"))

# Database Configuration (PostgreSQL)
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("PORT")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

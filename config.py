import os
from dotenv import load_dotenv

load_dotenv()

JWT_KEY = os.getenv("JWT_KEY", "your_super_secret_key")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin123@localhost:5432/database_db")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY","dummy_key_for_no_op")
LLM_BACKEND = os.getenv("LLM_BACKEND", "")

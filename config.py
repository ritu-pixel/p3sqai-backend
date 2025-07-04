import os

# Load .env ONLY in local development
if os.getenv("ENV", "local") == "local":
    from dotenv import load_dotenv
    load_dotenv()

# Now fetch environment variables
JWT_KEY = os.getenv("JWT_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_BACKEND = os.getenv("LLM_BACKEND")

# Fail-fast if critical config is missing
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

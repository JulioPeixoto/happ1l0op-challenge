import os
import dotenv

dotenv.load_dotenv()

__ORIGINS__ = os.getenv("ORIGINS", "http://localhost:3000")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./happyloop.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

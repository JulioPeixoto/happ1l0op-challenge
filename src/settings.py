import os

__ORIGINS__ = os.getenv("ORIGINS", "http://localhost:3000")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./happyloop.db")

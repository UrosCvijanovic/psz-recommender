import os

DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5433"),
    "user": os.getenv("DB_USER", "uros"),
    "password": os.getenv("DB_PASSWORD", "n21wVyLRCCckFotr"),
    "database": os.getenv("DB_NAME", "psz"),
}

RAW_SHEMA = "recommender_raw"
CLEAN_SHEMA = "recommender_clean"
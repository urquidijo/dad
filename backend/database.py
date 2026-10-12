import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

logger = logging.getLogger("up_pricing.database")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "up_pricing_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "223044571")
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

SQLITE_FALLBACK_URL = "sqlite:///./up_pricing_local.db"

Base = declarative_base()
engine = None
SessionLocal = None
is_postgres_active = False

def get_engine():
    global engine, is_postgres_active
    if engine is not None:
        return engine

    try:
        # Attempt PostgreSQL connection (supports Neon SSL)
        pg_engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}
        )
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        engine = pg_engine
        is_postgres_active = True
        logger.info("Connected successfully to PostgreSQL (%s)", DATABASE_URL.split('@')[-1])
    except Exception as e:
        logger.warning(
            "PostgreSQL not reachable (%s). Falling back gracefully to local SQLite store.", e
        )
        engine = create_engine(SQLITE_FALLBACK_URL, connect_args={"check_same_thread": False})
        is_postgres_active = False
    return engine

def get_session():
    global SessionLocal
    eng = get_engine()
    if SessionLocal is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    return SessionLocal()

import os
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DB URL and convert mysql:// to mysql+pymysql:// for sqlalchemy
db_url = os.environ.get("DATABASE_URL", "")
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://")

# Remove query params like sslaccept=strict from URL
if "?" in db_url:
    db_url = db_url.split("?")[0]

# Create engine with SSL dict for TiDB Serverless
engine = create_engine(
    db_url,
    connect_args={
        "ssl": {
            "rejectUnauthorized": True
        }
    }
)

def run_query(query: str, params: tuple = None) -> pd.DataFrame:
    """Run a SELECT query and return a pandas DataFrame."""
    try:
        if params:
            df = pd.read_sql_query(query, engine, params=params)
        else:
            df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        print(f"Error running query: {e}")
        return pd.DataFrame()

def execute_sql(query: str):
    """Execute an INSERT/UPDATE/DELETE statement or raw DDL."""
    try:
        with engine.begin() as conn:
            conn.execute(query)
    except Exception as e:
        print(f"Error executing statement: {e}")

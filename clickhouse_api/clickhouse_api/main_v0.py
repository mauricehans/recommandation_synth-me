from fastapi import FastAPI, HTTPException
from clickhouse_driver import Client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

app = FastAPI(title="ClickHouse Version API")

# ClickHouse connection parameters from .env
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = os.getenv("CLICKHOUSE_TCP_PORT", "9000")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "default")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "default")

@app.get("/")
async def root():
    return {
        "message": "API is running. Access /version to get ClickHouse version.",
        "config": {
            "clickhouse_host": CLICKHOUSE_HOST,
            "clickhouse_port": CLICKHOUSE_PORT,
            "clickhouse_db": CLICKHOUSE_DB,
            "clickhouse_user": CLICKHOUSE_USER
        }
    }

@app.get("/version")
async def get_clickhouse_version():
    try:
        # Create a ClickHouse client
        client = Client(
            host=CLICKHOUSE_HOST,
            port=int(CLICKHOUSE_PORT),
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            database=CLICKHOUSE_DB
        )
        
        # Query ClickHouse version
        result = client.execute("SELECT version()")
        
        # Return the version
        return {
            "clickhouse_version": result[0][0], 
            "connection_status": "successful",
            "connected_to": f"{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to ClickHouse: {str(e)}")
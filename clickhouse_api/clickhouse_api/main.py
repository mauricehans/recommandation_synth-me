from fastapi import FastAPI, HTTPException
from clickhouse_driver import Client
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, Any

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Définition de modèles pour les réponses API
class ConfigInfo(BaseModel):
    clickhouse_host: str
    clickhouse_port: str
    clickhouse_db: str
    clickhouse_user: str

class RootResponse(BaseModel):
    message: str
    config: ConfigInfo

class VersionResponse(BaseModel):
    clickhouse_version: str
    connection_status: str
    connected_to: str

# Création de l'application avec des métadonnées pour la documentation
app = FastAPI(
    title="ClickHouse Version API",
    description="Une simple API pour se connecter à ClickHouse et récupérer sa version",
    version="1.0.0",
    contact={
        "name": "Développeur",
        "email": "dev@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# ClickHouse connection parameters from .env
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = os.getenv("CLICKHOUSE_TCP_PORT", "9000")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "default")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "default")

@app.get(
    "/", 
    response_model=RootResponse,
    summary="Informations de base",
    description="Retourne un message de bienvenue et la configuration actuelle de connexion à ClickHouse."
)
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

@app.get(
    "/version", 
    response_model=VersionResponse,
    summary="Version de ClickHouse",
    description="Se connecte au serveur ClickHouse et récupère sa version.",
    responses={
        200: {
            "description": "Version récupérée avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "clickhouse_version": "23.8.1.94",
                        "connection_status": "successful",
                        "connected_to": "clickhouse:9000"
                    }
                }
            }
        },
        500: {
            "description": "Erreur de connexion à ClickHouse",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to connect to ClickHouse: Connection refused"
                    }
                }
            }
        }
    }
)
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
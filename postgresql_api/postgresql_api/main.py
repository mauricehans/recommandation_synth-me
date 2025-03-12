from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import text
from pydantic import BaseModel
from typing import Dict, Any

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Définition de modèles pour les réponses API
class ConfigInfo(BaseModel):
    postgres_host: str
    postgres_port: str
    postgres_db: str
    postgres_user: str
    database_url: str

class RootResponse(BaseModel):
    message: str
    config: ConfigInfo

class VersionResponse(BaseModel):
    postgres_version: str
    connection_status: str
    connected_to: str

# Création de l'application avec des métadonnées pour la documentation
app = FastAPI(
    title="PostgreSQL Version API",
    description="Une simple API pour se connecter à PostgreSQL et récupérer sa version",
    version="1.0.0",
    contact={
        "name": "Développeur",
        "email": "dev@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# PostgreSQL connection parameters from .env
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5434")  # Port 5434 comme demandé
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")

# Créer l'URL de connexion
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

@app.get(
    "/", 
    response_model=RootResponse,
    summary="Informations de base",
    description="Retourne un message de bienvenue et la configuration actuelle de connexion à PostgreSQL."
)
async def root():
    return {
        "message": "API is running. Access /version to get PostgreSQL version.",
        "config": {
            "postgres_host": POSTGRES_HOST,
            "postgres_port": POSTGRES_PORT,
            "postgres_db": POSTGRES_DB,
            "postgres_user": POSTGRES_USER,
            "database_url": DATABASE_URL
        }
    }

@app.get(
    "/version", 
    response_model=VersionResponse,
    summary="Version de PostgreSQL",
    description="Se connecte au serveur PostgreSQL et récupère sa version.",
    responses={
        200: {
            "description": "Version récupérée avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "postgres_version": "PostgreSQL 15.3 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 10.2.1 20210110, 64-bit",
                        "connection_status": "successful",
                        "connected_to": "postgres:5434"
                    }
                }
            }
        },
        500: {
            "description": "Erreur de connexion à PostgreSQL",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to connect to PostgreSQL: Connection refused"
                    }
                }
            }
        }
    }
)
async def get_postgres_version():
    try:
        # Afficher les informations de connexion pour le débogage
        print(f"Connecting to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}")
        
        # Créer un moteur SQLAlchemy
        engine = sqlalchemy.create_engine(DATABASE_URL)
        
        # Se connecter à la base de données
        with engine.connect() as connection:
            # Exécuter une requête pour obtenir la version
            result = connection.execute(text("SELECT version()"))
            version = result.scalar()
        
        # Retourner la version
        return {
            "postgres_version": version, 
            "connection_status": "successful",
            "connected_to": f"{POSTGRES_HOST}:{POSTGRES_PORT}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to PostgreSQL: {str(e)}")
import express from "express";
import dotenv from "dotenv";
import pkg from 'pg';

const { Pool } = pkg;

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Configuration PostgreSQL
const POSTGRES_HOST = process.env.POSTGRES_HOST; 
const POSTGRES_PORT = parseInt(process.env.POSTGRES_PORT, 10); // Convertir le port en nombre
const POSTGRES_USER = process.env.POSTGRES_USER;
const POSTGRES_PASSWORD = process.env.POSTGRES_PASSWORD;
const POSTGRES_DB = process.env.POSTGRES_DB;

const pool = new Pool({
    host: POSTGRES_HOST,
    port: POSTGRES_PORT,
    user: POSTGRES_USER,
    password: POSTGRES_PASSWORD,
    database: POSTGRES_DB,
});

app.get("/", (req, res) => {
    res.json({
        message: "API is running. Access /version to get PostgreSQL version.",
        config: {
            postgres_host: POSTGRES_HOST,
            postgres_port: POSTGRES_PORT,
            postgres_db: POSTGRES_DB,
            postgres_user: POSTGRES_USER,
        }
    });
});

app.get("/version", async (req, res) => {
    try {
        const client = await pool.connect();
        const result = await client.query("SELECT version()");
        client.release();

        res.json({
            postgres_version: result.rows[0].version,
            connection_status: "successful",
            connected_to: `${POSTGRES_HOST}:${POSTGRES_PORT}`
        });
    } catch (error) {
        res.status(500).json({ error: `Failed to connect to PostgreSQL: ${error.message}` });
    }
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});

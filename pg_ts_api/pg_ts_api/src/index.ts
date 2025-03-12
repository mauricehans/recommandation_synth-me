import * as express from "express";
import { Request, Response } from "express";
import * as dotenv from "dotenv";
import pkg from 'pg';
const { Pool } = pkg;

dotenv.config();

const app = express.default();
const port: number = parseInt(process.env.PORT || "3000", 10);

// Configuration PostgreSQL
const POSTGRES_HOST: string = process.env.POSTGRES_HOST || "localhost"; 
const POSTGRES_PORT: number = parseInt(process.env.POSTGRES_PORT || "5432", 10);
const POSTGRES_USER: string = process.env.POSTGRES_USER || "postgres";
const POSTGRES_PASSWORD: string = process.env.POSTGRES_PASSWORD || "postgres";
const POSTGRES_DB: string = process.env.POSTGRES_DB || "postgres";

const pool = new Pool({
    host: POSTGRES_HOST,
    port: POSTGRES_PORT,
    user: POSTGRES_USER,
    password: POSTGRES_PASSWORD,
    database: POSTGRES_DB,
});

app.get("/", (req: Request, res: Response) => {
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

app.get("/version", async (req: Request, res: Response) => {
    try {
        const client = await pool.connect();
        const result = await client.query("SELECT version()");
        client.release();
        res.json({
            postgres_version: result.rows[0].version,
            connection_status: "successful",
            connected_to: `${POSTGRES_HOST}:${POSTGRES_PORT}`
        });
    } catch (error: any) {
        res.status(500).json({ error: `Failed to connect to PostgreSQL: ${error.message}` });
    }
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
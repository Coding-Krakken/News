import { Pool, PoolConfig } from "pg";
import { config } from "./index";

const isTest = process.env.NODE_ENV === "test";

const dbConfig: PoolConfig = isTest
  ? {
      host: config.testDatabase.host,
      port: config.testDatabase.port,
      database: config.testDatabase.name,
      user: config.testDatabase.user,
      password: config.testDatabase.password,
    }
  : {
      host: config.database.host,
      port: config.database.port,
      database: config.database.name,
      user: config.database.user,
      password: config.database.password,
    };

export const pool = new Pool(dbConfig);

export async function query(text: string, params?: unknown[]) {
  const start = Date.now();
  const res = await pool.query(text, params);
  const duration = Date.now() - start;

  if (config.env === "development") {
    console.log("Executed query", { text, duration, rows: res.rowCount });
  }

  return res;
}

export async function testConnection(): Promise<boolean> {
  try {
    await pool.query("SELECT 1");
    return true;
  } catch (error) {
    console.error("Database connection failed:", error);
    return false;
  }
}

export async function closePool(): Promise<void> {
  await pool.end();
}

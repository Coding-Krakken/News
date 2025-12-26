import dotenv from "dotenv";

dotenv.config();

export const config = {
  env: process.env.NODE_ENV || "development",
  port: parseInt(process.env.PORT || "3000", 10),

  database: {
    host: process.env.DB_HOST || "localhost",
    port: parseInt(process.env.DB_PORT || "5432", 10),
    name: process.env.DB_NAME || "news_db",
    user: process.env.DB_USER || "news_user",
    password: process.env.DB_PASSWORD || "news_password",
  },

  testDatabase: {
    host: process.env.TEST_DB_HOST || "localhost",
    port: parseInt(process.env.TEST_DB_PORT || "5433", 10),
    name: process.env.TEST_DB_NAME || "news_test_db",
    user: process.env.TEST_DB_USER || "news_user",
    password: process.env.TEST_DB_PASSWORD || "news_password",
  },

  jwt: {
    accessSecret: process.env.JWT_ACCESS_SECRET || "your-access-token-secret",
    refreshSecret:
      process.env.JWT_REFRESH_SECRET || "your-refresh-token-secret",
    accessExpiry: process.env.JWT_ACCESS_EXPIRY || "15m",
    refreshExpiry: process.env.JWT_REFRESH_EXPIRY || "7d",
  },

  security: {
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS || "12", 10),
    cookieSecret: process.env.COOKIE_SECRET || "your-cookie-secret",
  },

  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || "900000", 10),
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || "100", 10),
    authMaxRequests: parseInt(
      process.env.AUTH_RATE_LIMIT_MAX_REQUESTS || "5",
      10,
    ),
  },

  cors: {
    origin: process.env.CORS_ORIGIN || "http://localhost:3001",
  },

  logging: {
    level: process.env.LOG_LEVEL || "info",
  },
};

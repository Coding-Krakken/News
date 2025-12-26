import winston from "winston";
import { config } from "../config";

// Define PII fields to redact
const PII_FIELDS = ["password", "email", "token", "authorization", "cookie"];

// Redact sensitive information
const redactSensitiveData = (obj: any): any => {
  if (typeof obj !== "object" || obj === null) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(redactSensitiveData);
  }

  const redacted: any = {};
  for (const [key, value] of Object.entries(obj)) {
    const lowerKey = key.toLowerCase();
    if (PII_FIELDS.some((field) => lowerKey.includes(field))) {
      redacted[key] = "[REDACTED]";
    } else if (typeof value === "object" && value !== null) {
      redacted[key] = redactSensitiveData(value);
    } else {
      redacted[key] = value;
    }
  }
  return redacted;
};

const format = winston.format.combine(
  winston.format.timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
  winston.format.errors({ stack: true }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    const redactedMeta = redactSensitiveData(meta);
    const metaStr =
      Object.keys(redactedMeta).length > 0 ? JSON.stringify(redactedMeta) : "";
    return `${timestamp} [${level.toUpperCase()}]: ${message} ${metaStr}`;
  }),
);

export const logger = winston.createLogger({
  level: config.logging.level,
  format,
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(winston.format.colorize(), format),
    }),
  ],
});

// Suppress logs during tests
if (config.env === "test") {
  logger.transports.forEach((transport) => {
    transport.silent = true;
  });
}

export { redactSensitiveData };

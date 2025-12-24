import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { config } from '../config';

export interface TokenPayload {
  userId: number;
  email: string;
}

/**
 * Generate JWT access token
 */
export function generateAccessToken(payload: TokenPayload): string {
  return jwt.sign(payload, config.jwt.accessSecret, {
    expiresIn: config.jwt.accessExpiry,
  } as jwt.SignOptions);
}

/**
 * Generate JWT refresh token
 */
export function generateRefreshToken(payload: TokenPayload): string {
  // Include a random JWT ID to ensure refresh tokens are unique even when
  // generated in quick succession with identical payloads.
  const jwtId = crypto.randomBytes(8).toString('hex');
  return jwt.sign({ ...payload, jti: jwtId }, config.jwt.refreshSecret, {
    expiresIn: config.jwt.refreshExpiry,
  } as jwt.SignOptions);
}

/**
 * Verify JWT access token
 */
export function verifyAccessToken(token: string): TokenPayload | null {
  try {
    const decoded = jwt.verify(token, config.jwt.accessSecret) as TokenPayload;
    return decoded;
  } catch (error) {
    return null;
  }
}

/**
 * Verify JWT refresh token
 */
export function verifyRefreshToken(token: string): TokenPayload | null {
  try {
    const decoded = jwt.verify(token, config.jwt.refreshSecret) as TokenPayload;
    return decoded;
  } catch (error) {
    return null;
  }
}

/**
 * Hash a token for storage (used for refresh tokens)
 */
export function hashToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex');
}

/**
 * Generate a random token
 */
export function generateRandomToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

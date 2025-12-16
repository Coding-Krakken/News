import { query } from '../config/database';
import { RefreshToken } from '../models/token.model';

export class TokenRepository {
  async create(tokenHash: string, userId: number, expiresAt: Date): Promise<RefreshToken> {
    const result = await query(
      `INSERT INTO refresh_tokens (token_hash, user_id, expires_at)
       VALUES ($1, $2, $3)
       RETURNING *`,
      [tokenHash, userId, expiresAt]
    );
    return result.rows[0];
  }

  async findByHash(tokenHash: string): Promise<RefreshToken | null> {
    const result = await query(
      'SELECT * FROM refresh_tokens WHERE token_hash = $1',
      [tokenHash]
    );
    return result.rows[0] || null;
  }

  async revoke(tokenHash: string): Promise<boolean> {
    const result = await query(
      'UPDATE refresh_tokens SET revoked_at = CURRENT_TIMESTAMP WHERE token_hash = $1',
      [tokenHash]
    );
    return result.rowCount !== null && result.rowCount > 0;
  }

  async revokeAllForUser(userId: number): Promise<boolean> {
    const result = await query(
      'UPDATE refresh_tokens SET revoked_at = CURRENT_TIMESTAMP WHERE user_id = $1 AND revoked_at IS NULL',
      [userId]
    );
    return result.rowCount !== null && result.rowCount > 0;
  }

  async deleteExpired(): Promise<number> {
    const result = await query(
      'DELETE FROM refresh_tokens WHERE expires_at < CURRENT_TIMESTAMP'
    );
    return result.rowCount || 0;
  }
}

export const tokenRepository = new TokenRepository();

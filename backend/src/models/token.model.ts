export interface RefreshToken {
  id: number;
  token_hash: string;
  user_id: number;
  expires_at: Date;
  revoked_at: Date | null;
  created_at: Date;
}

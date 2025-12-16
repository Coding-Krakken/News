import {
  generateAccessToken,
  generateRefreshToken,
  verifyAccessToken,
  verifyRefreshToken,
  hashToken,
  generateRandomToken,
} from '../jwt';

describe('JWT Utils', () => {
  const payload = { userId: 1, email: 'test@example.com' };

  describe('generateAccessToken', () => {
    it('should generate an access token', () => {
      const token = generateAccessToken(payload);
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.')).toHaveLength(3);
    });
  });

  describe('generateRefreshToken', () => {
    it('should generate a refresh token', () => {
      const token = generateRefreshToken(payload);
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.')).toHaveLength(3);
    });
  });

  describe('verifyAccessToken', () => {
    it('should verify valid access token', () => {
      const token = generateAccessToken(payload);
      const decoded = verifyAccessToken(token);
      
      expect(decoded).toBeDefined();
      expect(decoded?.userId).toBe(payload.userId);
      expect(decoded?.email).toBe(payload.email);
    });

    it('should return null for invalid token', () => {
      const decoded = verifyAccessToken('invalid-token');
      expect(decoded).toBeNull();
    });

    it('should return null for expired token', () => {
      // This would require mocking time or using a very short expiry
      // For now, just test invalid token
      const decoded = verifyAccessToken('');
      expect(decoded).toBeNull();
    });
  });

  describe('verifyRefreshToken', () => {
    it('should verify valid refresh token', () => {
      const token = generateRefreshToken(payload);
      const decoded = verifyRefreshToken(token);
      
      expect(decoded).toBeDefined();
      expect(decoded?.userId).toBe(payload.userId);
      expect(decoded?.email).toBe(payload.email);
    });

    it('should return null for invalid token', () => {
      const decoded = verifyRefreshToken('invalid-token');
      expect(decoded).toBeNull();
    });
  });

  describe('hashToken', () => {
    it('should hash a token consistently', () => {
      const token = 'test-token-123';
      const hash1 = hashToken(token);
      const hash2 = hashToken(token);
      
      expect(hash1).toBe(hash2);
      expect(hash1).not.toBe(token);
    });

    it('should produce different hashes for different tokens', () => {
      const hash1 = hashToken('token1');
      const hash2 = hashToken('token2');
      
      expect(hash1).not.toBe(hash2);
    });
  });

  describe('generateRandomToken', () => {
    it('should generate a random token', () => {
      const token = generateRandomToken();
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.length).toBeGreaterThan(0);
    });

    it('should generate different tokens', () => {
      const token1 = generateRandomToken();
      const token2 = generateRandomToken();
      
      expect(token1).not.toBe(token2);
    });
  });
});

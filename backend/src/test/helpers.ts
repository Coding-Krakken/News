import { userRepository } from '../services/user.repository';
import { preferenceRepository } from '../services/preference.repository';
import { bookmarkRepository } from '../services/bookmark.repository';
import { filterRepository } from '../services/filter.repository';
import { tokenRepository } from '../services/token.repository';
import { hashPassword } from '../utils/password';
import { generateAccessToken, generateRefreshToken, hashToken } from '../utils/jwt';
import { User } from '../models/user.model';

export class TestHelpers {
  static async createUser(email = 'test@example.com', password = 'Test1234'): Promise<User> {
    // If a user with this email already exists (e.g. test DB not fully cleaned), return it
    const existing = await userRepository.findByEmail(email);
    if (existing) {
      const pref = await preferenceRepository.findByUserId(existing.id);
      if (!pref) {
        await preferenceRepository.create(existing.id);
      }
      return existing;
    }

    const password_hash = await hashPassword(password);
    const user = await userRepository.create({
      email,
      password,
      password_hash,
      display_name: 'Test User',
    });
    // Ensure preferences exist for the created user
    const pref = await preferenceRepository.findByUserId(user.id);
    if (!pref) {
      await preferenceRepository.create(user.id);
    }
    return user;
  }

  static async createMultipleUsers(count: number): Promise<User[]> {
    const users: User[] = [];
    for (let i = 0; i < count; i++) {
      const user = await this.createUser(`test${i}@example.com`, 'Test1234');
      users.push(user);
    }
    return users;
  }

  static generateAuthTokens(userId: number, email: string) {
    const accessToken = generateAccessToken({ userId, email });
    const refreshToken = generateRefreshToken({ userId, email });
    return { accessToken, refreshToken };
  }

  static async createRefreshToken(userId: number, email: string): Promise<string> {
    const refreshToken = generateRefreshToken({ userId, email });
    const refreshTokenHash = hashToken(refreshToken);
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
    await tokenRepository.create(refreshTokenHash, userId, expiresAt);
    return refreshToken;
  }

  static async createBookmark(userId: number, targetType: 'article' | 'story' = 'article', targetId = 'test-article-1') {
    return await bookmarkRepository.create(userId, {
      target_type: targetType,
      target_id: targetId,
    });
  }

  static async createFilter(userId: number, name = 'Test Filter', filterQuery = { category: 'tech' }) {
    return await filterRepository.create(userId, {
      name,
      filter_query: filterQuery,
    });
  }
}

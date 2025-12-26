import request from 'supertest';
import { createApp } from '../../app';
import { TestHelpers } from '../../test/helpers';

const app = createApp();

describe('Bookmark Integration Tests', () => {
  beforeEach(async () => {
    await TestHelpers.cleanupDatabase();
  });

  afterAll(async () => {
    await TestHelpers.cleanupDatabase();
  });

  describe('POST /api/bookmarks', () => {
    it('should create a bookmark', async () => {
      const user = await TestHelpers.createUser(`bookmark-create-${Date.now()}@example.com`);
      const { accessToken } = TestHelpers.generateAuthTokens(user.id, user.email);

      const response = await request(app)
        .post('/api/bookmarks')
        .set('Authorization', `Bearer ${accessToken}`)
        .send({
          target_type: 'article',
          target_id: `article-${Date.now()}`,
        });

      expect(response.status).toBe(201);
      expect(response.body.bookmark).toBeDefined();
      expect(response.body.bookmark.target_type).toBe('article');
    });

    it('should reject duplicate bookmark', async () => {
      const user = await TestHelpers.createUser(`bookmark-dup-${Date.now()}@example.com`);
      const { accessToken } = TestHelpers.generateAuthTokens(user.id, user.email);
      const targetId = `article-${Date.now()}`;
      
      await TestHelpers.createBookmark(user.id, 'article', targetId);

      const response = await request(app)
        .post('/api/bookmarks')
        .set('Authorization', `Bearer ${accessToken}`)
        .send({
          target_type: 'article',
          target_id: targetId,
        });

      expect(response.status).toBe(409);
    });

    it('should require authentication', async () => {
      const response = await request(app)
        .post('/api/bookmarks')
        .send({
          target_type: 'article',
          target_id: 'article-123',
        });

      expect(response.status).toBe(401);
    });
  });

  describe('GET /api/bookmarks', () => {
    it('should list user bookmarks', async () => {
      const user = await TestHelpers.createUser(`bookmark-list-${Date.now()}@example.com`);
      const { accessToken } = TestHelpers.generateAuthTokens(user.id, user.email);
      
      await TestHelpers.createBookmark(user.id, 'article', `article-${Date.now()}-1`);
      await TestHelpers.createBookmark(user.id, 'story', `story-${Date.now()}-1`);

      const response = await request(app)
        .get('/api/bookmarks')
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body.bookmarks).toBeDefined();
      expect(response.body.bookmarks.length).toBe(2);
    });

    it('should only return user own bookmarks', async () => {
      const timestamp = Date.now();
      const [user1, user2] = await TestHelpers.createMultipleUsers(2);
      const { accessToken } = TestHelpers.generateAuthTokens(user1.id, user1.email);
      
      await TestHelpers.createBookmark(user1.id, 'article', `article-${timestamp}-1`);
      await TestHelpers.createBookmark(user2.id, 'article', `article-${timestamp}-2`);

      const response = await request(app)
        .get('/api/bookmarks')
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body.bookmarks.length).toBe(1);
      expect(response.body.bookmarks[0].user_id).toBe(user1.id);
    });
  });

  describe('DELETE /api/bookmarks/:id', () => {
    it('should delete a bookmark', async () => {
      const user = await TestHelpers.createUser(`bookmark-delete-${Date.now()}@example.com`);
      const { accessToken } = TestHelpers.generateAuthTokens(user.id, user.email);
      const bookmark = await TestHelpers.createBookmark(user.id, 'article', `article-${Date.now()}`);

      const response = await request(app)
        .delete(`/api/bookmarks/${bookmark.id}`)
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
    });

    it('should not delete other user bookmarks', async () => {
      const timestamp = Date.now();
      const [user1, user2] = await TestHelpers.createMultipleUsers(2);
      const { accessToken } = TestHelpers.generateAuthTokens(user1.id, user1.email);
      const bookmark = await TestHelpers.createBookmark(user2.id, 'article', `article-${timestamp}`);

      const response = await request(app)
        .delete(`/api/bookmarks/${bookmark.id}`)
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(403);
    });
  });
});

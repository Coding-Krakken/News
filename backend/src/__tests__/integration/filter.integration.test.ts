import request from 'supertest';
import { createApp } from '../../app';
import { TestHelpers } from '../../test/helpers';

const app = createApp();

describe('Filter Integration Tests', () => {
  describe('POST /api/saved-filters', () => {
    it('should create a saved filter', async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(user.id, user.email);

      const response = await request(app)
        .post('/api/saved-filters')
        .set('Authorization', `Bearer ${accessToken}`)
        .send({
          name: 'Tech News',
          filter_query: { category: 'technology', language: 'en' },
        });

      expect(response.status).toBe(201);
      expect(response.body.filter).toBeDefined();
      expect(response.body.filter.name).toBe('Tech News');
    });

    it('should require authentication', async () => {
      const response = await request(app)
        .post('/api/saved-filters')
        .send({
          name: 'Tech News',
          filter_query: { category: 'technology' },
        });

      expect(response.status).toBe(401);
    });
  });

  describe('GET /api/saved-filters', () => {
    it('should list user saved filters', async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(user.id, user.email);
      
      await TestHelpers.createFilter(user.id, 'Filter 1');
      await TestHelpers.createFilter(user.id, 'Filter 2');

      const response = await request(app)
        .get('/api/saved-filters')
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body.filters).toBeDefined();
      expect(response.body.filters.length).toBe(2);
    });
  });

  describe('PUT /api/saved-filters/:id', () => {
    it('should update a saved filter', async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(user.id, user.email);
      const filter = await TestHelpers.createFilter(user.id);

      const response = await request(app)
        .put(`/api/saved-filters/${filter.id}`)
        .set('Authorization', `Bearer ${accessToken}`)
        .send({
          name: 'Updated Filter',
        });

      expect(response.status).toBe(200);
      expect(response.body.filter.name).toBe('Updated Filter');
    });

    it('should not update other user filters', async () => {
      const [user1, user2] = await TestHelpers.createMultipleUsers(2);
      const { accessToken } = TestHelpers.generateAuthTokens(user1.id, user1.email);
      const filter = await TestHelpers.createFilter(user2.id);

      const response = await request(app)
        .put(`/api/saved-filters/${filter.id}`)
        .set('Authorization', `Bearer ${accessToken}`)
        .send({
          name: 'Updated Filter',
        });

      expect(response.status).toBe(403);
    });
  });

  describe('DELETE /api/saved-filters/:id', () => {
    it('should delete a saved filter', async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(user.id, user.email);
      const filter = await TestHelpers.createFilter(user.id);

      const response = await request(app)
        .delete(`/api/saved-filters/${filter.id}`)
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
    });
  });
});

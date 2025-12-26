import request from "supertest";
import { createApp } from "../../app";
import { TestHelpers } from "../../test/helpers";

const app = createApp();

describe("Bookmark Integration Tests", () => {
  describe("POST /api/bookmarks", () => {
    it("should create a bookmark", async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(
        user.id,
        user.email,
      );

      const response = await request(app)
        .post("/api/bookmarks")
        .set("Authorization", `Bearer ${accessToken}`)
        .send({
          target_type: "article",
          target_id: "article-123",
        });

      expect(response.status).toBe(201);
      expect(response.body.bookmark).toBeDefined();
      expect(response.body.bookmark.target_type).toBe("article");
      expect(response.body.bookmark.target_id).toBe("article-123");
    });

    it("should reject duplicate bookmark", async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(
        user.id,
        user.email,
      );

      await TestHelpers.createBookmark(user.id, "article", "article-123");

      const response = await request(app)
        .post("/api/bookmarks")
        .set("Authorization", `Bearer ${accessToken}`)
        .send({
          target_type: "article",
          target_id: "article-123",
        });

      expect(response.status).toBe(409);
    });

    it("should require authentication", async () => {
      const response = await request(app).post("/api/bookmarks").send({
        target_type: "article",
        target_id: "article-123",
      });

      expect(response.status).toBe(401);
    });
  });

  describe("GET /api/bookmarks", () => {
    it("should list user bookmarks", async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(
        user.id,
        user.email,
      );

      await TestHelpers.createBookmark(user.id, "article", "article-1");
      await TestHelpers.createBookmark(user.id, "story", "story-1");

      const response = await request(app)
        .get("/api/bookmarks")
        .set("Authorization", `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body.bookmarks).toBeDefined();
      expect(response.body.bookmarks.length).toBe(2);
    });

    it("should only return user own bookmarks", async () => {
      const [user1, user2] = await TestHelpers.createMultipleUsers(2);
      const { accessToken } = TestHelpers.generateAuthTokens(
        user1.id,
        user1.email,
      );

      await TestHelpers.createBookmark(user1.id, "article", "article-1");
      await TestHelpers.createBookmark(user2.id, "article", "article-2");

      const response = await request(app)
        .get("/api/bookmarks")
        .set("Authorization", `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body.bookmarks.length).toBe(1);
      expect(response.body.bookmarks[0].user_id).toBe(user1.id);
    });
  });

  describe("DELETE /api/bookmarks/:id", () => {
    it("should delete a bookmark", async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(
        user.id,
        user.email,
      );
      const bookmark = await TestHelpers.createBookmark(user.id);

      const response = await request(app)
        .delete(`/api/bookmarks/${bookmark.id}`)
        .set("Authorization", `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
    });

    it("should not delete other user bookmarks", async () => {
      const [user1, user2] = await TestHelpers.createMultipleUsers(2);
      const { accessToken } = TestHelpers.generateAuthTokens(
        user1.id,
        user1.email,
      );
      const bookmark = await TestHelpers.createBookmark(user2.id);

      const response = await request(app)
        .delete(`/api/bookmarks/${bookmark.id}`)
        .set("Authorization", `Bearer ${accessToken}`);

      expect(response.status).toBe(403);
    });
  });
});

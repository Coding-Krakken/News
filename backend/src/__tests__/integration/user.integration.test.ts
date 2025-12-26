import request from "supertest";
import { createApp } from "../../app";
import { TestHelpers } from "../../test/helpers";

const app = createApp();

describe("User Integration Tests", () => {
  describe("PATCH /api/users/me", () => {
    it("should update user profile", async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(
        user.id,
        user.email,
      );

      const response = await request(app)
        .patch("/api/users/me")
        .set("Authorization", `Bearer ${accessToken}`)
        .send({
          display_name: "Updated Name",
        });

      expect(response.status).toBe(200);
      expect(response.body.user.display_name).toBe("Updated Name");
    });

    it("should require authentication", async () => {
      const response = await request(app).patch("/api/users/me").send({
        display_name: "Updated Name",
      });

      expect(response.status).toBe(401);
    });
  });

  describe("GET /api/users/me/preferences", () => {
    it("should get user preferences", async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(
        user.id,
        user.email,
      );

      const response = await request(app)
        .get("/api/users/me/preferences")
        .set("Authorization", `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body.preferences).toBeDefined();
    });
  });

  describe("PUT /api/users/me/preferences", () => {
    it("should update user preferences", async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(
        user.id,
        user.email,
      );

      const response = await request(app)
        .put("/api/users/me/preferences")
        .set("Authorization", `Bearer ${accessToken}`)
        .send({
          custom_feed_config: { sources: ["bbc", "cnn"] },
          default_filters: { category: "tech" },
          timezone: "America/New_York",
        });

      expect(response.status).toBe(200);
      expect(response.body.preferences).toBeDefined();
      expect(response.body.preferences.timezone).toBe("America/New_York");
    });
  });
});

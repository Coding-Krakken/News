import request from "supertest";
import { createApp } from "../../app";
import { TestHelpers } from "../../test/helpers";

const app = createApp();

describe("Auth Integration Tests", () => {
  describe("POST /api/auth/signup", () => {
    it("should register a new user", async () => {
      const response = await request(app).post("/api/auth/signup").send({
        email: "newuser@example.com",
        password: "Test1234",
        display_name: "New User",
      });

      expect(response.status).toBe(201);
      expect(response.body.user).toBeDefined();
      expect(response.body.user.email).toBe("newuser@example.com");
      expect(response.body.user.display_name).toBe("New User");
      expect(response.body.user.password_hash).toBeUndefined();
      expect(response.body.accessToken).toBeDefined();
      expect(response.body.refreshToken).toBeDefined();
    });

    it("should reject duplicate email", async () => {
      await TestHelpers.createUser("duplicate@example.com");

      const response = await request(app).post("/api/auth/signup").send({
        email: "duplicate@example.com",
        password: "Test1234",
      });

      expect(response.status).toBe(409);
      expect(response.body.error).toBeDefined();
    });

    it("should reject invalid email", async () => {
      const response = await request(app).post("/api/auth/signup").send({
        email: "invalid-email",
        password: "Test1234",
      });

      expect(response.status).toBe(400);
    });

    it("should reject weak password", async () => {
      const response = await request(app).post("/api/auth/signup").send({
        email: "test@example.com",
        password: "weak",
      });

      expect(response.status).toBe(400);
    });
  });

  describe("POST /api/auth/login", () => {
    it("should login with correct credentials", async () => {
      await TestHelpers.createUser("login@example.com", "Test1234");

      const response = await request(app).post("/api/auth/login").send({
        email: "login@example.com",
        password: "Test1234",
      });

      expect(response.status).toBe(200);
      expect(response.body.user).toBeDefined();
      expect(response.body.user.email).toBe("login@example.com");
      expect(response.body.accessToken).toBeDefined();
      expect(response.body.refreshToken).toBeDefined();
    });

    it("should reject incorrect password", async () => {
      await TestHelpers.createUser("test@example.com", "Test1234");

      const response = await request(app).post("/api/auth/login").send({
        email: "test@example.com",
        password: "WrongPassword",
      });

      expect(response.status).toBe(401);
      expect(response.body.error).toBe("Invalid credentials");
    });

    it("should reject non-existent user", async () => {
      const response = await request(app).post("/api/auth/login").send({
        email: "nonexistent@example.com",
        password: "Test1234",
      });

      expect(response.status).toBe(401);
      expect(response.body.error).toBe("Invalid credentials");
    });
  });

  describe("GET /api/auth/me", () => {
    it("should return current user when authenticated", async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(
        user.id,
        user.email,
      );

      const response = await request(app)
        .get("/api/auth/me")
        .set("Authorization", `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body.user).toBeDefined();
      expect(response.body.user.id).toBe(user.id);
      expect(response.body.user.email).toBe(user.email);
    });

    it("should reject unauthenticated request", async () => {
      const response = await request(app).get("/api/auth/me");

      expect(response.status).toBe(401);
    });

    it("should reject invalid token", async () => {
      const response = await request(app)
        .get("/api/auth/me")
        .set("Authorization", "Bearer invalid-token");

      expect(response.status).toBe(401);
    });
  });

  describe("POST /api/auth/logout", () => {
    it("should logout successfully", async () => {
      const user = await TestHelpers.createUser();
      const { accessToken } = TestHelpers.generateAuthTokens(
        user.id,
        user.email,
      );
      const refreshToken = await TestHelpers.createRefreshToken(
        user.id,
        user.email,
      );

      const response = await request(app)
        .post("/api/auth/logout")
        .set("Authorization", `Bearer ${accessToken}`)
        .send({ refreshToken });

      expect(response.status).toBe(200);
      expect(response.body.message).toBeDefined();
    });

    it("should require authentication", async () => {
      const response = await request(app).post("/api/auth/logout");

      expect(response.status).toBe(401);
    });
  });

  describe("POST /api/auth/refresh", () => {
    it("should refresh tokens successfully", async () => {
      const user = await TestHelpers.createUser();
      const refreshToken = await TestHelpers.createRefreshToken(
        user.id,
        user.email,
      );

      const response = await request(app)
        .post("/api/auth/refresh")
        .send({ refreshToken });

      expect(response.status).toBe(200);
      expect(response.body.accessToken).toBeDefined();
      expect(response.body.refreshToken).toBeDefined();
      expect(response.body.refreshToken).not.toBe(refreshToken);
    });

    it("should reject invalid refresh token", async () => {
      const response = await request(app)
        .post("/api/auth/refresh")
        .send({ refreshToken: "invalid-token" });

      expect(response.status).toBe(401);
    });

    it("should reject missing refresh token", async () => {
      const response = await request(app).post("/api/auth/refresh").send({});

      expect(response.status).toBe(401);
    });
  });
});

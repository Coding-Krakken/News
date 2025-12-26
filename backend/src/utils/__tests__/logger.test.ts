import { redactSensitiveData } from "../logger";

describe("Logger Utils", () => {
  describe("redactSensitiveData", () => {
    it("should redact password field", () => {
      const data = { password: "secret123", username: "test" };
      const redacted = redactSensitiveData(data);

      expect(redacted.password).toBe("[REDACTED]");
      expect(redacted.username).toBe("test");
    });

    it("should redact email field", () => {
      const data = { email: "test@example.com", name: "Test" };
      const redacted = redactSensitiveData(data);

      expect(redacted.email).toBe("[REDACTED]");
      expect(redacted.name).toBe("Test");
    });

    it("should redact token field", () => {
      const data = { token: "abc123", data: "value" };
      const redacted = redactSensitiveData(data);

      expect(redacted.token).toBe("[REDACTED]");
      expect(redacted.data).toBe("value");
    });

    it("should redact authorization field", () => {
      const data = { authorization: "Bearer token", data: "value" };
      const redacted = redactSensitiveData(data);

      expect(redacted.authorization).toBe("[REDACTED]");
      expect(redacted.data).toBe("value");
    });

    it("should redact cookie field", () => {
      const data = { cookie: "session=abc", data: "value" };
      const redacted = redactSensitiveData(data);

      expect(redacted.cookie).toBe("[REDACTED]");
      expect(redacted.data).toBe("value");
    });

    it("should handle nested objects", () => {
      const data = {
        user: {
          email: "test@example.com",
          name: "Test",
          auth: { password: "secret" },
        },
      };
      const redacted = redactSensitiveData(data);

      expect(redacted.user.email).toBe("[REDACTED]");
      expect(redacted.user.name).toBe("Test");
      expect(redacted.user.auth.password).toBe("[REDACTED]");
    });

    it("should handle arrays", () => {
      const data = {
        users: [
          { email: "test1@example.com", name: "Test1" },
          { email: "test2@example.com", name: "Test2" },
        ],
      };
      const redacted = redactSensitiveData(data);

      expect(redacted.users[0].email).toBe("[REDACTED]");
      expect(redacted.users[0].name).toBe("Test1");
      expect(redacted.users[1].email).toBe("[REDACTED]");
      expect(redacted.users[1].name).toBe("Test2");
    });

    it("should handle null values", () => {
      const redacted = redactSensitiveData(null);
      expect(redacted).toBeNull();
    });

    it("should handle primitive values", () => {
      expect(redactSensitiveData("string")).toBe("string");
      expect(redactSensitiveData(123)).toBe(123);
      expect(redactSensitiveData(true)).toBe(true);
    });
  });
});

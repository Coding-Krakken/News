import { Response } from "express";
import { AuthRequest } from "../middleware/auth.middleware";
import { userRepository } from "../services/user.repository";
import { tokenRepository } from "../services/token.repository";
import { preferenceRepository } from "../services/preference.repository";
import { hashPassword, verifyPassword } from "../utils/password";
import {
  generateAccessToken,
  generateRefreshToken,
  verifyRefreshToken,
  hashToken,
} from "../utils/jwt";
import { toUserResponse } from "../models/user.model";
import { logger } from "../utils/logger";
import { config } from "../config";

export class AuthController {
  async signup(req: AuthRequest, res: Response): Promise<void> {
    try {
      const { email, password, display_name } = req.body;

      // Check if user already exists
      const existingUser = await userRepository.findByEmail(email);
      if (existingUser) {
        res.status(409).json({ error: "User already exists" });
        return;
      }

      // Hash password
      const password_hash = await hashPassword(password);

      // Create user
      const user = await userRepository.create({
        email,
        password,
        password_hash,
        display_name,
      });

      // Create default preferences
      await preferenceRepository.create(user.id);

      // Generate tokens
      const accessToken = generateAccessToken({
        userId: user.id,
        email: user.email,
      });
      const refreshToken = generateRefreshToken({
        userId: user.id,
        email: user.email,
      });

      // Store refresh token
      const refreshTokenHash = hashToken(refreshToken);
      const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
      await tokenRepository.create(refreshTokenHash, user.id, expiresAt);

      // Set cookies
      res.cookie("accessToken", accessToken, {
        httpOnly: true,
        secure: config.env === "production",
        sameSite: "strict",
        maxAge: 15 * 60 * 1000, // 15 minutes
      });

      res.cookie("refreshToken", refreshToken, {
        httpOnly: true,
        secure: config.env === "production",
        sameSite: "strict",
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      });

      logger.info("User registered successfully", { userId: user.id });

      res.status(201).json({
        user: toUserResponse(user),
        accessToken,
        refreshToken,
      });
    } catch (error) {
      logger.error("Signup error", { error });
      res.status(500).json({ error: "Registration failed" });
    }
  }

  async login(req: AuthRequest, res: Response): Promise<void> {
    try {
      const { email, password } = req.body;

      // Find user
      const user = await userRepository.findByEmail(email);
      if (!user) {
        res.status(401).json({ error: "Invalid credentials" });
        return;
      }

      // Verify password
      const isValid = await verifyPassword(user.password_hash, password);
      if (!isValid) {
        res.status(401).json({ error: "Invalid credentials" });
        return;
      }

      // Generate tokens
      const accessToken = generateAccessToken({
        userId: user.id,
        email: user.email,
      });
      const refreshToken = generateRefreshToken({
        userId: user.id,
        email: user.email,
      });

      // Store refresh token
      const refreshTokenHash = hashToken(refreshToken);
      const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
      await tokenRepository.create(refreshTokenHash, user.id, expiresAt);

      // Set cookies
      res.cookie("accessToken", accessToken, {
        httpOnly: true,
        secure: config.env === "production",
        sameSite: "strict",
        maxAge: 15 * 60 * 1000, // 15 minutes
      });

      res.cookie("refreshToken", refreshToken, {
        httpOnly: true,
        secure: config.env === "production",
        sameSite: "strict",
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      });

      logger.info("User logged in successfully", { userId: user.id });

      res.json({
        user: toUserResponse(user),
        accessToken,
        refreshToken,
      });
    } catch (error) {
      logger.error("Login error", { error });
      res.status(500).json({ error: "Login failed" });
    }
  }

  async logout(req: AuthRequest, res: Response): Promise<void> {
    try {
      const refreshToken = req.cookies?.refreshToken || req.body.refreshToken;

      if (refreshToken) {
        const refreshTokenHash = hashToken(refreshToken);
        await tokenRepository.revoke(refreshTokenHash);
      }

      // Clear cookies
      res.clearCookie("accessToken");
      res.clearCookie("refreshToken");

      logger.info("User logged out successfully", { userId: req.user?.userId });

      res.json({ message: "Logged out successfully" });
    } catch (error) {
      logger.error("Logout error", { error });
      res.status(500).json({ error: "Logout failed" });
    }
  }

  async me(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: "Not authenticated" });
        return;
      }

      const user = await userRepository.findById(req.user.userId);

      if (!user) {
        res.status(404).json({ error: "User not found" });
        return;
      }

      res.json({ user: toUserResponse(user) });
    } catch (error) {
      logger.error("Get current user error", { error });
      res.status(500).json({ error: "Failed to get user" });
    }
  }

  async refresh(req: AuthRequest, res: Response): Promise<void> {
    try {
      const refreshToken = req.cookies?.refreshToken || req.body.refreshToken;

      if (!refreshToken) {
        res.status(401).json({ error: "Refresh token required" });
        return;
      }

      // Verify refresh token
      const payload = verifyRefreshToken(refreshToken);
      if (!payload) {
        res.status(401).json({ error: "Invalid refresh token" });
        return;
      }

      // Check if token exists and not revoked
      const refreshTokenHash = hashToken(refreshToken);
      const storedToken = await tokenRepository.findByHash(refreshTokenHash);

      if (!storedToken || storedToken.revoked_at) {
        res.status(401).json({ error: "Refresh token revoked" });
        return;
      }

      if (new Date(storedToken.expires_at) < new Date()) {
        res.status(401).json({ error: "Refresh token expired" });
        return;
      }

      // Revoke old refresh token
      await tokenRepository.revoke(refreshTokenHash);

      // Generate new tokens
      const accessToken = generateAccessToken({
        userId: payload.userId,
        email: payload.email,
      });
      const newRefreshToken = generateRefreshToken({
        userId: payload.userId,
        email: payload.email,
      });

      // Store new refresh token
      const newRefreshTokenHash = hashToken(newRefreshToken);
      const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
      await tokenRepository.create(
        newRefreshTokenHash,
        payload.userId,
        expiresAt,
      );

      // Set cookies
      res.cookie("accessToken", accessToken, {
        httpOnly: true,
        secure: config.env === "production",
        sameSite: "strict",
        maxAge: 15 * 60 * 1000, // 15 minutes
      });

      res.cookie("refreshToken", newRefreshToken, {
        httpOnly: true,
        secure: config.env === "production",
        sameSite: "strict",
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      });

      logger.info("Token refreshed successfully", { userId: payload.userId });

      res.json({
        accessToken,
        refreshToken: newRefreshToken,
      });
    } catch (error) {
      // Log to console as well to aid test debugging
      // (logger may be silenced during tests)
      // eslint-disable-next-line no-console
      console.error("Refresh token error", error);
      logger.error("Refresh token error", { error });
      res.status(500).json({ error: "Token refresh failed" });
    }
  }
}

export const authController = new AuthController();

import { Response } from "express";
import { AuthRequest } from "../middleware/auth.middleware";
import { preferenceRepository } from "../services/preference.repository";
import { filterRepository } from "../services/filter.repository";
import { logger } from "../utils/logger";

export class FeedController {
  async getCustomFeed(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: "Not authenticated" });
        return;
      }

      // Get user preferences
      const preferences = await preferenceRepository.findByUserId(
        req.user.userId,
      );
      const savedFilters = await filterRepository.findByUserId(req.user.userId);

      // In a real application, this would fetch news based on preferences and filters
      // For now, we return the configuration
      const feedConfig = {
        customFeedConfig: preferences?.custom_feed_config || {},
        defaultFilters: preferences?.default_filters || {},
        savedFilters: savedFilters || [],
        message:
          "This endpoint would return personalized news based on your preferences",
      };

      logger.info("Custom feed accessed", { userId: req.user.userId });

      res.json(feedConfig);
    } catch (error) {
      logger.error("Get custom feed error", { error });
      res.status(500).json({ error: "Failed to get custom feed" });
    }
  }
}

export const feedController = new FeedController();

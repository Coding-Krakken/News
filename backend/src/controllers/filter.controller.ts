import { Response } from "express";
import { AuthRequest } from "../middleware/auth.middleware";
import { filterRepository } from "../services/filter.repository";
import { logger } from "../utils/logger";

export class FilterController {
  async create(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: "Not authenticated" });
        return;
      }

      const { name, filter_query } = req.body;

      const filter = await filterRepository.create(req.user.userId, {
        name,
        filter_query,
      });

      logger.info("Saved filter created", {
        userId: req.user.userId,
        filterId: filter.id,
      });

      res.status(201).json({ filter });
    } catch (error) {
      logger.error("Create filter error", { error });
      res.status(500).json({ error: "Failed to create filter" });
    }
  }

  async list(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: "Not authenticated" });
        return;
      }

      const filters = await filterRepository.findByUserId(req.user.userId);

      res.json({ filters });
    } catch (error) {
      logger.error("List filters error", { error });
      res.status(500).json({ error: "Failed to list filters" });
    }
  }

  async update(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: "Not authenticated" });
        return;
      }

      const { id } = req.params;
      const { name, filter_query } = req.body;

      const existingFilter = await filterRepository.findById(parseInt(id, 10));

      if (!existingFilter) {
        res.status(404).json({ error: "Filter not found" });
        return;
      }

      // Ensure user owns the filter
      if (existingFilter.user_id !== req.user.userId) {
        res.status(403).json({ error: "Forbidden" });
        return;
      }

      const filter = await filterRepository.update(parseInt(id, 10), {
        name,
        filter_query,
      });

      logger.info("Saved filter updated", {
        userId: req.user.userId,
        filterId: id,
      });

      res.json({ filter });
    } catch (error) {
      logger.error("Update filter error", { error });
      res.status(500).json({ error: "Failed to update filter" });
    }
  }

  async delete(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: "Not authenticated" });
        return;
      }

      const { id } = req.params;

      const filter = await filterRepository.findById(parseInt(id, 10));

      if (!filter) {
        res.status(404).json({ error: "Filter not found" });
        return;
      }

      // Ensure user owns the filter
      if (filter.user_id !== req.user.userId) {
        res.status(403).json({ error: "Forbidden" });
        return;
      }

      const deleted = await filterRepository.delete(parseInt(id, 10));

      if (!deleted) {
        res.status(404).json({ error: "Filter not found" });
        return;
      }

      logger.info("Saved filter deleted", {
        userId: req.user.userId,
        filterId: id,
      });

      res.json({ message: "Filter deleted successfully" });
    } catch (error) {
      logger.error("Delete filter error", { error });
      res.status(500).json({ error: "Failed to delete filter" });
    }
  }
}

export const filterController = new FilterController();

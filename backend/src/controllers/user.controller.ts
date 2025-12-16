import { Response } from 'express';
import { AuthRequest } from '../middleware/auth.middleware';
import { userRepository } from '../services/user.repository';
import { preferenceRepository } from '../services/preference.repository';
import { toUserResponse } from '../models/user.model';
import { logger } from '../utils/logger';

export class UserController {
  async updateProfile(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: 'Not authenticated' });
        return;
      }

      const { display_name, avatar_url } = req.body;

      const updatedUser = await userRepository.update(req.user.userId, {
        display_name,
        avatar_url,
      });

      if (!updatedUser) {
        res.status(404).json({ error: 'User not found' });
        return;
      }

      logger.info('User profile updated', { userId: req.user.userId });

      res.json({ user: toUserResponse(updatedUser) });
    } catch (error) {
      logger.error('Update profile error', { error });
      res.status(500).json({ error: 'Failed to update profile' });
    }
  }

  async getPreferences(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: 'Not authenticated' });
        return;
      }

      let preferences = await preferenceRepository.findByUserId(req.user.userId);

      // Create default preferences if they don't exist
      if (!preferences) {
        preferences = await preferenceRepository.create(req.user.userId);
      }

      res.json({ preferences });
    } catch (error) {
      logger.error('Get preferences error', { error });
      res.status(500).json({ error: 'Failed to get preferences' });
    }
  }

  async updatePreferences(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: 'Not authenticated' });
        return;
      }

      const { custom_feed_config, default_filters, timezone } = req.body;

      const preferences = await preferenceRepository.upsert(req.user.userId, {
        custom_feed_config,
        default_filters,
        timezone,
      });

      logger.info('User preferences updated', { userId: req.user.userId });

      res.json({ preferences });
    } catch (error) {
      logger.error('Update preferences error', { error });
      res.status(500).json({ error: 'Failed to update preferences' });
    }
  }
}

export const userController = new UserController();

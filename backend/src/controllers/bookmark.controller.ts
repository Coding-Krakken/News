import { Response } from 'express';
import { AuthRequest } from '../middleware/auth.middleware';
import { bookmarkRepository } from '../services/bookmark.repository';
import { logger } from '../utils/logger';

export class BookmarkController {
  async create(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: 'Not authenticated' });
        return;
      }

      const { target_type, target_id } = req.body;

      // Check if bookmark already exists
      const existing = await bookmarkRepository.findByTarget(
        req.user.userId,
        target_type,
        target_id
      );

      if (existing) {
        res.status(409).json({ error: 'Bookmark already exists' });
        return;
      }

      const bookmark = await bookmarkRepository.create(req.user.userId, {
        target_type,
        target_id,
      });

      logger.info('Bookmark created', { 
        userId: req.user.userId,
        bookmarkId: bookmark.id 
      });

      res.status(201).json({ bookmark });
    } catch (error) {
      logger.error('Create bookmark error', { error });
      res.status(500).json({ error: 'Failed to create bookmark' });
    }
  }

  async list(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: 'Not authenticated' });
        return;
      }

      const bookmarks = await bookmarkRepository.findByUserId(req.user.userId);

      res.json({ bookmarks });
    } catch (error) {
      logger.error('List bookmarks error', { error });
      res.status(500).json({ error: 'Failed to list bookmarks' });
    }
  }

  async delete(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.user) {
        res.status(401).json({ error: 'Not authenticated' });
        return;
      }

      const { id } = req.params;
      const { target_type, target_id } = req.query;

      let deleted = false;

      // Delete by ID
      if (id) {
        const bookmark = await bookmarkRepository.findById(parseInt(id, 10));
        
        if (!bookmark) {
          res.status(404).json({ error: 'Bookmark not found' });
          return;
        }

        // Ensure user owns the bookmark
        if (bookmark.user_id !== req.user.userId) {
          res.status(403).json({ error: 'Forbidden' });
          return;
        }

        deleted = await bookmarkRepository.delete(parseInt(id, 10));
      } 
      // Delete by target
      else if (target_type && target_id) {
        deleted = await bookmarkRepository.deleteByTarget(
          req.user.userId,
          target_type as string,
          target_id as string
        );
      } else {
        res.status(400).json({ error: 'Either id or target_type and target_id are required' });
        return;
      }

      if (!deleted) {
        res.status(404).json({ error: 'Bookmark not found' });
        return;
      }

      logger.info('Bookmark deleted', { userId: req.user.userId });

      res.json({ message: 'Bookmark deleted successfully' });
    } catch (error) {
      logger.error('Delete bookmark error', { error });
      res.status(500).json({ error: 'Failed to delete bookmark' });
    }
  }
}

export const bookmarkController = new BookmarkController();

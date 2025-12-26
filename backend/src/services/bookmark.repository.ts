import { query } from '../config/database';
import { Bookmark, CreateBookmarkDto } from '../models/bookmark.model';

export class BookmarkRepository {
  async create(userId: number, bookmarkData: CreateBookmarkDto): Promise<Bookmark> {
    const result = await query(
      `INSERT INTO bookmarks (user_id, target_type, target_id)
       VALUES ($1, $2, $3)
       RETURNING *`,
      [userId, bookmarkData.target_type, bookmarkData.target_id]
    );
    return result.rows[0];
  }

  async findByUserId(userId: number): Promise<Bookmark[]> {
    const result = await query(
      'SELECT * FROM bookmarks WHERE user_id = $1 ORDER BY created_at DESC',
      [userId]
    );
    return result.rows;
  }

  async findById(id: number): Promise<Bookmark | null> {
    const result = await query(
      'SELECT * FROM bookmarks WHERE id = $1',
      [id]
    );
    return result.rows[0] || null;
  }

  async findByTarget(userId: number, targetType: string, targetId: string): Promise<Bookmark | null> {
    const result = await query(
      'SELECT * FROM bookmarks WHERE user_id = $1 AND target_type = $2 AND target_id = $3',
      [userId, targetType, targetId]
    );
    return result.rows[0] || null;
  }

  async delete(id: number): Promise<boolean> {
    const result = await query(
      'DELETE FROM bookmarks WHERE id = $1',
      [id]
    );
    return result.rowCount !== null && result.rowCount > 0;
  }

  async deleteByTarget(userId: number, targetType: string, targetId: string): Promise<boolean> {
    const result = await query(
      'DELETE FROM bookmarks WHERE user_id = $1 AND target_type = $2 AND target_id = $3',
      [userId, targetType, targetId]
    );
    return result.rowCount !== null && result.rowCount > 0;
  }

  async deleteAll(): Promise<number> {
    const result = await query('DELETE FROM bookmarks');
    return result.rowCount || 0;
  }
}

export const bookmarkRepository = new BookmarkRepository();

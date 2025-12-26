import { query } from '../config/database';
import { UserPreference, UpdatePreferencesDto } from '../models/preference.model';

export class PreferenceRepository {
  async findByUserId(userId: number): Promise<UserPreference | null> {
    const result = await query(
      'SELECT * FROM user_preferences WHERE user_id = $1',
      [userId]
    );
    return result.rows[0] || null;
  }

  async create(userId: number): Promise<UserPreference> {
    const result = await query(
      `INSERT INTO user_preferences (user_id)
       VALUES ($1)
       RETURNING *`,
      [userId]
    );
    return result.rows[0];
  }

  async update(userId: number, preferences: UpdatePreferencesDto): Promise<UserPreference | null> {
    const fields: string[] = [];
    const values: any[] = [];
    let paramCount = 1;

    if (preferences.custom_feed_config !== undefined) {
      fields.push(`custom_feed_config = $${paramCount}`);
      values.push(JSON.stringify(preferences.custom_feed_config));
      paramCount++;
    }

    if (preferences.default_filters !== undefined) {
      fields.push(`default_filters = $${paramCount}`);
      values.push(JSON.stringify(preferences.default_filters));
      paramCount++;
    }

    if (preferences.timezone !== undefined) {
      fields.push(`timezone = $${paramCount}`);
      values.push(preferences.timezone);
      paramCount++;
    }

    if (fields.length === 0) {
      return await this.findByUserId(userId);
    }

    values.push(userId);

    const result = await query(
      `UPDATE user_preferences SET ${fields.join(', ')} WHERE user_id = $${paramCount} RETURNING *`,
      values
    );

    return result.rows[0] || null;
  }

  async upsert(userId: number, preferences: UpdatePreferencesDto): Promise<UserPreference> {
    const existing = await this.findByUserId(userId);
    
    if (existing) {
      return (await this.update(userId, preferences))!;
    } else {
      const created = await this.create(userId);
      return (await this.update(userId, preferences)) || created;
    }
  }

  async deleteAll(): Promise<number> {
    const result = await query('DELETE FROM user_preferences');
    return result.rowCount || 0;
  }
}

export const preferenceRepository = new PreferenceRepository();

import { query } from '../config/database';
import { SavedFilter, CreateSavedFilterDto, UpdateSavedFilterDto } from '../models/filter.model';

export class FilterRepository {
  async create(userId: number, filterData: CreateSavedFilterDto): Promise<SavedFilter> {
    const result = await query(
      `INSERT INTO saved_filters (user_id, name, filter_query)
       VALUES ($1, $2, $3)
       RETURNING *`,
      [userId, filterData.name, JSON.stringify(filterData.filter_query)]
    );
    return result.rows[0];
  }

  async findByUserId(userId: number): Promise<SavedFilter[]> {
    const result = await query(
      'SELECT * FROM saved_filters WHERE user_id = $1 ORDER BY created_at DESC',
      [userId]
    );
    return result.rows;
  }

  async findById(id: number): Promise<SavedFilter | null> {
    const result = await query(
      'SELECT * FROM saved_filters WHERE id = $1',
      [id]
    );
    return result.rows[0] || null;
  }

  async update(id: number, filterData: UpdateSavedFilterDto): Promise<SavedFilter | null> {
    const fields: string[] = [];
    const values: any[] = [];
    let paramCount = 1;

    if (filterData.name !== undefined) {
      fields.push(`name = $${paramCount}`);
      values.push(filterData.name);
      paramCount++;
    }

    if (filterData.filter_query !== undefined) {
      fields.push(`filter_query = $${paramCount}`);
      values.push(JSON.stringify(filterData.filter_query));
      paramCount++;
    }

    if (fields.length === 0) {
      return await this.findById(id);
    }

    values.push(id);

    const result = await query(
      `UPDATE saved_filters SET ${fields.join(', ')} WHERE id = $${paramCount} RETURNING *`,
      values
    );

    return result.rows[0] || null;
  }

  async delete(id: number): Promise<boolean> {
    const result = await query(
      'DELETE FROM saved_filters WHERE id = $1',
      [id]
    );
    return result.rowCount !== null && result.rowCount > 0;
  }
}

export const filterRepository = new FilterRepository();

import { query } from "../config/database";
import { User, CreateUserDto, UpdateUserDto } from "../models/user.model";

export class UserRepository {
  async create(
    userData: CreateUserDto & { password_hash: string },
  ): Promise<User> {
    const result = await query(
      `INSERT INTO users (email, password_hash, display_name)
       VALUES ($1, $2, $3)
       RETURNING *`,
      [userData.email, userData.password_hash, userData.display_name || null],
    );
    return result.rows[0];
  }

  async findByEmail(email: string): Promise<User | null> {
    const result = await query("SELECT * FROM users WHERE email = $1", [email]);
    return result.rows[0] || null;
  }

  async findById(id: number): Promise<User | null> {
    const result = await query("SELECT * FROM users WHERE id = $1", [id]);
    return result.rows[0] || null;
  }

  async update(id: number, userData: UpdateUserDto): Promise<User | null> {
    const fields: string[] = [];
    const values: any[] = [];
    let paramCount = 1;

    if (userData.display_name !== undefined) {
      fields.push(`display_name = $${paramCount}`);
      values.push(userData.display_name);
      paramCount++;
    }

    if (userData.avatar_url !== undefined) {
      fields.push(`avatar_url = $${paramCount}`);
      values.push(userData.avatar_url);
      paramCount++;
    }

    if (fields.length === 0) {
      return await this.findById(id);
    }

    values.push(id);

    const result = await query(
      `UPDATE users SET ${fields.join(", ")} WHERE id = $${paramCount} RETURNING *`,
      values,
    );

    return result.rows[0] || null;
  }

  async delete(id: number): Promise<boolean> {
    const result = await query("DELETE FROM users WHERE id = $1", [id]);
    return result.rowCount !== null && result.rowCount > 0;
  }
}

export const userRepository = new UserRepository();

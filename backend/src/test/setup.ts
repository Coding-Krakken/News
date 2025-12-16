import { pool, query } from '../config/database';
import fs from 'fs';
import path from 'path';

// Setup test database
beforeAll(async () => {
  // Run migrations
  const migrationsDir = path.join(__dirname, '../../migrations');
  const migrationFiles = fs.readdirSync(migrationsDir).sort();

  for (const file of migrationFiles) {
    const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf8');
    await query(sql);
  }
});

// Clean up after each test
afterEach(async () => {
  await query('TRUNCATE TABLE refresh_tokens, saved_filters, bookmarks, user_preferences, users RESTART IDENTITY CASCADE');
});

// Close database connection
afterAll(async () => {
  await pool.end();
});

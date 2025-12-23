import * as db from '../config/database';
import fs from 'fs';
import path from 'path';

// Setup test database
beforeAll(async () => {
  // Check DB availability and run migrations if available
  const connected = await db.testConnection();
  if (!connected) {
    // Mock query and pool.end to allow tests to run without a real Postgres instance
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (db as any).query = async () => ({ rowCount: 0, rows: [] });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (db as any).pool = { end: async () => {} } as any;
    console.warn('Test database not available — skipping migrations and using mocked DB.');
    return;
  }

  // Run migrations once per test run
  // Use a global flag to avoid applying migrations multiple times across suites
  if (!(global as any).__migrations_applied) {
    const migrationsDir = path.join(__dirname, '../../migrations');
    const migrationFiles = fs.readdirSync(migrationsDir).sort();

    for (const file of migrationFiles) {
      const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf8');
      try {
        await db.query(sql);
      } catch (err: any) {
        // Ignore errors about existing relations/indexes so migrations are idempotent
        const msg = (err && err.message) || '';
        if (msg.includes('already exists') || (err.code && err.code === '42P07')) {
          // already exists - safe to ignore in test runs
          continue;
        }
        throw err;
      }
    }

    (global as any).__migrations_applied = true;
  }
});

// Clean up after each test
afterEach(async () => {
  await db.query('TRUNCATE TABLE refresh_tokens, saved_filters, bookmarks, user_preferences, users RESTART IDENTITY CASCADE');
});

// Close database connection
afterAll(async () => {
  await db.pool.end();
});

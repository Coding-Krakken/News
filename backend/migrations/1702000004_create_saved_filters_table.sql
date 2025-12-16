-- Migration: create_saved_filters_table
-- Created at: 2025-12-16

CREATE TABLE IF NOT EXISTS saved_filters (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  filter_query JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_saved_filters_user_id ON saved_filters(user_id);

CREATE TRIGGER update_saved_filters_updated_at BEFORE UPDATE ON saved_filters
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

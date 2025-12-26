export interface SavedFilter {
  id: number;
  user_id: number;
  name: string;
  filter_query: Record<string, any>;
  created_at: Date;
  updated_at: Date;
}

export interface CreateSavedFilterDto {
  name: string;
  filter_query: Record<string, any>;
}

export interface UpdateSavedFilterDto {
  name?: string;
  filter_query?: Record<string, any>;
}

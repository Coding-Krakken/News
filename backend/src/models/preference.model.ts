export interface UserPreference {
  id: number;
  user_id: number;
  custom_feed_config: Record<string, any>;
  default_filters: Record<string, any>;
  timezone: string;
  created_at: Date;
  updated_at: Date;
}

export interface UpdatePreferencesDto {
  custom_feed_config?: Record<string, any>;
  default_filters?: Record<string, any>;
  timezone?: string;
}

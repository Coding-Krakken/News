export interface User {
  id: number;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserPreference {
  id: number;
  user_id: number;
  custom_feed_config: Record<string, any>;
  default_filters: Record<string, any>;
  timezone: string;
  created_at: string;
  updated_at: string;
}

export interface Bookmark {
  id: number;
  user_id: number;
  target_type: 'article' | 'story';
  target_id: string;
  created_at: string;
}

export interface SavedFilter {
  id: number;
  user_id: number;
  name: string;
  filter_query: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  display_name?: string;
}

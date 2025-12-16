export interface User {
  id: number;
  email: string;
  password_hash: string;
  display_name: string | null;
  avatar_url: string | null;
  created_at: Date;
  updated_at: Date;
}

export interface CreateUserDto {
  email: string;
  password: string;
  display_name?: string;
}

export interface UpdateUserDto {
  display_name?: string;
  avatar_url?: string;
}

export interface UserResponse {
  id: number;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
  created_at: Date;
  updated_at: Date;
}

export function toUserResponse(user: User): UserResponse {
  const { password_hash, ...userResponse } = user;
  return userResponse;
}

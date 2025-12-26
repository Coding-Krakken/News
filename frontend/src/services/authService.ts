import { apiClient } from './apiClient';
import { User, AuthResponse, LoginRequest, SignupRequest } from '../types';

export const authService = {
  async signup(data: SignupRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/signup', data);
    apiClient.setAccessToken(response.data.accessToken);
    apiClient.setRefreshToken(response.data.refreshToken);
    return response.data;
  },

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', data);
    apiClient.setAccessToken(response.data.accessToken);
    apiClient.setRefreshToken(response.data.refreshToken);
    return response.data;
  },

  async logout(): Promise<void> {
    await apiClient.post('/auth/logout');
    apiClient.clearTokens();
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<{ user: User }>('/auth/me');
    return response.data.user;
  },
};

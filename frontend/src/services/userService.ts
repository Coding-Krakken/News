import { apiClient } from "./apiClient";
import { User, UserPreference } from "../types";

export const userService = {
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await apiClient.patch<{ user: User }>("/users/me", data);
    return response.data.user;
  },

  async getPreferences(): Promise<UserPreference> {
    const response = await apiClient.get<{ preferences: UserPreference }>(
      "/users/me/preferences",
    );
    return response.data.preferences;
  },

  async updatePreferences(
    data: Partial<UserPreference>,
  ): Promise<UserPreference> {
    const response = await apiClient.put<{ preferences: UserPreference }>(
      "/users/me/preferences",
      data,
    );
    return response.data.preferences;
  },
};

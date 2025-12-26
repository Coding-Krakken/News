import { apiClient } from "./apiClient";
import { Bookmark } from "../types";

export const bookmarkService = {
  async create(
    targetType: "article" | "story",
    targetId: string,
  ): Promise<Bookmark> {
    const response = await apiClient.post<{ bookmark: Bookmark }>(
      "/bookmarks",
      {
        target_type: targetType,
        target_id: targetId,
      },
    );
    return response.data.bookmark;
  },

  async list(): Promise<Bookmark[]> {
    const response = await apiClient.get<{ bookmarks: Bookmark[] }>(
      "/bookmarks",
    );
    return response.data.bookmarks;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/bookmarks/${id}`);
  },

  async deleteByTarget(targetType: string, targetId: string): Promise<void> {
    await apiClient.delete(
      `/bookmarks?target_type=${targetType}&target_id=${targetId}`,
    );
  },
};

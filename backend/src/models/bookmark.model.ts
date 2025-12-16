export interface Bookmark {
  id: number;
  user_id: number;
  target_type: 'article' | 'story';
  target_id: string;
  created_at: Date;
}

export interface CreateBookmarkDto {
  target_type: 'article' | 'story';
  target_id: string;
}

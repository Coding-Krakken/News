import React, { useState, useEffect } from 'react';
import { bookmarkService } from '../services/bookmarkService';
import { Bookmark } from '../types';

export function BookmarksPage() {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadBookmarks();
  }, []);

  const loadBookmarks = async () => {
    try {
      const data = await bookmarkService.list();
      setBookmarks(data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load bookmarks');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await bookmarkService.delete(id);
      setBookmarks(bookmarks.filter(b => b.id !== id));
    } catch (err: any) {
      alert('Failed to delete bookmark');
    }
  };

  if (loading) {
    return <div>Loading bookmarks...</div>;
  }

  return (
    <div className="bookmarks-page">
      <h1>My Bookmarks</h1>
      {error && <div className="error">{error}</div>}
      
      {bookmarks.length === 0 ? (
        <p>No bookmarks yet</p>
      ) : (
        <ul>
          {bookmarks.map(bookmark => (
            <li key={bookmark.id}>
              <span>
                {bookmark.target_type}: {bookmark.target_id}
              </span>
              <button onClick={() => handleDelete(bookmark.id)}>Remove</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

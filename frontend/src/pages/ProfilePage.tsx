import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/userService';

export function ProfilePage() {
  const { user } = useAuth();
  const [displayName, setDisplayName] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('');
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user) {
      setDisplayName(user.display_name || '');
      setAvatarUrl(user.avatar_url || '');
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await userService.updateProfile({
        display_name: displayName || null,
        avatar_url: avatarUrl || null,
      });
      setSuccess('Profile updated successfully');
      setEditing(false);
    } catch (err: unknown) {
      type ErrorResponse = { response?: { data?: { error?: string } } };
      const msg = (err as ErrorResponse)?.response?.data?.error || 'Failed to update profile';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="profile-page">
      <h1>Profile</h1>
      
      {!editing ? (
        <div>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Display Name:</strong> {user.display_name || 'Not set'}</p>
          <p><strong>Avatar URL:</strong> {user.avatar_url || 'Not set'}</p>
          <button onClick={() => setEditing(true)}>Edit Profile</button>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="displayName">Display Name:</label>
            <input
              id="displayName"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              disabled={loading}
            />
          </div>
          <div>
            <label htmlFor="avatarUrl">Avatar URL:</label>
            <input
              id="avatarUrl"
              type="url"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              disabled={loading}
            />
          </div>
          {error && <div className="error">{error}</div>}
          {success && <div className="success">{success}</div>}
          <button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Save'}
          </button>
          <button type="button" onClick={() => setEditing(false)} disabled={loading}>
            Cancel
          </button>
        </form>
      )}
    </div>
  );
}

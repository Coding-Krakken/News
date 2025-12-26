import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function HomePage() {
  const { user } = useAuth();

  return (
    <div className="home-page">
      <h1>Welcome to News App</h1>
      {user ? (
        <div>
          <p>Hello, {user.display_name || user.email}!</p>
          <nav>
            <ul>
              <li><Link to="/profile">My Profile</Link></li>
              <li><Link to="/bookmarks">My Bookmarks</Link></li>
              <li><Link to="/filters">Saved Filters</Link></li>
            </ul>
          </nav>
        </div>
      ) : (
        <div>
          <p>Please <Link to="/login">login</Link> or <Link to="/signup">sign up</Link> to continue.</p>
        </div>
      )}
    </div>
  );
}

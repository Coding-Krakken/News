import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';

// We'll mock authService to control `getCurrentUser` behavior
jest.mock('../services/authService', () => ({
  authService: {
    getCurrentUser: jest.fn(),
    login: jest.fn(),
    signup: jest.fn(),
    logout: jest.fn(),
  },
}));

import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';

function TestConsumer() {
  const { loading, isAuthenticated, user } = useAuth();
  return (
    <div>
      <div>loading:{String(loading)}</div>
      <div>authenticated:{String(isAuthenticated)}</div>
      <div>user:{user ? user.email : 'null'}</div>
    </div>
  );
}

describe('AuthProvider', () => {
  afterEach(() => jest.clearAllMocks());

  it('sets user when getCurrentUser succeeds', async () => {
    (authService.getCurrentUser as jest.Mock).mockResolvedValue({ id: 1, email: 'a@a' });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => expect(screen.getByText(/loading:false/)).toBeInTheDocument());
    expect(screen.getByText(/authenticated:true/)).toBeInTheDocument();
    expect(screen.getByText(/user:a@a/)).toBeInTheDocument();
  });

  it('handles getCurrentUser failure and sets unauthenticated', async () => {
    (authService.getCurrentUser as jest.Mock).mockRejectedValue(new Error('nope'));

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => expect(screen.getByText(/loading:false/)).toBeInTheDocument());
    expect(screen.getByText(/authenticated:false/)).toBeInTheDocument();
    expect(screen.getByText(/user:null/)).toBeInTheDocument();
  });
});

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';

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

function ActionConsumer() {
  const { user, login, signup, logout } = useAuth();
  return (
    <div>
      <div>user:{user ? user.email : 'null'}</div>
      <button onClick={() => login({ email: 'a@a', password: 'p' } as any)}>login</button>
      <button onClick={() => signup({ email: 'b@b', password: 'p' } as any)}>signup</button>
      <button onClick={() => logout()}>logout</button>
    </div>
  );
}

describe('AuthContext actions', () => {
  afterEach(() => jest.clearAllMocks());

  it('throws when useAuth used outside provider', () => {
    function Comp() {
      useAuth();
      return <div />;
    }

    expect(() => render(<Comp />)).toThrow('useAuth must be used within an AuthProvider');
  });

  it('login sets user', async () => {
    (authService.login as jest.Mock).mockResolvedValue({ user: { email: 'a@a' } });

    render(
      <AuthProvider>
        <ActionConsumer />
      </AuthProvider>
    );

    fireEvent.click(screen.getByText('login'));
    await waitFor(() => expect(screen.getByText(/user:a@a/)).toBeInTheDocument());
  });

  it('signup sets user', async () => {
    (authService.signup as jest.Mock).mockResolvedValue({ user: { email: 'b@b' } });

    render(
      <AuthProvider>
        <ActionConsumer />
      </AuthProvider>
    );

    fireEvent.click(screen.getByText('signup'));
    await waitFor(() => expect(screen.getByText(/user:b@b/)).toBeInTheDocument());
  });

  it('logout clears user', async () => {
    (authService.logout as jest.Mock).mockResolvedValue(undefined);
    (authService.login as jest.Mock).mockResolvedValue({ user: { email: 'x@x' } });

    render(
      <AuthProvider>
        <ActionConsumer />
      </AuthProvider>
    );

    fireEvent.click(screen.getByText('login'));
    await waitFor(() => expect(screen.getByText(/user:x@x/)).toBeInTheDocument());

    fireEvent.click(screen.getByText('logout'));
    await waitFor(() => expect(screen.getByText(/user:null/)).toBeInTheDocument());
  });
});

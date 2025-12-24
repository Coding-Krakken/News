import React from 'react';
// Stub Navigate and useLocation to observe behavior
jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    Navigate: ({ to, state }: any) => <div data-testid="navigate">redirect:{to}</div>,
    useLocation: () => ({ pathname: '/protected' }),
  };
});

import { render, screen } from '@testing-library/react';

describe('ProtectedRoute', () => {
  it('shows loading while auth is loading', () => {
    jest.isolateModules(() => {
      jest.doMock('../contexts/AuthContext', () => ({ useAuth: () => ({ loading: true, isAuthenticated: false }) }));
      const { ProtectedRoute } = require('../components/ProtectedRoute');
      render(
        // @ts-ignore
        <ProtectedRoute>
          <div>secret</div>
        </ProtectedRoute>
      );
      expect(screen.getByText(/Loading.../i)).toBeInTheDocument();
    });
  });

  it('redirects when not authenticated', () => {
    jest.isolateModules(() => {
      jest.doMock('../contexts/AuthContext', () => ({ useAuth: () => ({ loading: false, isAuthenticated: false }) }));
      const { ProtectedRoute } = require('../components/ProtectedRoute');
      render(
        // @ts-ignore
        <ProtectedRoute>
          <div>secret</div>
        </ProtectedRoute>
      );
      expect(screen.getByTestId('navigate')).toHaveTextContent('redirect:/login');
    });
  });

  it('renders children when authenticated', () => {
    jest.isolateModules(() => {
      jest.doMock('../contexts/AuthContext', () => ({ useAuth: () => ({ loading: false, isAuthenticated: true }) }));
      const { ProtectedRoute } = require('../components/ProtectedRoute');
      render(
        // @ts-ignore
        <ProtectedRoute>
          <div>secret</div>
        </ProtectedRoute>
      );
      expect(screen.getByText('secret')).toBeInTheDocument();
    });
  });
});

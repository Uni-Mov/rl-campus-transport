import { renderHook, act, waitFor } from '@testing-library/react';
import { test, describe, expect, vi } from 'vitest';
import { useAuth } from '../hooks/useAuth';
 // mockeamos la api de auth
vi.mock('../api/auth-api', () => ({
  login: vi.fn().mockResolvedValue("token"),
  register: vi.fn().mockResolvedValue("token"),
  logout: vi.fn().mockResolvedValue(undefined),
}));

describe('useAuth hook', () => {
  test('inicialmente el usuario no está autenticado', async () => {
    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current.isLoggedIn).toBe(false);
    });
  });

test('login', async () => {
const { result } = renderHook(() => useAuth());
 await act(async () => {
     await result.current.login();
    });
    expect(result.current.isLoggedIn).toBe(true);
});

test('logout', async () => {
const { result } = renderHook(() => useAuth());
 await act(async () => {
     await result.current.logout();
    });
    expect(result.current.isLoggedIn).toBe(false);
});

test('register', async () => {
const { result } = renderHook(() => useAuth());
 await act(async () => {
     await result.current.register("example@example.com", "secret_password");
    });
    expect(result.current.isLoggedIn).toBe(false);
});

});

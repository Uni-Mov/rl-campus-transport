import { renderHook, act, waitFor } from '@testing-library/react';
import { test, describe, expect, vi } from 'vitest';
import { useAuth } from '../hooks/useAuth';

// mockeamos la api de auth
vi.mock('../api/auth-api', () => ({
    login: vi.fn().mockResolvedValue("test-token"),
    register: vi.fn().mockResolvedValue("test-token"),
    logout: vi.fn().mockResolvedValue(undefined),
}));

describe('useAuth hook', () => {
    test('inicialmente el usuario no está autenticado', () => {
        const { result } = renderHook(() => useAuth());
        expect(result.current.isLoggedIn).toBe(false);
    });

    test('login exitoso', async () => {
        const { result } = renderHook(() => useAuth());

        await act(async () => {
            await result.current.login("test@example.com", "password");
        });

        expect(result.current.isLoggedIn).toBe(true);
        expect(localStorage.getItem("authToken")).toBe("test-token");
    });
    
    test('register exitoso', async () => {
        const { result } = renderHook(() => useAuth());
        
        await act(async () => {
            await result.current.register(
                "sebastian",
                "driussi", 
                "12345678",
                "sebadriussi@example.com",
                "password",
                "PASSENGER"
            );
        });
        
        expect(result.current.isLoggedIn).toBe(true);
    });
    
    test('logout exitoso', async () => {
        const { result } = renderHook(() => useAuth());
        
        await act(async () => {
            await result.current.logout();
        });
        
        expect(result.current.isLoggedIn).toBe(false);
        expect(localStorage.getItem("authToken")).toBeNull();
    });

});

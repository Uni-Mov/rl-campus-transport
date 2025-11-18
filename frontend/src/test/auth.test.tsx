import { renderHook, act } from '@testing-library/react';
import { test, describe, expect, vi, beforeEach } from 'vitest';
import { useAuth } from '../hooks/useAuth';
import * as authApi from '@/api/auth-api';

vi.mock('react-router-dom', () => ({
    useNavigate: () => vi.fn(),
}));

// mockeamos la api de auth
vi.mock('@/api/auth-api', () => ({
    login: vi.fn().mockResolvedValue("test-token"),
    register: vi.fn().mockResolvedValue("test-token"),
    logout: vi.fn().mockResolvedValue(undefined),
}));

describe('useAuth hook', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

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
                "passenger"
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

    test('manejo de errores en login (rechaza promesa y no cambia estado)', async () => {
        (authApi.login as unknown as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error("Login failed"));
        const { result } = renderHook(() => useAuth());
        
        try {
            await act(async () => {
                await result.current.login("test@example.com", "password");
            });
        } catch (_) {

        }
        
        expect(result.current.isLoggedIn).toBe(false);
        expect(localStorage.getItem("authToken")).toBeNull();
    });

    test('manejo de errores en register (rechaza promesa y no cambia estado)', async () => {
        (authApi.register as unknown as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error("Register failed"));
        const { result } = renderHook(() => useAuth());
        
        try {
            await act(async () => {
                await result.current.register("sebastian", "driussi", "12345678", "sebadriussi@example.com", "password", "passenger");
            });
        } catch (_) {
        
        }
        
        expect(result.current.isLoggedIn).toBe(false);
        expect(localStorage.getItem("authToken")).toBeNull();
    });
    
});

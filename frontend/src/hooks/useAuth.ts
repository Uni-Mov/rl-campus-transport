import { useState, useEffect } from "react";
import { register as api_register, login as api_login, logout as api_logout } from "../api/auth-api";

export const useAuth = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
    useEffect(() => {
        const token = localStorage.getItem("authToken");
        setIsLoggedIn(!!token);
        setLoading(false);
    }
    , []);

    const login = async (email: string, password: string) => {
        try {
            setError(null);
            const token = await api_login(email, password);
            localStorage.setItem("authToken", token as string);
            setIsLoggedIn(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred during login");
            throw err;
        }
    };
    
    const register = async (
        firstname: string, 
        lastname : string,
        dni:string, 
        email: string, 
        password: string,
        role: string
    ) => {
        try {
            setError(null);
            await api_register(firstname, lastname, dni, email, password, role);
            setIsLoggedIn(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred during registration");
            throw err;
        }
    };

    const logout = async () => {
        try {
            setError(null);
            await api_logout();
            setIsLoggedIn(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred during logout");
            throw err;
        }
    };
    
    return { isLoggedIn, loading, error, login, logout, register };

};
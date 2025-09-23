import { useState, useEffect } from "react";
import { register as api_register, login as api_login, logout as api_logout } from "../api/auth-api";
export const useAuth = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        const token = localStorage.getItem("authToken");
        setIsLoggedIn(!!token);
        setLoading(false);
    }
    , []);

    const login = () => {
        const token = "hola soy un token";
        localStorage.setItem("authToken", token);
        setIsLoggedIn(true);
    }

    const logout = () => {
        api_logout();
        localStorage.removeItem("authToken");
        setIsLoggedIn(false);
    }

    const register = async (user: string, password: string) => {
        const res = await api_register(user, password);
        localStorage.setItem("authToken", res);
        setIsLoggedIn(true);
    }
    
    return { isLoggedIn, loading, login, logout, register };

};
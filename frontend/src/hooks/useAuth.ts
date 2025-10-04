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
        api_login("", "");
        const token = "hola soy un token";
        localStorage.setItem("authToken", token);
        setIsLoggedIn(true);
    }

    const logout = () => {
        api_logout();
        localStorage.removeItem("authToken");
        setIsLoggedIn(false);
    }

    const register = async (name: string, lastname : string, email: string, password: string): Promise<boolean> => {
        try {
            const res = await api_register(name, lastname, email, password);
            localStorage.setItem("authToken", res);
            setIsLoggedIn(true);
            return true;
        } catch (res) {
           return false;
        }
    }
    
    return { isLoggedIn, loading, login, logout, register };

};
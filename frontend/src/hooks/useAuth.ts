import { useState, useEffect } from "react";

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
        localStorage.removeItem("authToken");
        setIsLoggedIn(false);
    }
    return { isLoggedIn, loading, login, logout };

};
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { login as apiLogin, logout as apiLogout, register as apiRegister } from "@/api/auth-api";
import type { User } from "@/models/user"
import { jwtDecode } from "jwt-decode"; 

export const useAuth = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem("authToken");
        setIsLoggedIn(!!token);
        setLoading(false);
    }, []);

    const login = async (email: string, password: string) => {
        const token = await apiLogin(email, password);
        localStorage.setItem("authToken", token);
        setIsLoggedIn(true);
        navigate("/travel");
    };

    const logout = async () => {
        try {
            await apiLogout();
        } finally {
            localStorage.removeItem("authToken");
            setIsLoggedIn(false);
        }
    };

    const register = async (
        name: string,
        lastname: string,
        dni: string,
        email: string,
        password: string,
        role?: string
    ) => {
        const effectiveRole = role ?? "passenger";
        const token = await apiRegister(name, lastname, dni, email, password, effectiveRole);
        localStorage.setItem("authToken", token);
        setIsLoggedIn(true);
        navigate("/travel");
    };

    const getUserFromToken = async (): Promise<User> => {
        // esto espera una token JWT, pero el backend no manda un JSON normal
        // cambiar el backend para que mande un JWT
        if (isLoggedIn) {
            const token = localStorage.getItem("authToken");
            if (!token) {
                throw new Error("No token found");
            }
            const decoded = jwtDecode<User>(token);
            return decoded;
        }
        throw new Error("No user logged in");
    }

    return { isLoggedIn, loading, login, logout, register, getUserFromToken };
};

 
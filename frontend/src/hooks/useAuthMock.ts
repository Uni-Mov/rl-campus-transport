import { useState, useEffect } from "react";
import { MemoryDB } from "@/api/db"
import { useNavigate } from "react-router-dom";

export const useAuthMock = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    useEffect(() => {
        // agregar usuario de prueba solo si no existe
        const existingUser = MemoryDB.users.find(user => user.email === "borja@example.com");
        if (!existingUser) {
            MemoryDB.users.push({ firstname: "miguel", lastname: "borja", dni: "87654321", email: "borja@example.com", password: "password123", role: "passenger" });
        }
        
        const token = localStorage.getItem("authToken");
        setIsLoggedIn(!!token);
        setLoading(false);
        
        console.log("Usuarios en memoria:", MemoryDB.users);
    }, []);

    const login = (email : string, password: string) => {
        const user = MemoryDB.users.find(user => user.email === email && user.password === password);
        const token = user ? "token" : null;
        if (!token) throw new Error("Login failed");
        
        localStorage.setItem("authToken", token);
        setIsLoggedIn(true);
        navigate("/");
        }

    const logout = () => {
        localStorage.removeItem("authToken");
        setIsLoggedIn(false);
    }

    const register = (firstname: string, lastname: string, dni: string, email: string, password: string, role: string) => {
        try {
            const existingUser = MemoryDB.users.find(user => user.email === email);
            if (existingUser) {
                throw new Error("User already exists");
            }
            MemoryDB.users.push({ firstname, lastname, dni, email, password, role });
            localStorage.setItem("authToken", "token");
            setIsLoggedIn(true);
            navigate("/");
        } catch (res) {
            console.error("Error en registro:", res);
            throw res;
        }
    }
    
    return { isLoggedIn, loading, login, logout, register };

};
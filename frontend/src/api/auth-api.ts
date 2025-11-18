
export const login = async (email: string, password: string): Promise<string> => {
    const response = await fetch("http://localhost:5000/users/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
        throw new Error("Login failed");
    }

    const data = await response.json();
    localStorage.setItem("authToken", data.token);
    return data.token as string;
}

export const register = async (
    first_name: string,
    last_name: string,
    dni: string,
    email: string,
    password: string,
    role: string
): Promise<string> => {
    const response = await fetch("http://localhost:5000/users/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ first_name, last_name, dni, email, password, role })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error("Registration failed: " + error.description);
    }

    await response.json();
    const token = await login(email, password);
    return token;
}

export const logout = async (): Promise<void> => {
    const token = localStorage.getItem("authToken");
    if (!token) return;

    const response = await fetch("http://localhost:5000/users/logout", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) throw new Error("Logout failed");

    localStorage.removeItem("authToken");
}

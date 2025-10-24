
export const login = async (email: string, password: string): Promise<String> => {
    const response = fetch("https://localhost:5000/api/users/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    if (!(await response).ok) {
        throw new Error("Login failed");
    }

    const data = await (await response).json();
    localStorage.setItem("authToken", data.token);
    return data.token;
}

export const register = async (
    firstname: string,
    lastname: string,
    dni: string,
    email: string,
    password: string,
    role: string
): Promise<string> => {
    const response = await fetch("https://localhost:5000/api/users", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ firstname, lastname, dni, email, password, role })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error("Registration failed: " + error.description);
    }

    const data = await response.json();
    localStorage.setItem("authToken", data.token);
    return data.token;
}

export const logout = async (): Promise<void> => {
    const token = localStorage.getItem("authToken");
    if (!token) return;

    const response = await fetch("https://localhost:5000/api/users/logout", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) throw new Error("Logout failed");

    localStorage.removeItem("authToken");
}

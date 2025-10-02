
export const login = async (username: string, password: string): Promise<String> => {
  const token = fetch("https://localhost:3000/api/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  }).then(res => {
    if (!res.ok) throw new Error("Login failed");
    return res.text();
  });
  return token;
}

export const register = async (name: string, lastname : string, email : string, password: string): Promise<string> => {
  const token = await fetch("https://localhost:3000/api/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, lastname, email, password }),
  });
  if (!token.ok) throw new Error("Registration failed");
  return token.text();
}

export const logout = async (): Promise<void> => {
 const res = await fetch("https://localhost:3000/api/logout", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({token: localStorage.getItem("token")}), // send the token to invalidate it on the server
  });
  if (!res.ok) throw new Error("Logout failed");
}

  


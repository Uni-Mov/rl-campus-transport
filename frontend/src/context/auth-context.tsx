import { createContext, useContext } from "react"
import { useAuth as useAuthHook } from "../hooks/useAuth"
import type { User } from "@/models/user";

type AuthContextType = {
  isLoggedIn: boolean;
  loading: boolean;
  login: (email : string, password: string) => void;
  logout: () => void;
  register: (name: string, lastname: string, dni: string, email: string, password: string, role: string) => void;
  getUserFromToken: () => Promise<User>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const auth = useAuthHook();
  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
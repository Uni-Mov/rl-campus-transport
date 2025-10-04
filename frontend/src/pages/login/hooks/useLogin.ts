import { useState } from "react";
import { useAuth } from "@/context/auth-context";

export const useLogin = () => {
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  
  const validatePassword = (password: string): boolean => {
    if (password.length < 8) {
      setError("Password must be at least 8 characters long");
      return false;
    }
    return true; 
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    
    if (!validatePassword(password)) {
      return;
    } 
    setError("");
    try {
    login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  return {showPassword, setShowPassword, validatePassword, handleSubmit, error };
}
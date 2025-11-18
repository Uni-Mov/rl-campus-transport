import { useState } from "react";
import { useAuth } from "@/context/auth-context";

export const useRegister = () => {

  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { register } = useAuth();
  
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
    const name = formData.get('name') as string;
    const lastname = formData.get('lastName') as string;
    const dni = formData.get('dni') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const role = formData.get('role') as string;
    if (!validatePassword(password)) {
      return;
    }
    setError("");
    try {
      (register as any)(name, lastname, dni, email, password, role);
    } catch {
      setError("failed in register");
    }
  };

  return {
    showPassword, 
    setShowPassword, 
    showConfirmPassword, 
    setShowConfirmPassword,
    validatePassword, 
    handleSubmit, 
    error 
  };
};

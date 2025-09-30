import { useState } from "react";
import { useNavigate } from "react-router-dom";
export const useLogin = () => {
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  
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
    // TODO : call api to login and navigate to home
    navigate("/");
  };

  return {showPassword, setShowPassword, validatePassword, handleSubmit, error };
}
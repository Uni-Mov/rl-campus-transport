import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

export const useRegister = () => {

  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const navigate = useNavigate();
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
    const name = formData.get('username') as string;
    const lastname = formData.get('lastname') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    if (!validatePassword(password)) {
      return;
    }
    setError("");
    register(name, lastname, email, password)
    .then((success) => {
    if (success) {
      navigate("/login");
    } else {
      setError("An error occurred while registering");
    }
   })
  .catch((error) => {
    console.error(error);
    setError("An unexpected error occurred");
  });

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

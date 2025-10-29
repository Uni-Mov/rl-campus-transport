import { Eye, Lock, Mail, User } from 'lucide-react';
import { Alert, AlertTitle } from "@/components/ui/alert";
import { OctagonAlert } from "lucide-react";
import { useRegister } from "../hooks/useRegister";

export function RegisterForm() {
  const { 
    showPassword, 
    setShowPassword, 
    error, 
    handleSubmit 
  } = useRegister();
  
  return (
    <div className="bg-white shadow-lg rounded-lg border border-gray-200 p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-center text-gray-900">Create Account</h2>
        <p className="text-center text-gray-600 mt-1">Enter your information to create your account</p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label htmlFor="name" className="text-sm font-medium text-gray-700">
            Name
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              id="name"
              name="name"
              type="text"
              placeholder="Enter your name"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-colors"
              required
            />
          </div>
        </div>
        <div className="space-y-2">
        <label htmlFor="lastName" className="text-sm font-medium text-gray-700">
            Last name
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              id="lastName"
              name="lastName"
              type="text"
              placeholder="Enter your last name"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-colors"
              required
            />
          </div>
        </div>
 
        <div className="space-y-2">
          <label htmlFor="name" className="text-sm font-medium text-gray-700">
            DNI
          </label>

          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              id="dni"
              name="dni"
              type="text"
              inputMode="numeric"
              pattern="[0-9]{7,8}"
              placeholder="Enter your DNI"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-colors"
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium text-gray-700">
            Email address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-colors"
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="role" className="text-sm font-medium text-gray-700">
            Role
          </label>
          <div className="relative">
            <select
              id="role"
              name="role"
              defaultValue="passenger"
              className="w-full pl-3 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-colors"
              required
            >
              <option value="passenger">Passenger</option>
              <option value="driver">Driver</option>
            </select>
          </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium text-gray-700">
            Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-colors"
              required
            />
            <button
              type="button"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              onClick={() => setShowPassword((prev) => !prev)}
            >
              <Eye size={16} color="gray" />
            </button>
          </div>
        </div>

        <button
          type="submit"
          className="w-full py-3 bg-primary text-white font-medium rounded-lg transition-colors"
        >
          Create Account
        </button>
      </form>
      
      {error && 
        <Alert className="bg-destructive/10 dark:bg-destructive/15 py-4 mt-2 text-destructive border-none">
          <OctagonAlert className="size-4" />
          <AlertTitle>
            {error}
          </AlertTitle>
        </Alert>
      }
    </div>
  );
}
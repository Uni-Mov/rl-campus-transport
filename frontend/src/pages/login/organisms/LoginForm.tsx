import { useState } from "react";
import { Eye, Lock, Mail } from 'lucide-react';

export default function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="bg-white shadow-lg rounded-lg border border-gray-200 p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-center text-gray-900">Sign in</h2>
        <p className="text-center text-gray-600 mt-1">Enter your email and password to access your account</p>
      </div>

      <form className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium text-gray-700">
            Email address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-colors"
              required
            />
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
          Sign in
        </button>
      </form>
    </div>
  );
}

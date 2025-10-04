import { useAuth } from "../../../context/auth-context"
import { MapPin } from 'lucide-react';
import { Link, useLocation, useNavigate } from "react-router-dom"
import { useEffect, useState } from "react";

export default function Header() {
  const auth = useAuth()
  const location = useLocation();
  const navigate = useNavigate();
  
  const [landing, setLanding] = useState(true);

  useEffect(() => {
    setLanding(location.pathname === '/');
  }, [location]);

  const { isLoggedIn, login, logout } = auth;
  const buttons = [];
  
  if (isLoggedIn) {
  buttons.push({ label: "Logout", onClick: logout, bg: "primary" });
  } else {
  switch (location.pathname) {
    case "/login":
      buttons.push({ label: "Sign Up", to: "/register", bg: "primary" });
      break;
    case "/register":
      buttons.push({ label: "Login", to: "/login", bg: "primary" });
      break;
    default:
      buttons.push(
        { label: "Login", to: "/login", bg: "primary" },
        { label: "Sign Up", to: "/register", bg: "primary" }
      )
      break;
  }
}

  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link to="/">
            <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
              <MapPin color="white" size={20} />
            </div>
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Campus transport</h1>
        </div>
        <nav className="hidden md:flex items-center gap-4">
          {landing && (
            <>
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">
                Features
              </a>
              <a href="#community" className="text-gray-600 hover:text-gray-900 transition-colors">
                Community
              </a>
            </>
          )}

          {buttons.map((btn) => (
            <button
              key={btn.label}
              onClick={btn.onClick ?? (() => btn.to && navigate(btn.to))} // if onClick redirect to same page, else navigate to other route
              className={`px-6 py-2 bg-${btn.bg} text-white rounded-lg hover:bg-emerald-700 transition-colors`}
            >
              {btn.label}
            </button>
          ))}

        </nav>
      </div>
    </header>
  )
}

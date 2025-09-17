import {useAuth} from "../../hooks/useAuth";
export default function Header({isLoggedIn}: {isLoggedIn: boolean}) {
  const { login, logout } = useAuth();
 return (
        <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-gray-900">Campus transport</h1>
          </div>
          <nav className="hidden md:flex items-center gap-6">
          {!isLoggedIn && (
            <>
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">
                Features
              </a>
              <a href="#community" className="text-gray-600 hover:text-gray-900 transition-colors">
                Community
              </a>
              <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
                View on GitHub
              </button>
              <button onClick={() => login('soyuntoken')} className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors">
                login
              </button>
            </>
          )} 
          {isLoggedIn && (
            <>
              <button onClick={() => logout()} className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                Logout
              </button>
            </>
          )}
          </nav>
        </div> 
        </header>)
}

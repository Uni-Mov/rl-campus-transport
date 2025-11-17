import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { MapPin } from "lucide-react";
import { Navigation } from "lucide-react";
import { User } from "lucide-react";
import { Settings } from "lucide-react";
import { LogOut } from "lucide-react";
import { Menu } from "lucide-react";
import { X } from "lucide-react";
import { Info } from "lucide-react"

import { useAuth } from "@/context/auth-context";
import { useRouter } from "@/context/router-context";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"


export default function Sidebar() {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { useCustomRouter, setUseCustomRouter } = useRouter();
  const { logout, getUserFromToken } = useAuth();
  
  useEffect(() => {
    const fetchUser = async () => {
      try {
        await getUserFromToken();
        
      } catch (err) {
        console.error("Error fetching user:", err);
      }
    };
    
    fetchUser();
  }, []);
  

  const sidebarContent = (
    <>
      <div className="p-4 lg:p-6 border-b border-border">
        <div className="flex items-center justify-between mb-4 lg:mb-6">
          <div className="flex items-center gap-3">
            <Link to="/">
              <div className="w-10 h-10 rounded-lg bg-emerald-600 flex items-center justify-center">
                <MapPin className="w-6 h-6 text-white" />
              </div>
            </Link>
            <span className="text-xl font-semibold">Campus transport</span>
          </div>
          <button
            onClick={() => setIsMobileOpen(false)}
            className="lg:hidden p-2 hover:bg-muted rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
    
        {/* User Profile */}
        <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
          <Avatar className="w-12 h-12">
            <AvatarImage src="/abstract-geometric-shapes.png" />
            {/* <AvatarFallback>{user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}</AvatarFallback> */}
            <AvatarFallback>UN</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            {/* <p className="font-medium truncate">{user?.first_name}</p> */}
            <p className="font-medium truncate">User Name</p>
            <p className="font-light text-xs truncate">Driver</p>
          </div>
        </div>
      </div>
    
      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto min-h-0">
        <button
          className="w-full flex items-center justify-start gap-3 px-4 py-2 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 hover:text-emerald-800 transition-colors"
        >
          <Navigation className="w-5 h-5" />
          <span>Buscar viaje</span>
        </button>
        <button className="w-full flex items-center justify-start gap-3 px-4 py-2 rounded-lg hover:bg-muted transition-colors">
          <User className="w-5 h-5" />
          <span>Mi perfil</span>
        </button>
        <button className="w-full flex items-center justify-start gap-3 px-4 py-2 rounded-lg hover:bg-muted transition-colors">
          <Settings className="w-5 h-5" />
          <span>Configuración</span>
        </button>
      </nav>
    
      {/* Logout - Fixed at bottom */}
      <div className="flex-shrink-0">
        <div className="p-4 border-t border-border">
          {/* Custom Router Toggle */}
          <div className="flex items-center justify-between gap-3 p-3 rounded-lg hover:bg-muted transition-colors">
            <div className="flex items-center gap-2 flex-1">
              <div className="relative inline-block group/tooltip">
                <Info />
                {/* Tooltip */}
                <div className="absolute bottom-full left-0 mb-2 w-56 p-3 bg-slate-900 text-white text-xs rounded opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-opacity duration-200 pointer-events-none z-50">
                  El motor de rutas personalizado es un modelo de Reinforcement Learning construido por los creadores de este proyecto
                  <div className="absolute top-full left-3 border-4 border-transparent border-t-slate-900"></div>
                </div>
              </div>
              <span>Usar motor de rutas personalizado</span>
            </div>
            {/* Toggle Switch */}
            <button
              onClick={() => setUseCustomRouter(!useCustomRouter)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0 ${
                useCustomRouter ? 'bg-emerald-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  useCustomRouter ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
        <div className="p-4 border-t border-border">
          <Link to="/">
            <button
              className="w-full flex items-center justify-start gap-3 px-4 py-2 rounded-lg text-destructive hover:text-destructive hover:bg-destructive/10 transition-colors"
              onClick={logout}
            >
              <LogOut className="w-5 h-5" />
              <span>Cerrar sesión</span>
            </button>
          </Link>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="lg:hidden fixed top-4 right-4 z-50 p-2 bg-card border border-border rounded-lg shadow-lg hover:bg-muted transition-colors"
        aria-label="Abrir menú"
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40 transition-opacity"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static
        top-0 left-0
        h-screen
        w-64 sm:w-72
        flex flex-col
        border-r border-border
        bg-card
        z-40
        overflow-hidden
        transform transition-transform duration-300 ease-in-out
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {sidebarContent}
      </aside>
    </>
  );
}

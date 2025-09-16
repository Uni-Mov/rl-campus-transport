import { Link } from "react-router-dom"

export default function Header() {
  return (
    <nav className="bg-card border-b border-border shadow-sm">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-heading font-bold text-sm">CM</span>
            </div>
            <span className="font-heading font-semibold text-lg text-foreground">Client Manager</span>
          </div>

          <div className="flex space-x-1">
            <Link
              to="/"
              className="text-muted-foreground hover:text-primary hover:bg-muted px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus-ring"
            >
              Inicio
            </Link>
            <Link
              to="/clients"
              className="text-muted-foreground hover:text-primary hover:bg-muted px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus-ring"
            >
              Clientes
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

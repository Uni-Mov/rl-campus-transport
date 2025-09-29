"""Punto de entrada de backend Flask. Inicializa la app y registra los endpoints."""

from flask import Flask
from flask_cors import CORS
from app.api.users import bp as users_bp

def create_app():
    """Crea y configura la aplicacion Flask, habilita CORS y registra los blueprints."""
    app = Flask(__name__)
    CORS(app, origins="*")  # Enable CORS for all origins in development
    app.register_blueprint(users_bp, url_prefix="/users")
    return app

if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)

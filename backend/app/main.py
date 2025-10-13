"""Backend Flask entry point. Initializes the app and registers the endpoints."""

from flask import Flask
from flask_cors import CORS
from app.api.users import bp as users_bp
from app.core.database import create_tables  # import de función para crear tablas


def create_app():
    """Create and configure the Flask application.
    
    - Enables CORS for all origins (development mode).
    - Registers blueprints with their respective URL prefixes.
    - Creates all database tables.
    """
    app = Flask(__name__)
    CORS(app, origins="*")  # Allow all origins (use more restrictive config in production)
    app.register_blueprint(users_bp, url_prefix="/users")
    
    create_tables()

    return app


if __name__ == "__main__":
    # Run the application in debug mode on port 5000
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask
from flask_cors import CORS
from app.api.users import bp as users_bp

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")  # Enable CORS for all origins in development
    app.register_blueprint(users_bp, url_prefix="/users")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

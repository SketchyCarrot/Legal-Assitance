from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
    jwt = JWTManager(app)

    # Configure logging
    if not os.path.exists('logs'):
        os.makedirs('logs')

    file_handler = RotatingFileHandler(
        'logs/legal_saathi.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Legal-Saathi Python Service startup')

    # Register blueprints
    from .modules.browser import bp as browser_bp
    from .modules.form import bp as form_bp
    from .modules.data import bp as data_bp

    app.register_blueprint(browser_bp, url_prefix='/api/browser')
    app.register_blueprint(form_bp, url_prefix='/api/form')
    app.register_blueprint(data_bp, url_prefix='/api/data')

    return app 
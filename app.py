# app.py
from flask import Flask
from pykes.models import init_db
from pykes.routes import init_routes
from pykes.config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/dangote_app.log', maxBytes=10240000, backupCount=5)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Dangote Execution Tracker startup')

# Initialize database
init_db()

# Initialize routes BEFORE registering blueprints +tscQ#L4-+dSe%K
init_routes(app)

# Register blueprints
from app_reports import reports_bp
from app_admin import admin_bp
app.register_blueprint(reports_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
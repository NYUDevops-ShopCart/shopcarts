"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import os
import sys
import logging
from flask import Flask

# Get configuration from environment
DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:password@localhost:3306/shopcarts')
SECRET_KEY = os.getenv('SECRET_KEY', 's3cr3t-key-shhhh')

# Create Flask application
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

# Import the routes After the Flask app is created
from service import service, models

# Set up logging for production
service.initialize_logging()

app.logger.info(70 * '*')
app.logger.info('  S H O P  C A R T   S E R V I C E   R U N N I N G  '.center(70, '*'))
app.logger.info(70 * '*')

try:
    service.init_db()  # make our sqlalchemy tables
except Exception as error:
    app.logger.critical('%s: Cannot continue', error)
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info('Service inititalized!')

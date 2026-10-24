"""Controlled database migration entry point."""
from flask_migrate import Migrate
from main import app, db

migrate = Migrate(app, db)

# app/__init__.py
from .app import app  # exposes "app" at package level if you want "from app import app"
from . import routes  # ensures routes are registered
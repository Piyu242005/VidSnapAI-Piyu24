"""Vercel Python Function entry point for the Flask web application.

Vercel runs this app as a short-lived serverless function. The heavy media
generation endpoints are intentionally disabled in Vercel mode; run the
video worker on a persistent worker host instead.
"""
from main import app

# Vercel's Python runtime detects this WSGI application.

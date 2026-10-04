"""
Backend routes entry point - exposes FastAPI router from backend.api.routes.
"""

from backend.api.routes import router, _enrich_product

__all__ = ["router", "_enrich_product"]

"""
Central model registry.
Imports all SQLAlchemy models so that Alembic and the app
can discover them via Base.metadata.
"""

# Import Base first
from app.core.database import Base  # noqa: F401

# Import all models for discovery
from app.models.user import User # noqa: F401
from app.models.resume import MasterResume, GeneratedResume # noqa: F401


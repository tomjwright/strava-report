"""Database connection using Supabase client."""
from app.db.supabase_adapter import db as supabase_db

# Re-export for compatibility
db = supabase_db

def get_db():
    """Get database instance."""
    return db

def init_db():
    """Initialize database - no-op for Supabase client."""
    # Tables are created manually in Supabase SQL Editor
    pass

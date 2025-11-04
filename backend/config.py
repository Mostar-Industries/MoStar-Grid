import os
from typing import Optional

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MOGRID_DB_HOST', 'localhost'),
    'port': int(os.getenv('MOGRID_DB_PORT', '5432')),
    'database': os.getenv('MOGRID_DB_NAME', 'MoGrid'),
    'user': os.getenv('MOGRID_DB_USER', 'postgres'),
    'password': os.getenv('MOGRID_DB_PASS', 'mostar')
}

def get_db_connection_string() -> Optional[str]:
    """Returns the database connection string or None if not configured"""
    try:
        return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    except Exception:
        return None

# Grid settings
GRID_MODE = os.getenv('MOGRID_MODE', 'development')
API_PORT = int(os.getenv('MOGRID_PORT', '7000'))
API_HOST = os.getenv('MOGRID_HOST', '0.0.0.0')
DEBUG_MODE = GRID_MODE == 'development'
ALLOW_NO_DB = os.getenv('MOGRID_ALLOW_NO_DB', 'true').lower() == 'true'

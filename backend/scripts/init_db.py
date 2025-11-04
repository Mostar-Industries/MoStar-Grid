import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from models.database import Base
from config import get_db_connection_string
import logging

logger = logging.getLogger("grid.db")

def init_database():
    """Initialize the MoGrid database schema"""
    conn_str = get_db_connection_string()
    if not conn_str:
        raise ValueError("Database connection string not configured")
    
    try:
        engine = create_engine(conn_str)
        try:
            Base.metadata.create_all(engine)
            logger.info("✅ Database schema created successfully")
        except Exception as e:
            msg = str(e).lower()
            # Detect managed-provider schema mutation policy messages
            if ("covenantal" in msg) or ("forbidden" in msg) or ("permission denied" in msg) or ("schema mutation" in msg):
                logger.error("❌ Schema mutation appears to be forbidden by the managed DB provider.")
                logger.error("Guidance: use your provider's migration tool (e.g. Neon Code Conduit) or run the DDL via the DB admin UI.")
                # Respect explicit override if operator chooses to force mutation
                if os.getenv("FORCE_SCHEMA_MUTATION", "false").lower() == "true":
                    logger.warning("FORCE_SCHEMA_MUTATION=true — re-raising the original error to attempt direct mutation.")
                    raise
                else:
                    logger.info("Skipping schema creation due to provider policy. Exiting init script without raising.")
                    return
            else:
                logger.error(f"❌ Database initialization failed during schema creation: {str(e)}")
                raise
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()

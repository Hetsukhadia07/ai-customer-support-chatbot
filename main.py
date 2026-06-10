"""
Main entry point for the AI Customer Support Chatbot
Run with: python main.py
Or: uvicorn api:app --reload
"""

import uvicorn
import logging
from api import app
import config

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"API will be available at http://{config.API_HOST}:{config.API_PORT}")
    logger.info(f"Swagger UI: http://{config.API_HOST}:{config.API_PORT}/docs")
    logger.info(f"ReDoc: http://{config.API_HOST}:{config.API_PORT}/redoc")
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()

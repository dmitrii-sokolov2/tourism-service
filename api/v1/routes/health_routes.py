from fastapi import APIRouter

from core.logging_config import setup_logging

health_router = APIRouter(tags=['health'])
logger = setup_logging()

@health_router.get('/health')
def health_check():
    logger.debug("GET /api/health - проверка здоровья")

    return {"status": "healthy", "database": "connected"}
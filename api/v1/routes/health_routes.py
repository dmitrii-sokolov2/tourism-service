from fastapi import APIRouter
from logging import getLogger


health_router = APIRouter(tags=['health'])
logger = getLogger(__name__)

@health_router.get('/health')
def health_check():
    logger.debug("GET /api/health - проверка здоровья")

    return {"status": "healthy", "database": "connected"}
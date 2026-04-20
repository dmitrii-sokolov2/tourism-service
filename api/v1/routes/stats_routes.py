from fastapi import APIRouter

from core.logging_config import setup_logging

stats_router = APIRouter(prefix='/stats', tags=['stats'])
logger = setup_logging()

@stats_router.get('/threads')
def thread_stats():
    try:
        import threading
        return {
            "thread_pool_workers": 5,
            "active_threads": threading.active_count(),
            "current_thread": threading.current_thread().name,
            "message": "Многопоточная архитектура активна",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in thread stats: {str(e)}")

        return {
            "status": "error",
            "message": "Thread statistics temporarily unavailable",
            "active_threads": "unknown"
        }
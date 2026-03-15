from flask import Blueprint, jsonify
import logging, logging.config
import yaml

from core.logging_config import setup_logging

stats_bp = Blueprint('stats', __name__)
logger = setup_logging()

@stats_bp.route('/threads')
def thread_stats():
    try:
        import threading
        return jsonify({
            "thread_pool_workers": 5,
            "active_threads": threading.active_count(),
            "current_thread": threading.current_thread().name,
            "message": "Многопоточная архитектура активна",
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error in thread stats: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Thread statistics temporarily unavailable",
            "active_threads": "unknown"
        })
from flask import Blueprint, jsonify
import logging, logging.config
import yaml

from core.logging_config import setup_logging

health_bp = Blueprint('health', __name__)
logger = setup_logging()

@health_bp.route('/health')
def health_check():
    logger.debug("GET /api/health - проверка здоровья")
    return jsonify({"status": "healthy", "database": "connected"})
import logging
import logging.config
import yaml

def setup_logging():
    try:
        with open('logging_config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
        logger = logging.getLogger(__name__)
        logger.info("✅ Логирование настроено из YAML конфигурации")
        return logger
    except FileNotFoundError:
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        logger.warning("⚠️ Файл конфигурации логирования не найден, используется базовая настройка")
        return logger
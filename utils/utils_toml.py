import os
import sys
import toml
import logging

# Настройка базовой конфигурации для логирования
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# load toml file
def load_toml(path):
    if not os.path.exists(path):
        logger.error(f"Файл конфигурации не найден: {path}")
        sys.exit(1)
    with open(path, "r") as f:
        return toml.load(f)


def get_config_value(config, key, default):
    return config[key] if key in config else default

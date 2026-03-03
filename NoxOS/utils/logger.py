import logging
import logging.handlers
import os
from core.config import settings

# Crear directorio de logs si no existe
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configurar logger
logger = logging.getLogger("restaurante")
logger.setLevel(getattr(logging, settings.LOG_LEVEL))

# Formato de logs
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler para archivo
file_handler = logging.handlers.RotatingFileHandler(
    f"{logs_dir}/app.log",
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler para consola (solo en desarrollo)
if settings.DEBUG:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

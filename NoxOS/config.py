"""
Configuración centralizada del proyecto
"""

from pathlib import Path

# Rutas principales
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
TESTS_DIR = BASE_DIR / "tests"
LOGS_DIR = BASE_DIR / "logs"

# Crear directorios si no existen
LOGS_DIR.mkdir(exist_ok=True)

# Aplicación
APP_TITLE = "NoxOS API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "API REST para sistema de gestión de discoteca con pedidos por QR"

# Base de datos
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/discoteca_app"

# Seguridad
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "app.log"
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# API
API_V1_STR = "/api/v1"
CORS_ORIGINS = ["*"]  # Cambiar en producción

# Paginación
DEFAULT_LIMIT = 10
MAX_LIMIT = 100

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# Crear motor de base de datos
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Mostrar queries en desarrollo
    pool_pre_ping=True,   # Verificar conexión antes de usarla
    pool_size=20,
    max_overflow=40
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

def get_db():
    """
    Dependencia para obtener la sesión de base de datos.
    Se usa en los endpoints de FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

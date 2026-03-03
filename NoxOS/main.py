# coding=utf-8
"""
DiscotecaAPI - Sistema de Pedidos por QR para Discotecas
FastAPI + MariaDB + SQLAlchemy
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from core.config import settings
from database.config import Base, engine
from utils.logger import logger

# Importar rutas
from routes import usuarios, categorias, productos, mesas, pedidos, inventario, facturas, datos

# Crear tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST para sistema de pedidos en mesas mediante QR - Discotecas",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rutas


app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(productos.router)
app.include_router(mesas.router)
app.include_router(pedidos.router)
app.include_router(inventario.router)
app.include_router(facturas.router)
app.include_router(datos.router)



# Endpoints de Salud


@app.get("/")
async def root():
    """
    Endpoint raíz - Información de la API
    """
    return {
        "message": "Bienvenido a DiscotecaAPI - Sistema de Pedidos por QR",
        "version": settings.APP_VERSION,
        "status": "online",
        "endpoints": {
            "docs": "/api/docs",
            "redoc": "/api/redoc",
            "health": "/api/health"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/health")
async def health_check():
    """
    Verificar salud de la API
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }



# Manejadores de Errores


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Manejador global de excepciones
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "timestamp": datetime.utcnow().isoformat()
        }
    )



# Evento de Inicio


@app.on_event("startup")
async def startup_event():
    """
    Ejecutarse al iniciar la aplicación
    """
    logger.info(f"={settings.APP_NAME}=")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info("Aplicación iniciada correctamente")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Ejecutarse al cerrar la aplicación
    """
    logger.info("Aplicación cerrada")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
        reload=False
    )

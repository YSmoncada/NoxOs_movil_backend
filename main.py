from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine, Base
from api.endpoints import auth, pedidos, inventario, mesas, usuarios, config
from fastapi.staticfiles import StaticFiles
import os
import logging

# Configurar logging solo a consola para evitar bucles de reinicio
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("mandala")

# Crear tablas y semillar si es necesario
Base.metadata.create_all(bind=engine)

# Auto-seed si la base de datos está vacía (Especialmente para Render)
from db.database import SessionLocal
from db.models import Usuario
from seed import seed

db = SessionLocal()
try:
    if db.query(Usuario).count() == 0:
        logger.info("Base de datos vacía. Iniciando semillado automático...")
        seed()
        logger.info("Semillado completado.")
finally:
    db.close()

app = FastAPI(title="Mandala API (FastAPI)")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos para las imágenes (Ruta Relativa)
current_dir = os.path.dirname(os.path.abspath(__file__))
possible_media_paths = [
    os.path.join(current_dir, "media"),
    os.path.join(os.path.dirname(current_dir), "MANDALA APP", "backend", "media")
]

for mp in possible_media_paths:
    if os.path.exists(mp):
        app.mount("/media", StaticFiles(directory=mp), name="media")
        logger.info(f"Carpeta media montada desde: {mp}")
        break

# Incluir rutas
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(pedidos.router, prefix="/api/pedidos", tags=["pedidos"])
app.include_router(inventario.router, prefix="/api", tags=["inventario"])
app.include_router(mesas.router, prefix="/api/mesas", tags=["mesas"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
app.include_router(config.router, prefix="/api/config", tags=["config"])

@app.get("/")
def read_root():
    return {"message": "Mandala FastAPI Backend System - Operational"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor Mandala API...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

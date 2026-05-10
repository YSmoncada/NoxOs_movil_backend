from db.database import SessionLocal
from db import models

db = SessionLocal()
try:
    turnos = db.query(models.Turno).all()
    print(f"Total turnos: {len(turnos)}")
    for t in turnos:
        print(f"ID: {t.id}, Estado: {t.estado}, Abierto Por: {t.abierto_por}, Fecha: {t.fecha_apertura}")
    
    users = db.query(models.Usuario).all()
    print(f"\nTotal usuarios: {len(users)}")
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Activo: {u.activo}, CreatedAt: {u.created_at}")

finally:
    db.close()

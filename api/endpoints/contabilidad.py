from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from db import models
from schemas import schemas
from api.deps import get_db, get_current_active_user, check_admin_role
from datetime import datetime
from sqlalchemy.sql import func

router = APIRouter()

@router.get("/turno/actual/")
def get_turno_actual(db: Session = Depends(get_db)):
    turno = db.query(models.Turno).filter(models.Turno.estado == "abierto").first()
    if not turno:
        return None
    
    # Calcular ventas totales actuales de pedidos vinculados al turno
    # Si no hay ventas, devolvemos 0
    total_ventas = db.query(func.sum(models.Pedido.total)).filter(
        models.Pedido.turno_id == turno.id,
        models.Pedido.estado != 6 # Asumiendo que 6 es Cancelado (ver estados_pedido)
    ).scalar() or 0
    
    turno.total_ventas = total_ventas
    return turno

@router.post("/turno/abrir/", response_model=schemas.Turno)
def abrir_turno(
    turno_in: schemas.TurnoCreate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    # Verificar si ya hay uno abierto
    existe = db.query(models.Turno).filter(models.Turno.estado == "abierto").first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya hay un turno abierto")
    
    db_turno = models.Turno(
        abierto_por=current_user.id,
        base_inicial=turno_in.base_inicial,
        observaciones=turno_in.observaciones,
        estado="abierto"
    )
    db.add(db_turno)
    db.commit()
    db.refresh(db_turno)
    return db_turno

@router.post("/turno/cerrar/", response_model=schemas.Turno)
def cerrar_turno(
    cierre: schemas.TurnoCierre,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    turno = db.query(models.Turno).filter(models.Turno.estado == "abierto").first()
    if not turno:
        raise HTTPException(status_code=404, detail="No hay un turno abierto para cerrar")
    
    # Calcular ventas finales
    total_ventas = db.query(func.sum(models.Pedido.total)).filter(
        models.Pedido.turno_id == turno.id,
        models.Pedido.estado != 6
    ).scalar() or 0
    
    turno.cerrado_por = current_user.id
    turno.fecha_cierre = datetime.now()
    turno.total_ventas = total_ventas
    turno.efectivo_real = cierre.efectivo_real
    turno.observaciones = f"{turno.observaciones or ''}\n--- NOTAS DE CIERRE ---\n{cierre.observaciones or ''}"
    turno.estado = "cerrado"
    
    db.commit()
    db.refresh(turno)
    return turno

@router.get("/turnos/historial/", response_model=List[schemas.Turno])
def get_historial_turnos(
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(check_admin_role)
):
    turnos = db.query(models.Turno).order_by(models.Turno.fecha_apertura.desc()).offset(skip).limit(limit).all()
    return turnos

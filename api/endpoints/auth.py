from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import database, models
from core import security
from schemas import schemas
from api import deps
from typing import Optional
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger("mandala.auth")
router = APIRouter()

@router.post("/login/", response_model=schemas.Token)
def login(login_data: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.username == login_data.username).first()
    if not user or not security.verify_password(login_data.password, user.password):
        logger.warning(f"Intento de login fallido para: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.activo:
        logger.warning(f"Intento de login para usuario inactivo: {user.username}")
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    # Obtener rol
    role = "usuario"
    user_rol = db.query(models.UsuarioRol).filter(models.UsuarioRol.usuario_id == user.id).first()
    if user_rol:
        role = user_rol.rol.nombre.lower()

    # Generar Opaque Token y guardarlo en DB
    logger.info(f"Generando token para {user.username}...")
    token_str = security.create_opaque_token()
    expires = datetime.utcnow() + timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    try:
        logger.info("Guardando sesión en DB...")
        new_session = models.UserSession(
            token=token_str,
            user_id=user.id,
            expires_at=expires
        )
        db.add(new_session)
        db.commit()
        logger.info("Sesión guardada exitosamente.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error al guardar sesión: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al crear sesión")

    logger.info(f"Login exitoso: {user.username} (Rol: {role})")
    return {
        "token": token_str,
        "refresh": token_str, # Usamos el mismo token opaco para el refresh para compatibilidad con el frontend
        "role": role,
        "username": user.username,
        "nombre": user.nombre_completo or user.username,
        "user_id": user.id,
        "detail": f"Bienvenido {user.nombre_completo or user.username}"
    }

@router.post("/token/refresh/", response_model=schemas.TokenRefreshResponse)
def refresh_token(refresh_data: dict, db: Session = Depends(deps.get_db)):
    token = refresh_data.get("refresh")
    if not token:
        raise HTTPException(status_code=400, detail="Refresh token requerido")
    
    session = db.query(models.UserSession).filter(models.UserSession.token == token).first()
    if not session or (session.expires_at and session.expires_at < datetime.utcnow()):
        if session:
            db.delete(session)
            db.commit()
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    user = session.user
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    # Renovar el token
    new_token_str = security.create_opaque_token()
    expires = datetime.utcnow() + timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Actualizar la sesión actual o crear una nueva y borrar la vieja
    session.token = new_token_str
    session.expires_at = expires
    db.commit()

    return {"token": new_token_str}

@router.post("/logout/")
def logout(db: Session = Depends(deps.get_db), token: str = Depends(deps.oauth2_scheme)):
    if not token:
        return {"detail": "No se proporcionó token"}
        
    session = db.query(models.UserSession).filter(models.UserSession.token == token).first()
    if session:
        db.delete(session)
        db.commit()
        logger.info(f"Sesión cerrada exitosamente para token: {token[:10]}...")
        
    return {"detail": "Sesión cerrada correctamente"}

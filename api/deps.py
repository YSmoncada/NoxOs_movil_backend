from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db import database, models
from datetime import datetime, timezone
import logging

logger = logging.getLogger("mandala.deps")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login/", auto_error=False)

from typing import Optional

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

from core import security

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = security.decode_token(token)
    if not payload or payload.get("type") != "access":
        # Si no es válido o expiró, levantamos 401
        raise credentials_exception
    
    username = payload.get("sub")
    if not username:
        raise credentials_exception

    user = db.query(models.Usuario).filter(models.Usuario.username == username).first()
    if not user:
        raise credentials_exception
    
    return user

def get_optional_user(db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)):
    if not token:
        return None
    try:
        payload = security.decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        
        username = payload.get("sub")
        return db.query(models.Usuario).filter(models.Usuario.username == username).first()
    except Exception as e:
        logger.error(f"Error en get_optional_user: {str(e)}")
        return None

def get_current_active_user(current_user: models.Usuario = Depends(get_current_user)):
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

def check_admin_role(current_user: models.Usuario = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user_rol = db.query(models.UsuarioRol).filter(models.UsuarioRol.usuario_id == current_user.id).first()
    if not user_rol or user_rol.rol.nombre.lower() != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    return current_user

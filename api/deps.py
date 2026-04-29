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

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    session = db.query(models.UserSession).filter(models.UserSession.token == token).first()
    if not session:
        raise credentials_exception
    
    # Optional: check if token expired
    if session.expires_at and session.expires_at < datetime.utcnow():
        raise credentials_exception
    
    user = session.user
    if not user:
        raise credentials_exception
    
    return user

def get_optional_user(db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)):
    if not token:
        return None
    try:
        session = db.query(models.UserSession).filter(models.UserSession.token == token).first()
        if not session or (session.expires_at and session.expires_at < datetime.utcnow()):
            return None
        return session.user
    except:
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

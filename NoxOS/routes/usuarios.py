from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database.config import get_db
from database.models import Usuario
from schemas.schemas import (
    UsuarioCreate, UsuarioResponse, UsuarioUpdate, LoginRequest, TokenResponse
)
from utils.security import hash_password, verify_password, create_access_token
from utils.logger import logger
from core.config import settings

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])

@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def registro(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario
    """
    try:
        # Verificar si el email ya existe
        db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
        if db_usuario:
            logger.warning(f"Intento de registro con email existente: {usuario.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=usuario.nombre,
            email=usuario.email,
            password=hash_password(usuario.password),
            activo=usuario.activo
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        logger.info(f"Nuevo usuario registrado: {nuevo_usuario.email}")
        return nuevo_usuario
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al registrar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar el usuario"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credenciales: LoginRequest, db: Session = Depends(get_db)):
    """
    Autenticarse y obtener token JWT
    """
    try:
        # Buscar usuario
        usuario = db.query(Usuario).filter(Usuario.email == credenciales.email).first()
        
        if not usuario or not verify_password(credenciales.password, usuario.password):
            logger.warning(f"Intento de login fallido: {credenciales.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not usuario.activo:
            logger.warning(f"Login intento con usuario inactivo: {usuario.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        
        # Crear token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": usuario.email, "user_id": usuario.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Usuario autenticado: {usuario.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en autenticación"
        )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Obtener información de un usuario por ID
    """
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return usuario
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener usuario"
        )


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar información de un usuario
    """
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Actualizar campos si se proporcionan
        if usuario_update.nombre:
            usuario.nombre = usuario_update.nombre
        if usuario_update.email:
            usuario.email = usuario_update.email
        if usuario_update.activo is not None:
            usuario.activo = usuario_update.activo
        
        db.commit()
        db.refresh(usuario)
        
        logger.info(f"Usuario actualizado: {usuario.email}")
        return usuario
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar usuario"
        )


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un usuario
    """
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        db.delete(usuario)
        db.commit()
        
        logger.info(f"Usuario eliminado: {usuario.email}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar usuario"
        )


@router.get("/", response_model=list[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Listar todos los usuarios (con paginación)
    """
    try:
        usuarios = db.query(Usuario).offset(skip).limit(limit).all()
        return usuarios
        
    except Exception as e:
        logger.error(f"Error al listar usuarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar usuarios"
        )

# coding=utf-8
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from database.models import Usuario
from schemas.schemas import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from utils.logger import logger
from core.config import settings

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario
    """
    try:
        # Verificar si el email ya existe
        db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
        if db_usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        nuevo_usuario = Usuario(
            nombre=usuario.nombre,
            email=usuario.email,
            password=usuario.password,
            activo=usuario.activo
        )

        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        logger.info(f"Usuario creado: {nuevo_usuario.email}")
        return nuevo_usuario

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear usuario: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al crear usuario"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/", response_model=list[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 10,
    activo: bool = None,
    db: Session = Depends(get_db)
):
    """
    Listar todos los usuarios con filtros opcionales
    """
    try:
        query = db.query(Usuario)

        if activo is not None:
            query = query.filter(Usuario.activo == activo)

        usuarios = query.offset(skip).limit(limit).all()
        return usuarios

    except Exception as e:
        logger.error(f"Error al listar usuarios: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al listar usuarios"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Obtener un usuario por ID
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
        detail = str(e) if settings.DEBUG else "Error al obtener usuario"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar información de un usuario (UPDATE)
    """
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Verificar email único si se cambia
        if usuario_update.email and usuario_update.email != usuario.email:
            email_existente = db.query(Usuario).filter(
                Usuario.email == usuario_update.email
            ).first()
            if email_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está en uso por otro usuario"
                )

        # Actualizar campos
        datos_actualizacion = usuario_update.dict(exclude_unset=True)
        for campo, valor in datos_actualizacion.items():
            setattr(usuario, campo, valor)

        db.commit()
        db.refresh(usuario)

        logger.info(f"Usuario actualizado: {usuario.email}")
        return usuario

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar usuario: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al actualizar usuario"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un usuario (DELETE)
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
        detail = str(e) if settings.DEBUG else "Error al eliminar usuario"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

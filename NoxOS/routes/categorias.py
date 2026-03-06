from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from database.models import Categoria
from schemas.schemas import CategoriaCreate, CategoriaResponse, CategoriaUpdate
from utils.logger import logger
from core.config import settings

router = APIRouter(prefix="/api/v1/categorias", tags=["Categorías"])


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva categoría
    """
    try:
        nueva_categoria = Categoria(**categoria.dict())
        db.add(nueva_categoria)
        db.commit()
        db.refresh(nueva_categoria)
        
        logger.info(f"Categoría creada: {nueva_categoria.nombre}")
        return nueva_categoria
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear categoría: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al crear categoría"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/", response_model=list[CategoriaResponse])
async def listar_categorias(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Listar todas las categorías
    """
    try:
        categorias = db.query(Categoria).offset(skip).limit(limit).all()
        return categorias
        
    except Exception as e:
        logger.error(f"Error al listar categorías: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al listar categorías"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """
    Obtener una categoría por ID
    """
    try:
        categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
        
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        
        return categoria
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener categoría: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al obtener categoría"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def actualizar_categoria(
    categoria_id: int,
    categoria_update: CategoriaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una categoría
    """
    try:
        categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
        
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        
        datos_actualizacion = categoria_update.dict(exclude_unset=True)
        for campo, valor in datos_actualizacion.items():
            setattr(categoria, campo, valor)
        
        db.commit()
        db.refresh(categoria)
        
        logger.info(f"Categoría actualizada: {categoria.nombre}")
        return categoria
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar categoría: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al actualizar categoría"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """
    Eliminar una categoría
    """
    try:
        categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
        
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        
        db.delete(categoria)
        db.commit()
        
        logger.info(f"Categoría eliminada: {categoria.nombre}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar categoría: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al eliminar categoría"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

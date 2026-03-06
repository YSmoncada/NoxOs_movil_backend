from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from database.models import Producto, Categoria
from schemas.schemas import ProductoCreate, ProductoResponse, ProductoUpdate
from utils.logger import logger
from core.config import settings

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])


@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo producto
    """
    try:
        # Verificar que la categoría existe
        categoria = db.query(Categoria).filter(Categoria.id == producto.categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        
        nuevo_producto = Producto(**producto.dict())
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        
        logger.info(f"Producto creado: {nuevo_producto.nombre}")
        return nuevo_producto
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear producto: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al crear producto"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/", response_model=list[ProductoResponse])
async def listar_productos(
    skip: int = 0,
    limit: int = 10,
    activo: bool = None,
    categoria_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Listar productos con filtros opcionales
    """
    try:
        query = db.query(Producto)
        
        if activo is not None:
            query = query.filter(Producto.activo == activo)
        
        if categoria_id is not None:
            query = query.filter(Producto.categoria_id == categoria_id)
        
        productos = query.offset(skip).limit(limit).all()
        return productos
        
    except Exception as e:
        logger.error(f"Error al listar productos: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al listar productos"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/{producto_id}", response_model=ProductoResponse)
async def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Obtener un producto por ID
    """
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()
        
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        return producto
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener producto: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al obtener producto"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.put("/{producto_id}", response_model=ProductoResponse)
async def actualizar_producto(
    producto_id: int,
    producto_update: ProductoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un producto
    """
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()
        
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Verificar categoría si se actualiza
        if producto_update.categoria_id:
            categoria = db.query(Categoria).filter(Categoria.id == producto_update.categoria_id).first()
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada"
                )
        
        # Actualizar campos
        datos_actualizacion = producto_update.dict(exclude_unset=True)
        for campo, valor in datos_actualizacion.items():
            setattr(producto, campo, valor)
        
        db.commit()
        db.refresh(producto)
        
        logger.info(f"Producto actualizado: {producto.nombre}")
        return producto
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar producto: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al actualizar producto"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un producto
    """
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()
        
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        db.delete(producto)
        db.commit()
        
        logger.info(f"Producto eliminado: {producto.nombre}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar producto: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al eliminar producto"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

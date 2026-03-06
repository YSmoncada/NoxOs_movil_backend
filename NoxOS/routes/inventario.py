from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from database.models import MovimientoInventario, Producto, TipoMovimiento, Usuario
from schemas.schemas import MovimientoInventarioCreate, MovimientoInventarioResponse, MovimientoInventarioUpdate
from utils.logger import logger
from core.config import settings

router = APIRouter(prefix="/api/v1/inventario", tags=["Inventario"])


@router.post("/movimientos", response_model=MovimientoInventarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_movimiento(
    movimiento: MovimientoInventarioCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar un movimiento de inventario
    """
    try:
        # Verificar que el producto existe
        producto = db.query(Producto).filter(Producto.id == movimiento.producto_id).first()
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Verificar que el tipo de movimiento existe
        tipo = db.query(TipoMovimiento).filter(TipoMovimiento.id == movimiento.tipo_id).first()
        if not tipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de movimiento no encontrado"
            )
        
        # Aquí debería venir del token JWT, por ahora usamos 1
        usuario_id = 1
        
        # Crear movimiento
        nuevo_movimiento = MovimientoInventario(
            producto_id=movimiento.producto_id,
            tipo_id=movimiento.tipo_id,
            cantidad=movimiento.cantidad,
            motivo=movimiento.motivo,
            usuario_id=usuario_id
        )
        
        # Actualizar stock del producto según el tipo de movimiento
        if tipo.nombre == "ENTRADA":
            producto.stock_actual += movimiento.cantidad
        elif tipo.nombre == "SALIDA":
            if producto.stock_actual < movimiento.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Stock insuficiente para realizar esta salida"
                )
            producto.stock_actual -= movimiento.cantidad
        elif tipo.nombre in ["AJUSTE", "MERMA"]:
            producto.stock_actual -= movimiento.cantidad
        
        db.add(nuevo_movimiento)
        db.commit()
        db.refresh(nuevo_movimiento)
        
        logger.info(f"Movimiento de inventario creado: {tipo.nombre} de {movimiento.cantidad} {producto.nombre}")
        return nuevo_movimiento
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear movimiento de inventario: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al crear movimiento de inventario"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/movimientos", response_model=list[MovimientoInventarioResponse])
async def listar_movimientos(
    skip: int = 0,
    limit: int = 10,
    producto_id: int = None,
    tipo_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Listar movimientos de inventario
    """
    try:
        query = db.query(MovimientoInventario)
        
        if producto_id is not None:
            query = query.filter(MovimientoInventario.producto_id == producto_id)
        
        if tipo_id is not None:
            query = query.filter(MovimientoInventario.tipo_id == tipo_id)
        
        movimientos = query.order_by(MovimientoInventario.fecha.desc()).offset(skip).limit(limit).all()
        return movimientos
        
    except Exception as e:
        logger.error(f"Error al listar movimientos: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al listar movimientos"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/movimientos/{movimiento_id}", response_model=MovimientoInventarioResponse)
async def obtener_movimiento(movimiento_id: int, db: Session = Depends(get_db)):
    """
    Obtener un movimiento de inventario por ID
    """
    try:
        movimiento = db.query(MovimientoInventario).filter(
            MovimientoInventario.id == movimiento_id
        ).first()
        
        if not movimiento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimiento no encontrado"
            )
        
        return movimiento
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener movimiento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener movimiento"
        )


@router.put("/movimientos/{movimiento_id}", response_model=MovimientoInventarioResponse)
async def actualizar_movimiento(
    movimiento_id: int,
    movimiento_update: MovimientoInventarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un movimiento de inventario (UPDATE)
    Solo permite modificar el motivo y la cantidad (sin recalcular stock)
    """
    try:
        movimiento = db.query(MovimientoInventario).filter(
            MovimientoInventario.id == movimiento_id
        ).first()

        if not movimiento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimiento no encontrado"
            )

        # Actualizar campos
        datos_actualizacion = movimiento_update.dict(exclude_unset=True)
        for campo, valor in datos_actualizacion.items():
            setattr(movimiento, campo, valor)

        db.commit()
        db.refresh(movimiento)

        logger.info(f"Movimiento actualizado: ID {movimiento.id}")
        return movimiento

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar movimiento: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al actualizar movimiento"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.delete("/movimientos/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_movimiento(movimiento_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un movimiento de inventario (DELETE)
    """
    try:
        movimiento = db.query(MovimientoInventario).filter(
            MovimientoInventario.id == movimiento_id
        ).first()

        if not movimiento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimiento no encontrado"
            )

        db.delete(movimiento)
        db.commit()

        logger.info(f"Movimiento eliminado: ID {movimiento_id}")

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar movimiento: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al eliminar movimiento"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/productos/{producto_id}/stock")
async def obtener_stock_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Obtener el stock actual de un producto
    """
    try:
        producto = db.query(Producto).filter(Producto.id == producto_id).first()

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )

        return {
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "stock_actual": producto.stock_actual,
            "activo": producto.activo
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener stock"
        )

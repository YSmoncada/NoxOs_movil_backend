from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from database.config import get_db
from database.models import (
    Pedido, PedidoProducto, Producto, Mesa, EstadoPedido, Usuario
)
from schemas.schemas import PedidoCreate, PedidoResponse, PedidoUpdate
from utils.logger import logger
from core.config import settings

router = APIRouter(prefix="/api/v1/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def crear_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo pedido con sus productos
    """
    try:
        # Verificar que la mesa existe
        mesa = db.query(Mesa).filter(Mesa.id == pedido.mesa_id).first()
        if not mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesa no encontrada"
            )
        
        # Verificar que hay productos
        if not pedido.productos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pedido debe tener al menos un producto"
            )
        
        # Obtener ID de usuario (aquí debería venir del token JWT, par este ejemplo usamos 1)
        usuario_id = 1
        
        # Obtener estado "ABIERTO"
        estado_abierto = db.query(EstadoPedido).filter(
            EstadoPedido.nombre == "ABIERTO"
        ).first()
        
        if not estado_abierto:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Estado ABIERTO no encontrado en base de datos"
            )
        
        # Crear pedido
        nuevo_pedido = Pedido(
            mesa_id=pedido.mesa_id,
            estado_id=estado_abierto.id,
            creado_por=usuario_id,
            total=Decimal("0")
        )
        
        total_pedido = Decimal("0")
        
        # Agregar productos al pedido
        for pp in pedido.productos:
            # Verificar que el producto existe
            producto = db.query(Producto).filter(Producto.id == pp.producto_id).first()
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con ID {pp.producto_id} no encontrado"
                )
            
            # Verificar stock
            if producto.stock_actual < pp.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para {producto.nombre}"
                )
            
            # Crear relación pedido-producto
            pedido_producto = PedidoProducto(
                producto_id=pp.producto_id,
                cantidad=pp.cantidad,
                precio_unitario=pp.precio_unitario
            )
            nuevo_pedido.productos.append(pedido_producto)
            
            # Calcular total
            total_pedido += pp.precio_unitario * pp.cantidad
        
        nuevo_pedido.total = total_pedido
        
        db.add(nuevo_pedido)
        db.commit()
        db.refresh(nuevo_pedido)
        
        logger.info(f"Pedido creado: ID {nuevo_pedido.id}, Mesa {mesa.numero}, Total: {total_pedido}")
        return nuevo_pedido
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear pedido: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al crear pedido"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/", response_model=list[PedidoResponse])
async def listar_pedidos(
    skip: int = 0,
    limit: int = 10,
    estado_id: int = None,
    mesa_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Listar pedidos con filtros opcionales
    """
    try:
        query = db.query(Pedido)
        
        if estado_id is not None:
            query = query.filter(Pedido.estado_id == estado_id)
        
        if mesa_id is not None:
            query = query.filter(Pedido.mesa_id == mesa_id)
        
        pedidos = query.offset(skip).limit(limit).all()
        return pedidos
        
    except Exception as e:
        logger.error(f"Error al listar pedidos: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al listar pedidos"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/{pedido_id}", response_model=PedidoResponse)
async def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Obtener un pedido por ID
    """
    try:
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        return pedido
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener pedido: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al obtener pedido"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.put("/{pedido_id}", response_model=PedidoResponse)
async def actualizar_pedido(
    pedido_id: int,
    pedido_update: PedidoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar estado de un pedido
    """
    try:
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        # Verificar estado si se actualiza
        if pedido_update.estado_id:
            estado = db.query(EstadoPedido).filter(
                EstadoPedido.id == pedido_update.estado_id
            ).first()
            if not estado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Estado no encontrado"
                )
            pedido.estado_id = pedido_update.estado_id
        
        if pedido_update.total is not None:
            pedido.total = pedido_update.total
        
        db.commit()
        db.refresh(pedido)
        
        logger.info(f"Pedido actualizado: ID {pedido.id}")
        return pedido
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar pedido: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al actualizar pedido"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un pedido
    """
    try:
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        db.delete(pedido)
        db.commit()
        
        logger.info(f"Pedido eliminado: ID {pedido.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar pedido: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al eliminar pedido"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

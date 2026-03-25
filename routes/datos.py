from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from database.models import (
    EstadoMesa, EstadoPedido, TipoMovimiento, TipoFactura
)
from schemas.schemas import (
    EstadoMesaResponse, EstadoPedidoResponse, 
    TipoMovimientoResponse, TipoFacturaResponse
)
from utils.logger import logger
from core.config import settings

router = APIRouter(prefix="/api/v1/datos", tags=["Datos"])


@router.get("/estados-mesa", response_model=list[EstadoMesaResponse])
async def obtener_estados_mesa(db: Session = Depends(get_db)):
    """
    Obtener todos los estados de mesa
    """
    try:
        estados = db.query(EstadoMesa).all()
        return estados
    except Exception as e:
        logger.error(f"Error al obtener estados mesa: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al obtener estados"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/estados-pedido", response_model=list[EstadoPedidoResponse])
async def obtener_estados_pedido(db: Session = Depends(get_db)):
    """
    Obtener todos los estados de pedido
    """
    try:
        estados = db.query(EstadoPedido).all()
        return estados
    except Exception as e:
        logger.error(f"Error al obtener estados pedido: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al obtener estados"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/tipos-movimiento", response_model=list[TipoMovimientoResponse])
async def obtener_tipos_movimiento(db: Session = Depends(get_db)):
    """
    Obtener todos los tipos de movimiento de inventario
    """
    try:
        tipos = db.query(TipoMovimiento).all()
        return tipos
    except Exception as e:
        logger.error(f"Error al obtener tipos movimiento: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al obtener tipos"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/tipos-factura", response_model=list[TipoFacturaResponse])
async def obtener_tipos_factura(db: Session = Depends(get_db)):
    """
    Obtener todos los tipos de factura
    """
    try:
        tipos = db.query(TipoFactura).all()
        return tipos
    except Exception as e:
        logger.error(f"Error al obtener tipos factura: {str(e)}")
        detail = str(e) if settings.DEBUG else "Error al obtener tipos"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

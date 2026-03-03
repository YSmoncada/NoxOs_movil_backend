from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from database.models import Factura, Pedido, TipoFactura
from schemas.schemas import FacturaCreate, FacturaResponse
from utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/api/v1/facturas", tags=["Facturas"])


def generar_numero_factura(db: Session, tipo_id: int) -> str:
    """
    Generar un número de factura único basado en fecha y tipo
    """
    tipo = db.query(TipoFactura).filter(TipoFactura.id == tipo_id).first()
    
    if not tipo:
        return None
    
    # Obtener el número del tipo (primera letra)
    tipo_letra = tipo.nombre[0]  # T para TICKET, F para FACTURA
    
    # Obtener el siguiente número secuencial
    contador = db.query(Factura).filter(
        Factura.tipo_id == tipo_id
    ).count()
    
    fecha_actual = datetime.utcnow()
    numero = f"{tipo_letra}{fecha_actual.strftime('%Y%m%d')}{str(contador + 1).zfill(6)}"
    
    return numero


@router.post("/", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
async def crear_factura(factura: FacturaCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva factura
    """
    try:
        # Verificar que el pedido existe
        pedido = db.query(Pedido).filter(Pedido.id == factura.pedido_id).first()
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado"
            )
        
        # Verificar que el tipo de factura existe
        tipo = db.query(TipoFactura).filter(TipoFactura.id == factura.tipo_id).first()
        if not tipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de factura no encontrado"
            )
        
        # Verificar que el número es único
        factura_existente = db.query(Factura).filter(
            Factura.numero == factura.numero
        ).first()
        if factura_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este número de factura ya está registrado"
            )
        
        # Crear factura
        nueva_factura = Factura(
            pedido_id=factura.pedido_id,
            numero=factura.numero,
            tipo_id=factura.tipo_id,
            total=factura.total
        )
        
        db.add(nueva_factura)
        db.commit()
        db.refresh(nueva_factura)
        
        logger.info(f"Factura creada: {nueva_factura.numero}, Total: {nueva_factura.total}")
        return nueva_factura
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear factura: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear factura"
        )


@router.get("/", response_model=list[FacturaResponse])
async def listar_facturas(
    skip: int = 0,
    limit: int = 10,
    tipo_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Listar facturas
    """
    try:
        query = db.query(Factura)
        
        if tipo_id is not None:
            query = query.filter(Factura.tipo_id == tipo_id)
        
        facturas = query.order_by(Factura.fecha.desc()).offset(skip).limit(limit).all()
        return facturas
        
    except Exception as e:
        logger.error(f"Error al listar facturas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar facturas"
        )


@router.get("/{factura_id}", response_model=FacturaResponse)
async def obtener_factura(factura_id: int, db: Session = Depends(get_db)):
    """
    Obtener una factura por ID
    """
    try:
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        
        if not factura:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada"
            )
        
        return factura
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener factura: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener factura"
        )


@router.get("/numero/generar/{tipo_id}")
async def generar_numero(tipo_id: int, db: Session = Depends(get_db)):
    """
    Generar un número de factura automático
    """
    try:
        numero = generar_numero_factura(db, tipo_id)
        
        if not numero:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de factura no encontrado"
            )
        
        return {"numero": numero}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar número: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar número de factura"
        )

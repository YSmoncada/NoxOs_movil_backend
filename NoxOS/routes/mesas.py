from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from database.models import Mesa, EstadoMesa
from schemas.schemas import MesaCreate, MesaResponse, MesaUpdate
from utils.logger import logger

router = APIRouter(prefix="/api/v1/mesas", tags=["Mesas"])


@router.post("/", response_model=MesaResponse, status_code=status.HTTP_201_CREATED)
async def crear_mesa(mesa: MesaCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva mesa
    """
    try:
        # Verificar que el estado existe
        estado = db.query(EstadoMesa).filter(EstadoMesa.id == mesa.estado_id).first()
        if not estado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estado no encontrado"
            )
        
        # Verificar que el número de mesa sea único
        mesa_existente = db.query(Mesa).filter(Mesa.numero == mesa.numero).first()
        if mesa_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una mesa con este número"
            )
        
        nueva_mesa = Mesa(**mesa.dict())
        db.add(nueva_mesa)
        db.commit()
        db.refresh(nueva_mesa)
        
        logger.info(f"Mesa creada: {nueva_mesa.numero}")
        return nueva_mesa
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear mesa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear mesa"
        )


@router.get("/", response_model=list[MesaResponse])
async def listar_mesas(
    skip: int = 0,
    limit: int = 10,
    estado_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Listar todas las mesas con filtros opcionales
    """
    try:
        query = db.query(Mesa)
        
        if estado_id is not None:
            query = query.filter(Mesa.estado_id == estado_id)
        
        mesas = query.offset(skip).limit(limit).all()
        return mesas
        
    except Exception as e:
        logger.error(f"Error al listar mesas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar mesas"
        )


@router.get("/{mesa_id}", response_model=MesaResponse)
async def obtener_mesa(mesa_id: int, db: Session = Depends(get_db)):
    """
    Obtener una mesa por ID
    """
    try:
        mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        
        if not mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesa no encontrada"
            )
        
        return mesa
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener mesa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener mesa"
        )


@router.put("/{mesa_id}", response_model=MesaResponse)
async def actualizar_mesa(
    mesa_id: int,
    mesa_update: MesaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una mesa
    """
    try:
        mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        
        if not mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesa no encontrada"
            )
        
        # Verificar estado si se actualiza
        if mesa_update.estado_id:
            estado = db.query(EstadoMesa).filter(EstadoMesa.id == mesa_update.estado_id).first()
            if not estado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Estado no encontrado"
                )
        
        # Verificar número único si se actualiza
        if mesa_update.numero and mesa_update.numero != mesa.numero:
            mesa_existente = db.query(Mesa).filter(Mesa.numero == mesa_update.numero).first()
            if mesa_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe una mesa con este número"
                )
        
        datos_actualizacion = mesa_update.dict(exclude_unset=True)
        for campo, valor in datos_actualizacion.items():
            setattr(mesa, campo, valor)
        
        db.commit()
        db.refresh(mesa)
        
        logger.info(f"Mesa actualizada: {mesa.numero}")
        return mesa
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar mesa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar mesa"
        )


@router.delete("/{mesa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_mesa(mesa_id: int, db: Session = Depends(get_db)):
    """
    Eliminar una mesa
    """
    try:
        mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        
        if not mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesa no encontrada"
            )
        
        db.delete(mesa)
        db.commit()
        
        logger.info(f"Mesa eliminada: {mesa.numero}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar mesa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar mesa"
        )

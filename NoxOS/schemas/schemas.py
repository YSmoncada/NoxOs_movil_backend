from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Schemas: Usuario

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe tener al menos una mayúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe tener al menos un número')
        return v

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UsuarioResponseWithRoles(UsuarioResponse):
    roles: List['RolResponse'] = []



# Schemas: Rol

class RolBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)

class RolCreate(RolBase):
    pass

class RolResponse(RolBase):
    id: int
    
    class Config:
        from_attributes = True



# Schemas: Categoría

class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)

class CategoriaResponse(CategoriaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True



# Schemas: Producto

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    precio: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    stock_actual: int = Field(default=0, ge=0)
    activo: bool = True
    categoria_id: int

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    precio: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    stock_actual: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None
    categoria_id: Optional[int] = None

class ProductoResponse(ProductoBase):
    id: int
    created_at: datetime
    categoria: CategoriaResponse
    
    class Config:
        from_attributes = True



# Schemas: Mesa

class MesaBase(BaseModel):
    numero: int = Field(..., gt=0)
    estado_id: int

class MesaCreate(MesaBase):
    pass

class MesaUpdate(BaseModel):
    numero: Optional[int] = Field(None, gt=0)
    estado_id: Optional[int] = None

class MesaResponse(MesaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True



# Schemas: Pedido

class PedidoProductoCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)

class PedidoProductoResponse(PedidoProductoCreate):
    id: int
    cantidad_despachada: int
    
    class Config:
        from_attributes = True

class PedidoBase(BaseModel):
    mesa_id: int
    estado_id: int

class PedidoCreate(BaseModel):
    mesa_id: int
    productos: List[PedidoProductoCreate]

class PedidoUpdate(BaseModel):
    estado_id: Optional[int] = None
    total: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)

class PedidoResponse(BaseModel):
    id: int
    fecha_hora: datetime
    estado_id: int
    total: Decimal
    mesa_id: int
    creado_por: int
    updated_at: datetime
    productos: List[PedidoProductoResponse] = []
    
    class Config:
        from_attributes = True



# Schemas: Movimiento de Inventario

class MovimientoInventarioCreate(BaseModel):
    producto_id: int
    tipo_id: int
    cantidad: int
    motivo: Optional[str] = Field(None, max_length=255)

class MovimientoInventarioResponse(MovimientoInventarioCreate):
    id: int
    fecha: datetime
    usuario_id: int
    
    class Config:
        from_attributes = True



# Schemas: Factura

class FacturaCreate(BaseModel):
    pedido_id: int
    numero: str = Field(..., min_length=1, max_length=50)
    tipo_id: int
    total: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)

class FacturaResponse(FacturaCreate):
    id: int
    fecha: datetime
    
    class Config:
        from_attributes = True



# Schemas: Estados

class EstadoMesaResponse(BaseModel):
    id: int
    nombre: str
    
    class Config:
        from_attributes = True

class EstadoPedidoResponse(BaseModel):
    id: int
    nombre: str
    
    class Config:
        from_attributes = True

class TipoMovimientoResponse(BaseModel):
    id: int
    nombre: str
    
    class Config:
        from_attributes = True

class TipoFacturaResponse(BaseModel):
    id: int
    nombre: str
    
    class Config:
        from_attributes = True



# Schemas: Autenticación

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

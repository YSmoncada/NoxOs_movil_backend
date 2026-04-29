from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
from decimal import Decimal

# Base schemas
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    nombre_completo: Optional[str] = None
    activo: bool = True

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "usuario"

class UserUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    activo: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: datetime
    user_role: Optional[str] = None
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    token: str
    refresh: str
    role: str
    username: str
    nombre: str
    user_id: int
    detail: str

class TokenData(BaseModel):
    username: Optional[str] = None

class TokenRefreshResponse(BaseModel):
    token: str

# Role schemas
class RolBase(BaseModel):
    nombre: str

class RolCreate(RolBase):
    pass

class Rol(RolBase):
    id: int
    class Config:
        from_attributes = True

# Category schemas
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class Categoria(CategoriaBase):
    id: int
    class Config:
        from_attributes = True

# Product schemas
class ProductoBase(BaseModel):
    nombre: str
    precio: Decimal
    stock_actual: int = 0
    activo: bool = True
    categoria: Optional[int] = None
    imagen: Optional[str] = None
    categoria_nombre: Optional[str] = None

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[Decimal] = None
    stock_actual: Optional[int] = None
    activo: Optional[bool] = None
    categoria: Optional[int] = None
    imagen: Optional[str] = None

class Producto(ProductoBase):
    id: int
    class Config:
        from_attributes = True

# Order schemas
class PedidoProductoBase(BaseModel):
    producto_id: Optional[int] = None
    cantidad: int
    precio_unitario: Optional[Decimal] = None

class PedidoProductoCreate(PedidoProductoBase):
    pass

class PedidoProducto(PedidoProductoBase):
    id: int
    cantidad_despachada: int
    producto_nombre: Optional[str] = None
    producto_precio: Optional[Decimal] = None
    class Config:
        from_attributes = True

class PedidoBase(BaseModel):
    mesa: int
    estado: Optional[Union[int, str]] = None
    total: Decimal = Decimal(0)
    estado_nombre: Optional[str] = None
    mesa_numero: Optional[int] = None
    creado_por: Optional[int] = None
    pidiendo_cuenta: Optional[bool] = False

class PedidoCreate(PedidoBase):
    productos: Optional[List[PedidoProductoCreate]] = None
    detalles: Optional[List[PedidoProductoCreate]] = None
    usuario: Optional[int] = None # Alias para creado_por enviado por el móvil
    force_append: Optional[bool] = False

class Pedido(PedidoBase):
    id: int
    fecha_hora: datetime
    creado_por: Optional[int] = None
    usuario_nombre: Optional[str] = None
    detalles: List[PedidoProducto]
    productos_detalle: Optional[List[PedidoProducto]] = None # Alias para el móvil
    class Config:
        from_attributes = True

class PedidoSimplified(PedidoBase):
    pass

class PedidoUpdate(BaseModel):
    mesa: Optional[int] = None
    estado: Optional[Union[int, str]] = None
    estado_nombre: Optional[str] = None
    total: Optional[Decimal] = None

# Mesa schemas
class MesaBase(BaseModel):
    numero: int
    capacidad: Optional[int] = 1
    estado: Optional[int] = None
    estado_nombre: Optional[str] = None
    mesero_id: Optional[int] = None
    mesero_nombre: Optional[str] = None
    pidiendo_cuenta: Optional[bool] = False

class MesaUpdate(BaseModel):
    numero: Optional[int] = None
    capacidad: Optional[int] = None
    estado: Optional[int] = None
    mesero_id: Optional[int] = None
    pidiendo_cuenta: Optional[bool] = None

class Mesa(MesaBase):
    id: int
    class Config:
        from_attributes = True

# State schemas
class EstadoBase(BaseModel):
    nombre: str

class Estado(EstadoBase):
    id: int
    class Config:
        from_attributes = True

# Config schemas
class EmpresaConfigUpdate(BaseModel):
    nombre: Optional[str] = None
    nit: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    mensaje_footer: Optional[str] = None
    moneda: Optional[str] = None
    impuesto_porcentaje: Optional[Decimal] = None

class EmpresaConfigBase(BaseModel):
    nombre: str
    nit: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    mensaje_footer: str = "¡Gracias por su visita!"
    moneda: str = "$"
    impuesto_porcentaje: Decimal = Decimal(0)

class EmpresaConfig(EmpresaConfigBase):
    id: int
    class Config:
        from_attributes = True

# Movimiento Inventario schemas
class TipoMovimientoBase(BaseModel):
    nombre: str

class TipoMovimiento(TipoMovimientoBase):
    id: int
    class Config:
        from_attributes = True

class MovimientoInventarioBase(BaseModel):
    producto_id: int
    tipo_id: int
    cantidad: int
    motivo: Optional[str] = None

class MovimientoInventarioCreate(MovimientoInventarioBase):
    pass

class MovimientoInventario(MovimientoInventarioBase):
    id: int
    fecha: datetime
    usuario_id: Optional[int] = None
    producto_nombre: Optional[str] = None
    tipo_nombre: Optional[str] = None
    usuario_nombre: Optional[str] = None
    class Config:
        from_attributes = True

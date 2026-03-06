from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database.config import Base

# =====================
# Modelo: Usuario
# =====================
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    roles = relationship("UsuarioRol", back_populates="usuario", cascade="all, delete-orphan")
    pedidos = relationship("Pedido", back_populates="creado_por_usuario", foreign_keys="Pedido.creado_por")
    movimientos = relationship("MovimientoInventario", back_populates="usuario")


# =====================
# Modelo: Rol
# =====================
class Rol(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(String(255))
    
    # Relaciones
    usuarios = relationship("UsuarioRol", back_populates="rol")


# =====================
# Modelo: UsuarioRol
# =====================
class UsuarioRol(Base):
    __tablename__ = "usuario_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    __table_args__ = (
        UniqueConstraint('usuario_id', 'rol_id', name='unique_usuario_rol'),
    )
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="roles")
    rol = relationship("Rol", back_populates="usuarios")


# =====================
# Modelos de Estados (Dominio)
# =====================
class EstadoMesa(Base):
    __tablename__ = "estados_mesa"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relaciones
    mesas = relationship("Mesa", back_populates="estado")


class EstadoPedido(Base):
    __tablename__ = "estados_pedido"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relaciones
    pedidos = relationship("Pedido", back_populates="estado")


class TipoMovimiento(Base):
    __tablename__ = "tipos_movimiento"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relaciones
    movimientos = relationship("MovimientoInventario", back_populates="tipo")


class TipoFactura(Base):
    __tablename__ = "tipos_factura"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relaciones
    facturas = relationship("Factura", back_populates="tipo")


# =====================
# Modelos de Catálogo
# =====================
class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    productos = relationship("Producto", back_populates="categoria", cascade="all, delete-orphan")


class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    precio = Column(Numeric(10, 2), nullable=False)
    stock_actual = Column(Integer, default=0, nullable=False)
    activo = Column(Boolean, default=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    pedido_productos = relationship("PedidoProducto", back_populates="producto", cascade="all, delete-orphan")
    movimientos = relationship("MovimientoInventario", back_populates="producto", cascade="all, delete-orphan")


# =====================
# Modelos de Operación
# =====================
class Mesa(Base):
    __tablename__ = "mesas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, unique=True, nullable=False, index=True)
    estado_id = Column(Integer, ForeignKey("estados_mesa.id", ondelete="RESTRICT"), nullable=False, index=True)  # RESTRICT: no se puede borrar un estado si hay mesas
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    estado = relationship("EstadoMesa", back_populates="mesas")
    pedidos = relationship("Pedido", back_populates="mesa", cascade="all, delete-orphan")


class Pedido(Base):
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(DateTime, default=datetime.utcnow, index=True)
    estado_id = Column(Integer, ForeignKey("estados_pedido.id", ondelete="RESTRICT"), nullable=False, index=True)
    total = Column(Numeric(10, 2), default=0, nullable=False)
    mesa_id = Column(Integer, ForeignKey("mesas.id", ondelete="CASCADE"), nullable=False, index=True)
    creado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    estado = relationship("EstadoPedido", back_populates="pedidos")
    mesa = relationship("Mesa", back_populates="pedidos")
    creado_por_usuario = relationship("Usuario", back_populates="pedidos", foreign_keys=[creado_por])
    productos = relationship("PedidoProducto", back_populates="pedido", cascade="all, delete-orphan")
    facturas = relationship("Factura", back_populates="pedido", cascade="all, delete-orphan")


class PedidoProducto(Base):
    __tablename__ = "pedido_productos"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)
    cantidad_despachada = Column(Integer, default=0, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="productos")
    producto = relationship("Producto", back_populates="pedido_productos")


class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"
    
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_id = Column(Integer, ForeignKey("tipos_movimiento.id", ondelete="RESTRICT"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String(255))
    fecha = Column(DateTime, default=datetime.utcnow, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Relaciones
    producto = relationship("Producto", back_populates="movimientos")
    tipo = relationship("TipoMovimiento", back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos")


# =====================
# Modelo: Factura
# =====================
class Factura(Base):
    __tablename__ = "facturas"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False, index=True)  # CASCADE: factura se borra si se borra el pedido
    numero = Column(String(50), unique=True, nullable=False, index=True)
    tipo_id = Column(Integer, ForeignKey("tipos_factura.id", ondelete="RESTRICT"), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="facturas")
    tipo = relationship("TipoFactura", back_populates="facturas")

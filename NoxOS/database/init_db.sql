-- =====================
-- Base de Datos: discoteca_app
-- Motor: MariaDB
-- Codificación: utf8mb4
-- Sistema de Pedidos por QR para Discotecas
-- =====================

DROP DATABASE IF EXISTS discoteca_app;
CREATE DATABASE discoteca_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE discoteca_app;

-- =====================
-- Tabla: usuarios
-- =====================
CREATE TABLE usuarios (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  activo BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_email (email),
  INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================
-- Tabla: roles
-- =====================
CREATE TABLE roles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(50) UNIQUE NOT NULL,
  descripcion VARCHAR(255),
  INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================
-- Tabla: usuario_roles
-- =====================
CREATE TABLE usuario_roles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  usuario_id INT NOT NULL,
  rol_id INT NOT NULL,
  UNIQUE KEY unique_usuario_rol (usuario_id, rol_id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
  INDEX idx_usuario_id (usuario_id),
  INDEX idx_rol_id (rol_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================
-- Tablas de Estados (Dominio)
-- =====================
CREATE TABLE estados_mesa (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(50) UNIQUE NOT NULL,
  INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE estados_pedido (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(50) UNIQUE NOT NULL,
  INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tipos_movimiento (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(50) UNIQUE NOT NULL,
  INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tipos_factura (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(50) UNIQUE NOT NULL,
  INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================
-- Tablas de Catálogo
-- =====================
CREATE TABLE categorias (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  descripcion VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE productos (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  precio DECIMAL(10, 2) NOT NULL,
  stock_actual INT NOT NULL DEFAULT 0,
  activo BOOLEAN DEFAULT TRUE,
  categoria_id INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE,
  INDEX idx_nombre (nombre),
  INDEX idx_activo (activo),
  INDEX idx_categoria_id (categoria_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================
-- Tablas de Operación
-- =====================
CREATE TABLE mesas (
  id INT PRIMARY KEY AUTO_INCREMENT,
  numero INT NOT NULL UNIQUE,
  estado_id INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (estado_id) REFERENCES estados_mesa(id) ON DELETE RESTRICT,
  INDEX idx_numero (numero),
  INDEX idx_estado_id (estado_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pedidos (
  id INT PRIMARY KEY AUTO_INCREMENT,
  fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
  estado_id INT NOT NULL,
  total DECIMAL(10, 2) NOT NULL DEFAULT 0,
  mesa_id INT NOT NULL,
  creado_por INT,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (estado_id) REFERENCES estados_pedido(id) ON DELETE RESTRICT,
  FOREIGN KEY (mesa_id) REFERENCES mesas(id) ON DELETE CASCADE,
  FOREIGN KEY (creado_por) REFERENCES usuarios(id) ON DELETE CASCADE,
  INDEX idx_fecha_hora (fecha_hora),
  INDEX idx_estado_id (estado_id),
  INDEX idx_mesa_id (mesa_id),
  INDEX idx_creado_por (creado_por)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pedido_productos (
  id INT PRIMARY KEY AUTO_INCREMENT,
  pedido_id INT NOT NULL,
  producto_id INT NOT NULL,
  cantidad INT NOT NULL,
  cantidad_despachada INT NOT NULL DEFAULT 0,
  precio_unitario DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
  FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
  INDEX idx_pedido_id (pedido_id),
  INDEX idx_producto_id (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE movimientos_inventario (
  id INT PRIMARY KEY AUTO_INCREMENT,
  producto_id INT NOT NULL,
  tipo_id INT NOT NULL,
  cantidad INT NOT NULL,
  motivo VARCHAR(255),
  fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
  usuario_id INT,
  FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
  FOREIGN KEY (tipo_id) REFERENCES tipos_movimiento(id) ON DELETE RESTRICT,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  INDEX idx_producto_id (producto_id),
  INDEX idx_tipo_id (tipo_id),
  INDEX idx_fecha (fecha),
  INDEX idx_usuario_id (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================
-- Tabla: facturas
-- =====================
CREATE TABLE facturas (
  id INT PRIMARY KEY AUTO_INCREMENT,
  pedido_id INT NOT NULL,
  numero VARCHAR(50) UNIQUE NOT NULL,
  tipo_id INT NOT NULL,
  total DECIMAL(10, 2) NOT NULL,
  fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
  FOREIGN KEY (tipo_id) REFERENCES tipos_factura(id) ON DELETE RESTRICT,
  INDEX idx_numero (numero),
  INDEX idx_pedido_id (pedido_id),
  INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================
-- Datos Iniciales
-- =====================

-- Insertar roles
INSERT INTO roles (nombre, descripcion) VALUES
('ADMIN', 'Administrador del sistema'),
('MESERO', 'Personal de servicio'),
('BARTENDER', 'Personal de barra/cocina');

-- Insertar estados
INSERT INTO estados_mesa (nombre) VALUES
('LIBRE'),
('OCUPADA'),
('RESERVADA');

INSERT INTO estados_pedido (nombre) VALUES
('ABIERTO'),
('ENVIADO_BARRA'),
('ACEPTADO'),
('RECHAZADO'),
('DESPACHADO'),
('CERRADO'),
('CANCELADO');

INSERT INTO tipos_movimiento (nombre) VALUES
('ENTRADA'),
('SALIDA'),
('AJUSTE'),
('MERMA');

INSERT INTO tipos_factura (nombre) VALUES
('TICKET'),
('FACTURA');

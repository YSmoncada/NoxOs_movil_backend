# coding=utf-8
import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# ─────────────────────────────────────────────
# Conexión a la base de datos
# ─────────────────────────────────────────────
DB_HOST   = "localhost"
DB_PORT   = 3306
DB_NAME   = "discoteca_app"
DB_USER   = "root"
DB_PASSWD = ""

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWD,
        cursorclass=pymysql.cursors.DictCursor
    )

# ─────────────────────────────────────────────
# Mapa completo de dependencias entre tablas
# "tabla_padre": [("tabla_hija", "columna_fk")]
# ─────────────────────────────────────────────
CASCADE_MAP = {
    "categorias":       [("productos",              "categoria_id")],
    "productos":        [("pedido_productos",        "producto_id"),
                         ("movimientos_inventario",  "producto_id")],
    "mesas":            [("pedidos",                 "mesa_id")],
    "pedidos":          [("pedido_productos",        "pedido_id"),
                         ("facturas",                "pedido_id")],
    "usuarios":         [("usuario_roles",           "usuario_id"),
                         ("movimientos_inventario",  "usuario_id"),
                         ("pedidos",                 "creado_por")],
    "roles":            [("usuario_roles",           "rol_id")],
    "estados_mesa":     [("mesas",                   "estado_id")],
    "estados_pedido":   [("pedidos",                 "estado_id")],
    "tipos_movimiento": [("movimientos_inventario",  "tipo_id")],
    "tipos_factura":    [("facturas",                "tipo_id")],
}

# ─────────────────────────────────────────────
# Función recursiva: borra hijos antes que padre
# ─────────────────────────────────────────────
def delete_en_cascada(cur, tabla: str, id: int, eliminados: list):
    """Borra recursivamente todos los registros dependientes antes del padre."""
    if tabla in CASCADE_MAP:
        for tabla_hija, columna_fk in CASCADE_MAP[tabla]:
            # Obtener los IDs de los hijos
            cur.execute(f"SELECT id FROM {tabla_hija} WHERE {columna_fk} = %s", (id,))
            hijos = cur.fetchall()
            for hijo in hijos:
                # Recursión: borrar los hijos del hijo primero
                delete_en_cascada(cur, tabla_hija, hijo["id"], eliminados)
            # Borrar todos los hijos de este nivel
            if hijos:
                cur.execute(f"DELETE FROM {tabla_hija} WHERE {columna_fk} = %s", (id,))
                eliminados.append(f"{len(hijos)} registro(s) de '{tabla_hija}'")
    # Borrar el registro principal
    cur.execute(f"DELETE FROM {tabla} WHERE id = %s", (id,))

# ─────────────────────────────────────────────
# Crear la API
# ─────────────────────────────────────────────
app = FastAPI(
    title="DiscotecaAPI",
    version="1.0.0",
    description="API REST - Sistema de Pedidos por QR para Discotecas"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras
)


# ══════════════════════════════════════════════
# SELECT  →  GET /select/{tabla}
# ══════════════════════════════════════════════
@app.get("/select/{tabla}", tags=["SELECT"])
async def select(tabla: str):
    """Obtener todos los registros de una tabla"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {tabla} ORDER BY id")
        rows = cur.fetchall()
        con.close()
        return {"tabla": tabla, "total": len(rows), "datos": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# SELECT por ID  →  GET /select/{tabla}/{id}
# ══════════════════════════════════════════════
@app.get("/select/{tabla}/{id}", tags=["SELECT"])
async def select_by_id(tabla: str, id: int):
    """Obtener un registro por su ID"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {tabla} WHERE id = %s", (id,))
        row = cur.fetchone()
        con.close()
        if not row:
            raise HTTPException(status_code=404, detail=f"Registro id={id} no encontrado en '{tabla}'")
        return {"tabla": tabla, "dato": row}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# INSERT categorias  →  POST
# ══════════════════════════════════════════════
@app.post("/insert/categoria", tags=["INSERT"])
async def insert_categoria(nombre: str, descripcion: Optional[str] = None):
    """Insertar una nueva categoría"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)", (nombre, descripcion))
        con.commit()
        nuevo_id = cur.lastrowid
        con.close()
        return {"mensaje": "Categoría creada", "id": nuevo_id, "nombre": nombre}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# INSERT productos  →  POST
# ══════════════════════════════════════════════
@app.post("/insert/producto", tags=["INSERT"])
async def insert_producto(nombre: str, precio: float, categoria_id: int, stock_actual: int = 0):
    """Insertar un nuevo producto"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO productos (nombre, precio, stock_actual, categoria_id) VALUES (%s, %s, %s, %s)",
            (nombre, precio, stock_actual, categoria_id)
        )
        con.commit()
        nuevo_id = cur.lastrowid
        con.close()
        return {"mensaje": "Producto creado", "id": nuevo_id, "nombre": nombre}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# INSERT usuarios  →  POST
# ══════════════════════════════════════════════
@app.post("/insert/usuario", tags=["INSERT"])
async def insert_usuario(nombre: str, email: str, password: str):
    """Insertar un nuevo usuario"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        cur.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, password)
        )
        con.commit()
        nuevo_id = cur.lastrowid
        con.close()
        return {"mensaje": "Usuario creado", "id": nuevo_id, "nombre": nombre}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# INSERT mesas  →  POST
# ══════════════════════════════════════════════
@app.post("/insert/mesa", tags=["INSERT"])
async def insert_mesa(numero: int, estado_id: int = 1):
    """Insertar una nueva mesa (estado_id: 1=LIBRE, 2=OCUPADA, 3=RESERVADA)"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT id FROM mesas WHERE numero = %s", (numero,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail=f"La mesa número {numero} ya existe")
        cur.execute("INSERT INTO mesas (numero, estado_id) VALUES (%s, %s)", (numero, estado_id))
        con.commit()
        nuevo_id = cur.lastrowid
        con.close()
        return {"mensaje": "Mesa creada", "id": nuevo_id, "numero": numero}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# INSERT pedidos  →  POST
# ══════════════════════════════════════════════
@app.post("/insert/pedido", tags=["INSERT"])
async def insert_pedido(mesa_id: int, estado_id: int = 1, total: float = 0.0, creado_por: Optional[int] = None):
    """Insertar un nuevo pedido (estado_id: 1=ABIERTO)"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO pedidos (mesa_id, estado_id, total, creado_por) VALUES (%s, %s, %s, %s)",
            (mesa_id, estado_id, total, creado_por)
        )
        con.commit()
        nuevo_id = cur.lastrowid
        con.close()
        return {"mensaje": "Pedido creado", "id": nuevo_id, "mesa_id": mesa_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# INSERT pedido_productos  →  POST
# ══════════════════════════════════════════════
@app.post("/insert/pedido_producto", tags=["INSERT"])
async def insert_pedido_producto(pedido_id: int, producto_id: int, cantidad: int, precio_unitario: float):
    """Agregar un producto a un pedido"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO pedido_productos (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
            (pedido_id, producto_id, cantidad, precio_unitario)
        )
        con.commit()
        nuevo_id = cur.lastrowid
        con.close()
        return {"mensaje": "Producto agregado al pedido", "id": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# INSERT movimientos_inventario  →  POST
# ══════════════════════════════════════════════
@app.post("/insert/movimiento_inventario", tags=["INSERT"])
async def insert_movimiento(producto_id: int, tipo_id: int, cantidad: int,
                             motivo: Optional[str] = None, usuario_id: Optional[int] = None):
    """Registrar movimiento (tipo_id: 1=ENTRADA, 2=SALIDA, 3=AJUSTE, 4=MERMA)"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO movimientos_inventario (producto_id, tipo_id, cantidad, motivo, usuario_id) VALUES (%s, %s, %s, %s, %s)",
            (producto_id, tipo_id, cantidad, motivo, usuario_id)
        )
        con.commit()
        nuevo_id = cur.lastrowid
        con.close()
        return {"mensaje": "Movimiento registrado", "id": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# INSERT facturas  →  POST
# ══════════════════════════════════════════════
@app.post("/insert/factura", tags=["INSERT"])
async def insert_factura(pedido_id: int, numero: str, tipo_id: int, total: float):
    """Crear factura (tipo_id: 1=TICKET, 2=FACTURA)"""
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT id FROM facturas WHERE numero = %s", (numero,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail=f"Número de factura '{numero}' ya existe")
        cur.execute(
            "INSERT INTO facturas (pedido_id, numero, tipo_id, total) VALUES (%s, %s, %s, %s)",
            (pedido_id, numero, tipo_id, total)
        )
        con.commit()
        nuevo_id = cur.lastrowid
        con.close()
        return {"mensaje": "Factura creada", "id": nuevo_id, "numero": numero}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# UPDATE  →  PUT /update/{tabla}/{id}
# ══════════════════════════════════════════════
@app.put("/update/{tabla}/{id}", tags=["UPDATE"])
async def update(tabla: str, id: int, campo: str, valor: str):
    """
    Actualizar un campo de cualquier tabla por ID.
    Ejemplo: PUT /update/categorias/1?campo=nombre&valor=Bebidas
    """
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(f"SELECT id FROM {tabla} WHERE id = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Registro id={id} no encontrado en '{tabla}'")
        cur.execute(f"UPDATE {tabla} SET {campo} = %s WHERE id = %s", (valor, id))
        con.commit()
        filas = cur.rowcount
        con.close()
        return {
            "mensaje": "Registro actualizado correctamente",
            "tabla": tabla,
            "id": id,
            "campo_modificado": campo,
            "nuevo_valor": valor,
            "filas_afectadas": filas
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# DELETE con cascada recursiva  →  DELETE /delete/{tabla}/{id}
# ══════════════════════════════════════════════
@app.delete("/delete/{tabla}/{id}", tags=["DELETE"])
async def delete(tabla: str, id: int):
    """
    Eliminar un registro por ID con cascada automática.
    Borra todos los registros dependientes en todos los niveles.
    Ejemplo: DELETE /delete/categorias/1
    """
    try:
        con = get_connection()
        cur = con.cursor()

        # Verificar que el registro existe
        cur.execute(f"SELECT id FROM {tabla} WHERE id = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Registro id={id} no encontrado en '{tabla}'")

        eliminados = []
        # Borrar recursivamente todos los hijos y luego el registro
        delete_en_cascada(cur, tabla, id, eliminados)
        con.commit()
        con.close()

        respuesta = {
            "mensaje": "Registro eliminado correctamente ✅",
            "tabla": tabla,
            "id_eliminado": id
        }
        if eliminados:
            respuesta["registros_dependientes_eliminados"] = eliminados

        return respuesta

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════
# Raíz  →  GET /
# ══════════════════════════════════════════════
@app.get("/", tags=["Info"])
async def root():
    return {
        "mensaje": "DiscotecaAPI funcionando ✅",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
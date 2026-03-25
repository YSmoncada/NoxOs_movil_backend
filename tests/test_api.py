#!/usr/bin/env python3
"""
Script para probar todos los métodos de la API
"""
import json
import urllib.request
import urllib.error
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_result(method: str, endpoint: str, status: int, success: bool = True):
    color = Colors.GREEN if success else Colors.RED
    status_text = f"{status}"
    print(f"{color}[{method}] {endpoint} → {status_text}{Colors.END}")

def test_usuarios():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("PROBANDO: USUARIOS")
    print(f"{'='*60}{Colors.END}")
    
    # GET - Listar
    try:
        resp = requests.get(f"{BASE_URL}/usuarios/")
        print_result("GET", "/usuarios/", resp.status_code, resp.status_code == 200)
        usuarios = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"{Colors.RED}Error GET usuarios: {e}{Colors.END}")
        usuarios = []
    
    # GET - Obtener un usuario
    if usuarios:
        try:
            usuario_id = usuarios[0][0] if isinstance(usuarios[0], (list, tuple)) else usuarios[0].get('id')
            resp = requests.get(f"{BASE_URL}/usuarios/{usuario_id}")
            print_result("GET", f"/usuarios/{usuario_id}", resp.status_code, resp.status_code == 200)
        except Exception as e:
            print(f"{Colors.RED}Error GET usuario específico: {e}{Colors.END}")
    
    # POST - Crear
    try:
        nuevo_usuario = {
            "nombre": "Test User",
            "email": f"test{hash('test')}@test.com",
            "password": "Password123"
        }
        resp = requests.post(f"{BASE_URL}/usuarios/registro", json=nuevo_usuario)
        print_result("POST", "/usuarios/registro", resp.status_code, resp.status_code == 201)
        if resp.status_code == 201:
            test_user = resp.json()
            test_user_id = test_user.get('id') if isinstance(test_user, dict) else test_user[0]
            
            # PUT - Actualizar
            actualizar = {"nombre": "Updated User"}
            resp_put = requests.put(f"{BASE_URL}/usuarios/{test_user_id}", json=actualizar)
            print_result("PUT", f"/usuarios/{test_user_id}", resp_put.status_code, resp_put.status_code == 200)
            
            # DELETE - Eliminar
            resp_del = requests.delete(f"{BASE_URL}/usuarios/{test_user_id}")
            print_result("DELETE", f"/usuarios/{test_user_id}", resp_del.status_code, resp_del.status_code == 204)
    except Exception as e:
        print(f"{Colors.RED}Error POST/PUT/DELETE usuarios: {e}{Colors.END}")

def test_categorias():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("PROBANDO: CATEGORÍAS")
    print(f"{'='*60}{Colors.END}")
    
    # GET - Listar
    try:
        resp = requests.get(f"{BASE_URL}/categorias/")
        print_result("GET", "/categorias/", resp.status_code, resp.status_code == 200)
        categorias = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"{Colors.RED}Error GET categorias: {e}{Colors.END}")
        categorias = []
    
    # GET - Obtener una
    if categorias:
        try:
            cat_id = categorias[0][0] if isinstance(categorias[0], (list, tuple)) else categorias[0].get('id')
            resp = requests.get(f"{BASE_URL}/categorias/{cat_id}")
            print_result("GET", f"/categorias/{cat_id}", resp.status_code, resp.status_code == 200)
        except Exception as e:
            print(f"{Colors.RED}Error GET categoría específica: {e}{Colors.END}")
    
    # POST - Crear
    try:
        nueva_cat = {
            "nombre": "Test Category",
            "descripcion": "Categoría de prueba"
        }
        resp = requests.post(f"{BASE_URL}/categorias/", json=nueva_cat)
        print_result("POST", "/categorias/", resp.status_code, resp.status_code == 201)
        if resp.status_code == 201:
            cat = resp.json()
            cat_id = cat.get('id') if isinstance(cat, dict) else cat[0]
            
            # PUT - Actualizar
            actualizar = {"nombre": "Updated Category"}
            resp_put = requests.put(f"{BASE_URL}/categorias/{cat_id}", json=actualizar)
            print_result("PUT", f"/categorias/{cat_id}", resp_put.status_code, resp_put.status_code == 200)
            
            # DELETE - Eliminar
            resp_del = requests.delete(f"{BASE_URL}/categorias/{cat_id}")
            print_result("DELETE", f"/categorias/{cat_id}", resp_del.status_code, resp_del.status_code == 204)
    except Exception as e:
        print(f"{Colors.RED}Error POST/PUT/DELETE categorias: {e}{Colors.END}")

def test_productos():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("PROBANDO: PRODUCTOS")
    print(f"{'='*60}{Colors.END}")
    
    # GET - Listar
    try:
        resp = requests.get(f"{BASE_URL}/productos/")
        print_result("GET", "/productos/", resp.status_code, resp.status_code == 200)
        productos = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"{Colors.RED}Error GET productos: {e}{Colors.END}")
        productos = []
    
    # GET - Obtener uno
    if productos:
        try:
            prod_id = productos[0][0] if isinstance(productos[0], (list, tuple)) else productos[0].get('id')
            resp = requests.get(f"{BASE_URL}/productos/{prod_id}")
            print_result("GET", f"/productos/{prod_id}", resp.status_code, resp.status_code == 200)
        except Exception as e:
            print(f"{Colors.RED}Error GET producto específico: {e}{Colors.END}")
    
    # POST - Crear
    try:
        nuevo_prod = {
            "nombre": "Test Producto",
            "precio": 99.99,
            "stock_actual": 10,
            "categoria_id": 1,
            "activo": True
        }
        resp = requests.post(f"{BASE_URL}/productos/", json=nuevo_prod)
        print_result("POST", "/productos/", resp.status_code, resp.status_code == 201)
        if resp.status_code == 201:
            prod = resp.json()
            prod_id = prod.get('id') if isinstance(prod, dict) else prod[0]
            
            # PUT - Actualizar
            actualizar = {"nombre": "Updated Producto"}
            resp_put = requests.put(f"{BASE_URL}/productos/{prod_id}", json=actualizar)
            print_result("PUT", f"/productos/{prod_id}", resp_put.status_code, resp_put.status_code == 200)
            
            # DELETE - Eliminar
            resp_del = requests.delete(f"{BASE_URL}/productos/{prod_id}")
            print_result("DELETE", f"/productos/{prod_id}", resp_del.status_code, resp_del.status_code == 204)
    except Exception as e:
        print(f"{Colors.RED}Error POST/PUT/DELETE productos: {e}{Colors.END}")

def test_mesas():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("PROBANDO: MESAS")
    print(f"{'='*60}{Colors.END}")
    
    # GET - Listar
    try:
        resp = requests.get(f"{BASE_URL}/mesas/")
        print_result("GET", "/mesas/", resp.status_code, resp.status_code == 200)
        mesas = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"{Colors.RED}Error GET mesas: {e}{Colors.END}")
        mesas = []
    
    # GET - Obtener una
    if mesas:
        try:
            mesa_id = mesas[0][0] if isinstance(mesas[0], (list, tuple)) else mesas[0].get('id')
            resp = requests.get(f"{BASE_URL}/mesas/{mesa_id}")
            print_result("GET", f"/mesas/{mesa_id}", resp.status_code, resp.status_code == 200)
        except Exception as e:
            print(f"{Colors.RED}Error GET mesa específica: {e}{Colors.END}")
    
    # POST - Crear
    try:
        nueva_mesa = {
            "numero": 999,
            "estado_id": 1
        }
        resp = requests.post(f"{BASE_URL}/mesas/", json=nueva_mesa)
        print_result("POST", "/mesas/", resp.status_code, resp.status_code == 201)
        if resp.status_code == 201:
            mesa = resp.json()
            mesa_id = mesa.get('id') if isinstance(mesa, dict) else mesa[0]
            
            # PUT - Actualizar
            actualizar = {"estado_id": 2}
            resp_put = requests.put(f"{BASE_URL}/mesas/{mesa_id}", json=actualizar)
            print_result("PUT", f"/mesas/{mesa_id}", resp_put.status_code, resp_put.status_code == 200)
            
            # DELETE - Eliminar
            resp_del = requests.delete(f"{BASE_URL}/mesas/{mesa_id}")
            print_result("DELETE", f"/mesas/{mesa_id}", resp_del.status_code, resp_del.status_code == 204)
    except Exception as e:
        print(f"{Colors.RED}Error POST/PUT/DELETE mesas: {e}{Colors.END}")

def test_pedidos():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("PROBANDO: PEDIDOS")
    print(f"{'='*60}{Colors.END}")
    
    # GET - Listar
    try:
        resp = requests.get(f"{BASE_URL}/pedidos/")
        print_result("GET", "/pedidos/", resp.status_code, resp.status_code == 200)
        pedidos = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"{Colors.RED}Error GET pedidos: {e}{Colors.END}")
        pedidos = []
    
    # GET - Obtener uno
    if pedidos:
        try:
            ped_id = pedidos[0][0] if isinstance(pedidos[0], (list, tuple)) else pedidos[0].get('id')
            resp = requests.get(f"{BASE_URL}/pedidos/{ped_id}")
            print_result("GET", f"/pedidos/{ped_id}", resp.status_code, resp.status_code == 200)
        except Exception as e:
            print(f"{Colors.RED}Error GET pedido específico: {e}{Colors.END}")
    
    # POST - Crear
    try:
        nuevo_pedido = {
            "mesa_id": 1,
            "estado_id": 1,
            "creado_por": 1,
            "productos": [
                {"producto_id": 1, "cantidad": 2}
            ]
        }
        resp = requests.post(f"{BASE_URL}/pedidos/", json=nuevo_pedido)
        print_result("POST", "/pedidos/", resp.status_code, resp.status_code == 201)
        if resp.status_code == 201:
            ped = resp.json()
            ped_id = ped.get('id') if isinstance(ped, dict) else ped[0]
            
            # PUT - Actualizar
            actualizar = {"estado_id": 2}
            resp_put = requests.put(f"{BASE_URL}/pedidos/{ped_id}", json=actualizar)
            print_result("PUT", f"/pedidos/{ped_id}", resp_put.status_code, resp_put.status_code == 200)
            
            # DELETE - Eliminar
            resp_del = requests.delete(f"{BASE_URL}/pedidos/{ped_id}")
            print_result("DELETE", f"/pedidos/{ped_id}", resp_del.status_code, resp_del.status_code == 204)
    except Exception as e:
        print(f"{Colors.RED}Error POST/PUT/DELETE pedidos: {e}{Colors.END}")

def test_inventario():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("PROBANDO: MOVIMIENTOS INVENTARIO")
    print(f"{'='*60}{Colors.END}")
    
    # GET - Listar
    try:
        resp = requests.get(f"{BASE_URL}/inventario/movimientos/")
        print_result("GET", "/inventario/movimientos/", resp.status_code, resp.status_code == 200)
        movimientos = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"{Colors.RED}Error GET movimientos: {e}{Colors.END}")
        movimientos = []
    
    # POST - Crear movimiento
    try:
        nuevo_mov = {
            "producto_id": 1,
            "tipo_id": 1,
            "cantidad": 5,
            "motivo": "Reposición de stock",
            "usuario_id": 1
        }
        resp = requests.post(f"{BASE_URL}/inventario/movimientos/", json=nuevo_mov)
        print_result("POST", "/inventario/movimientos/", resp.status_code, resp.status_code == 201)
    except Exception as e:
        print(f"{Colors.RED}Error POST movimiento: {e}{Colors.END}")

def test_facturas():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("PROBANDO: FACTURAS")
    print(f"{'='*60}{Colors.END}")
    
    # GET - Listar
    try:
        resp = requests.get(f"{BASE_URL}/facturas/")
        print_result("GET", "/facturas/", resp.status_code, resp.status_code == 200)
        facturas = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"{Colors.RED}Error GET facturas: {e}{Colors.END}")
        facturas = []
    
    # GET - Obtener una
    if facturas:
        try:
            fact_id = facturas[0][0] if isinstance(facturas[0], (list, tuple)) else facturas[0].get('id')
            resp = requests.get(f"{BASE_URL}/facturas/{fact_id}")
            print_result("GET", f"/facturas/{fact_id}", resp.status_code, resp.status_code == 200)
        except Exception as e:
            print(f"{Colors.RED}Error GET factura específica: {e}{Colors.END}")

def test_datos():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("PROBANDO: DATOS (Reference Data)")
    print(f"{'='*60}{Colors.END}")
    
    try:
        resp = requests.get(f"{BASE_URL}/datos/estados-mesa")
        print_result("GET", "/datos/estados-mesa", resp.status_code, resp.status_code == 200)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
    
    try:
        resp = requests.get(f"{BASE_URL}/datos/estados-pedido")
        print_result("GET", "/datos/estados-pedido", resp.status_code, resp.status_code == 200)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
    
    try:
        resp = requests.get(f"{BASE_URL}/datos/tipos-movimiento")
        print_result("GET", "/datos/tipos-movimiento", resp.status_code, resp.status_code == 200)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
    
    try:
        resp = requests.get(f"{BASE_URL}/datos/tipos-factura")
        print_result("GET", "/datos/tipos-factura", resp.status_code, resp.status_code == 200)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")

def main():
    print(f"{Colors.BLUE}" + "="*60)
    print("PRUEBA COMPLETA DE API - DISCOTECA")
    print("="*60 + f"{Colors.END}\n")
    
    test_usuarios()
    test_categorias()
    test_productos()
    test_mesas()
    test_pedidos()
    test_inventario()
    test_facturas()
    test_datos()
    
    print(f"\n{Colors.BLUE}{'='*60}")
    print("✅ PRUEBAS COMPLETADAS")
    print(f"{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    main()

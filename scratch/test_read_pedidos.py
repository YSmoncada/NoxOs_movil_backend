import json
import urllib.request
import urllib.error

# Test read_pedidos for usuario=2
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/pedidos/?usuario=2', 
)

try:
    resp = urllib.request.urlopen(req)
    print("SUCCESS")
    data = json.loads(resp.read().decode())
    print(f"Count: {len(data)}")
    if len(data) > 0:
        print(f"First Order ID: {data[0].get('id')}")
        print(f"Details: {len(data[0].get('detalles', []))}")
        print(f"Prod Det: {len(data[0].get('productos_detalle', []))}")
except urllib.error.HTTPError as e:
    print(f"FAILED: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"ERROR: {str(e)}")

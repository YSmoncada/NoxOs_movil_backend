import json
import urllib.request
import urllib.error

data = json.dumps({
    'mesa': 1, 
    'total': 12000.0, 
    'productos': [{
        'producto_id': 1, 
        'cantidad': 1, 
        'precio_unitario': 12000.0
    }]
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/pedidos/', 
    data=data, 
    headers={'Content-Type': 'application/json'}
)

try:
    resp = urllib.request.urlopen(req)
    print("SUCCESS")
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    print(f"FAILED: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"ERROR: {str(e)}")

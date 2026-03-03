# Script para probar todos los endpoints de la API

$BaseUrl = "http://localhost:8000/api/v1"

function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null
    )
    
    try {
        $Uri = "$BaseUrl$Endpoint"
        $Params = @{
            Uri = $Uri
            Method = $Method
            Headers = @{ 'Content-Type' = 'application/json' }
            ErrorAction = 'SilentlyContinue'
        }
        
        if ($Body) {
            $Params['Body'] = $Body | ConvertTo-Json
        }
        
        $Result = Invoke-RestMethod @Params
        Write-Host "✅ [$Method] $Endpoint → 200 OK" -ForegroundColor Green
        return $Result
    }
    catch {
        $StatusCode = $_.Exception.Response.StatusCode.Value__
        if ($StatusCode -eq 204) {
            Write-Host "✅ [$Method] $Endpoint → 204 NO CONTENT" -ForegroundColor Green
            return $null
        }
        else {
            Write-Host "❌ [$Method] $Endpoint → $StatusCode" -ForegroundColor Red
            return $null
        }
    }
}

Write-Host "`n" + "="*60
Write-Host "PRUEBA COMPLETA DE API - DISCOTECA"
Write-Host "="*60 + "`n"

# ==================== USUARIOS ====================
Write-Host "PROBANDO: USUARIOS" -ForegroundColor Cyan
Write-Host "="*60
$usuarios = Test-Endpoint -Method GET -Endpoint "/usuarios/"
if ($usuarios.Count -gt 0) {
    $usuario_id = $usuarios[0].id
    Test-Endpoint -Method GET -Endpoint "/usuarios/$usuario_id" | Out-Null
}

# ==================== CATEGORÍAS ====================
Write-Host "`nPROBANDO: CATEGORÍAS" -ForegroundColor Cyan
Write-Host "="*60
$categorias = Test-Endpoint -Method GET -Endpoint "/categorias/"
if ($categorias.Count -gt 0) {
    $cat_id = $categorias[0].id
    Test-Endpoint -Method GET -Endpoint "/categorias/$cat_id" | Out-Null
}

# ==================== PRODUCTOS ====================
Write-Host "`nPROBANDO: PRODUCTOS" -ForegroundColor Cyan
Write-Host "="*60
$productos = Test-Endpoint -Method GET -Endpoint "/productos/"
if ($productos.Count -gt 0) {
    $prod_id = $productos[0].id
    Test-Endpoint -Method GET -Endpoint "/productos/$prod_id" | Out-Null
}

# ==================== MESAS ====================
Write-Host "`nPROBANDO: MESAS" -ForegroundColor Cyan
Write-Host "="*60
$mesas = Test-Endpoint -Method GET -Endpoint "/mesas/"
if ($mesas.Count -gt 0) {
    $mesa_id = $mesas[0].id
    Test-Endpoint -Method GET -Endpoint "/mesas/$mesa_id" | Out-Null
}

# ==================== PEDIDOS ====================
Write-Host "`nPROBANDO: PEDIDOS" -ForegroundColor Cyan
Write-Host "="*60
$pedidos = Test-Endpoint -Method GET -Endpoint "/pedidos/"
if ($pedidos.Count -gt 0) {
    $ped_id = $pedidos[0].id
    Test-Endpoint -Method GET -Endpoint "/pedidos/$ped_id" | Out-Null
}

# ==================== INVENTARIO ====================
Write-Host "`nPROBANDO: MOVIMIENTOS INVENTARIO" -ForegroundColor Cyan
Write-Host "="*60
Test-Endpoint -Method GET -Endpoint "/inventario/movimientos/" | Out-Null

# ==================== FACTURAS ====================
Write-Host "`nPROBANDO: FACTURAS" -ForegroundColor Cyan
Write-Host "="*60
$facturas = Test-Endpoint -Method GET -Endpoint "/facturas/"
if ($facturas.Count -gt 0) {
    $fact_id = $facturas[0].id
    Test-Endpoint -Method GET -Endpoint "/facturas/$fact_id" | Out-Null
}

# ==================== DATOS ====================
Write-Host "`nPROBANDO: DATOS (Reference Data)" -ForegroundColor Cyan
Write-Host "="*60
Test-Endpoint -Method GET -Endpoint "/datos/estados-mesa" | Out-Null
Test-Endpoint -Method GET -Endpoint "/datos/estados-pedido" | Out-Null
Test-Endpoint -Method GET -Endpoint "/datos/tipos-movimiento" | Out-Null
Test-Endpoint -Method GET -Endpoint "/datos/tipos-factura" | Out-Null

Write-Host "`n" + "="*60
Write-Host "✅ PRUEBAS COMPLETADAS" -ForegroundColor Green
Write-Host "="*60 + "`n"

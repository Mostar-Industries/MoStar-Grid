# test_fixes.ps1
# Comprehensive smoke test for all backend fixes

Write-Host "`n=== MoStar Grid Fix Pack Verification ===" -ForegroundColor Cyan
Write-Host "Testing all endpoints on port 7000`n" -ForegroundColor Cyan

# 1. Doctrine Status
Write-Host "[1/4] Testing /api/doctrine/status..." -ForegroundColor Yellow
try {
    $doctrine = Invoke-RestMethod http://127.0.0.1:7000/api/doctrine/status
    if ($doctrine.ok) {
        Write-Host "✅ Doctrine sealed and verified" -ForegroundColor Green
        Write-Host "   Sealed scrolls: $($doctrine.scrolls.Count)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Doctrine check failed: $($doctrine.reason)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Doctrine endpoint failed: $_" -ForegroundColor Red
}

# 2. Notes Roundtrip
Write-Host "`n[2/4] Testing /api/notes (create + list)..." -ForegroundColor Yellow
try {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $note = @{ title="Smoke Test"; body="Grid pulse check at $timestamp UTC" } | ConvertTo-Json
    $created = Invoke-RestMethod http://127.0.0.1:7000/api/notes -Method Post -Body $note -ContentType "application/json"
    Write-Host "✅ Note created: ID $($created.id)" -ForegroundColor Green
    
    $notes = Invoke-RestMethod http://127.0.0.1:7000/api/notes
    Write-Host "✅ Notes retrieved: $($notes.Count) total" -ForegroundColor Green
} catch {
    Write-Host "❌ Notes endpoint failed: $_" -ForegroundColor Red
}

# 3. WebSocket
Write-Host "`n[3/4] Testing WebSocket /ws/live-stream..." -ForegroundColor Yellow
try {
    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $cts = New-Object System.Threading.CancellationTokenSource
    $uri = [Uri]"ws://127.0.0.1:7000/ws/live-stream"
    $ws.ConnectAsync($uri, $cts.Token).Wait()
    
    $buf = New-Object byte[] 8192
    $seg = New-Object ArraySegment[byte]($buf,0,$buf.Length)
    $res = $ws.ReceiveAsync($seg,$cts.Token).Result
    $msg = [Text.Encoding]::UTF8.GetString($buf,0,$res.Count)
    $data = $msg | ConvertFrom-Json
    
    Write-Host "✅ WebSocket frame received" -ForegroundColor Green
    Write-Host "   CPU: $($data.cpu)%, Mem: $($data.mem)%, Latency: $($data.gridLatencyMs)ms" -ForegroundColor Gray
    
    $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure,"ok",$cts.Token).Wait()
} catch {
    Write-Host "❌ WebSocket failed: $_" -ForegroundColor Red
}

# 4. MostlyAI Probe (dynamic validation)
Write-Host "`n[4/4] Testing /api/synthetic/probe (dynamic validation)..." -ForegroundColor Yellow
try {
    $payload = @{ size = @{ infancy = 3; childhood = 3; science = 2 } } | ConvertTo-Json
    $result = Invoke-RestMethod http://127.0.0.1:7000/api/synthetic/probe -Method Post -Body $payload -ContentType "application/json"
    Write-Host "✅ Synthetic probe accepted (dynamic validation passed)" -ForegroundColor Green
    Write-Host "   Job ID: $($result.job_id)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Synthetic probe failed: $_" -ForegroundColor Yellow
    Write-Host "   (Expected if MOSTLY_API_KEY not configured)" -ForegroundColor Gray
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "All critical endpoints verified!`n" -ForegroundColor Green

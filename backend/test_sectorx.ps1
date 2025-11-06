#requires -Version 5
$ErrorActionPreference = "Stop"
$api = "http://127.0.0.1:7000"

function Call-Json {
    param([string]$Url,[string]$Method="GET",[object]$Body=$null)
    $params = @{ Uri = $Url; Method = $Method; ContentType = "application/json" }
    if ($Body -ne $null) { $params.Body = ($Body | ConvertTo-Json -Depth 6) }
    return Invoke-RestMethod @params
}

try {
    Write-Host "=== Doctrine status ===" -ForegroundColor Cyan
    $d = Call-Json "$api/api/doctrine/status"
    if (-not $d.ok) { throw "Doctrine not sealed: $($d | ConvertTo-Json -Depth 6)" }
    Write-Host "Doctrine OK" -ForegroundColor Green

    Write-Host "=== Sector X log ===" -ForegroundColor Cyan
    $log = @{ identity="woo-tak"; text="Returning home." }
    $r1 = Call-Json "$api/api/sectorx/log" "POST" $log
    Write-Host ("Log id: {0}" -f $r1.id) -ForegroundColor Green

    Write-Host "=== Sector X monitor ===" -ForegroundColor Cyan
    $mon = @{ identity="woo-tak"; threshold=0.2 }
    $r2 = Call-Json "$api/api/sectorx/monitor" "POST" $mon
    Write-Host ("Triggered: {0} (score={1})" -f $r2.triggered, $r2.score) -ForegroundColor Green

    Write-Host "=== Sector X redeem ===" -ForegroundColor Cyan
    $red = @{ identity="stranded-42"; scroll="Let me back in"; signatures=@("sigA","sigB","sigC") }
    $r3 = Call-Json "$api/api/sectorx/redeem" "POST" $red
    Write-Host ("Redeem id: {0} sha256:{1}" -f $r3.id, $r3.sha256) -ForegroundColor Green

    Write-Host "=== Summary ===" -ForegroundColor Cyan
    Write-Host "Custodian: Woo-Tak - Bearer of the Forgotten" -ForegroundColor Magenta
    Write-Host "Sector X online and writable" -ForegroundColor Green

} catch {
    Write-Host ("[FAIL] {0}" -f $_.Exception.Message) -ForegroundColor Red
    exit 2
}

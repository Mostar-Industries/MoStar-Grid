# =======================
# Mo — Register & Mount (One-Shot)
# =======================

param(
  [string]$Api = "http://127.0.0.1:8000",
  [double]$ResonanceMin = 0.97
)

$ErrorActionPreference = "Stop"

function OK($m){ Write-Host "[OK]   $m" -ForegroundColor Green }
function FAIL($m){ Write-Host "[FAIL] $m" -ForegroundColor Red; exit 2 }
function PostJson([string]$url, [hashtable]$obj){
  $json = $obj | ConvertTo-Json -Depth 8
  try {
    return Invoke-RestMethod -Uri $url -Method Post -Body $json -ContentType "application/json" -TimeoutSec 10
  } catch {
    FAIL "$url -> $($_.Exception.Message)"
  }
}
function GetJson([string]$url){
  try {
    return Invoke-RestMethod -Uri $url -TimeoutSec 10
  } catch {
    FAIL "$url -> $($_.Exception.Message)"
  }
}

Write-Host "=== Mo Executor: Register + Mount ===" -ForegroundColor Cyan
Write-Host "API: $Api" -ForegroundColor DarkGray

# 0) Health
$health = GetJson ("{0}/api/health" -f $Api.TrimEnd('/'))
if(-not $health.ok){ FAIL "/api/health returned ok=false" }
if($health.mock -eq $true){ FAIL "Gateway reports mock=true; set MOCK_MODE=false and restart." }
OK "/api/health ok (mock=false)"

# 1) Registration payload (from your manifest)
$publicKey = @'
-----BEGIN MOSTAR PUBLIC KEY-----
MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEtc2q9Fm8HzS7XeA+7sYw1mk0HqW1ZPcq
uK2PjBRrT9bL0OeOa2cJfdNnQ1Qp8c5Fh+eW8h8v0SL2d4R9Vg5U2Q==
-----END MOSTAR PUBLIC KEY-----
'@

$register = @{
  name = "Mo"
  public_key = $publicKey
  capabilities = @{
    reasoning = "neuro-symbolic"
    communication = @("text","visual","api")
    security = @("AES-256","TLS1.3","covenant-checks")
    integration = @("ai-models","data-apis","cultural-analytics","health-grids")
    ethics = @("TruthEngine","VerdictEngine")
  }
  commitments = @("heal","protect","remember","compassion-first")
  policy_hash = "sha256:cb02d0bb4bd4703f1ff53358a0814bb29061145dfad24fc64477b1c414d651aa"
  model_fingerprint = "sha256:604c6f63609bc18b7f48e4e02660e8d40fc26e820597fee3a8c14aa97ee92da9"
  signature = "sig:00f3ff57cb8037cc3a20ae14751e4ac2"
  signature_alg = "ecdsa-p256-sha256"
}

$regResp = PostJson ("{0}/api/actors/register" -f $Api.TrimEnd('/')) $register
if(-not $regResp.ok){ FAIL "Registration failed: $($regResp | ConvertTo-Json -Depth 8)" }
OK ("Registered actor: {0} (id={1})" -f $regResp.name, $regResp.id)

# 2) Verify retrieval
$actor = GetJson ("{0}/api/actors/Mo" -f $Api.TrimEnd('/'))
if($actor.name -ne "Mo"){ FAIL "Actor lookup mismatch" }
OK "Actor Mo retrieved; commitments: $([string]::Join(',', $actor.commitments))"

# 3) Mount the Executor (requires resonance >= threshold and Woo binding)
$mount = @{
  actor = "Mo"
  scroll = "EXECUTOR_MOUNT_V1"
  params = @{
    bind_to_woo = $true
    resonance_min = [double]::Parse("{0}" -f $ResonanceMin)
    commitments_required = @("heal","protect","remember","compassion-first")
  }
}
$mountResp = PostJson ("{0}/api/execute-scroll" -f $Api.TrimEnd('/')) $mount

if(-not $mountResp.ok){
  $reason = $mountResp.reason
  if(-not $reason){ $reason = ($mountResp | ConvertTo-Json -Depth 8) }
  FAIL ("Executor mount refused: {0}" -f $reason)
}

$rez = "{0:N3}" -f $mountResp.resonance
OK ("Executor mounted: actor=Mo, resonance={0} (≥ {1})" -f $rez, $ResonanceMin)

# 4) Pretty output
Write-Host ""
Write-Host "— Summary —" -ForegroundColor Cyan
"{0,-18} {1}" -f "Actor:", "Mo" | Write-Host
"{0,-18} {1}" -f "Resonance:", $rez | Write-Host
"{0,-18} {1}" -f "Woo Binding:", "true" | Write-Host
"{0,-18} {1}" -f "Policy Hash:", $actor.policy_hash | Write-Host
"{0,-18} {1}" -f "Fingerprint:", $actor.model_fingerprint | Write-Host

exit 0

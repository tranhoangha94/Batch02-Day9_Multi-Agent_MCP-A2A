# Start all Legal Multi-Agent System services (Windows)
# Equivalent to start_all.sh
#
# Usage:
#   .\start_all.ps1
#   or double-click start_all.bat

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

$Processes = [System.Collections.Generic.List[System.Diagnostics.Process]]::new()
$LogDir = Join-Path $Root "logs"
$Python = Join-Path $Root ".venv\Scripts\python.exe"

function Ensure-Environment {
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Error "uv not found in PATH. Install: pip install uv"
        exit 1
    }

    if (-not (Test-Path $Python)) {
        Write-Host "Creating virtual environment (.venv)..."
        uv sync | Out-Host
    }

    if (-not (Test-Path $Python)) {
        Write-Error "Python not found at $Python"
        exit 1
    }

    if (-not (Test-Path (Join-Path $Root ".env"))) {
        Write-Warning ".env not found. Copy .env.example to .env and set OPENROUTER_API_KEY."
    }

    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir | Out-Null
    }
}

function Start-AgentService {
    param(
        [string]$Label,
        [string]$Module,
        [int]$DelaySeconds = 0
    )

    $logOut = Join-Path $LogDir "$Module.log"
    $logErr = Join-Path $LogDir "$Module.err.log"
    Write-Host "Starting $Label... (log: logs\$Module.log)"

    $proc = Start-Process `
        -FilePath $Python `
        -ArgumentList @("-m", $Module) `
        -WorkingDirectory $Root `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $logOut `
        -RedirectStandardError $logErr

    $Processes.Add($proc) | Out-Null

    if ($DelaySeconds -gt 0) {
        Start-Sleep -Seconds $DelaySeconds
    }
}

function Stop-AllServices {
    if ($Processes.Count -eq 0) { return }

    Write-Host ""
    Write-Host "Stopping all services..."
    foreach ($proc in $Processes) {
        if ($proc.HasExited) { continue }
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction Stop
        } catch {
            Write-Warning "Could not stop process $($proc.Id): $_"
        }
    }
}

Ensure-Environment

try {
    # Registry first, then leaf agents, then orchestrators (same order as start_all.sh)
    Start-AgentService "Registry service on port 10000" "registry" -DelaySeconds 2
    Start-AgentService "Tax Agent on port 10102" "tax_agent"
    Start-AgentService "Compliance Agent on port 10103" "compliance_agent" -DelaySeconds 3
    Start-AgentService "Law Agent on port 10101" "law_agent" -DelaySeconds 3
    Start-AgentService "Customer Agent on port 10100" "customer_agent"

    Write-Host ""
    Write-Host "All services started:"
    Write-Host "  Registry:         http://localhost:10000"
    Write-Host "  Customer Agent:   http://localhost:10100"
    Write-Host "  Law Agent:        http://localhost:10101"
    Write-Host "  Tax Agent:        http://localhost:10102"
    Write-Host "  Compliance Agent: http://localhost:10103"
    Write-Host ""
    Write-Host "Run test_client.py to send a query:"
    Write-Host "  uv run python test_client.py"
    Write-Host ""
    Write-Host "Logs: $LogDir"
    Write-Host "Press Ctrl+C to stop all services."

    while ($true) {
        $alive = $Processes | Where-Object { -not $_.HasExited }
        if ($alive.Count -eq 0) {
            Write-Warning "All services have exited. Check logs in $LogDir"
            break
        }
        Start-Sleep -Seconds 1
    }
}
finally {
    Stop-AllServices
}

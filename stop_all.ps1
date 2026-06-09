# Stop services started by start_all.ps1 (ports 10000-10103)

$ports = 10000, 10100, 10101, 10102, 10103

foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $conns) {
        $pid = $conn.OwningProcess
        Write-Host "Stopping process $pid on port $port..."
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Done."

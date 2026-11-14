# Собирает сценарии, загружает их в n8n и публикует. Запуск: powershell -File tools\deploy.ps1
$ErrorActionPreference = "Continue"
Set-Location (Split-Path $PSScriptRoot -Parent)
# Рабочая сборка с настоящими ID лежит в secrets и в репозиторий не попадает.
$env:MYATA_SHEET_ID = (Get-Content secrets\sheet_id.txt -Raw).Trim()
$env:MYATA_OUT = "$PWD\secrets\workflows_live"
node tools\build_workflows.js secrets\creds_map.json
docker exec myata_n8n sh -c "rm -rf /tmp/wf && mkdir -p /tmp/wf" | Out-Null
docker cp secrets/workflows_live/. myata_n8n:/tmp/wf/ | Out-Null
docker exec myata_n8n n8n import:workflow --separate --input=/tmp/wf/ 2>&1 | Select-Object -Last 1
foreach ($id in "MyataAgent000001", "MyataOtchet00001", "MyataPriem000001") {
  docker exec myata_n8n n8n publish:workflow --id=$id 2>&1 | Select-Object -First 1
}
docker restart myata_n8n | Out-Null
foreach ($i in 1..25) {
  $c = curl.exe -s --noproxy "*" -o NUL -m 4 -w "%{http_code}" http://127.0.0.1:5678/healthz
  if ($c -eq "200") { break }
  Start-Sleep -Seconds 3
}
"n8n healthz: $c"
# Проверяем, что все три сценария активны. Если нет, публикуем повторно.
foreach ($try in 1..3) {
  $active = (docker exec myata_n8n n8n list:workflow --active=true 2>&1 | Select-String -Pattern "Myata").Count
  if ($active -ge 3) { break }
  foreach ($id in "MyataAgent000001", "MyataOtchet00001", "MyataPriem000001") { docker exec myata_n8n n8n publish:workflow --id=$id 2>&1 | Out-Null }
  Start-Sleep -Seconds 5
}
"активных сценариев: $active из 3"
docker cp tools\exec_peek.js myata_n8n:/tmp/exec_peek.js | Out-Null

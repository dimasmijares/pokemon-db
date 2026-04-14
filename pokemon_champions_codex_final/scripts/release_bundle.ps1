$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot
Set-Location ..

python scripts\sync_current_champions.py
python scripts\derive_competitive_layer.py
python scripts\validate_data.py
python scripts\build_db.py
python scripts\export_views.py
python scripts\build_data_bundle.py

Write-Output "[OK] Release completada"

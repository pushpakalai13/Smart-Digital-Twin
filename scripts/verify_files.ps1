$targetPath = "C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin\sample_data\real"

Write-Host "=== STEP 1: CHECK FOLDER EXISTENCE ==="
if (Test-Path $targetPath) {
    Write-Host "Folder EXISTS at: $targetPath"
    Get-ChildItem -Path $targetPath | Select-Object Name, Length, LastWriteTime | Format-Table
} else {
    Write-Host "Folder DOES NOT EXIST at: $targetPath"
}

Write-Host "`n=== STEP 2: CURRENT WORKING DIRECTORY & ABSOLUTE PATH ==="
Get-Location

Write-Host "`n=== STEP 3: RE-RUNNING TRANSFORMATION SCRIPTS ==="
Set-Location "C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin"

Write-Host "[1/2] Executing transform_energy_uci.py..."
.\venv\Scripts\python.exe scripts/transform_real_data/transform_energy_uci.py

Write-Host "`n[2/2] Executing transform_all_real_datasets.py..."
.\venv\Scripts\python.exe scripts/transform_real_data/transform_all_real_datasets.py

Write-Host "`n=== STEP 4: VERIFYING FILES ON DISK & CONTENT PREVIEWS ==="
if (Test-Path $targetPath) {
    $files = Get-ChildItem -Path $targetPath
    foreach ($f in $files) {
        Write-Host "--------------------------------------------------------"
        Write-Host "FILE       : $($f.FullName)"
        Write-Host "SIZE BYTES : $($f.Length) bytes"
        Write-Host "FIRST 3 LINES OF CONTENT:"
        Get-Content $f.FullName -Head 3
    }
} else {
    Write-Host "ERROR: Target path $targetPath still does not exist!"
}

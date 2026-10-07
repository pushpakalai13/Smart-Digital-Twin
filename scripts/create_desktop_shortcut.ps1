$WshShell = New-Object -ComObject WScript.Shell

$targetPath = "C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin\start.bat"
$workingDir = "C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin"

$desktopPaths = @(
    [Environment]::GetFolderPath('Desktop'),
    "C:\Users\pushpakalai\Desktop",
    "C:\Users\pushpakalai\OneDrive\Desktop"
)

foreach ($dPath in $desktopPaths) {
    if (Test-Path $dPath) {
        $shortcutPath = Join-Path -Path $dPath -ChildPath "Smart Campus Digital Twin.lnk"
        $shortcut = $WshShell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $targetPath
        $shortcut.WorkingDirectory = $workingDir
        $shortcut.Description = "Launch Smart Campus Digital Twin (Backend & Frontend)"
        $shortcut.Save()
        Write-Host "Created Desktop shortcut at: $shortcutPath"
    }
}

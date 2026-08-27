@echo off
setlocal
cd /d "%~dp0"

echo Creating Desktop Shortcut for Namura Invoice Studio...

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$desktop = [Environment]::GetFolderPath('Desktop'); " ^
  "$shortcutPath = Join-Path $desktop 'Namura Invoice Studio.lnk'; " ^
  "$shortcut = $ws.CreateShortcut($shortcutPath); " ^
  "$shortcut.TargetPath = 'pythonw.exe'; " ^
  "$shortcut.Arguments = '\"%~dp0main.py\"'; " ^
  "$shortcut.WorkingDirectory = '%~dp0'; " ^
  "$shortcut.Description = 'Namura Invoice Studio - Desktop GST Invoicing'; " ^
  "$shortcut.Save()"

echo [DONE] Desktop shortcut created successfully on your Desktop!
echo You can now launch the app directly by double-clicking 'Namura Invoice Studio' on your Desktop.
pause

# Using RegForge

## Option 1: Run a .reg file directly
Open the tweak folder, read its `README.md`, then double-click `enable.reg`. To undo, double-click `disable.reg`.

## Option 2: Use the CLI (recommended)
`regforge.ps1` backs up the affected keys automatically before applying.

```powershell
# Allow the script for this session only
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\regforge.ps1 list
.\regforge.ps1 info explorer/show-file-extensions
.\regforge.ps1 apply explorer/show-file-extensions
.\regforge.ps1 revert explorer/show-file-extensions
.\regforge.ps1 profiles
.\regforge.ps1 profile essentials
```

Flags: `-Force` (skip prompt), `-NoBackup`, `-RestartExplorer`, `-BackupRoot <path>`.

Backups are saved to `%LOCALAPPDATA%\RegForge\backups\<timestamp>\`. To restore one, double-click the `.reg` files inside.
Tweaks marked **Requires admin** need an elevated PowerShell.

## Safety checklist
1. Create a system restore point for anything beyond HKCU tweaks.
2. Read the tweak README and the `.reg` file.
3. Apply, check the result, and keep the rollback handy.

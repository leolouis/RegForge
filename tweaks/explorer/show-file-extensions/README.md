Show File Extensions

Shows file extensions for known file types in Windows File Explorer.

What it changes

This tweak changes the following registry value:

Setting	Value
Hive	HKEY_CURRENT_USER
Path	Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced
Value	HideFileExt
Type	DWORD
Enable value	0
Revert value	1
Files

enable.reg — Shows file extensions.

disable.reg — Reverts the change and restores the default behavior.

Example

With extensions visible:

document.txt
photo.jpg
archive.zip
program.exe

Scope

This is a per-user setting under HKEY_CURRENT_USER.

Administrator privileges are not required.

Windows Compatibility

Intended for supported versions of Windows 10 and Windows 11.

Before Applying

Review the registry path and value above before applying the tweak.

For important systems, create an appropriate registry backup before making configuration changes.

Rollback

Run disable.reg to restore the original setting.

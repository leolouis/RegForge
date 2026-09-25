# Show File Extensions

Display file extensions for known file types in Windows File Explorer.

## Overview

Windows hides file extensions for known file types by default.

This tweak configures Windows File Explorer to display file extensions such as `.txt`, `.jpg`, `.zip`, and `.exe`.

## Registry Change

| Property | Value |
|---|---|
| Hive | `HKEY_CURRENT_USER` |
| Key | `Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced` |
| Value | `HideFileExt` |
| Type | `REG_DWORD` |
| Enable | `0` |
| Revert | `1` |
| Scope | Current user |

## Files

| File | Description |
|---|---|
| `enable.reg` | Enables file extensions |
| `disable.reg` | Reverts the change |
| `README.md` | Documentation |

## Usage

### Enable

Double-click `enable.reg` and confirm the Windows Registry prompt.

The following value will be set:

```text
HideFileExt = 0

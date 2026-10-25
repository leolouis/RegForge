# Contributing to RegForge

Thanks for helping! Every tweak must be **documented, reversible, and safe to review**.

## Adding a tweak

1. Pick the category: `explorer`, `taskbar`, `desktop`, `privacy`, `performance`, `networking`, `windows-update`, `system`.
2. Create `tweaks/<category>/<kebab-case-name>/` containing:

| File | Purpose |
|---|---|
| `enable.reg` | Applies the tweak |
| `disable.reg` | Restores the original state |
| `README.md` | Documentation (see `docs/TWEAK_TEMPLATE.md`) |
| `tweak.json` | Metadata used by the CLI and catalog |

3. Run the checks:

```bash
python scripts/validate.py
python scripts/build_catalog.py
python -m unittest discover -s tests
```

4. Open a PR and fill in the checklist.

## Rules for `.reg` files

- First line is exactly `Windows Registry Editor Version 5.00`, CRLF line endings, ASCII (or UTF-16 LE with BOM).
- Only `HKEY_CURRENT_USER` and `HKEY_LOCAL_MACHINE`. Never a hive root.
- `enable.reg` must **not** delete keys.
- `disable.reg` must cover every key `enable.reg` touches.
- **Rollback restores the default**: if the value did not exist by default, delete it (`"Name"=-`);
  if you created a whole key, remove it (`[-HKEY_...]`). Do not just flip to an opposite value
  unless that is the documented Windows default.
- Set `requiresAdmin` to `true` exactly when HKLM is touched (CI enforces this).

## `tweak.json` fields

`id` (`category/folder`), `name`, `category`, `description`, `requiresAdmin`, `windows`, `restart`,
`risk` (`low` | `medium` | `high`), `tags`, `tested`.

`tested` is a list of entries such as:

```json
{ "windows": "Windows 11 23H2 (22631)", "tester": "github-username", "date": "2026-01-15" }
```

Only add an entry if you actually applied **and** reverted the tweak on that build.

## Testing locally

On Windows, use a VM or restore point:

```powershell
.\regforge.ps1 apply <id>
.\regforge.ps1 revert <id>
```

# RegForge

[![CI](https://github.com/leolouis/RegForge/actions/workflows/ci.yml/badge.svg)](https://github.com/leolouis/RegForge/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A curated collection of safe, documented, and reversible Windows Registry tweaks.

## What is RegForge?

RegForge is an open-source collection of Windows Registry tweaks designed to make configuration changes easier to discover, understand, apply, and reverse.

Every tweak is intended to be:

- **Documented**: each key and value is explained
- **Reversible**: a rollback file restores the default state
- **Categorized**: easy to browse
- **Validated**: CI checks structure, rollback coverage and admin flags

See the full [tweak catalog](docs/CATALOG.md).

## Quick start

```powershell
git clone https://github.com/leolouis/RegForge.git
cd RegForge
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\regforge.ps1 list
.\regforge.ps1 info explorer/show-file-extensions
.\regforge.ps1 apply explorer/show-file-extensions    # backs up affected keys first
.\regforge.ps1 revert explorer/show-file-extensions
.\regforge.ps1 profile essentials                      # apply a bundle of tweaks
```

Prefer manual? Open a tweak folder, read its `README.md`, and double-click `enable.reg` (or `disable.reg` to undo). More in [docs/USAGE.md](docs/USAGE.md).

## Categories

| Category | Description |
|---|---|
| `explorer` | Windows File Explorer tweaks |
| `taskbar` | Taskbar and Start menu configuration |
| `desktop` | Desktop and visual settings |
| `privacy` | Privacy-related Windows settings |
| `performance` | System and UI performance settings |
| `networking` | Windows networking configuration |
| `windows-update` | Windows Update configuration |
| `system` | General Windows system settings |

## Repository structure

```
RegForge/
├── tweaks/<category>/<tweak>/
│   ├── enable.reg      apply
│   ├── disable.reg     rollback
│   ├── README.md       documentation
│   └── tweak.json      metadata
├── profiles/           bundles of tweaks (JSON)
├── docs/               usage guide, template, generated catalog
├── scripts/            validate.py, build_catalog.py
├── tests/              unit tests for the validator
├── regforge.ps1        CLI: list / info / apply / revert / backup / profile
└── .github/            CI, issue and PR templates
```

## Safety

Registry changes can affect Windows configuration and behavior. Before applying a tweak:

1. Read its documentation and the `.reg` file.
2. Create a restore point for anything beyond per-user (HKCU) tweaks.
3. Do not apply tweaks you do not understand.

RegForge aims to provide documented and reversible changes, but you are responsible for reviewing and testing changes on your own system. See [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome. Each tweak needs `enable.reg`, `disable.reg`, a `README.md` and a `tweak.json`. Full rules and the validation commands are in [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
python scripts/validate.py
python scripts/build_catalog.py
python -m unittest discover -s tests
```

## License

RegForge is released under the [MIT License](LICENSE).

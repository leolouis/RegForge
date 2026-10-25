#!/usr/bin/env python3
"""Validate every tweak and profile in the repository.

Usage: python scripts/validate.py [repo_root]
Exit code 0 = valid, 1 = problems found. Standard library only (Python 3.9+).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HEADER = "Windows Registry Editor Version 5.00"
CATEGORIES = {"explorer", "taskbar", "desktop", "privacy", "performance",
              "networking", "windows-update", "system"}
REQUIRED_META = {"id", "name", "category", "description", "requiresAdmin",
                 "windows", "restart", "risk", "tags", "tested"}
RISKS = {"low", "medium", "high"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KEY_LINE = re.compile(r"^\[(-?)(HKEY_[A-Z_]+)(\\[^\]]*)?\]$")
VALUE_LINE = re.compile(
    r'^(@|"(?:[^"\\]|\\.)+")=('
    r'-|"(?:[^"\\]|\\.)*"|dword:[0-9a-fA-F]{8}|hex(?:\([0-9a-fA-F]+\))?:[0-9a-fA-F,\\ \t]*)$'
)
ALLOWED_HIVES = {"HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE"}
README_SECTIONS = ["## What it changes", "## Rollback", "## Testing"]


def parse_reg(path: Path, errors: list[str]) -> tuple[list[tuple[str, bool]], set[str]]:
    """Return ([(key_path, is_key_delete)], {hives}) and append problems to errors."""
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe"):
        text = raw.decode("utf-16")
    else:
        try:
            text = raw.decode("ascii")
        except UnicodeDecodeError:
            errors.append(f"{path}: must be ASCII or UTF-16 LE with BOM")
            return [], set()
    if b"\r\n" not in raw.replace(b"\x00", b"") and len(text.splitlines()) > 1:
        errors.append(f"{path}: use CRLF line endings (.gitattributes handles this)")
    lines = text.splitlines()
    if not lines or lines[0].strip() != HEADER:
        errors.append(f"{path}: first line must be '{HEADER}'")
    keys: list[tuple[str, bool]] = []
    hives: set[str] = set()
    current = False
    for n, line in enumerate(lines[1:], start=2):
        s = line.strip()
        if not s or s.startswith(";"):
            continue
        m = KEY_LINE.match(s)
        if m:
            delete, hive, rest = m.group(1) == "-", m.group(2), m.group(3) or ""
            if hive not in ALLOWED_HIVES:
                errors.append(f"{path}:{n}: hive {hive} not allowed (use HKCU or HKLM)")
            if not rest:
                errors.append(f"{path}:{n}: refusing to touch a hive root")
            hives.add(hive)
            keys.append((hive + rest, delete))
            current = True
            continue
        if VALUE_LINE.match(s):
            if not current:
                errors.append(f"{path}:{n}: value before any [key]")
            continue
        if s.startswith(("\"", "@")) or "\\" in s and not s.startswith("["):
            continue  # continuation of a multi-line hex value
        errors.append(f"{path}:{n}: unrecognised line: {s[:60]}")
    if not keys:
        errors.append(f"{path}: contains no registry keys")
    return keys, hives


def covered(key: str, by: list[tuple[str, bool]]) -> bool:
    k = key.lower()
    return any(k == b.lower() or k.startswith(b.lower() + "\\") for b, _ in by)


def validate_tweak(d: Path, root: Path) -> list[str]:
    errors: list[str] = []
    rel = d.relative_to(root)
    for name in ("enable.reg", "disable.reg", "README.md", "tweak.json"):
        if not (d / name).is_file():
            errors.append(f"{rel}: missing {name}")
    if errors:
        return errors
    category, slug = d.parent.name, d.name
    if category not in CATEGORIES:
        errors.append(f"{rel}: unknown category '{category}'")
    if not SLUG.match(slug):
        errors.append(f"{rel}: folder name must be lowercase-kebab-case")
    try:
        meta = json.loads((d / "tweak.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return errors + [f"{rel}/tweak.json: invalid JSON ({e})"]
    missing = REQUIRED_META - set(meta)
    if missing:
        errors.append(f"{rel}/tweak.json: missing fields {sorted(missing)}")
    if meta.get("id") != f"{category}/{slug}":
        errors.append(f"{rel}/tweak.json: id must be '{category}/{slug}'")
    if meta.get("category") != category:
        errors.append(f"{rel}/tweak.json: category must match folder '{category}'")
    if meta.get("risk") not in RISKS:
        errors.append(f"{rel}/tweak.json: risk must be one of {sorted(RISKS)}")
    if not isinstance(meta.get("requiresAdmin"), bool):
        errors.append(f"{rel}/tweak.json: requiresAdmin must be true/false")
    if not isinstance(meta.get("tags"), list) or not isinstance(meta.get("tested"), list):
        errors.append(f"{rel}/tweak.json: tags and tested must be lists")

    en_keys, en_hives = parse_reg(d / "enable.reg", errors)
    di_keys, di_hives = parse_reg(d / "disable.reg", errors)
    for key, delete in en_keys:
        if delete:
            errors.append(f"{rel}/enable.reg: must not delete keys ([-{key}])")
        if not covered(key, di_keys):
            errors.append(f"{rel}/disable.reg: no rollback for key {key}")
    if isinstance(meta.get("requiresAdmin"), bool):
        needs_admin = "HKEY_LOCAL_MACHINE" in en_hives | di_hives
        if needs_admin != meta["requiresAdmin"]:
            errors.append(f"{rel}/tweak.json: requiresAdmin={meta['requiresAdmin']} "
                          f"but registry hives imply {needs_admin}")
    readme = (d / "README.md").read_text(encoding="utf-8")
    for sec in README_SECTIONS:
        if sec not in readme:
            errors.append(f"{rel}/README.md: missing section '{sec}'")
    return errors


def validate_repo(root: Path) -> list[str]:
    errors: list[str] = []
    tweaks_dir = root / "tweaks"
    ids: set[str] = set()
    if not tweaks_dir.is_dir():
        return ["tweaks/ directory not found"]
    for cat in sorted(p for p in tweaks_dir.iterdir() if p.is_dir()):
        for d in sorted(p for p in cat.iterdir() if p.is_dir()):
            errors += validate_tweak(d, root)
            ids.add(f"{cat.name}/{d.name}")
    prof_dir = root / "profiles"
    if prof_dir.is_dir():
        for p in sorted(prof_dir.glob("*.json")):
            try:
                prof = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                errors.append(f"{p.name}: invalid JSON ({e})")
                continue
            for field in ("name", "description", "tweaks"):
                if field not in prof:
                    errors.append(f"profiles/{p.name}: missing '{field}'")
            for tid in prof.get("tweaks", []):
                if tid not in ids:
                    errors.append(f"profiles/{p.name}: unknown tweak '{tid}'")
    return errors


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    errors = validate_repo(root)
    for e in errors:
        print(f"ERROR: {e}")
    count = sum(1 for _ in (root / "tweaks").glob("*/*/tweak.json"))
    print(f"{'FAILED' if errors else 'OK'}: {count} tweak(s), {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate  # noqa: E402

HDR = "Windows Registry Editor Version 5.00\r\n\r\n"


def make_tweak(root, cat="explorer", slug="demo", enable=None, disable=None, **meta):
    d = root / "tweaks" / cat / slug
    d.mkdir(parents=True)
    key = r"[HKEY_CURRENT_USER\Software\RegForgeTest]"
    (d / "enable.reg").write_bytes((enable or HDR + key + '\r\n"A"=dword:00000001\r\n').encode())
    (d / "disable.reg").write_bytes((disable or HDR + key + '\r\n"A"=-\r\n').encode())
    (d / "README.md").write_text("## What it changes\n## Rollback\n## Testing\n")
    base = dict(id=f"{cat}/{slug}", name="Demo", category=cat, description="d",
                requiresAdmin=False, windows="Windows 10", restart="None",
                risk="low", tags=[], tested=[])
    base.update(meta)
    (d / "tweak.json").write_text(json.dumps(base))


class RepoTests(unittest.TestCase):
    def test_real_repo_is_valid(self):
        self.assertEqual(validate.validate_repo(ROOT), [])

    def test_good_tweak_passes(self):
        with tempfile.TemporaryDirectory() as t:
            make_tweak(Path(t))
            self.assertEqual(validate.validate_repo(Path(t)), [])

    def test_missing_rollback_key_fails(self):
        with tempfile.TemporaryDirectory() as t:
            other = HDR + "[HKEY_CURRENT_USER\\Software\\Other]\r\n\"A\"=-\r\n"
            make_tweak(Path(t), disable=other)
            self.assertTrue(any("no rollback" in e for e in validate.validate_repo(Path(t))))

    def test_admin_flag_must_match_hive(self):
        with tempfile.TemporaryDirectory() as t:
            key = "[HKEY_LOCAL_MACHINE\\SOFTWARE\\RegForgeTest]"
            make_tweak(Path(t),
                       enable=HDR + key + '\r\n"A"=dword:00000001\r\n',
                       disable=HDR + key + '\r\n"A"=-\r\n')
            self.assertTrue(any("requiresAdmin" in e for e in validate.validate_repo(Path(t))))

    def test_bad_header_and_hive_root(self):
        with tempfile.TemporaryDirectory() as t:
            make_tweak(Path(t), enable="oops\r\n[HKEY_CURRENT_USER]\r\n")
            errs = validate.validate_repo(Path(t))
            self.assertTrue(any("first line" in e for e in errs))
            self.assertTrue(any("hive root" in e for e in errs))

    def test_enable_must_not_delete_keys(self):
        with tempfile.TemporaryDirectory() as t:
            make_tweak(Path(t), enable=HDR + "[-HKEY_CURRENT_USER\\Software\\RegForgeTest]\r\n")
            self.assertTrue(any("must not delete" in e for e in validate.validate_repo(Path(t))))

    def test_profile_unknown_tweak(self):
        with tempfile.TemporaryDirectory() as t:
            make_tweak(Path(t))
            (Path(t) / "profiles").mkdir()
            (Path(t) / "profiles" / "p.json").write_text(
                json.dumps({"name": "p", "description": "d", "tweaks": ["system/nope"]}))
            self.assertTrue(any("unknown tweak" in e for e in validate.validate_repo(Path(t))))


if __name__ == "__main__":
    unittest.main()

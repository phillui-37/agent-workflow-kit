import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "tool_index.py"
ENTRY = {
    "id": "helper", "summary": "Archive safely", "aliases": ["pack", "zip files"],
    "category": "backup", "kind": "script", "source": "./missing.py",
    "command": "python missing.py", "platforms": ["darwin"], "dependencies": [],
    "effects": "read-only", "status": "unverified", "verified_at": None
}


class ToolIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = self.root / "registry.json"
        self.registry.write_text(json.dumps({"version": 1, "tools": [ENTRY]}), encoding="utf-8")

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--registry", str(self.registry), *args], cwd=self.root, text=True, capture_output=True)

    def test_alias_search_and_os_alias_filter(self):
        found = self.run_cli("find", "zip", "--os", "macos", "--json")
        self.assertEqual(found.returncode, 0, found.stderr)
        self.assertEqual(json.loads(found.stdout)[0]["id"], "helper")
        absent = self.run_cli("find", "zip", "--os", "windows", "--json")
        self.assertEqual(json.loads(absent.stdout), [])
        self.assertEqual(absent.returncode, 0)

    def test_add_validates_and_requires_replace(self):
        entry_path = self.root / "entry.json"
        entry_path.write_text(json.dumps(ENTRY), encoding="utf-8")
        refused = self.run_cli("add", str(entry_path))
        self.assertEqual(refused.returncode, 2)
        bad = dict(ENTRY, id="INVALID ID")
        entry_path.write_text(json.dumps(bad), encoding="utf-8")
        invalid = self.run_cli("add", str(entry_path), "--replace")
        self.assertEqual(invalid.returncode, 2)
        entry_path.write_text(json.dumps(dict(ENTRY, summary="Updated")), encoding="utf-8")
        replaced = self.run_cli("add", str(entry_path), "--replace")
        self.assertEqual(replaced.returncode, 0, replaced.stderr)
        self.assertTrue(Path(str(self.registry) + ".bak").exists())

    def test_missing_registry_is_not_an_empty_search(self):
        self.registry.unlink()
        result = self.run_cli("find", "zip", "--json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("registry not found", result.stderr)
        self.assertFalse(self.registry.exists())
        entry_path = self.root / "entry.json"
        entry_path.write_text(json.dumps(ENTRY), encoding="utf-8")
        result = self.run_cli("add", str(entry_path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(self.registry.read_text())["tools"]), 1)

    def test_check_does_not_execute_catalog_command(self):
        marker = self.root / "executed"
        entry = dict(ENTRY, command="python -c 'open(%r, \\\"w\\\").write(\\\"bad\\\")'" % str(marker))
        self.registry.write_text(json.dumps({"version": 1, "tools": [entry]}), encoding="utf-8")
        result = self.run_cli("check", "helper")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        self.assertIn("unavailable", result.stdout)
        self.assertIn("unverified", result.stdout)


if __name__ == "__main__":
    unittest.main()

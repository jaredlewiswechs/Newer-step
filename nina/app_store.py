"""Simple App Store/Packaging utilities for TinyTalk apps.

Provides packaging (manifest + script), install, list, and uninstall utilities.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import hashlib
import json
from pathlib import Path
import zipfile

APPS_DIR = Path("nina/apps")
APPS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class AppManifest:
    name: str
    version: str = "0.1.0"
    entry: str = "main.tt"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def package_app_from_files(src_dir: Path, out_path: Path):
    """Create a zip package from a directory containing an app (manifest + script)."""
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src_dir.rglob("*"):
            z.write(p, p.relative_to(src_dir))
    # add a simple checksum
    h = hashlib.sha256(out_path.read_bytes()).hexdigest()
    return {"path": str(out_path), "sha256": h}


def install_app_from_payload(
    name: str, manifest: Dict[str, Any], script_content: str
) -> Dict[str, Any]:
    """Install app by writing files under `nina/apps/{name}` and return manifest."""
    app_dir = APPS_DIR / name
    app_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = app_dir / "manifest.json"
    script_path = app_dir / manifest.get("entry", "main.tt")

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    script_path.write_text(script_content, encoding="utf-8")

    return {"installed": True, "name": name, "manifest": manifest}


def list_installed_apps() -> List[Dict[str, Any]]:
    apps = []
    for d in APPS_DIR.iterdir():
        if d.is_dir():
            mf = d / "manifest.json"
            if mf.exists():
                try:
                    apps.append(json.loads(mf.read_text(encoding="utf-8")))
                except Exception:
                    apps.append({"name": d.name, "error": "manifest invalid"})
            else:
                apps.append({"name": d.name, "error": "missing manifest"})
    return apps


def uninstall_app(name: str) -> bool:
    app_dir = APPS_DIR / name
    if not app_dir.exists():
        return False
    # remove files
    for p in reversed(list(app_dir.rglob("*"))):
        try:
            if p.is_file():
                p.unlink()
            else:
                p.rmdir()
        except Exception:
            pass
    try:
        app_dir.rmdir()
    except Exception:
        pass
    return True

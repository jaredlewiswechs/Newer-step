"""Create a GitHub release and upload built artifacts.
Usage:
  GITHUB_TOKEN=<token> python scripts/release.py v0.1.0

This script builds a wheel/sdist and creates a release with assets.
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("tag")
parser.add_argument("--draft", action="store_true", help="Create a draft release")
parser.add_argument(
    "--prerelease", action="store_true", help="Mark release as prerelease"
)
args = parser.parse_args()

TAG = args.tag
IS_DRAFT = args.draft
IS_PRERELEASE = args.prerelease

RELEASE_NOTES = (
    Path("RELEASE_NOTES.md").read_text(encoding="utf-8")
    if Path("RELEASE_NOTES.md").exists()
    else ""
)
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY") or "yourorg/yourrepo"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("GITHUB_TOKEN not set. Aborting.")
    sys.exit(1)

# build
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "build"])
subprocess.check_call([sys.executable, "-m", "build"])

# find artifacts
dist = Path("dist")
artifacts = list(dist.glob("*"))

# create release
api = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
hdr = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
body = {
    "tag_name": TAG,
    "name": TAG,
    "body": RELEASE_NOTES,
    "draft": bool(IS_DRAFT),
    "prerelease": bool(IS_PRERELEASE),
}
resp = requests.post(api, headers=hdr, data=json.dumps(body))
if resp.status_code not in (200, 201):
    print("Failed to create release:", resp.status_code, resp.text)
    sys.exit(1)
release = resp.json()
upload_url = release["upload_url"].split("{")[0]

for a in artifacts:
    print("Uploading", a)
    headers = hdr.copy()
    headers["Content-Type"] = "application/octet-stream"
    params = {"name": a.name}
    with open(a, "rb") as f:
        r = requests.post(upload_url, headers=headers, params=params, data=f)
        if r.status_code not in (200, 201):
            print("Upload failed:", r.status_code, r.text)
        else:
            print("Uploaded", a.name)

print("Release complete:", TAG)

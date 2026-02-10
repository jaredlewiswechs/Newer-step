#!/usr/bin/env python3
"""Monitor GitHub Releases and Actions for a given repo and tag.
Usage: python scripts/monitor_release.py --repo owner/repo --tag v0.1.0 --interval 15 --tries 20
"""

import time
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True)
parser.add_argument("--tag", required=True)
parser.add_argument("--interval", type=int, default=15)
parser.add_argument("--tries", type=int, default=20)
args = parser.parse_args()

REPO = args.repo
TAG = args.tag
INTERVAL = args.interval
TRIES = args.tries

RELEASE_URL = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"
WORKFLOWS_URL = f"https://api.github.com/repos/{REPO}/actions/runs"

print(f"Monitoring release {TAG} in {REPO} (interval={INTERVAL}s, tries={TRIES})")

for i in range(TRIES):
    try:
        r = requests.get(RELEASE_URL)
        if r.status_code == 200:
            rel = r.json()
            print(
                f"Release found: id={rel.get('id')} name={rel.get('name')} draft={rel.get('draft')} prerelease={rel.get('prerelease')}"
            )
            print(f"HTML: {rel.get('html_url')}")
            break
        else:
            print(f"[{i+1}/{TRIES}] Release not found yet (status {r.status_code})")
    except Exception as e:
        print("Error fetching release:", e)

    # check actions runs for tag / workflow runs
    try:
        wr = requests.get(WORKFLOWS_URL)
        if wr.status_code == 200:
            runs = wr.json().get("workflow_runs", [])
            tag_runs = [
                run
                for run in runs
                if run.get("head_branch") in (TAG, f"refs/tags/{TAG}")
                or (
                    run.get("event") == "push"
                    and run.get("head_branch") == "main"
                    and any(
                        TAG in c.get("message", "")
                        for c in [run.get("head_commit", {})]
                    )
                )
            ]
            if tag_runs:
                for run in tag_runs[:5]:
                    print(
                        f"Workflow run: id={run.get('id')} name={run.get('name')} status={run.get('status')} conclusion={run.get('conclusion')} url={run.get('html_url')}"
                    )
            else:
                print("No tag-related workflow runs found yet.")
        else:
            print("Failed to fetch workflow runs:", wr.status_code)
    except Exception as e:
        print("Error fetching workflow runs:", e)

    time.sleep(INTERVAL)
else:
    print("Finished polling; release not found.")

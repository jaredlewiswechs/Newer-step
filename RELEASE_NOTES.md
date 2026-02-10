Newton Desktop Beta — Release Notes

Overview
--------
This release presents an interactive Desktop Shell prototype with built-in scripting (realTinyTalk), secure encrypted Vault storage, and an app packaging workflow.

Highlights
----------
- Desktop Shell with windowing and SVG rendering
- realTinyTalk scripting — apps are Turing-complete and sandboxable
- Per-process policy flags to limit FFI capabilities (vault/filesystem/system/network)
- Vault-backed persistence for apps (encrypted entries tied to process identities)
- Notes demo app with in-window editing and autosave
- IPC publish/subscribe model for inter-app messaging
- Simple App Store (install/uninstall) and demo UI
- CI workflow, tests, and packaging scripts

Getting Started
---------------
1. Install dependencies:
   pip install -r requirements.txt
2. Run the demo server:
   python -m uvicorn Kernel.demo.server:app --reload --port 9009
3. Open the shell demo:
   http://127.0.0.1:9009/kernel/demo/shell_page

Release Artifacts
-----------------
- Source sdist and wheel are built by CI on tag pushes (see .github/workflows/ci.yml)
- Use the included `scripts/release.py` to create a GitHub release and upload built artifacts (requires GITHUB_TOKEN env var)
- Optionally publish to PyPI by adding a secret `PYPI_API_TOKEN` to repository secrets. The release workflow will upload artifacts when this secret is present.

Known Issues
------------
- The cryptography library is optional; production deployments should ensure `cryptography` is available for secure Vault encryption.
- The platform is a prototype; do not use for sensitive production workloads without hardening.

Contributors
------------
- Jared Nashon Lewis and collaborators

License
-------
See LICENSE file in repository root.

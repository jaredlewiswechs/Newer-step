import subprocess

def test_release_script_dryrun():
    # Ensure the script handles --draft flag without token (should exit 1)
    res = subprocess.run(['python', 'scripts/release.py', 'v0.1.0', '--draft'], capture_output=True, text=True)
    assert res.returncode == 1
    assert 'GITHUB_TOKEN not set' in res.stdout or 'GITHUB_TOKEN not set' in res.stderr

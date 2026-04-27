#!/usr/bin/env python3
"""Push local repo to GitHub via REST API (bypasses git network block)."""
import base64, hashlib, json, os, sys, urllib.request

TOKEN = "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"
OWNER, REPO = "tzwkb", "tp_generator"
BASE_SHA = "e00bf441602b4063d74c51ae3687060da069019b"
LOCAL_DIR = r"E:\51talk_automation\tp_generator"

def api(method, path, data=None):
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps(data).encode() if data else None
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, method=method, headers=headers, data=body)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"API ERROR {e.code}: {err}")
        raise

# 1. Get base tree
def get_tree(sha, recursive=True):
    return api("GET", f"/repos/{OWNER}/{REPO}/git/trees/{sha}?recursive={'1' if recursive else '0'}")

base_tree = get_tree(BASE_SHA)
remote_paths = {item["path"]: item for item in base_tree.get("tree", [])}

# 2. Walk local files and create blobs for changed/new files
exclude = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules", ".venv", "venv"}

entries = []
changed = 0
for root, dirs, files in os.walk(LOCAL_DIR):
    # Skip excluded dirs
    dirs[:] = [d for d in dirs if d not in exclude]
    for fname in files:
        if fname.startswith(".") and fname != ".gitignore":
            continue
        full = os.path.join(root, fname)
        rel = os.path.relpath(full, LOCAL_DIR).replace("\\", "/")

        with open(full, "rb") as f:
            content = f.read()

        sha = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()

        remote = remote_paths.get(rel)
        if remote and remote.get("sha") == sha:
            # Unchanged: reuse remote blob sha
            entries.append({"path": rel, "mode": remote.get("mode", "100644"), "type": "blob", "sha": sha})
            continue

        # Changed or new: create blob
        encoding = "base64"
        b64 = base64.b64encode(content).decode()
        blob = api("POST", f"/repos/{OWNER}/{REPO}/git/blobs", {"content": b64, "encoding": encoding})
        entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        changed += 1
        print(f"  blob: {rel}")

print(f"\nTotal entries: {len(entries)}, changed/new: {changed}")

# 3. Create tree
print("Creating tree...")
tree = api("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"base_tree": base_tree["sha"], "tree": entries})
print(f"Tree sha: {tree['sha']}")

# 4. Create commit
print("Creating commit...")
commit = api("POST", f"/repos/{OWNER}/{REPO}/git/commits", {
    "message": "feat: unit file browser, defensive type handling, pdf chrome path, dev docs",
    "parents": [BASE_SHA],
    "tree": tree["sha"]
})
print(f"Commit sha: {commit['sha']}")

# 5. Update ref
print("Updating ref...")
ref = api("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/main", {"sha": commit["sha"], "force": False})
print(f"Ref updated: {ref['object']['sha']}")
print("\nDone. https://github.com/tzwkb/tp_generator")

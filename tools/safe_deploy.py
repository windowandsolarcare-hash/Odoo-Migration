#!/usr/bin/env python3
"""
safe_deploy.py  -  regression-guarded GitHub push for large Render-app files.

Reconstructed 2026-09-18 by the Specialists session from the documented spec
(memory/feedback_regression_guard_pushes.md) after the original was found
missing from C:\\Users\\dj\\. Behavior matches the documented guard:

  * Fetches the CURRENTLY-DEPLOYED version of the target path from GitHub.
  * Compares it to the local file you are about to push.
  * REFUSES the push if the local file is either:
        - more than 100 LINES shorter than deployed, OR
        - more than 25% SMALLER in bytes than deployed.
  * --force overrides the guard (only after you have diffed and confirmed
    the deletions are intentional).

Uses the `gh` CLI (already authenticated) for both the fetch and the push,
so it satisfies the protected-main ruleset (Contents API, not git push).

Usage:
  python C:/Users/dj/safe_deploy.py \
    --repo  windowandsolarcare-hash/saunders-render-app \
    --path  routers/owner/dashboard.py \
    --local "C:\\Users\\dj\\Documents\\Business\\Saunders Render App\\routers\\owner\\dashboard.py" \
    --msg   "2026-09-18 | dashboard.py | what changed" \
    [--branch main] [--force]
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile


def gh_api(args, input_file=None):
    """Run `gh api ...` and return (returncode, stdout, stderr)."""
    cmd = ["gh", "api"] + args
    if input_file:
        cmd += ["--input", input_file]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def fetch_deployed(repo, path, branch):
    """Return (content_bytes, sha) for the deployed file, or (None, None) if absent."""
    rc, out, err = gh_api([
        f"repos/{repo}/contents/{path}",
        "-f", f"ref={branch}",
    ])
    if rc != 0:
        if "Not Found" in (out + err) or "404" in (out + err):
            return None, None
        sys.exit(f"ERROR fetching deployed file: {err.strip() or out.strip()}")
    try:
        obj = json.loads(out)
    except json.JSONDecodeError:
        sys.exit(f"ERROR: could not parse gh api response for {path}")
    b64 = obj.get("content", "")
    sha = obj.get("sha")
    content = base64.b64decode(b64) if b64 else b""
    return content, sha


def count_lines(b):
    return b.count(b"\n") + (1 if b and not b.endswith(b"\n") else 0)


def main():
    ap = argparse.ArgumentParser(description="Regression-guarded GitHub push.")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--path", required=True, help="repo-relative path")
    ap.add_argument("--local", required=True, help="local file to push")
    ap.add_argument("--msg", required=True, help="commit message")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--force", action="store_true",
                    help="override the regression guard (diff first!)")
    args = ap.parse_args()

    if not os.path.isfile(args.local):
        sys.exit(f"ERROR: local file not found: {args.local}")

    with open(args.local, "rb") as f:
        local_bytes = f.read()
    if len(local_bytes) < 20:
        sys.exit(f"ERROR: local file is suspiciously tiny ({len(local_bytes)} bytes) "
                 f"- refusing to push an empty/near-empty file.")

    local_lines = count_lines(local_bytes)
    local_size = len(local_bytes)

    deployed_bytes, sha = fetch_deployed(args.repo, args.path, args.branch)

    if deployed_bytes is None:
        print(f"[safe_deploy] No deployed version of {args.path} - treating as NEW file.")
    else:
        dep_lines = count_lines(deployed_bytes)
        dep_size = len(deployed_bytes)
        line_drop = dep_lines - local_lines
        size_ratio = (local_size / dep_size) if dep_size else 1.0
        print(f"[safe_deploy] deployed: {dep_lines} lines / {dep_size} bytes")
        print(f"[safe_deploy] local:    {local_lines} lines / {local_size} bytes")
        print(f"[safe_deploy] delta:    {line_drop:+d} lines, "
              f"local is {size_ratio*100:.1f}% of deployed bytes")

        regressed = (line_drop > 100) or (size_ratio < 0.75)
        if regressed and not args.force:
            sys.exit(
                "\n[safe_deploy] BLOCKED: local is >100 lines shorter or >25% smaller "
                "than deployed.\n"
                "  Your local copy is probably STALE. Fetch the live file, re-apply your\n"
                "  edit, and try again. If the deletions are truly intentional, diff to\n"
                "  confirm, then re-run with --force.\n"
            )
        if regressed and args.force:
            print("[safe_deploy] WARNING: regression guard tripped but --force given; proceeding.")

    # Build payload and push via Contents API PUT.
    b64_content = base64.b64encode(local_bytes).decode("ascii")
    payload = {"message": args.msg, "content": b64_content, "branch": args.branch}
    if sha:
        payload["sha"] = sha

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        json.dump(payload, tf)
        payload_path = tf.name
    try:
        rc, out, err = gh_api([
            f"repos/{args.repo}/contents/{args.path}",
            "--method", "PUT",
        ], input_file=payload_path)
    finally:
        os.unlink(payload_path)

    if rc != 0:
        sys.exit(f"[safe_deploy] PUSH FAILED: {err.strip() or out.strip()}")

    try:
        commit = json.loads(out).get("commit", {}).get("sha", "")[:8]
    except Exception:
        commit = ""
    print(f"[safe_deploy] PUSHED {args.path} to {args.repo}@{args.branch} "
          f"({local_lines} lines) commit {commit}")


if __name__ == "__main__":
    main()

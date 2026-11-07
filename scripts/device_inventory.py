#!/usr/bin/env python3
"""Read-only, metadata-only inventory for explicitly selected project roots.

This tool does not read file contents, inspect environment values, follow symlinks,
access browser profiles/credential stores, or upload results. Output is local and
ignored by Git. Review the roots and output before sharing anything.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__",
    ".ssh", ".gnupg", ".android", ".mozilla", ".config", ".cache",
    "browser", "profiles", "credentials", "keychains", "vault", "secrets",
    "backups", "downloads", "DCIM", "Pictures", "Movies", "Music",
    "Android", "apks", "dist", "build", "target",
}
SKIP_NAMES = {
    ".env", ".env.local", ".env.production", "id_rsa", "id_ed25519",
    "known_hosts", "authorized_keys", "credentials.json", "secrets.json",
    "token.json", "cookies", "cookies.sqlite", ".git-credentials",
}
SECRET_NAME = re.compile(r"(^|[._-])(secret|credential|token|password|private.?key|api.?key)([._-]|$)", re.I)
MAX_ENTRIES = 100_000


def category(path: Path) -> str:
    suffix = path.suffix.lower()
    name = path.name.lower()
    if name in {"pyproject.toml", "package.json", "cargo.toml", "go.mod", "requirements.txt"}:
        return "project-manifest"
    if suffix in {".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd"}:
        return "script"
    if suffix in {".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".java", ".kt", ".c", ".h", ".cpp", ".cs"}:
        return "source"
    if suffix in {".toml", ".yaml", ".yml", ".json", ".ini", ".conf"}:
        return "config-file"
    if suffix in {".md", ".rst", ".txt"}:
        return "documentation"
    if suffix in {".html", ".css", ".scss"}:
        return "web-ui"
    if suffix in {".zip", ".tar", ".gz", ".7z", ".apk"}:
        return "archive-or-binary"
    return "other"


def safe_root_label(path: Path, index: int) -> str:
    # Do not put absolute device/user paths into the portable report.
    label = path.name.strip() or f"root-{index}"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", label)[:64] or f"root-{index}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", required=True, help="directory to inspect; repeat to add explicit roots")
    parser.add_argument("--device-id", required=True, help="non-sensitive label, e.g. termux-phone (never use a serial number)")
    parser.add_argument("--output-dir", default=".workbench-local", help="local output directory (default: .workbench-local)")
    parser.add_argument("--max-entries", type=int, default=MAX_ENTRIES)
    args = parser.parse_args()

    device_id = re.sub(r"[^A-Za-z0-9._-]+", "-", args.device_id).strip("-.")[:48]
    if not device_id:
        parser.error("--device-id must contain letters or numbers")
    if args.max_entries < 1 or args.max_entries > MAX_ENTRIES:
        parser.error(f"--max-entries must be between 1 and {MAX_ENTRIES}")

    records: list[dict[str, object]] = []
    skipped = 0
    roots: list[tuple[Path, str]] = []
    for i, raw in enumerate(args.root, start=1):
        root = Path(raw).expanduser()
        if not root.exists() or not root.is_dir():
            print(f"Skipping unavailable directory: {root}", file=sys.stderr)
            continue
        roots.append((root.resolve(), safe_root_label(root, i)))
    if not roots:
        parser.error("no accessible directories were supplied")

    for root, label in roots:
        for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
            current_path = Path(current)
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS
                       and not SECRET_NAME.search(d)
                       and not (current_path / d).is_symlink()]
            for filename in files:
                if len(records) >= args.max_entries:
                    skipped += 1
                    break
                path = current_path / filename
                if filename.startswith(".") or filename in SKIP_NAMES or SECRET_NAME.search(filename):
                    skipped += 1
                    continue
                try:
                    if path.is_symlink() or not path.is_file():
                        skipped += 1
                        continue
                    stat = path.stat()
                    relative = path.relative_to(root).as_posix()
                    records.append({
                        "root": label,
                        "relative_path": relative,
                        "name": filename,
                        "kind": category(path),
                        "extension": path.suffix.lower(),
                        "size_bytes": stat.st_size,
                        "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                    })
                except (OSError, ValueError):
                    skipped += 1
            if len(records) >= args.max_entries:
                break

    records.sort(key=lambda item: (str(item["root"]).casefold(), str(item["relative_path"]).casefold()))
    result = {
        "schema_version": 1,
        "device_label": device_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host_platform": platform.system().lower(),
        "host_machine": platform.machine(),
        "roots": [label for _, label in roots],
        "mode": "metadata-only; no file contents read; no upload performed",
        "entry_count": len(records),
        "skipped_count": skipped,
        "entries": records,
    }
    outdir = Path(args.output_dir).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / f"inventory-{device_id}.json"
    outfile.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for row in records:
        kind = str(row["kind"])
        counts[kind] = counts.get(kind, 0) + 1
    print(f"Inventory saved locally: {outfile}")
    print(f"Device label: {device_id}; entries: {len(records)}; skipped: {skipped}")
    for kind, count in sorted(counts.items()):
        print(f"  {kind}: {count}")
    print("No upload or Git operation was performed. Review and sanitize before sharing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

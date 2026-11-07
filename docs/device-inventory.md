# Device inventory quick start

The inventory helper is intentionally local-only. It records file metadata under directories explicitly passed with `--root`; it does not read file bodies or upload anything.

## Termux / Linux / macOS

```sh
python3 scripts/device_inventory.py \
  --device-id phone-a \
  --root "$HOME/projects" \
  --root /storage/XXXX-XXXX/projects
```

## Review before any sharing

- Do not point it at all of `/`, `/storage/emulated/0`, or an entire removable volume on the first run. Start with known project folders.
- Hidden directories, common dependency/build/cache directories, browser/credential locations, and secret-named files are excluded.
- The report uses root labels and relative paths, but filenames and project names can still be private. Inspect the JSON before sharing it.
- The script does not read file contents, environment-variable values, browser cookies, tokens, or keys.
- Output is written to `.workbench-local/`, which is ignored by Git. Nothing is pushed automatically.

Windows users can run this script with Python and pass explicit paths, for example `--root "$HOME\\source"`. Device-specific storage paths vary.

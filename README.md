# Workbench

**A local-first host for composing the tools you already have.**

Workbench is inspired by the DAW model: tools, models, scripts, agents, and services are independent instruments; adapters let them participate in a shared session; and a session composes them into a useful workflow. It is not a repository merger or a file-search product.

## Start here

This branch establishes the project direction and a deliberately conservative first utility: a local metadata-only inventory script. It does **not** upload device data, read file contents, inspect environment-variable values, scrape browser sessions, or modify discovered files.

```sh
python3 scripts/device_inventory.py \
  --device-id termux-phone \
  --root ~/projects \
  --root /storage/XXXX-XXXX/projects
```

The script prints a summary and writes JSON under `.workbench-local/` (ignored by Git). Review the selected roots before running. Add only directories you intend to inventory. To retain or share results, inspect and manually sanitize the generated JSON first; do not commit raw inventories.

## Product shape

- **Host:** adapts to the current device and provides a consistent session surface.
- **Instruments:** existing local tools and services, kept independent.
- **Adapters:** explicit, inspectable connections to CLIs, local model APIs, browser extensions, and approved service APIs.
- **Sessions:** visible compositions of instruments, with inputs, outputs, and provenance.
- **Presets:** repeatable workflows, such as project review or a local-business pitch package.
- **Safety:** least privilege, local-first operation, secret redaction, visible actions, and confirmation before installs, network access, or writes.

## Current status

Bootstrap only. No device scan has been run from this repository, and no existing project has yet been confirmed as a working plugin. Candidate projects named in the initial exploration include Whorl, Code-City-Apocalypse, Tribunal, and the IDE/DAW-related local folders; each needs an entry-point and runtime check before integration.

See [ROADMAP.md](ROADMAP.md) for staged implementation and safety boundaries.

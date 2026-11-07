# Workbench connectors

`workbench_connect.py` is the first operational slice: a provider-neutral CLI host with explicit adapters, not a catalog. It currently supports local Ollama and OpenAI-compatible HTTP APIs; it does not yet support native Claude/Gemini APIs or browser/app sessions.

Read [provider-connections.md](docs/provider-connections.md) before configuring providers. Remote calls require explicit opt-in and per-request confirmation. Keep credentials outside the repository.

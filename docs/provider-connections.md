# Provider connector: first working slice

The first connector slice is intentionally small: it proves the host can invoke an existing local model or a user-configured OpenAI-compatible endpoint without absorbing either into Workbench. It is not a claim that every named service uses the same API protocol.

## Setup

```sh
mkdir -p ~/.config/workbench
cp config/providers.example.json ~/.config/workbench/providers.json
```

Edit the copy, set a real installed model/provider, and leave unused providers disabled. For a remote API, set the credential in your shell using the provider's documented method; configure only the environment-variable *name* in JSON. Never put the key itself in the config, command history, repository, or report.

## Use

```sh
python3 scripts/workbench_connect.py list
python3 scripts/workbench_connect.py models ollama-local
printf '%s\n' 'Summarize this non-sensitive test prompt.' | \
  python3 scripts/workbench_connect.py ask ollama-local
```

Remote endpoints require HTTPS, `--allow-remote`, and typing `SEND` for each request. Example:

```sh
printf '%s\n' 'Explain this harmless example.' | \
  python3 scripts/workbench_connect.py ask openai-compatible-example --allow-remote
```

The confirmation names the endpoint host. Prompts are sent only when `ask` is run. `list` is offline. Requests have a timeout and response-size cap; request/response data and credentials are not saved by this script.

## Scope and next adapters

- Implemented: local Ollama `/api/chat` and `/api/tags`; OpenAI-compatible `/chat/completions` and `/models`.
- Not implemented: Anthropic Messages, Google Gemini, browser sessions, IDE protocol, Android app handoff, or automatic credential discovery. Add each as a separate adapter after checking its supported API and auth model.
- Browser integration should use an explicitly installed extension and authorized interfaces. Do not scrape session cookies or reuse browser tokens.
- For providers that require different protocol semantics, write a native adapter rather than assuming OpenAI compatibility.

This is a connector proof, not yet a visual DAW/session canvas. Next: define a versioned capability contract, then compose two real existing tools with visible inputs, outputs, and provenance.

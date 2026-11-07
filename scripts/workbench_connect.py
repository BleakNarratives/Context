#!/usr/bin/env python3
"""Small, opt-in connector host for local Ollama and OpenAI-compatible APIs.

No provider is contacted by listing or inspecting configuration. Network calls
require an explicit `ask`/`models` command; non-loopback calls additionally need
--allow-remote and an interactive confirmation. Secrets are referenced by
environment-variable name and are never printed or written to disk.
"""
from __future__ import annotations

import argparse
import getpass
import ipaddress
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

MAX_RESPONSE_BYTES = 2 * 1024 * 1024
TIMEOUT_SECONDS = 45


def default_config() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    return Path(base).expanduser() / "workbench" / "providers.json" if base else Path.home() / ".config" / "workbench" / "providers.json"


def is_loopback(host: str) -> bool:
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host.split("%", 1)[0]).is_loopback
    except ValueError:
        return False


def validate_base_url(raw: str) -> tuple[str, bool]:
    parsed = urllib.parse.urlsplit(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("endpoint must be an http(s) URL with a hostname")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("endpoint URL must not contain credentials, query, or fragment")
    local = is_loopback(parsed.hostname)
    if parsed.scheme != "https" and not local:
        raise ValueError("non-local endpoints must use HTTPS")
    return raw.rstrip("/"), local


def load_providers(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("providers") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise ValueError("config must contain a providers array")
    providers: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not row.get("name"):
            raise ValueError("each provider must be an object with a name")
        name = str(row["name"])
        if name in providers:
            raise ValueError(f"duplicate provider name: {name}")
        if row.get("type") not in {"ollama", "openai-compatible"}:
            raise ValueError(f"unsupported provider type for {name}")
        if not isinstance(row.get("model"), str) or not row["model"].strip():
            raise ValueError(f"provider {name} needs a model")
        row["base_url"], row["_loopback"] = validate_base_url(str(row.get("base_url", "")))
        row["enabled"] = row.get("enabled", True) is True
        providers[name] = row
    return providers


def request_json(url: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request_headers = {"Accept": "application/json", **(headers or {})}
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=request_headers, method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"provider returned HTTP {exc.code}; response body suppressed") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"provider connection failed: {type(exc).__name__}") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("provider response exceeded 2 MiB limit")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("provider returned invalid JSON") from None


def authorize_call(provider: dict[str, Any], args: argparse.Namespace) -> None:
    if not provider["enabled"]:
        raise RuntimeError("provider is disabled in configuration")
    if provider["_loopback"]:
        return
    if not args.allow_remote:
        raise RuntimeError("remote endpoint blocked; rerun with --allow-remote after reviewing its destination")
    if not sys.stdin.isatty():
        raise RuntimeError("remote calls require an interactive confirmation")
    host = urllib.parse.urlsplit(provider["base_url"]).hostname
    print(f"This will send your prompt to the configured remote provider at {host}.")
    if input("Type SEND to confirm this request: ") != "SEND":
        raise RuntimeError("remote request cancelled")


def api_headers(provider: dict[str, Any]) -> dict[str, str]:
    if provider["type"] != "openai-compatible":
        return {}
    env_name = provider.get("api_key_env")
    if env_name:
        if not str(env_name).replace("_", "").isalnum():
            raise RuntimeError("api_key_env must be an environment-variable name")
        value = os.environ.get(str(env_name))
        if not value:
            raise RuntimeError(f"required environment variable {env_name} is not set")
        return {"Authorization": f"Bearer {value}"}
    return {}


def get_models(provider: dict[str, Any], headers: dict[str, str]) -> list[str]:
    base = provider["base_url"]
    if provider["type"] == "ollama":
        result = request_json(base + "/api/tags", headers=headers)
        return sorted(str(m.get("name", "")) for m in result.get("models", []) if m.get("name"))
    result = request_json(base + "/models", headers=headers)
    return sorted(str(m.get("id", "")) for m in result.get("data", []) if m.get("id"))


def ask(provider: dict[str, Any], prompt: str, headers: dict[str, str]) -> str:
    base, model = provider["base_url"], provider["model"]
    if provider["type"] == "ollama":
        result = request_json(base + "/api/chat", {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}, headers)
        return str(result.get("message", {}).get("content", ""))
    result = request_json(base + "/chat/completions", {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}, headers)
    choices = result.get("choices", [])
    if not choices:
        raise RuntimeError("provider response contained no completion")
    return str(choices[0].get("message", {}).get("content", ""))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=default_config(), help="provider config JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list configured providers without contacting them")
    models_cmd = sub.add_parser("models", help="request model list from one provider")
    models_cmd.add_argument("provider")
    models_cmd.add_argument("--allow-remote", action="store_true", help="permit remote HTTPS request after interactive confirmation")
    ask_cmd = sub.add_parser("ask", help="send one prompt to a configured provider")
    ask_cmd.add_argument("provider")
    ask_cmd.add_argument("--prompt", help="prompt text; if omitted, read stdin")
    ask_cmd.add_argument("--allow-remote", action="store_true", help="permit remote HTTPS request after interactive confirmation")
    args = parser.parse_args()

    try:
        providers = load_providers(args.config)
        if args.command == "list":
            for name, p in sorted(providers.items()):
                state = "enabled" if p["enabled"] else "disabled"
                print(f"{name}\t{p['type']}\tmodel={p['model']}\t{state}")
            return 0
        provider = providers.get(args.provider)
        if provider is None:
            raise RuntimeError(f"unknown provider: {args.provider}")
        authorize_call(provider, args)
        headers = api_headers(provider)
        if args.command == "models":
            for model in get_models(provider, headers):
                print(model)
            return 0
        prompt = args.prompt if args.prompt is not None else sys.stdin.read()
        if not prompt.strip():
            raise RuntimeError("prompt is empty")
        answer = ask(provider, prompt, headers)
        print(answer)
        return 0
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(f"workbench: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

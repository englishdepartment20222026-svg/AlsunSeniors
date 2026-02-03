from __future__ import annotations

import json
import os
import subprocess
import tempfile
from hashlib import sha256
from pathlib import Path
from typing import Any

DEFAULT_REPO_PATH = Path(__file__).resolve().parent / "FBScrapeIdeas"


def _normalize_text(payload: dict[str, Any]) -> str:
    for key in ("text", "message", "content", "body"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _normalize_title(payload: dict[str, Any]) -> str:
    for key in ("title", "headline", "subject"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Facebook update"


def _normalize_timestamp(payload: dict[str, Any]) -> str:
    for key in ("time", "timestamp", "published_at", "published"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "just now"


def _build_external_id(payload: dict[str, Any]) -> str:
    for key in ("id", "post_id", "external_id"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    seed = json.dumps(payload, sort_keys=True)
    return sha256(seed.encode()).hexdigest()


def _load_posts_from_output(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        data = data.get("posts", [])
    if not isinstance(data, list):
        return []
    return data


def _resolve_command() -> str | None:
    command = os.environ.get("FBSCRAPE_CMD")
    if command:
        return command
    local_entry = DEFAULT_REPO_PATH / "main.py"
    if local_entry.exists():
        return f"python {local_entry}"
    return None


def scrape_facebook_posts(page_url: str, cookies_path: Path, cursor: str | None) -> tuple[list[dict[str, Any]], str, str]:
    command = _resolve_command()
    if not command:
        return [], cursor or "initial", "missing_command"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "fb_posts.json"
        env = os.environ.copy()
        env.update(
            {
                "FB_PAGE_URL": page_url,
                "FB_COOKIES_PATH": str(cookies_path),
                "FB_CURSOR": cursor or "",
                "FB_OUTPUT_PATH": str(output_path),
            }
        )
        result = subprocess.run(command, shell=True, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            return [], cursor or "initial", "command_failed"
        raw_posts = _load_posts_from_output(output_path)

    normalized: list[dict[str, Any]] = []
    for payload in raw_posts:
        if not isinstance(payload, dict):
            continue
        normalized.append(
            {
                "external_id": _build_external_id(payload),
                "title": _normalize_title(payload),
                "body": _normalize_text(payload),
                "time": _normalize_timestamp(payload),
            }
        )

    new_cursor = normalized[0]["external_id"] if normalized else (cursor or "initial")
    return normalized, new_cursor, "ok"

"""Deterministic, UTF-8-safe I/O helpers for the Obsidian learning vault."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f\x7f]')


def safe_slug(value: str, fallback: str = "untitled") -> str:
    """Return a Windows-safe, non-blank filename component."""
    text = "" if value is None else str(value)
    text = _INVALID.sub("-", text).strip().strip(".")
    text = re.sub(r"\s+", " ", text)
    if not text:
        text = str(fallback)
        text = _INVALID.sub("-", text).strip().strip(".") or "untitled"
    # Windows reserves device names even with an extension.
    stem = text.split(".", 1)[0].upper()
    if stem in {"CON", "PRN", "AUX", "NUL"} or re.fullmatch(r"COM[1-9]|LPT[1-9]", stem):
        text = f"-{text}"
    return text


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_utf8_atomic(path: Path, text: str) -> None:
    """Write normalized UTF-8/LF bytes using a sibling temporary file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    normalized = str(text).replace("\r\n", "\n").replace("\r", "\n")
    payload = normalized.encode("utf-8")
    temporary: Path | None = None
    try:
        fd, name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
        temporary = Path(name)
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        temporary = None
        final = target.read_bytes()
        if final.decode("utf-8") != normalized or final != payload:
            raise IOError(f"atomic write verification failed for {target}")
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def append_unique_section(path: Path, source_id: str, section: str) -> bool:
    target = Path(path)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    marker = f"<!-- source-id: {source_id} -->"
    if marker in existing:
        return False
    block = f"{marker}\n{str(section).replace(chr(13)+chr(10), chr(10)).replace(chr(13), chr(10)).rstrip(chr(10))}"
    if existing and not existing.endswith("\n"):
        existing += "\n"
    if existing:
        existing += "\n"
    write_utf8_atomic(target, existing + block + "\n")
    return True


def copy_attachment(source: Path, vault_root: Path, relative_dir: str) -> tuple[Path, str]:
    src = Path(source)
    root = Path(vault_root).resolve()
    if not src.is_file():
        raise FileNotFoundError(src)
    rel = Path(relative_dir)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("relative_dir must remain within vault root")
    destination_dir = (root / rel).resolve()
    try:
        destination_dir.relative_to(root)
    except ValueError as exc:
        raise ValueError("attachment destination escapes vault root") from exc
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / safe_slug(src.name)
    # Never overwrite an existing file (or follow a pre-existing symlink).
    # ``lexists`` also catches dangling symlinks, which ``Path.exists`` misses.
    if os.path.lexists(destination):
        raise FileExistsError(f"attachment destination already exists: {destination}")
    shutil.copyfile(src, destination)
    return destination, sha256_file(src)


class LearningVault:
    def __init__(self, vault_root: Path):
        self.vault_root = Path(vault_root).resolve()
        self.vault_root.mkdir(parents=True, exist_ok=True)

    def assert_inside(self, path: Path) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.vault_root / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.vault_root)
        except ValueError as exc:
            raise ValueError(f"path escapes vault root: {path}") from exc
        return resolved

    def draft_metadata(
        self,
        *,
        source_kind: str,
        course: str,
        topic: str,
        source_id: str,
        content: str = "",
        source: str | None = None,
        created: str | None = None,
        updated: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        payload = str(content).replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        return {
            "agent_status": "draft",
            "source": source if source is not None else source_id,
            "created": created or now,
            "updated": updated or now,
            "source_kind": source_kind,
            "course": course,
            "topic": topic,
            "content_hash": hashlib.sha256(payload).hexdigest(),
        }

    def write_draft(
        self,
        path: Path,
        content: str,
        metadata: dict[str, Any] | None = None,
        *,
        source_kind: str = "chat",
        course: str = "",
        topic: str = "",
        source_id: str = "",
        source: str | None = None,
    ) -> Path:
        target = self.assert_inside(path)
        generated = self.draft_metadata(
            source_kind=source_kind, course=course, topic=topic,
            source_id=source_id, content=content, source=source,
        )
        if metadata:
            # Required fields are authoritative and cannot be overridden by
            # caller-supplied extension metadata.
            required = set(generated)
            generated.update({k: v for k, v in metadata.items() if k not in required})
        frontmatter = "---\n" + "".join(f"{k}: {str(v).replace(chr(10), ' ')}\n" for k, v in generated.items()) + "---\n\n"
        write_utf8_atomic(target, frontmatter + str(content))
        return target

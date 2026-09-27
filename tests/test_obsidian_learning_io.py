import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.obsidian_learning_io import (  # noqa: E402
    LearningVault,
    append_unique_section,
    copy_attachment,
    safe_slug,
    sha256_file,
    write_utf8_atomic,
)


class TestLearningVaultIO(unittest.TestCase):
    def test_utf8_without_bom_and_lf_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "中文.md"
            text = "# 课堂\n\n公式：\u222b x e^x dx\n"
            write_utf8_atomic(path, text)
            raw = path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
            self.assertNotIn(b"\r", raw)
            self.assertEqual(raw.decode("utf-8"), text)

    def test_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = LearningVault(Path(tmp))
            with self.assertRaises(ValueError):
                vault.assert_inside(Path(tmp).parent / "outside.md")

    def test_safe_slug_removes_windows_invalid_characters(self):
        self.assertEqual(safe_slug('a:b*c?d"e<f>g|h'), "a-b-c-d-e-f-g-h")
        self.assertEqual(safe_slug("   "), "untitled")

    def test_append_unique_section_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "daily.md"
            first = "### 问题\n答案"
            self.assertTrue(append_unique_section(path, "abc123", first))
            before = path.read_bytes()
            self.assertFalse(append_unique_section(path, "abc123", first))
            self.assertEqual(path.read_bytes(), before)

    def test_copy_attachment_preserves_bytes_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "原始.pdf"
            source.write_bytes("pdf-bytes-中文".encode("utf-8"))
            dest, digest = copy_attachment(source, root, "附件/学习输入/2026/09")
            self.assertTrue(dest.is_file())
            self.assertEqual(dest.read_bytes(), source.read_bytes())
            self.assertEqual(digest, sha256_file(source))
            self.assertTrue(str(dest.relative_to(root)).startswith("附件"))

    def test_copy_attachment_rejects_existing_destination_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.bin"
            source.write_bytes(b"payload")
            dest_dir = root / "attachments"
            dest_dir.mkdir()
            existing = dest_dir / source.name
            existing.write_bytes(b"old")
            with self.assertRaises(FileExistsError):
                copy_attachment(source, root, "attachments")
            existing.unlink()
            outside = root.parent / (root.name + "-outside.bin")
            outside.write_bytes(b"outside")
            try:
                existing.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with self.assertRaises(FileExistsError):
                copy_attachment(source, root, "attachments")
            self.assertEqual(outside.read_bytes(), b"outside")

    def test_draft_metadata_contains_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = LearningVault(Path(tmp))
            metadata = vault.draft_metadata(
                source_kind="chat", course="高等数学", topic="拉格朗日中值定理", source_id="abc123"
            )
            for key in (
                "agent_status",
                "source",
                "created",
                "updated",
                "source_kind",
                "course",
                "topic",
                "content_hash",
            ):
                self.assertIn(key, metadata)
            self.assertEqual(metadata["agent_status"], "draft")

    def test_write_draft_required_metadata_is_authoritative(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = LearningVault(Path(tmp))
            content = "# draft\ncontent\n"
            target = vault.write_draft(
                "draft.md", content,
                {"agent_status": "published", "content_hash": "bad", "course": "tampered", "extra": "ok"},
                source_kind="chat", course="calculus", topic="limits", source_id="s1",
            )
            text = target.read_text(encoding="utf-8")
            self.assertIn("agent_status: draft", text)
            self.assertNotIn("content_hash: bad", text)
            self.assertIn("course: calculus", text)
            self.assertIn("extra: ok", text)


if __name__ == "__main__":
    unittest.main()

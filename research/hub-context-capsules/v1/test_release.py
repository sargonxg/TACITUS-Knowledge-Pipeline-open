import json
from pathlib import Path
import shutil
import tempfile
import unittest
from hashlib import sha256
from build import build, canonical
from verify import verify


class ContextReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage = tempfile.TemporaryDirectory()
        cls.release = Path(cls.storage.name) / "release"
        build(cls.release)

    @classmethod
    def tearDownClass(cls):
        cls.storage.cleanup()

    def setUp(self):
        self.storage_copy = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage_copy.cleanup)
        self.base = Path(self.storage_copy.name) / "release"
        shutil.copytree(self.release, self.base)

    def rewrite_manifest_hash(self, path):
        manifest_path = self.base / "release.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"][path] = sha256((self.base / path).read_bytes()).hexdigest()
        manifest_path.write_bytes(canonical(manifest))

    def test_exact_release_verifies_without_network_or_model(self):
        self.assertEqual(verify(self.base), {"verified": True, "records": 4808, "links": 7427, "capsules": 7, "model_calls": 0, "human_approval": False})

    def test_source_text_change_cannot_be_hidden_by_a_rewritten_manifest(self):
        path = "sources/gdpr.txt"
        target = self.base / path
        target.write_text(target.read_text().replace("where designated", "in every case", 1))
        self.rewrite_manifest_hash(path)
        with self.assertRaisesRegex(ValueError, "Changed source edition"):
            verify(self.base)

    def test_omitting_a_qualification_cannot_be_recertified_as_the_published_capsule(self):
        path = "capsules/qualified-advice.json"
        packet = json.loads((self.base / path).read_text())
        packet["records"] = [row for row in packet["records"] if "where designated" not in row["quote"]]
        packet["integrity"]["sha256"] = sha256(canonical({key: value for key, value in packet.items() if key != "integrity"})).hexdigest()
        (self.base / path).write_bytes(canonical(packet))
        self.rewrite_manifest_hash(path)
        with self.assertRaisesRegex(ValueError, "Published capsule pin changed"):
            verify(self.base)

    def test_dataset_viewer_cannot_silently_show_different_evidence(self):
        path = "records.jsonl"
        lines = (self.base / path).read_text().splitlines()
        row = json.loads(lines[0])
        row["quote"] = "Changed evidence"
        lines[0] = canonical(row).decode()
        (self.base / path).write_text("\n".join(lines) + "\n")
        self.rewrite_manifest_hash(path)
        with self.assertRaisesRegex(ValueError, "Viewer rows differ"):
            verify(self.base)

    def test_existing_release_cannot_be_overwritten(self):
        with self.assertRaises(FileExistsError):
            build(self.base)


if __name__ == "__main__":
    unittest.main()

"""Prepare the public Hub release from unchanged, source-pinned research data."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
from verify import verify

ROOT = Path(__file__).resolve().parents[3]
GRAPH_SHA = "31841211f001820b43cf3fbe9f209cd3cf1d70a6a26b5bef7a9c6b20f05680a6"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def build(destination):
    if destination.exists():
        raise FileExistsError("Refusing to replace an existing release")
    destination.parent.mkdir(parents=True, exist_ok=True)
    atlas = ROOT / "research/ai-governance-source-map/v2"
    graph_bytes = (atlas / "graph.json").read_bytes()
    if sha256(graph_bytes).hexdigest() != GRAPH_SHA:
        raise ValueError("Source graph changed; review a new release instead of relabeling it")
    graph = json.loads(graph_bytes)
    registry = json.loads((ROOT / "research/ai-governance-source-map/context-packets-v1/packets.json").read_text())
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        out = Path(temporary) / "release"
        out.mkdir()
        (out / "source-map.json").write_bytes(graph_bytes)
        for name in ["RIGHTS.md", "ontology.json"]:
            shutil.copyfile(atlas / name, out / name)
        for source in graph["meta"]["sources"]:
            path = Path(source["extracted_text"])
            if path.is_absolute() or ".." in path.parts or path.parts[0] != "sources":
                raise ValueError("Unexpected source path")
            target = out / path
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(atlas / path, target)
        for name, rows in [("records", graph["nodes"]), ("relations", graph["edges"])]:
            (out / (name + ".jsonl")).write_bytes(b"".join(canonical(row) + b"\n" for row in rows))
        (out / "capsules").mkdir()
        summaries = []
        for identity, packet in sorted(registry["packets"].items()):
            if not identity or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in identity):
                raise ValueError("Unexpected capsule identifier")
            path = "capsules/" + identity + ".json"
            (out / path).write_bytes(canonical(packet) + b"\n")
            summaries.append({"id": identity, "title": packet["title"], "question": packet["editorial_context"]["question"],
                              "canonical_utf8_bytes": packet["measurements"]["packet_utf8_bytes"],
                              "review_status": packet["review"]["status"], "path": path})
        (out / "capsules.jsonl").write_bytes(b"".join(canonical(row) + b"\n" for row in summaries))
        shutil.copyfile(Path(__file__).with_name("DATASET_CARD.md"), out / "README.md")
        shutil.copyfile(Path(__file__).with_name("verify.py"), out / "verify.py")
        manifest = {"schema": "tacitus.hub-context-release/1", "source_graph_sha256": GRAPH_SHA,
                    "source_graph_commit": "b96550da802c2992577142016245c6453d937e8b",
                    "context_packets_commit": "c18dc4e84d77fea4699365184a3c0784cda21ad8",
                    "counts": {"records": len(graph["nodes"]), "links": len(graph["edges"]), "capsules": len(summaries)},
                    "files": {str(p.relative_to(out)): sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob("*")) if p.is_file()}}
        (out / "release.json").write_bytes(canonical(manifest) + b"\n")
        result = verify(out)
        out.rename(destination)
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(build(parser.parse_args().output), sort_keys=True))

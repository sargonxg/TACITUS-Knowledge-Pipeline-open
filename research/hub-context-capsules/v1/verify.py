"""Verify the downloadable context release offline; makes no network/model calls."""
from hashlib import sha256
import json
from pathlib import Path
import sys

GRAPH_SHA = "31841211f001820b43cf3fbe9f209cd3cf1d70a6a26b5bef7a9c6b20f05680a6"
CAPSULE_SHA = {'assessment-boundaries': '76ba2fe899cc365f976e8868f1132198f543bc7fa51e71054bbf923fcd3f24e1', 'dsa-systemic-risks': '467781b798cb4d2e67d7125cc26cfb6abefabc0ed49c8e6ea107722a1bd2390f', 'human-oversight': 'cf1495be79fb01fdb6014316bb42a0ee946b390246817b64016d67633defd1f7', 'meta-cooperation-consent': '45505e17d7b9ab0ffc8c36ee26fda44cec0e57e888b7e43732d13ef2d270717e', 'online-declarations': '1ee4408f09dbdef2973e6c6e675d96e96895608fe5491c5a9b4f5a3becdc75a5', 'qualified-advice': '4a09f9e23c843a64bf7ebfafe49d8cc4073538e33228cbc16a950e61cad0a27f', 'schufa-scoring': 'c735f01255e544042938a692d4e27e90dd85f454f34403dcc8323fd4d498e271'}


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def verify(base):
    base = Path(base)
    manifest = json.loads((base / "release.json").read_text())
    require(manifest["schema"] == "tacitus.hub-context-release/1", "Unknown release")
    require(manifest["source_graph_sha256"] == GRAPH_SHA, "Source graph release pin changed")
    for name, digest in manifest["files"].items():
        path = Path(name)
        require(not path.is_absolute() and ".." not in path.parts and (base / path).resolve().is_relative_to(base.resolve()), "Unsafe release path")
        require(sha256((base / path).read_bytes()).hexdigest() == digest, "Changed file: " + name)
    raw = (base / "source-map.json").read_bytes()
    require(sha256(raw).hexdigest() == manifest["source_graph_sha256"], "Changed source graph")
    graph = json.loads(raw)
    nodes = {node["id"]: node for node in graph["nodes"]}
    require(len(nodes) == len(graph["nodes"]), "Duplicate source identity")
    texts = {}
    for source in graph["meta"]["sources"]:
        source_path = Path(source["extracted_text"])
        require(not source_path.is_absolute() and ".." not in source_path.parts and (base / source_path).resolve().is_relative_to(base.resolve()), "Unsafe source path")
        data = (base / source_path).read_bytes()
        require(sha256(data).hexdigest() == source["extracted_sha256"], "Changed source edition")
        texts[source["id"]] = data.decode("utf8")
    for node in nodes.values():
        require(isinstance(node["source_start"], int) and isinstance(node["source_end"], int) and 0 <= node["source_start"] < node["source_end"] <= len(texts[node["document_id"]]), "Invalid source offsets")
        require(texts[node["document_id"]][node["source_start"]:node["source_end"]] == node["quote"], "Quotation or offset differs: " + node["id"])
    edge_ids = set()
    for edge in graph["edges"]:
        require(edge["id"] not in edge_ids and edge["source"] in nodes and edge["target"] in nodes, "Invalid relation")
        edge_ids.add(edge["id"])
    for filename, expected in [("records.jsonl", graph["nodes"]), ("relations.jsonl", graph["edges"])]:
        require([json.loads(line) for line in (base / filename).read_text().splitlines()] == expected, "Viewer rows differ from graph")
    capsules = [json.loads(line) for line in (base / "capsules.jsonl").read_text().splitlines()]
    require({row["id"] for row in capsules} == set(CAPSULE_SHA) and len(capsules) == len(CAPSULE_SHA), "Capsule membership changed")
    for summary in capsules:
        require(summary["path"] == "capsules/" + summary["id"] + ".json", "Unexpected capsule path")
        packet = json.loads((base / summary["path"]).read_text())
        require(packet["id"] == summary["id"] and packet["integrity"]["sha256"] == CAPSULE_SHA[packet["id"]], "Published capsule pin changed")
        body = {key: value for key, value in packet.items() if key != "integrity"}
        require(sha256(canonical(body)).hexdigest() == packet["integrity"]["sha256"], "Changed capsule body")
        require(packet["source_graph"]["sha256"] == manifest["source_graph_sha256"], "Capsule source pin changed")
        require(packet["review"]["status"] == "not_expert_approved" == summary["review_status"], "Approval provenance changed")
        size = len(canonical(packet))
        require(size == summary["canonical_utf8_bytes"] == packet["measurements"]["packet_utf8_bytes"] <= packet["selection"]["budget_utf8_bytes"], "Capsule exceeds its declared budget")
        for record in packet["records"]:
            require(record["quote"] == nodes[record["id"]]["quote"], "Capsule evidence changed")
    counts = {"records": len(nodes), "links": len(edge_ids), "capsules": len(capsules)}
    require(counts == manifest["counts"], "Release counts differ")
    return {"verified": True, **counts, "model_calls": 0, "human_approval": False}


if __name__ == "__main__":
    print(json.dumps(verify(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent), sort_keys=True))

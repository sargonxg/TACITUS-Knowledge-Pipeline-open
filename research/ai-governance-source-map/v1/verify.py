#!/usr/bin/env python3
"""Offline checks of source integrity, exact evidence and reproducible extraction."""
from collections import Counter
import json
from pathlib import Path
import re

from build import BASE, build_graph, compact, digest, record_list


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def verify(base=BASE):
    raw = (base / "graph.json").read_bytes()
    graph = json.loads(raw)
    rebuilt, snapshots = build_graph(base)
    require(compact(rebuilt) == raw, "Graph is not an exact deterministic rebuild from pinned sources")
    require(record_list(graph) == (base / "records.csv").read_bytes(), "Record list differs from graph")
    vocab = json.loads((base / "ontology.json").read_text())
    nodes = {n["id"]: n for n in graph["nodes"]}
    require(len(nodes) == len(graph["nodes"]), "Duplicate node IDs")
    require(len({e["id"] for e in graph["edges"]}) == len(graph["edges"]), "Duplicate edge IDs")
    require(len({(e['source'], e['target'], e['relation']) for e in graph['edges']}) == len(graph['edges']), "Duplicate relation")
    for source in graph["meta"]["sources"]:
        doc = source["id"]
        snapshot = (base / source["extracted_text"]).read_text(encoding="utf-8")
        require(snapshot == snapshots[doc], "Text extraction differs from source XHTML: " + doc)
        require(digest(snapshot.encode()) == source["extracted_sha256"], "Text snapshot hash mismatch")
        kind_counts = Counter(n["kind"] for n in nodes.values() if n["document_id"] == doc)
        require(kind_counts["article"] == source["expected_articles"], "Unexpected article count: " + doc)
        require(kind_counts["recital"] == source["expected_recitals"], "Unexpected recital count: " + doc)
    for n in nodes.values():
        require(n["kind"] in vocab["node_kinds"], "Unknown kind")
        require(n["layer"] == vocab["node_kinds"][n["kind"]]["layer"], "Incorrect node layer")
        s, e = n["source_start"], n["source_end"]
        require(0 <= s < e <= len(snapshots[n["document_id"]]), "Invalid source offsets")
        require(snapshots[n["document_id"]][s:e] == n["quote"], "Quote mismatch: " + n["id"])
        require(n["quote"].strip(), "Empty source quote")
        if n["kind"] == "passage":
            require(not re.fullmatch(r"(?:\([\w]+\)|[\d.]+)", n["quote"]), "Bare list label padded into a record")
            require(n["parent_id"] in nodes, "Missing passage container")
    for e in graph["edges"]:
        require(e["source"] in nodes and e["target"] in nodes, "Dangling edge")
        relation = vocab["edge_relations"][e["relation"]]
        require(e["layer"] == relation["layer"], "Incorrect edge layer")
        require(nodes[e["source"]]["kind"] in relation["domain"], "Invalid relation source")
        require(nodes[e["target"]]["kind"] in relation["range"], "Invalid relation target")
        require(e["method"] in vocab["methods"], "Unknown extraction method")
        if "evidence" in e:
            evidence_node = nodes[e.get("evidence_node", e["source"])]
            require(evidence_node["quote"][e["match_start"]:e["match_end"]] == e["evidence"], "Untraceable edge evidence")
        if e["relation"] == "mentions_term":
            term = nodes[e["target"]]
            require(nodes[e["source"]]["document_id"] == term["document_id"], "Unwarranted cross-document term equivalence")
            require(e["evidence"].casefold() == term["label"].casefold(), "Non-literal terminology match")
        if e["relation"] == "defines_term":
            require(e["target"] and "‘" + nodes[e["target"]]["label"] + "’" in nodes[e["source"]]["quote"], "Invented definition")
    for preset in graph["meta"]["presets"]:
        require(all(i in nodes for i in preset["node_ids"]), "Broken reading preset")
    counts = graph["meta"]["counts"]
    require(counts["nodes"] == len(nodes) and counts["edges"] == len(graph["edges"]), "Incorrect published scale")
    require(counts["node_kinds"] == dict(sorted(Counter(n["kind"] for n in nodes.values()).items())), "Incorrect kind counts")
    require(counts["edge_relations"] == dict(sorted(Counter(e["relation"] for e in graph["edges"]).items())), "Incorrect relation counts")
    for layer, c in counts["layers"].items():
        require(c["nodes"] == sum(n["layer"] == layer for n in nodes.values()), "Incorrect node layer count")
        require(c["edges"] == sum(e["layer"] == layer for e in graph["edges"]), "Incorrect edge layer count")

    # Regression checks for substantive errors that would mislead a policy analyst.
    def links(source, relation="references_article"):
        return {e["target"] for e in graph["edges"] if e["source"] == source and e["relation"] == relation}
    require("gdpr:article:35" in links("ai-act:passage:027.004"), "Lost explicit AI Act → GDPR reference")
    require("ai-act:article:27" not in links("ai-act:passage:027.004"), "Foreign Directive 2016/680 reference falsely resolved to AI Act 27")
    require("gdpr:article:4" in links("ai-act:passage:art_3:p057"), "Qualified personal-data reference mis-scoped")
    require("ai-act:article:4" not in links("ai-act:passage:art_3:p057"), "GDPR definition reference falsely resolved to AI Act 4")
    require(not links("ai-act:passage:art_3:p028"), "Foreign standardisation act reference falsely resolved locally")
    require(not links("gdpr:passage:093.003"), "Foreign ‘thereof’ antecedent falsely resolved to GDPR")
    require("where designated" in nodes["gdpr:passage:035.002"]["quote"], "Dropped important DPO condition")
    require("according to the instructions for use" in nodes["ai-act:passage:027.001:p06"]["quote"], "Oversight source or reading preset is wrong")
    require("ai-act:passage:005.004:in-art_107" in nodes, "Quoted amendment anchor collision not disambiguated")
    for art in range(99, 111):
        require(not any(e["layer"] == "references" and nodes[e["source"]].get("parent_id") == f"ai-act:article:{art}" for e in graph["edges"]), "Inserted amendment text incorrectly scope-resolved")
    require(sum(n["kind"] == "defined_term" and n["document_id"] == "ai-act" for n in nodes.values()) == 68, "AI Act qualified definition omitted")
    require(sum(n["kind"] == "defined_term" and n["document_id"] == "gdpr" for n in nodes.values()) == 26, "GDPR definition omitted")
    return dict(status="passed", nodes=len(nodes), edges=len(graph["edges"]),
                graph_bytes=len(raw), graph_sha256=digest(raw),
                checks=["pinned official source hashes", "212 articles / 353 recitals", "exact quote offsets",
                        "all relation domains and ranges", "literal edge evidence", "cross-instrument scope regressions",
                        "94 explicit definitions", "qualifiers preserved", "reading preset references",
                        "record list fidelity", "byte-for-byte reproducible build"])


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))

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
        if source.get("format") == "curia_html":
            records = [n for n in nodes.values() if n["document_id"] == doc and n.get("record_role") == "judgment_paragraph"]
            numbers = {int(n["locator"].split(":")[-1]) for n in records}
            require(numbers == set(range(1, source["expected_numbered_paragraphs"]+1)), "Missing or duplicate numbered judgment paragraph: " + doc)
            require(source["ecli"] in (base / "sources" / (doc + ".html")).read_text(), "Wrong case identity: " + doc)
            heading = nodes[doc + ":document"]["quote"]
            require("JUDGMENT OF THE COURT" in heading, "Not an issued Court judgment: " + doc)
            require(source["source_date_text"] in heading, "Wrong event date: " + doc)
            require(source["decision_date"] == next(c["decision_date"] for c in graph["meta"]["cases"] if c["id"] == doc), "Case event date drift")
        else:
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
        require(preset["route_kind"].startswith("editorial_"), "Editorial route presented as extraction")
    for case in graph["meta"]["cases"]:
        require(case["route_id"] in {p["id"] for p in graph["meta"]["presets"]}, "Missing case route")
        require(case["outcome_node_ids"] and all(nodes[i].get("record_role") == "judgment_operative_part" for i in case["outcome_node_ids"]), "Outcome not anchored to operative text")
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
    require("led:article:27" in links("ai-act:passage:027.004"), "Lost distinct explicit Law Enforcement Directive assessment reference")
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
    require(sum(n["kind"] == "defined_term" and n["document_id"] == "dsa" for n in nodes.values()) == 24, "DSA definition omitted")
    require(sum(n["kind"] == "defined_term" and n["document_id"] == "led" for n in nodes.values()) == 16, "LED definition omitted")
    require("draws strongly" in nodes["schufa:passage:operative:1"]["quote"], "SCHUFA reliance condition dropped")
    require("for the referring court to verify" in nodes["schufa:passage:paragraph:72"]["quote"], "National-court question turned into a decided finding")
    require("liable to disclose indirectly" in nodes["online-declarations:passage:operative:2"]["quote"], "Indirect sensitive-data condition dropped")
    require("in so far as, in particular" in nodes["online-declarations:passage:operative:1"]["quote"], "Declaration-publication finding broadened")
    require("subject to compliance with its duty of sincere cooperation" in nodes["meta-platforms:passage:operative:1"]["quote"], "Authority cooperation limit dropped")
    require("does not, as such, preclude" in nodes["meta-platforms:passage:operative:8"]["quote"], "Dominance incorrectly turned into automatic invalid consent")
    require("which it is for that operator to prove" in nodes["meta-platforms:passage:operative:8"]["quote"], "Consent burden dropped")
    for e in graph["edges"]:
        if nodes[e["source"]]["document_id"] in {c["id"] for c in graph["meta"]["cases"]} and e["relation"] == "references_article":
            require(e["method"] == "lexical_explicit_instrument_reference", "A judgment reference guessed statute scope")
            require(not e["target"].startswith("ai-act:"), "Historical GDPR judgment falsely made an AI Act ruling")
    previous = json.loads((base / "previous-release-lock.json").read_text())
    for name, sha in previous["files"].items():
        require(digest((base.parent / previous["release"] / name).read_bytes()) == sha, "Immutable v1 artifact changed: " + name)
    original = json.loads((base.parent / "v1" / "graph.json").read_text())
    for n in original["nodes"]:
        require(nodes[n["id"]] == n, "Original source record or exact quotation changed: " + n["id"])
    return dict(status="passed", nodes=len(nodes), edges=len(graph["edges"]),
                graph_bytes=len(raw), graph_sha256=digest(raw),
                cases=len(graph["meta"]["cases"]),
                checks=["seven pinned official source hashes", "370 articles / 616 recitals", "exact quote offsets",
                        "all relation domains and ranges", "literal edge evidence", "cross-instrument scope regressions",
                        "134 explicit definition openings", "three complete numbered judgments and operative parts",
                        "historical dates and judgment identities", "case outcome qualifiers and cooperation conditions",
                        "editorial routes separated from extracted links", "all immutable v1 files and records preserved",
                        "record list fidelity", "byte-for-byte reproducible build"])


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))

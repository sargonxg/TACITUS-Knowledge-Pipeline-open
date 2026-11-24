#!/usr/bin/env python3
"""Verify route packets against frozen official sources, not merely a checksum."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from build import (BASE, GRAPH_DIR, GRAPH_SHA256, BUNDLE_SCHEMA, PACKET_SCHEMA,
                   CANONICALIZATION, DEFAULT_BUDGET, ContextBudgetError,
                   canonical, sha256, compile_packets, complete_packet, load_frozen_graph)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def reject_floats(value):
    if isinstance(value, float):
        raise AssertionError("Canonical packet numbers must be integers")
    if isinstance(value, dict):
        for v in value.values():
            reject_floats(v)
    elif isinstance(value, list):
        for v in value:
            reject_floats(v)


def validate_bundle(bundle, graph, snapshots):
    reject_floats(bundle)
    require(bundle["schema"] == BUNDLE_SCHEMA, "Unexpected bundle schema")
    require(bundle["source_graph"]["sha256"] == GRAPH_SHA256, "Unpinned source graph")
    node_index = {n["id"]: n for n in graph["nodes"]}
    sources = {s["id"]: s for s in graph["meta"]["sources"]}
    presets = {p["id"]: p for p in graph["meta"]["presets"]}
    require(set(bundle["packets"]) == set(presets), "Missing or substituted route packet")
    require(bundle["packet_count"] == len(presets) == 7, "Incorrect packet count")
    all_checks = 0
    for ident, packet in bundle["packets"].items():
        require(packet["schema"] == PACKET_SCHEMA and packet["id"] == ident, "Wrong standalone packet identity")
        require(packet["editorial_context"]["id"] == ident, "Wrong editorial route identity")
        require(all(packet["editorial_context"][k] == v for k, v in presets[ident].items()), "Frozen route guidance changed")
        require(packet["selection"]["requested_node_ids"] == presets[ident]["node_ids"], "Route requests changed")
        require(packet["review"]["status"] == "not_expert_approved", "False expert approval state")
        require(packet["source_graph"] == bundle["source_graph"], "Mismatched packet graph identity")
        records = {n["id"]: n for n in packet["records"]}
        navigation = {n["id"]: n for n in packet["navigation"]}
        require(len(records) == len(packet["records"]), "Repeated evidence record")
        require(not set(records) & set(navigation), "Heading counted as substantive evidence")
        require(packet["selection"]["retained_record_ids"] == [n["id"] for n in packet["records"]], "Retained record list differs")
        require(packet["selection"]["navigation_ids"] == [n["id"] for n in packet["navigation"]], "Navigation list differs")
        require(not packet["selection"]["omitted_requested_node_ids"] and not packet["selection"]["omitted_expanded_record_ids"], "Silent omission")
        for record in records.values():
            require(record["kind"] == "passage", "Heading treated as model evidence")
            require(record == node_index[record["id"]], "Source record changed: " + record["id"])
            start, end = record["source_start"], record["source_end"]
            require(snapshots[record["document_id"]][start:end] == record["quote"], "Official source span differs")
            require(record["parent_id"] in navigation, "Source heading/parent identity lost")
        for nav in navigation.values():
            require(nav["role"] == "navigation_only", "Unlabelled navigation heading")
            source = node_index[nav["id"]]
            require(nav["heading_quote"] == source["quote"], "Heading source text changed")
            for key in ("kind", "label", "document_id", "locator", "source_url", "source_start", "source_end"):
                require(nav[key] == source[key], "Heading provenance changed")
        selected = set(records) | set(navigation)
        for requested in presets[ident]["node_ids"]:
            require(requested in selected, "Requested source record absent: " + requested)
            if node_index[requested]["kind"] == "article":
                genuine = {e["target"] for e in graph["edges"] if e["source"] == requested and e["relation"] == "contains" and node_index[e["target"]]["kind"] == "passage"}
                require(genuine <= set(records), "Article body or subpoint lost: " + requested)
                require(set(packet["selection"]["article_expansions"][requested]) == genuine, "Article expansion is not genuine source containment")
        expected_edges = [e for e in graph["edges"] if e["layer"] == "references" and e["source"] in selected and e["target"] in selected]
        require(packet["relations"] == expected_edges, "Invented, modified or missing retained source reference")
        for pointer in packet["selection"]["outside_packet_reference_targets"]:
            require(pointer["role"] == "pointer_only_not_supplied_evidence" and pointer["id"] not in selected, "Missing evidence disguised as supplied context")
            require("quote" not in pointer, "External pointer contains an unverified snippet")
            for key in ("id", "label", "document_id", "source_url"):
                require(pointer[key] == node_index[pointer["id"]][key], "Outside reference identity changed")
        docs = {n["document_id"] for n in packet["records"] + packet["navigation"]}
        require(set(packet["sources"]) == docs, "Standalone packet lacks source identities")
        require(all(source == sources[doc] for doc, source in packet["sources"].items()), "Source edition, rights or hashes changed")
        for q in packet["selection"]["required_qualifiers"]:
            require(q["record_id"] in records, "Required qualifier source absent")
            require(records[q["record_id"]]["quote"][q["within_record_start"]:q["within_record_end"]] == q["exact_text"], "Qualifier text or span lost")
            all_checks += 1
        m = packet["measurements"]
        require(m["packet_utf8_bytes"] == len(canonical(packet)), "Wrong standalone UTF-8 byte measurement")
        require(m["packet_utf8_bytes"] <= packet["selection"]["budget_utf8_bytes"] == DEFAULT_BUDGET, "Unbounded packet or undisclosed budget drift")
        require(m["substantive_records"] == len(records) and m["navigation_records"] == len(navigation), "Incorrect evidence count")
        require(m["quoted_utf8_bytes"] == sum(len(n["quote"].encode("utf-8")) for n in records.values()), "Incorrect quote byte measurement")
        require(m["retained_reference_edges"] == len(expected_edges) and m["source_documents"] == len(docs), "Incorrect relation/source count")
        require(m["required_qualifier_checks"] == len(packet["selection"]["required_qualifiers"]), "Incorrect qualifier count")
        require(packet["integrity"]["algorithm"] == "sha256" and packet["integrity"]["canonicalization"] == CANONICALIZATION, "Unknown checksum convention")
        unsigned = {k: v for k, v in packet.items() if k != "integrity"}
        require(packet["integrity"]["sha256"] == sha256(canonical(unsigned)), "Packet checksum mismatch")

    # Independent source-condition regressions: not inferred merely from the
    # compiler's own list of required qualifiers.
    def quote(route, record):
        return next(n["quote"] for n in bundle["packets"][route]["records"] if n["id"] == record)
    require("draws strongly on that probability value" in quote("schufa-scoring", "schufa:passage:operative:1"), "SCHUFA reliance condition lost")
    require("for the referring court to verify" in quote("schufa-scoring", "schufa:passage:paragraph:72"), "National-court reservation lost")
    for route in ("assessment-boundaries", "qualified-advice"):
        require("where designated" in quote(route, "gdpr:passage:035.002"), "GDPR designation qualifier lost")
    require("by competent authorities" in quote("assessment-boundaries", "led:passage:001.001"), "LED scope lost")
    require("shall always be considered to be high-risk where" in quote("assessment-boundaries", "ai-act:passage:006.003:p07"), "AI classification override lost")
    require("in so far as, in particular" in quote("online-declarations", "online-declarations:passage:operative:1"), "Declaration-publication scope broadened")
    require("liable to disclose indirectly" in quote("online-declarations", "online-declarations:passage:operative:2"), "Indirect sensitive disclosure lost")
    require("subject to compliance with its duty of sincere cooperation" in quote("meta-cooperation-consent", "meta-platforms:passage:operative:1"), "Authority cooperation condition lost")
    require("does not, as such, preclude" in quote("meta-cooperation-consent", "meta-platforms:passage:operative:8"), "Consent finding overgeneralized")
    require("which it is for that operator to prove" in quote("meta-cooperation-consent", "meta-platforms:passage:operative:8"), "Consent burden lost")
    require("and which are designated" in quote("dsa-systemic-risks", "dsa:passage:033.001"), "DSA designation condition lost")
    require(all_checks == 21, "Reviewed qualifier coverage changed")
    return all_checks


def negative_checks(bundle, graph, snapshots):
    changed = deepcopy(bundle)
    p = changed["packets"]["schufa-scoring"]
    next(n for n in p["records"] if n["id"] == "schufa:passage:operative:1")["quote"] = "A fabricated blanket prohibition on scoring."
    complete_packet(p)  # Even a newly valid checksum cannot make a wrong quote true.
    try:
        validate_bundle(changed, graph, snapshots)
    except AssertionError as e:
        require("Source record changed" in str(e), "Unexpected tamper rejection")
    else:
        raise AssertionError("A rehashed source misquotation was accepted")
    with TemporaryDirectory(prefix="tacitus-context-packet-", dir="/tmp") as tmp:
        output = Path(tmp) / "prior.json"
        output.write_bytes(b"PRESERVE THE PREVIOUS OUTPUT")
        result = subprocess.run([sys.executable, "-B", str(BASE / "build.py"), "--budget-utf8-bytes", "1", "--output", str(output)], capture_output=True)
        require(result.returncode != 0 and b"no source text was clipped" in result.stderr, "Insufficient budget did not fail explicitly")
        require(output.read_bytes() == b"PRESERVE THE PREVIOUS OUTPUT", "Budget failure overwrote an existing output")
        concurrent = Path(tmp) / "concurrent.json"
        commands = [[sys.executable, "-B", str(BASE / "build.py"), "--output", str(concurrent)]] * 2
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for command in commands]
        for process in processes:
            _, stderr = process.communicate()
            require(process.returncode == 0, "Concurrent rebuild failed: " + stderr.decode())
        require(concurrent.read_bytes() == canonical(bundle), "Concurrent rebuild corrupted the output")
        require(not list(Path(tmp).glob(".concurrent.json.*.tmp")), "Temporary publication file was not cleaned up")
        copied = Path(tmp) / "graph"
        copied.mkdir()
        shutil.copy2(GRAPH_DIR / "graph.json", copied / "graph.json")
        shutil.copytree(GRAPH_DIR / "sources", copied / "sources")
        source = copied / "sources" / "schufa.html"
        source.write_bytes(source.read_bytes() + b"\n")
        try:
            load_frozen_graph(copied)
        except ValueError as e:
            require("Pinned official source snapshot differs: schufa" in str(e), "Unexpected raw-source rejection")
        else:
            raise AssertionError("A changed official judgment snapshot was accepted")


def main():
    raw = (BASE / "packets.json").read_bytes()
    bundle = json.loads(raw)
    require(raw == canonical(bundle), "Bundle is not the declared canonical JSON serialization")
    graph, snapshots = load_frozen_graph()
    checks = validate_bundle(bundle, graph, snapshots)
    require(canonical(compile_packets()) == raw, "Bundle is not a byte-for-byte offline rebuild")
    negative_checks(bundle, graph, snapshots)
    print(json.dumps(dict(status="passed", routes=len(bundle["packets"]), required_qualifier_checks=checks,
                          bundle_utf8_bytes=len(raw), bundle_sha256=sha256(raw),
                          smallest_packet_bytes=min(p["measurements"]["packet_utf8_bytes"] for p in bundle["packets"].values()),
                          largest_packet_bytes=max(p["measurements"]["packet_utf8_bytes"] for p in bundle["packets"].values()),
                          budget_utf8_bytes=DEFAULT_BUDGET,
                          negative_checks=["rehashed misquotation rejected", "insufficient budget preserves prior output", "concurrent atomic rebuilds preserve exact output and clean up", "altered official judgment snapshot rejected"],
                          limitation="Source-context assembly and fidelity checks only; no model generation or answer-quality comparison"), indent=2))


if __name__ == "__main__":
    main()

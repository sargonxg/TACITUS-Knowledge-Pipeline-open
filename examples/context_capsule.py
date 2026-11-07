#!/usr/bin/env python3
"""Compile inspectable, byte-bounded context from reviewed, source-linked claims.

Standard library only. No model calls, inferred facts, credentials or network access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


def encoded(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compile_context(capsule: dict[str, Any], query: str, budget_bytes: int, as_of: str) -> dict[str, Any]:
    """Select whole evidence groups; retain opposing claims together or omit both.

    Query overlap is a transparent heuristic, not a measure of political importance
    or truth. Budget applies to the serialized packet, including source metadata.
    """
    if not isinstance(budget_bytes, int) or budget_bytes < 256:
        raise ValueError("budget_bytes must be an integer of at least 256")
    date.fromisoformat(as_of)
    if capsule.get("format") != "tacitus-context-example/1":
        raise ValueError("unsupported capsule format")
    sources: dict[str, dict[str, Any]] = {}
    for source in capsule["sources"]:
        if not isinstance(source.get("id"), str) or source["id"] in sources:
            raise ValueError("source IDs must be unique strings")
        if not all(isinstance(source.get(key), str) and source[key] for key in ["id", "title", "text"]):
            raise ValueError("sources require non-empty id, title and text")
        sources[source["id"]] = source
    groups: dict[str, list[dict[str, Any]]] = {}
    excluded: list[dict[str, str]] = []
    seen: set[str] = set()
    for claim in capsule["claims"]:
        cid = claim.get("id")
        if not isinstance(cid, str) or not cid or cid in seen:
            raise ValueError("claim IDs must be unique non-empty strings")
        seen.add(cid)
        source = sources.get(claim.get("source_id"))
        quote = claim.get("quote")
        if not source or not isinstance(quote, str) or not quote or quote not in source["text"]:
            raise ValueError(f"{cid}: quote must match an existing source passage")
        if not isinstance(claim.get("text"), str) or not claim["text"]:
            raise ValueError(f"{cid}: claim text is required")
        if claim.get("review") != "accepted":
            excluded.append({"id": cid, "reason": "review_required"})
            continue
        if claim.get("valid_until") and date.fromisoformat(claim["valid_until"]) < date.fromisoformat(as_of):
            excluded.append({"id": cid, "reason": "expired"})
            continue
        if claim.get("valid_from") and date.fromisoformat(claim["valid_from"]) > date.fromisoformat(as_of):
            excluded.append({"id": cid, "reason": "not_yet_valid"})
            continue
        group = claim.get("comparison_group")
        if group is not None and (not isinstance(group, str) or not group):
            raise ValueError(f"{cid}: comparison_group must be a non-empty string")
        groups.setdefault("group:" + group if group else "claim:" + cid, []).append(claim)
    # Missing, unreviewed or time-inapplicable counterparts must never disappear silently.
    excluded_ids = {item["id"] for item in excluded}
    incomplete = {claim.get("comparison_group") for claim in capsule["claims"] if claim["id"] in excluded_ids}
    tokens = set(re.findall(r"\w+", query.casefold()))
    def relevance(items: list[dict[str, Any]]) -> int:
        return len(tokens & set(re.findall(r"\w+", " ".join(x["text"] for x in items).casefold())))
    ordered = sorted(groups.items(), key=lambda pair: (-relevance(pair[1]), pair[0]))
    selected: list[dict[str, Any]] = []

    def packet_for(claims: list[dict[str, Any]]) -> dict[str, Any]:
        used = sorted({c["source_id"] for c in claims})
        return {"format": "tacitus-context-packet/1", "as_of": as_of, "query": query,
                "claims": claims, "sources": [{"id": sid, "title": sources[sid]["title"],
                "url": sources[sid].get("url"), "sha256": hashlib.sha256(sources[sid]["text"].encode()).hexdigest()}
                for sid in used], "policy": "Source assertions require human judgment; comparison is not proof of contradiction."}
    if len(encoded(packet_for([]))) > budget_bytes:
        raise ValueError("budget is smaller than the packet envelope and query")
    for _, items in ordered:
        if items[0].get("comparison_group") in incomplete and items[0].get("comparison_group"):
            excluded.extend({"id": item["id"], "reason": "comparison_incomplete"} for item in items)
        elif len(encoded(packet_for(selected + items))) <= budget_bytes:
            selected.extend(items)
        else:
            excluded.extend({"id": item["id"], "reason": "budget"} for item in items)
            # Continue: a large group must not starve later fitting evidence.
    packet = packet_for(selected)
    return {"packet": packet, "receipt": {"input_sha256": hashlib.sha256(encoded(capsule)).hexdigest(),
            "packet_sha256": hashlib.sha256(encoded(packet)).hexdigest(), "packet_bytes": len(encoded(packet)),
            "budget_bytes": budget_bytes, "included": [c["id"] for c in selected],
            "packet_encoding": "compact_sorted_json_utf8",
            "omitted": sorted(excluded, key=lambda item: item["id"]),
            "selection": "query-token overlap; stable ID tie-break; whole comparison groups",
            "scope": "deterministic selection example; no generation or analytical-quality measurement"}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("policy_capsule.json"))
    parser.add_argument("--query", default="What is adopted, proposed or unfunded in the corridor plan?")
    parser.add_argument("--as-of", default="2026-11-07")
    parser.add_argument("--budget-bytes", type=int, default=4000)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--packet-only", action="store_true", help="Write only compact packet bytes within the bound; omit the larger inspection receipt.")
    args = parser.parse_args()
    try:
        result = compile_context(json.loads(args.input.read_text(encoding="utf-8")), args.query, args.budget_bytes, args.as_of)
    except (ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    output = encoded(result["packet"]).decode("utf-8") if args.packet_only else json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()

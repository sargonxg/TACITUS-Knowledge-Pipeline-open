"""Offline, source-attributed political task lenses; no model or external services."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
NS = "urn:tacitus:political-demo:"
PRIMITIVES = {"Actor", "Claim", "Interest", "Constraint", "Commitment", "Event", "Narrative", "Evidence"}
REVIEW_STATES = {"source_verified", "candidate", "analyst_draft", "human_reviewed"}
EVIDENCE_STATES = {"source_verified", "human_reviewed"}
MODALITIES = {"endorses", "shall", "guidance", "reports", "observation", "hypothesis"}
STAGES = {"adopted_text", "issued_text", "proposed_text", "not_applicable"}


def digest(text: str) -> str:
    """Hash the exact retained UTF-8 excerpt, not the unretained full document."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load(path: Path = HERE / "corpus.json") -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate(data)
    return data


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _day(value: str) -> date:
    _check(isinstance(value, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)), "expected ISO day")
    return date.fromisoformat(value)


def _timestamp(value: str) -> None:
    _check(isinstance(value, str) and value.endswith("Z"), "recorded_at must be a UTC timestamp")
    datetime.fromisoformat(value.replace("Z", "+00:00"))


def _publication(value: dict[str, str]) -> None:
    _check(set(value) == {"value", "precision"}, "publication requires value and precision")
    if value["precision"] == "year":
        _check(bool(re.fullmatch(r"\d{4}", value["value"])) and int(value["value"]) > 0, "invalid publication year")
    else:
        _check(value["precision"] == "day", "unsupported publication precision")
        _day(value["value"])


def _review(item: dict[str, Any]) -> None:
    _check(item["review_state"] in REVIEW_STATES, "unknown review state")
    if item["review_state"] == "human_reviewed" or item.get("human_reviewed"):
        _check(item["review_state"] == "human_reviewed" and item.get("human_reviewed") is True,
               "human review flag and state must agree")
        review = item.get("review", {})
        _check(isinstance(review.get("reviewer"), str) and bool(review["reviewer"].strip())
               and review.get("decision") == "approved", "human review requires reviewer identity and approved decision")
        _timestamp(review.get("reviewed_at"))


def validate(data: dict[str, Any]) -> None:
    """Reject broken evidence and unsafe semantic promotions before querying/export."""
    _check(data.get("schema_version") == "political-demo/1", "unsupported schema_version")
    groups = ("actors", "sources", "evidence", "concepts", "records")
    all_ids: set[str] = set()
    for group in groups:
        _check(isinstance(data.get(group), list), f"missing {group}")
        for item in data[group]:
            identifier = item.get("id", "")
            _check(bool(re.fullmatch(r"[a-z][a-z0-9-]*", identifier)), "invalid local id")
            _check(identifier not in all_ids, f"duplicate id: {identifier}")
            all_ids.add(identifier)
    actors = {x["id"]: x for x in data["actors"]}
    sources = {x["id"]: x for x in data["sources"]}
    evidence = {x["id"]: x for x in data["evidence"]}
    concepts = {x["id"] for x in data["concepts"]}
    for actor in actors.values():
        _check(actor.get("primitive") == "Actor" and bool(actor.get("roles")), "actor requires explicit roles")
    for source in sources.values():
        _check(urlparse(source["url"]).scheme == "https", "source requires HTTPS provenance")
        _check(source["publisher_id"] in actors and source["issuer_id"] in actors, "dangling source actor")
        _check(source.get("author_id") is None or source["author_id"] in actors, "dangling source author")
        _publication(source["published"])
        _timestamp(source["recorded_at"])
        _check(source["verification"] in {"direct_pdf", "direct_web", "indexed_candidate"}, "unknown verification method")
        if source["verification"] == "direct_pdf":
            _check(bool(re.fullmatch(r"[a-f0-9]{64}", source.get("original_sha256", ""))), "PDF representation hash required")
    for item in evidence.values():
        _check(item["primitive"] == "Evidence" and item["source_id"] in sources, "dangling evidence source")
        _check(bool(item.get("locator")) and bool(item.get("text")), "evidence requires locator and retained text")
        _check(digest(item["text"]) == item.get("retained_sha256"), "retained excerpt hash mismatch")
        _check(item.get("representation") == "selected_excerpt_utf8", "only selected excerpt representation supported")
        _review(item)
        if item["review_state"] in EVIDENCE_STATES:
            _check(sources[item["source_id"]]["verification"] != "indexed_candidate", "indexed text cannot be promoted to verified evidence")
    for source in sources.values():
        ownership = source.get("ownership", {})
        _check(ownership.get("owner_id") is None or ownership["owner_id"] in actors, "dangling owner")
        _check(set(ownership.get("evidence_ids", [])) <= set(evidence), "dangling ownership evidence")
    for record in data["records"]:
        _check(record["primitive"] in PRIMITIVES - {"Actor", "Evidence"}, "unsupported primitive")
        _check(record["attributed_to"] in actors, "dangling attributed actor")
        _check(record["reported_by"] is None or record["reported_by"] in actors, "dangling reporting actor")
        _check(set(record.get("attribution_chain", [])) <= set(actors), "dangling attribution chain")
        _review(record)
        _check(record["basis"] in {"source_assertion", "analyst_interpretation", "motive_hypothesis"}, "unknown assertion basis")
        _check(record["modality"] in MODALITIES and record["document_stage"] in STAGES, "unknown modality or document stage")
        _check(record["implementation"] in {"not_assessed", "proposed", "observed"}, "unknown implementation state")
        _check(bool(record["authority"]) and bool(record["scope"]), "authority and scope required")
        _check(isinstance(record["evidence"], list) and bool(record["evidence"]), "record must retain evidence")
        for link in record["evidence"]:
            _check(link["evidence_id"] in evidence, "dangling evidence reference")
            retained = evidence[link["evidence_id"]]
            _check(bool(link["quote"]) and link["quote"] in retained["text"], "quote does not match retained excerpt")
            if record["review_state"] in EVIDENCE_STATES:
                _check(retained["review_state"] in EVIDENCE_STATES, "verified record depends on candidate evidence")
        if record["basis"] != "source_assertion":
            _check(record["review_state"] in {"analyst_draft", "human_reviewed"}, "interpretation cannot masquerade as source assertion")
        if record["basis"] == "motive_hypothesis":
            _check(record["modality"] == "hypothesis" and bool(record.get("alternatives")), "motives require alternatives, not causal certainty")
        if record["implementation"] == "observed":
            _check(record["document_stage"] == "not_applicable" and bool(record.get("implementation_evidence")), "adopted text does not prove implementation")
            for ref in record["implementation_evidence"]:
                _check(ref in evidence and evidence[ref]["review_state"] in EVIDENCE_STATES, "implementation needs verified observation evidence")
        temporal = record["time"]
        _check(set(temporal) == {"occurred_on", "valid_from", "valid_to", "validity_status", "recorded_at"}, "distinct temporal fields required")
        for field in ("occurred_on", "valid_from", "valid_to"):
            if temporal[field] is not None:
                _day(temporal[field])
        _timestamp(temporal["recorded_at"])
        _check(temporal["validity_status"] in {"not_assessed", "source_specified"}, "unknown validity status")
        if temporal["valid_from"] and temporal["valid_to"]:
            _check(temporal["valid_from"] <= temporal["valid_to"], "reversed validity interval")
        if temporal["validity_status"] == "not_assessed":
            _check(temporal["valid_from"] is None and temporal["valid_to"] is None, "unknown validity cannot imply interval")
        _check(set(record["concept_ids"]) <= concepts, "dangling concept reference")
        _check(set(record["lenses"]) <= set(data["lenses"]), "unknown task lens")
        if "hr_policy" in record["lenses"]:
            _check(record.get("applicability", {}).get("status") == "not_assessed", "demo cannot determine HR legal applicability")
    for relation in data["relations"]:
        _check(relation["subject"] in all_ids and relation["object"] in all_ids, "dangling relation")
        _check(relation["predicate"] in {"references", "reports_on", "informs_task"}, "unreviewed ontology relation")
    forbidden = {"sameAs", "owl:sameAs", "bias_score", "causal_certainty"}

    def check_keys(value: Any) -> None:
        if isinstance(value, dict):
            _check(not forbidden.intersection(value), "unsupported equivalence, bias score or causal certainty")
            for child in value.values():
                check_keys(child)
        elif isinstance(value, list):
            for child in value:
                check_keys(child)

    check_keys(data)
    for name, recipe in data["recipes"].items():
        _check(recipe["lens"] in data["lenses"] and bool(recipe["review_questions"]), f"invalid task recipe {name}")


def query(data: dict[str, Any], lens: str, *, include_drafts: bool = False,
          published_by: str | None = None) -> dict[str, Any]:
    """Select by explicit tags and review state; never infer law, motives or truth."""
    validate(data)
    _check(lens in data["lenses"], "unknown lens")
    cutoff = _day(published_by) if published_by else None
    evidence = {x["id"]: x for x in data["evidence"]}
    sources = {x["id"]: x for x in data["sources"]}
    selected = []
    for record in sorted(data["records"], key=lambda x: x["id"]):
        if lens not in record["lenses"] or (not include_drafts and record["review_state"] not in EVIDENCE_STATES):
            continue
        linked = [evidence[x["evidence_id"]] for x in record["evidence"]]
        # For year precision, only admit it when the entire publication year is past.
        if cutoff and any(date.fromisoformat(sources[x["source_id"]]["published"]["value"] +
                    ("-12-31" if sources[x["source_id"]]["published"]["precision"] == "year" else "")) > cutoff for x in linked):
            continue
        selected.append(record)
    evidence_ids = {x["evidence_id"] for row in selected for x in row["evidence"]}
    source_ids = {evidence[x]["source_id"] for x in evidence_ids}
    return {"lens": lens, "purpose": data["lenses"][lens], "published_by": published_by,
            "include_drafts": include_drafts, "selection_method": "explicit tags; no relevance or bias scoring",
            "records": selected, "evidence": [evidence[x] for x in sorted(evidence_ids)],
            "sources": [sources[x] for x in sorted(source_ids)],
            "limits": data["limits"]}


def export_jsonld(data: dict[str, Any]) -> dict[str, Any]:
    """Export auditable provenance using a deliberately local demo vocabulary."""
    validate(data)
    context = {"demo": NS, "prov": "http://www.w3.org/ns/prov#", "skos": "http://www.w3.org/2004/02/skos/core#",
               "dct": "http://purl.org/dc/terms/", "xsd": "http://www.w3.org/2001/XMLSchema#"}
    graph = []
    for actor in data["actors"]:
        graph.append({"@id": NS + actor["id"], "@type": ["demo:Actor", "prov:Agent"],
                      "skos:prefLabel": actor["label"], "demo:roles": actor["roles"]})
    for concept in data["concepts"]:
        graph.append({"@id": NS + concept["id"], "@type": "skos:Concept", "skos:prefLabel": concept["label"]})
    for source in data["sources"]:
        graph.append({"@id": NS + source["id"], "@type": "prov:Entity", "dct:title": source["title"],
                      "dct:source": {"@id": source["url"]},
                      "dct:issued": {"@value": source["published"]["value"], "@type": "xsd:" + ("date" if source["published"]["precision"] == "day" else "gYear")},
                      "dct:publisher": {"@id": NS + source["publisher_id"]},
                      "demo:issuer": {"@id": NS + source["issuer_id"]},
                      "demo:metadata": {"@value": source, "@type": "@json"}})
    for item in data["evidence"]:
        graph.append({"@id": NS + item["id"], "@type": ["demo:Evidence", "prov:Entity"],
                      "prov:wasDerivedFrom": {"@id": NS + item["source_id"]}, "prov:value": item["text"],
                      "demo:locator": item["locator"], "demo:retainedSha256": item["retained_sha256"],
                      "demo:reviewState": item["review_state"]})
    for record in data["records"]:
        # JSON literal preserves nested qualification fields without inventing RDF predicates for each key.
        graph.append({"@id": NS + record["id"], "@type": ["demo:" + record["primitive"], "prov:Entity"],
                      "prov:wasAttributedTo": {"@id": NS + record["attributed_to"]},
                      "prov:wasDerivedFrom": [{"@id": NS + x["evidence_id"]} for x in record["evidence"]],
                      "dct:subject": [{"@id": NS + x} for x in record["concept_ids"]],
                      "demo:statement": record["statement"], "demo:reviewState": record["review_state"],
                      "demo:qualifiedRecord": {"@value": record, "@type": "@json"}})
    for relation in data["relations"]:
        graph.append({"@id": NS + relation["subject"], "demo:" + relation["predicate"]: {"@id": NS + relation["object"]}})
    return {"@context": context, "@graph": sorted(graph, key=lambda x: (x["@id"], json.dumps(x, sort_keys=True)))}


def export_sql(data: dict[str, Any]) -> str:
    """Build a portable SQLite SQL dump with bound inserts and enforced references."""
    validate(data)
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript("""
        CREATE TABLE policy_semantic_actors (
          id TEXT PRIMARY KEY, label TEXT NOT NULL, metadata_json TEXT NOT NULL);
        CREATE TABLE policy_semantic_sources (
          id TEXT PRIMARY KEY, publisher_id TEXT NOT NULL REFERENCES policy_semantic_actors(id) DEFERRABLE INITIALLY DEFERRED,
          issuer_id TEXT NOT NULL REFERENCES policy_semantic_actors(id) DEFERRABLE INITIALLY DEFERRED,
          url TEXT NOT NULL, published_value TEXT NOT NULL, published_precision TEXT NOT NULL,
          recorded_at TEXT NOT NULL, metadata_json TEXT NOT NULL);
        CREATE TABLE policy_semantic_evidence (
          id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES policy_semantic_sources(id) DEFERRABLE INITIALLY DEFERRED,
          locator TEXT NOT NULL, retained_text TEXT NOT NULL, retained_sha256 TEXT NOT NULL,
          review_state TEXT NOT NULL, metadata_json TEXT NOT NULL);
        CREATE TABLE policy_semantic_assertions (
          id TEXT PRIMARY KEY, primitive TEXT NOT NULL,
          actor_id TEXT NOT NULL REFERENCES policy_semantic_actors(id) DEFERRABLE INITIALLY DEFERRED,
          reporter_id TEXT REFERENCES policy_semantic_actors(id) DEFERRABLE INITIALLY DEFERRED,
          statement TEXT NOT NULL, basis TEXT NOT NULL, modality TEXT NOT NULL,
          document_stage TEXT NOT NULL, implementation TEXT NOT NULL,
          review_state TEXT NOT NULL, occurred_on TEXT, valid_from TEXT, valid_to TEXT,
          recorded_at TEXT NOT NULL, metadata_json TEXT NOT NULL);
        CREATE TABLE policy_semantic_assertion_evidence (
          assertion_id TEXT NOT NULL REFERENCES policy_semantic_assertions(id) DEFERRABLE INITIALLY DEFERRED,
          evidence_id TEXT NOT NULL REFERENCES policy_semantic_evidence(id) DEFERRABLE INITIALLY DEFERRED,
          quote TEXT NOT NULL, PRIMARY KEY(assertion_id, evidence_id));
        CREATE TABLE policy_semantic_lenses (id TEXT PRIMARY KEY, metadata_json TEXT NOT NULL);
        CREATE TABLE policy_semantic_assertion_lenses (
          lens_id TEXT NOT NULL REFERENCES policy_semantic_lenses(id) DEFERRABLE INITIALLY DEFERRED,
          assertion_id TEXT NOT NULL REFERENCES policy_semantic_assertions(id) DEFERRABLE INITIALLY DEFERRED,
          PRIMARY KEY(lens_id, assertion_id));
        CREATE TABLE policy_semantic_recipes (
          id TEXT PRIMARY KEY, lens_id TEXT NOT NULL REFERENCES policy_semantic_lenses(id) DEFERRABLE INITIALLY DEFERRED,
          metadata_json TEXT NOT NULL);
        CREATE INDEX policy_semantic_assertion_review ON policy_semantic_assertions(review_state, primitive);
        CREATE INDEX policy_semantic_evidence_source ON policy_semantic_evidence(source_id);
        CREATE INDEX policy_semantic_evidence_reverse ON policy_semantic_assertion_evidence(evidence_id);
        CREATE INDEX policy_semantic_recipe_lens ON policy_semantic_recipes(lens_id);
        CREATE VIEW policy_semantic_verified_assertions AS
          SELECT * FROM policy_semantic_assertions
          WHERE review_state IN ('source_verified', 'human_reviewed');
    """)
    pack = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True)
    with connection:
        connection.executemany("INSERT INTO policy_semantic_actors VALUES (?,?,?)",
                               [(x["id"], x["label"], pack(x)) for x in data["actors"]])
        connection.executemany("INSERT INTO policy_semantic_sources VALUES (?,?,?,?,?,?,?,?)",
                               [(x["id"], x["publisher_id"], x["issuer_id"], x["url"], x["published"]["value"],
                                 x["published"]["precision"], x["recorded_at"], pack(x)) for x in data["sources"]])
        connection.executemany("INSERT INTO policy_semantic_evidence VALUES (?,?,?,?,?,?,?)",
                               [(x["id"], x["source_id"], x["locator"], x["text"], x["retained_sha256"],
                                 x["review_state"], pack(x)) for x in data["evidence"]])
        connection.executemany("INSERT INTO policy_semantic_assertions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                               [(x["id"], x["primitive"], x["attributed_to"], x["reported_by"], x["statement"],
                                 x["basis"], x["modality"], x["document_stage"], x["implementation"], x["review_state"],
                                 x["time"]["occurred_on"], x["time"]["valid_from"], x["time"]["valid_to"],
                                 x["time"]["recorded_at"], pack(x)) for x in data["records"]])
        connection.executemany("INSERT INTO policy_semantic_assertion_evidence VALUES (?,?,?)",
                               [(r["id"], e["evidence_id"], e["quote"]) for r in data["records"] for e in r["evidence"]])
        connection.executemany("INSERT INTO policy_semantic_lenses VALUES (?,?)", [(key, pack(value)) for key, value in data["lenses"].items()])
        connection.executemany("INSERT INTO policy_semantic_assertion_lenses VALUES (?,?)",
                               [(lens, r["id"]) for r in data["records"] for lens in r["lenses"]])
        connection.executemany("INSERT INTO policy_semantic_recipes VALUES (?,?,?)",
                               [(key, value["lens"], pack(value)) for key, value in data["recipes"].items()])
    _check(not connection.execute("PRAGMA foreign_key_check").fetchall(), "SQL export has broken references")
    # iterdump interleaves table creation/inserts alphabetically. Create all referenced
    # tables first; deferred foreign keys then validate the complete transaction.
    dump = list(connection.iterdump())
    tables = [line for line in dump if line.startswith("CREATE TABLE ")]
    inserts = sorted(line for line in dump if line.startswith("INSERT INTO "))
    other = [line for line in dump if not line.startswith(("CREATE TABLE ", "INSERT INTO "))
             and line not in {"BEGIN TRANSACTION;", "COMMIT;"}]
    output = "\n".join(["PRAGMA foreign_keys=ON;", "BEGIN TRANSACTION;", *tables, *inserts, *other, "COMMIT;", ""])
    connection.close()
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=HERE / "corpus.json")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    q = sub.add_parser("query")
    q.add_argument("--lens", required=True)
    q.add_argument("--include-drafts", action="store_true")
    q.add_argument("--published-by", help="ISO day; filters publication, not historical truth or ingestion time")
    sub.add_parser("recipes")
    exp = sub.add_parser("export")
    exp.add_argument("--out", type=Path)
    sql = sub.add_parser("export-sql")
    sql.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        data = load(args.corpus)
        if args.command == "validate":
            result = {"valid": True, "sources": len(data["sources"]), "records": len(data["records"]),
                      "human_reviewed": sum(x["review_state"] == "human_reviewed" for x in data["records"])}
        elif args.command == "query":
            result = query(data, args.lens, include_drafts=args.include_drafts, published_by=args.published_by)
        elif args.command == "recipes":
            result = data["recipes"]
        elif args.command == "export":
            result = export_jsonld(data)
        else:
            result = export_sql(data)
        output = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.command in {"export", "export-sql"} and args.out:
            args.out.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"Semantic validation failed: {error}\n")


if __name__ == "__main__":
    main()

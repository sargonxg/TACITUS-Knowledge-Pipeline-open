"""Portable source material for an explicitly reviewed TACITUS App import."""
from copy import deepcopy
from .core import PipelineError, build, canonical, digest, validate

APP_SCHEMA = "tacitus-pipeline-import/1"


def app_bundle(data, ontology, layer, *, question, budget=24000):
    validate(data, ontology)
    compiled = build(data, ontology, layer, question=question, budget=budget)
    collection = deepcopy(data)
    for source in collection["sources"]:
        source.pop("file", None)
    body = {
        "schema": APP_SCHEMA, "collection": collection,
        "ontology": deepcopy(ontology), "layer": deepcopy(layer),
        "question": question.strip(), "budget_bytes": budget,
        "capsule": compiled["capsule.json"], "receipt": compiled["receipt.json"],
    }
    if len(canonical(body).encode("utf-8")) > 524288:
        raise PipelineError("App export exceeds 512 KiB. Select a smaller collection.")
    return {**body, "sha256": digest(body)}


def collection_diff(before, after):
    old_sources = {source["id"]: source for source in before["sources"]}
    new_sources = {source["id"]: source for source in after["sources"]}
    changed = []
    for identifier in sorted(old_sources.keys() | new_sources.keys()):
        old, new = old_sources.get(identifier), new_sources.get(identifier)
        if old is None or new is None or old["version"] != new["version"] or old["url"] != new["url"]:
            changed.append({"source_id": identifier,
                            "before_version": old["version"] if old else None,
                            "after_version": new["version"] if new else None})
    source_ids = {row["source_id"] for row in changed}
    old_statements = {row["id"]: row for row in before["statements"]}
    new_statements = {row["id"]: row for row in after["statements"]}
    affected = sorted({identifier for identifier in old_statements.keys() | new_statements.keys()
                       if old_statements.get(identifier) != new_statements.get(identifier)
                       or old_statements.get(identifier, {}).get("source_id") in source_ids
                       or new_statements.get(identifier, {}).get("source_id") in source_ids})
    return {"schema": "tacitus-source-change-report/1", "changed_sources": changed,
            "interpretations_requiring_review": affected, "model_calls": 0}

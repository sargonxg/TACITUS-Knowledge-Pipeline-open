"""Deterministic lexical selection and bounded relationships for small graphs."""
from collections import Counter
from copy import deepcopy
from math import log
import re
from .core import PipelineError, validate


def select_layer(data, ontology, layer, question, *, mode="graph", limit=8):
    sources, _, statements = validate(data, ontology)
    if mode not in {"bm25", "graph"} or type(limit) is not int or not 1 <= limit <= 32:
        raise PipelineError("Choose bm25 or graph selection with a limit from 1 to 32.")
    included, required = layer.get("statement_ids", []), layer.get("required_statement_ids", [])
    if not included or any(identifier not in statements for identifier in included) or not set(required) <= set(included):
        raise PipelineError("Selection requires a valid authored layer.")
    tokens = lambda text: re.findall(r"\w+", text.casefold())
    documents = {identifier: tokens(statements[identifier]["quote"] + " " + statements[identifier]["interpretation"])
                 for identifier in included}
    terms = set(tokens(question))
    average = sum(map(len, documents.values())) / len(documents)
    frequencies = {term: sum(term in document for document in documents.values()) for term in terms}
    scores = {}
    for identifier, document in documents.items():
        counts = Counter(document)
        scores[identifier] = sum(
            log(1 + (len(documents) - frequencies[term] + .5) / (frequencies[term] + .5))
            * counts[term] * 2.2 / (counts[term] + 1.2 * (.25 + .75 * len(document) / max(average, 1)))
            for term in terms if counts[term])
    ranked = sorted(included, key=lambda identifier: (-scores[identifier], identifier))
    selected = set(required)
    reasons = {identifier: "required_by_layer" for identifier in required}
    seed_limit = max(1, limit // 2) if mode == "graph" else limit
    for identifier in ranked[:seed_limit]:
        if scores[identifier] > 0:
            selected.add(identifier)
            reasons.setdefault(identifier, "bm25_passage_match")
    frontier = set(selected)
    if mode == "graph":
        for hop in range(1, 3):
            entities = {statements[identifier][key] for identifier in frontier for key in ("subject", "object")}
            neighbours = [identifier for identifier in ranked if identifier not in selected and (
                statements[identifier]["subject"] in entities or statements[identifier]["object"] in entities)]
            frontier = set(neighbours[:max(0, limit - len(selected))])
            for identifier in frontier:
                reasons[identifier] = f"shared_entity_hop_{hop}"
            selected.update(frontier)
    if not selected:
        raise PipelineError("No passage matches the question. Choose records explicitly or revise the query.")
    result = deepcopy(layer)
    result["statement_ids"] = sorted(selected)
    explanation = {
        "schema": "tacitus-context-selection/1", "method": mode,
        "maximum_hops": 2 if mode == "graph" else 0,
        "selected": [{"statement_id": identifier, "reason": reasons[identifier], "score": round(scores[identifier], 6)} for identifier in sorted(selected)],
        "omitted": sorted(set(included) - selected),
        "source_editions": {identifier: source["version"] for identifier, source in sorted(sources.items())},
        "model_calls": 0,
    }
    return result, explanation

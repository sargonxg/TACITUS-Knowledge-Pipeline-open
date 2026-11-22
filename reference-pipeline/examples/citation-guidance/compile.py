"""Reproduce the source-edition proof without network access or a provider."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from unicodedata import normalize

from tacitus_pipeline.core import PipelineError, build, canonical, digest, write_bundle


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ACTION = re.compile(r"\bMS-2\.5-\d{3}\b")
QUESTION = "Did NIST change its guidance on when to verify citations in AI outputs?"
PRACTICE = "Citation verification"
SCOPE = "Selected action IDs and suggested-action text from the MEASURE 2.5 table."
TIMING = (
    "pre-deployment risk measurement",
    "ongoing monitoring activities",
)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_pdf(pdf, source, snapshot):
    """Optional capture check against a locally downloaded, pinned official PDF."""
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != source["pdf_sha256"]:
        raise PipelineError(f"Official PDF hash mismatch for {source['id']}.")
    page = str(source["pdf_page"])
    extracted = subprocess.run(
        ["pdftotext", "-f", page, "-l", page, "-layout", str(pdf), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    rows = []
    for block in re.split(r"\n\s*\n", extracted):
        actions = ACTION.findall(block)
        if not actions:
            continue
        if len(actions) != 1:
            raise PipelineError("Expected one action ID per table row.")
        parts = [" ".join(line[14:source["action_column_end"]].split()) for line in block.splitlines()]
        action = normalize("NFKC", " ".join(part for part in parts if part))
        action = re.sub(r"(?<=\w)- (?=\w)", "-", action)
        rows.append(f"{actions[0]}  {action}")
    if len(rows) != source["action_count"] or "\n".join(rows) + "\n" != snapshot:
        raise PipelineError(f"Reproduced excerpt differs for {source['id']}.")


def passage(source, statement_id, action_id):
    pattern = r"^" + re.escape(action_id) + r"  (.+)$"
    matches = list(re.finditer(pattern, source["text"], flags=re.MULTILINE))
    if len(matches) != 1:
        raise PipelineError(f"Expected exactly one {action_id} in {source['id']}.")
    match = matches[0]
    return {
        "id": statement_id, "source_id": source["id"], "action_id": action_id,
        "quote": match.group(1), "start": match.start(1), "end": match.end(1),
        "offset_unit": "unicode_codepoints",
    }


def statement(anchor, sources, *, interpretation, target, qualifications=()):
    quote = anchor["quote"]
    qualifiers = []
    for text in qualifications:
        start = quote.find(text)
        if start < 0:
            raise PipelineError(f"Required qualification is missing from {anchor['id']}.")
        qualifiers.append({"text": text, "start": start, "end": start + len(text)})
    return {
        **{key: anchor[key] for key in ("id", "source_id", "quote", "start", "end")},
        "source_version": sources[anchor["source_id"]]["version"],
        "subject": "release-review", "relation": "considers_guidance_for", "object": target,
        "interpretation": interpretation, "modality": "suggested guidance", "review_state": "proposed",
        "qualifiers": qualifiers, "required_qualifier_literals": list(qualifications),
    }


def standards_export(fixture_sources, anchors, collection):
    """Map the edition evidence to SKOS concepts and PROV-O entities."""
    base = "urn:tacitus:nist-ai-600-1:"
    editions = {
        source["id"]: base + "edition:" + source["id"] + ":" + source["text_sha256"]
        for source in fixture_sources
    }
    practices = {
        entity["id"]: base + "practice:" + entity["id"]
        for entity in collection["entities"] if entity["type"] == "ReviewPractice"
    }
    graph = [
        {"@id": practices[entity["id"]], "@type": "skos:Concept",
         "skos:prefLabel": {"@value": entity["label"], "@language": "en"}}
        for entity in collection["entities"] if entity["id"] in practices
    ]
    for source in fixture_sources:
        graph.append({
            "@id": editions[source["id"]], "@type": ["prov:Entity", "tac:SourceEdition"],
            "dcterms:title": source["title"],
            "dcterms:source": {"@id": source["url"]},
            "dcterms:issued": {"@value": source["date"], "@type": "xsd:date"},
            "tac:textSha256": source["text_sha256"], "tac:pdfSha256": source["pdf_sha256"],
            "tac:pdfPage": source["pdf_page"], "tac:printedPage": source["printed_page"],
        })
    for anchor, record in zip(anchors, collection["statements"], strict=True):
        span_id = base + "span:" + anchor["id"] + ":" + record["source_version"]
        graph.extend([
            {
                "@id": span_id, "@type": ["prov:Entity", "tac:EvidenceSpan"],
                "prov:wasDerivedFrom": {"@id": editions[anchor["source_id"]]},
                "tac:actionId": anchor["action_id"], "tac:exactQuote": anchor["quote"],
                "tac:start": anchor["start"], "tac:end": anchor["end"], "tac:offsetUnit": anchor["offset_unit"],
            },
            {
                "@id": base + "statement:" + record["id"] + ":" + digest(record),
                "@type": ["prov:Entity", "tac:ProposedStatement"],
                "prov:wasDerivedFrom": {"@id": span_id},
                "tac:practice": {"@id": practices[record["object"]]},
                "tac:interpretation": record["interpretation"],
                "tac:modality": record["modality"], "tac:reviewStatus": record["review_state"],
                "tac:qualification": record["required_qualifier_literals"],
            },
        ])
    return {
        "@context": {
            "dcterms": "http://purl.org/dc/terms/", "prov": "http://www.w3.org/ns/prov#",
            "skos": "http://www.w3.org/2004/02/skos/core#", "tac": "https://tacitus.me/ns/reference#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@graph": graph,
    }


def compile_proof(pdfs=None):
    capture = load(HERE / "capture.json")
    sources = {}
    for fixture_source in capture["sources"]:
        source_id = fixture_source["id"]
        snapshot = (HERE / fixture_source["snapshot"]).read_bytes()
        if hashlib.sha256(snapshot).hexdigest() != fixture_source["text_sha256"]:
            raise PipelineError(f"Captured text hash mismatch for {source_id}.")
        text = snapshot.decode("utf-8")
        if pdfs:
            verify_pdf(pdfs / f"{source_id}.pdf", fixture_source, text)
        sources[source_id] = {
            "id": source_id,
            "title": fixture_source["title"],
            "url": fixture_source["url"],
            "text": text,
            "version": fixture_source["text_sha256"],
            "scope": SCOPE,
            "rights_note": capture["rights_note"],
        }

    before = passage(sources["draft"], "draft-citation-review", "MS-2.5-008")
    after = passage(sources["final"], "final-citation-review", "MS-2.5-003")
    collision = passage(sources["draft"], "draft-id-collision", after["action_id"])
    if before["quote"] != after["quote"] or collision["quote"] == after["quote"]:
        raise PipelineError("The pinned edition comparison no longer supports the stated result.")

    collection = {
        "sources": list(sources.values()),
        "entities": [
            {"id": "release-review", "type": "ReleaseDecision", "label": "Release review"},
            {"id": "citation-verification", "type": "ReviewPractice", "label": PRACTICE},
            {"id": "integrity-audit", "type": "ReviewPractice", "label": "Integrity audit"},
        ],
        "statements": [
            statement(before, sources, target="citation-verification", qualifications=TIMING,
                      interpretation="The draft lists citation verification as action MS-2.5-008."),
            statement(after, sources, target="citation-verification", qualifications=TIMING,
                      interpretation="The final lists the same citation-verification wording as MS-2.5-003."),
            statement(collision, sources, target="integrity-audit",
                      interpretation="The same identifier in the draft refers to a security audit."),
        ],
    }
    bundle = build(collection, load(ROOT / "ontology" / "release-review.json"),
                   load(ROOT / "layers" / "citation-guidance-change.json"), question=QUESTION)
    bundle["standards.jsonld"] = standards_export(capture["sources"], [before, after, collision], collection)
    proof = {
        "format": "tacitus-source-edition-proof/1",
        "title": "A reference changed. The guidance didn’t.",
        "question": QUESTION,
        "summary": "NIST gave its citation-checking guidance a new action ID without changing the wording.",
        "judgment": "Keep the citation checks. Update the reference from MS-2.5-008 to MS-2.5-003.",
        "reason": "The action wording is identical in the two source editions. The draft’s MS-2.5-003 concerns a different review practice.",
        "status": "proposed",
        "scope": SCOPE,
        "publisher": capture["publisher"],
        "retrieved_on": capture["retrieved_on"],
        "rights_note": capture["rights_note"],
        "rights_url": capture["rights_url"],
        "sources": [
            {key: value for key, value in source.items() if key not in ("action_column_end", "action_count")}
            for source in capture["sources"]
        ],
        "passages": [before, after, collision],
        "comparison": {
            "before": before["id"], "after": after["id"], "collision": collision["id"],
            "wording_unchanged": True, "modality": "suggested guidance",
        },
        "receipt": {
            **bundle["receipt.json"],
            "capture_sha256": digest(capture),
            "graph_sha256": digest(bundle["graph.json"]),
        },
    }
    return proof, bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify-pdfs", type=Path, help="Directory containing downloaded draft.pdf and final.pdf")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        proof, bundle = compile_proof(args.verify_pdfs)
        output = args.output
        if (output / "proof.json").exists() and not args.force:
            raise PipelineError("Proof exists. Choose another directory or explicitly use --force.")
        write_bundle(bundle, output / "compiled", force=args.force)
        (output / "proof.json").write_text(canonical(proof) + "\n", encoding="utf-8")
    except (PipelineError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"Proof refused: {error}\n")


if __name__ == "__main__":
    main()

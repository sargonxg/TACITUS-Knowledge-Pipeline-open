#!/usr/bin/env python3
"""Build an inspectable source graph from two pinned official EU XHTML texts.

Python 3.10+ standard library only. No model, credentials or network are needed.
This is a document/terminology graph, not an automatically validated legal ontology.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
BUILD_DATE = "2026-11-24"
SCHEMA = "tacitus.source-graph/1"
BARE_LABEL = re.compile(r"(?:\([\w]+\)|[\d.]+)")
ARTICLE_RE = re.compile(
    r"\bArticles?\s+(\d+(?:\([0-9a-z]+\))*(?:(?:\s*,\s*(?:(?:and|or)\s+)?|\s+(?:and|or|to)\s+)\d+(?:\([0-9a-z]+\))*)*)"
)
NUMBER_RE = re.compile(r"(?<![\d(])(\d+)(?:\(([0-9]+)\))?")
ANNEX_RE = re.compile(r"\bAnnex\s+([IVX]+)\b")
SCOPE_RE = re.compile(
    r"^[\s,]*(?:(?:points?|paragraphs?)\s+(?:\([a-z0-9]+\)|\d+)"
    r"(?:\s*(?:,|and|or)\s*\(?[a-z0-9]+\)?)*[\s,]*|"
    r"(?:first|second|third|fourth|fifth|last)\s+subparagraph[\s,]*)*of\s+(.+)"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def text(e: ET.Element) -> str:
    return " ".join("".join(e.itertext()).split())


def local(e: ET.Element) -> str:
    return e.tag.rsplit("}", 1)[-1]


def ancestors(e, parents):
    while e in parents:
        e = parents[e]
        yield e


def classification(anchor):
    if re.fullmatch(r"art_\d+", anchor):
        return "article", anchor[4:]
    if re.fullmatch(r"rct_\d+", anchor):
        return "recital", anchor[4:]
    if re.fullmatch(r"cpt_[IVXLCDM]+", anchor):
        return "chapter", anchor[4:]
    if re.fullmatch(r"cpt_[IVXLCDM]+\.sct_\d+", anchor):
        return "section", anchor
    if re.fullmatch(r"anx_[IVXLCDM]+", anchor):
        return "annex", anchor[4:]
    return None


def build_graph(base=BASE):
    specs = json.loads((base / "source-lock.json").read_text())["sources"]
    nodes, edges, node_index, snapshots = [], [], {}, {}
    edge_keys = set()
    article_passages = defaultdict(list)
    definitions = []
    all_passages = []

    def add_node(n):
        if n["id"] in node_index:
            raise ValueError("Duplicate node: " + n["id"])
        nodes.append(n)
        node_index[n["id"]] = n
        return n

    def add_edge(source, target, relation, layer, method, **evidence):
        key = (source, target, relation)
        if key in edge_keys:
            return
        edge_keys.add(key)
        # Stable IDs encode the relation identity, not the list position.
        ident = "e:" + digest("\0".join(key).encode())[:16]
        edges.append(dict(id=ident, source=source, target=target, relation=relation,
                          layer=layer, method=method, **evidence))

    for spec in specs:
        doc = spec["id"]
        raw = (base / "sources" / (doc + ".html")).read_bytes()
        if digest(raw) != spec["sha256"] or len(raw) != spec["bytes"]:
            raise ValueError("Source differs from pinned official snapshot: " + doc)
        root = ET.fromstring(raw)
        parents = {c: p for p in root.iter() for c in p}
        paragraphs = [e for e in root.iter() if local(e) == "p" and text(e)]
        # Exact offsets refer to THIS normalized UTF-8 snapshot, never raw HTML.
        positions, parts, pos = {}, [], 0
        for e in paragraphs:
            q = text(e)
            positions[e] = (pos, pos + len(q))
            parts.append(q)
            pos += len(q) + 2
        snapshot = "\n\n".join(parts) + "\n"
        snapshots[doc] = snapshot
        spec["extracted_text"] = "sources/" + doc + ".txt"
        spec["extracted_sha256"] = digest(snapshot.encode())

        def source_fields(es, anchor):
            start, end = positions[es[0]][0], positions[es[-1]][1]
            return dict(document_id=doc, locator=anchor, quote=snapshot[start:end],
                        source_url=spec["url"] + "#" + anchor,
                        source_start=start, source_end=end)

        title_p = next((e for e in paragraphs if "oj-doc-ti" in e.get("class", "").split()
                        and "REGULATION" in text(e)), paragraphs[0])
        add_node(dict(id=doc + ":document", kind="document", label=spec["title"],
                      layer="structure", **source_fields([title_p], "tit_1")))
        structure_nodes = {}
        for e in root.iter():
            cls = classification(e.get("id", ""))
            if not cls:
                continue
            kind, number = cls
            anchor = e.get("id")
            child_ps = [p for p in e.iter() if p in positions]
            if kind == "recital":
                selected = [p for p in child_ps if "oj-normal" in p.get("class", "").split()
                            and not BARE_LABEL.fullmatch(text(p))]
                label = "Recital " + number
            else:
                selected = []
                # Actual heading paragraphs only; do not duplicate article bodies.
                for p in child_ps:
                    if p.get("class", "") in ("oj-normal", "oj-note"):
                        break
                    if any(classification(a.get("id", "")) and a is not e
                           for a in ancestors(p, parents) if a is not root
                           and a is not e and e in list(ancestors(a, parents))):
                        continue
                    selected.append(p)
                    if len(selected) == 2:
                        break
                label = kind.title() + " " + (number.split("sct_")[-1] if kind == "section" else number)
                if len(selected) > 1:
                    label += " · " + text(selected[-1])
            if not selected:
                raise ValueError("Missing structural quote: " + doc + " " + anchor)
            n = add_node(dict(id=f"{doc}:{kind}:{number}", kind=kind, label=label,
                              layer="structure", **source_fields(selected, anchor)))
            structure_nodes[e] = n["id"]
        for e, ident in structure_nodes.items():
            parent = next((structure_nodes[a] for a in ancestors(e, parents) if a in structure_nodes),
                          doc + ":document")
            add_edge(parent, ident, "contains", "structure", "xhtml_ancestry")

        counters = Counter()
        point_counters = Counter()
        for p in paragraphs:
            if "oj-normal" not in p.get("class", "").split() or BARE_LABEL.fullmatch(text(p)):
                continue
            struct_e = next((a for a in ancestors(p, parents) if a in structure_nodes), None)
            if struct_e is None or node_index[structure_nodes[struct_e]]["kind"] not in ("article", "annex"):
                continue
            struct_id = structure_nodes[struct_e]
            anchor = next((a.get("id") for a in ancestors(p, parents)
                           if re.fullmatch(r"\d{3}\.\d{3}", a.get("id", ""))), None)
            counters[struct_id] += 1
            # Preserve official numbered paragraph anchors when present. Unnumbered
            # paragraphs receive a transparent extraction-order locator.
            seed = anchor or struct_e.get("id") + ":p" + str(counters[struct_id]).zfill(3)
            # Some adopted XHTML IDs are reused inside quoted amendments to
            # other legislation. Keep the record identity unambiguous.
            ambiguous_anchor = bool(anchor and node_index[struct_id]["kind"] == "article"
                                    and int(anchor.split(".")[0]) != int(struct_id.rsplit(":", 1)[-1]))
            if ambiguous_anchor:
                seed += ":in-" + struct_e.get("id")
            point_counters[(struct_id, seed)] += 1
            point_index = point_counters[(struct_id, seed)]
            suffix = "" if point_index == 1 else ":p" + str(point_index).zfill(2)
            point_label = ""
            row = next((a for a in ancestors(p, parents) if local(a) == "tr"), None)
            if row is not None:
                row_ps = [q for q in row.iter() if local(q) == "p"]
                if row_ps and BARE_LABEL.fullmatch(text(row_ps[0])):
                    point_label = text(row_ps[0])
            locator = seed + suffix
            # The URL fragment is always an existing source anchor; the local
            # locator can be finer-grained than that anchor.
            fields = source_fields([p], struct_e.get("id") if ambiguous_anchor else anchor or struct_e.get("id"))
            fields["locator"] = locator
            title = node_index[struct_id]["label"].split(" · ")[0]
            para_number = anchor.split(".")[-1].lstrip("0") if anchor else ""
            label = title + ("(" + para_number + ")" if para_number else "")
            label += (" " + point_label) if point_label else " · passage " + str(counters[struct_id])
            n = add_node(dict(id=f"{doc}:passage:{locator}", kind="passage", label=label,
                              layer="structure", parent_id=struct_id, **fields))
            add_edge(struct_id, n["id"], "contains", "structure", "xhtml_ancestry")
            all_passages.append(n)
            if node_index[struct_id]["kind"] == "article":
                article_passages[struct_id].append(n)
            definition = re.match(
                r"^‘([^’]+)’(?:\s+of the data subject|, for the purpose of real-world testing,)?\s+means\b",
                n["quote"])
            if definition and struct_id == f"{doc}:article:{spec['definition_article']}":
                term = definition.group(1)
                t_id = doc + ":term:" + digest(term.casefold().encode())[:12]
                term_fields = {k: n[k] for k in ("document_id", "locator", "quote", "source_url", "source_start", "source_end")}
                add_node(dict(id=t_id, kind="defined_term", label=term, layer="terminology",
                              **term_fields))
                add_edge(n["id"], t_id, "defines_term", "terminology", "literal_definition_pattern")
                definitions.append((doc, term, t_id))

    # Only article and annex body passages are scanned for references. Recitals,
    # footnotes and inserted amendment text are deliberately not scope-resolved.
    unresolved = Counter()
    for n in all_passages:
        doc, q = n["document_id"], n["quote"]
        art_match = re.search(r":article:(\d+)$", n["parent_id"])
        if doc == "ai-act" and art_match and 99 <= int(art_match.group(1)) <= 110:
            continue
        for m in ARTICLE_RE.finditer(q):
            tail = q[m.end():]
            if re.match(r"\s+thereof\b", tail):
                # A legal antecedent must not be guessed from a local article ID.
                continue
            scope = SCOPE_RE.match(tail)
            external = scope if scope and not scope.group(1).startswith("this Regulation") else None
            target_doc, method = doc, "lexical_local_article_reference"
            if external:
                if re.match(r"Regulation\s+\(EU\)\s+2016/679\b", external.group(1)):
                    target_doc, method = "gdpr", "lexical_explicit_instrument_reference"
                elif re.match(r"Regulation\s+\(EU\)\s+2024/1689\b", external.group(1)):
                    target_doc, method = "ai-act", "lexical_explicit_instrument_reference"
                else:
                    unresolved[external.group(1).split(",")[0][:65]] += 1
                    continue
            for number in NUMBER_RE.finditer(m.group(1)):
                target = f"{target_doc}:article:{number.group(1)}"
                if target not in node_index:
                    continue
                add_edge(n["id"], target, "references_article", "references", method,
                         source_locator=n["locator"], evidence=m.group(0),
                         match_start=m.start(), match_end=m.end())
        for m in ANNEX_RE.finditer(q):
            # Annex references remain local; explicitly foreign annexes are omitted.
            if re.match(r"\s+(?:of|to)\s+(?!this\s+Regulation)", q[m.end():]):
                continue
            target = f"{doc}:annex:{m.group(1)}"
            if target in node_index:
                add_edge(n["id"], target, "references_annex", "references", "lexical_local_annex_reference",
                         source_locator=n["locator"], evidence=m.group(0),
                         match_start=m.start(), match_end=m.end())

    # Aggregate exact lexical matches by (article, document-specific term).
    # This avoids thousands of repetitive links without inventing semantic edges.
    for doc, term, term_id in definitions:
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.I)
        for article, passages in sorted(article_passages.items()):
            if not article.startswith(doc + ":"):
                continue
            hits = [(p, list(pattern.finditer(p["quote"]))) for p in passages]
            hits = [(p, matches) for p, matches in hits if matches]
            if not hits:
                continue
            p, matches = hits[0]
            first = matches[0]
            add_edge(article, term_id, "mentions_term", "terminology", "case_insensitive_literal_phrase",
                     evidence_node=p["id"], evidence=first.group(0),
                     match_start=first.start(), match_end=first.end(),
                     occurrences=sum(len(ms) for _, ms in hits), passage_count=len(hits))

    nodes.sort(key=lambda n: n["id"])
    edges.sort(key=lambda e: e["id"])
    counts = dict(nodes=len(nodes), edges=len(edges),
                  node_kinds=dict(sorted(Counter(n["kind"] for n in nodes).items())),
                  edge_relations=dict(sorted(Counter(e["relation"] for e in edges).items())),
                  layers={l: dict(nodes=sum(n["layer"] == l for n in nodes), edges=sum(e["layer"] == l for e in edges))
                          for l in ("structure", "references", "terminology")})
    presets = [
        dict(id="assessment-boundaries", title="Before drafting an assessment", start_id="ai-act:article:27",
             question="Which classification, role and impact-assessment conditions must an analyst inspect?",
             description="An authored reading route, not a finding of applicability. Compare Article 6 classification, Article 26 deployer duties, Article 27 scope and exceptions, and the explicit link to GDPR Article 35.",
             node_ids=["ai-act:article:6", "ai-act:passage:006.002", "ai-act:article:26", "ai-act:article:27", "ai-act:passage:027.001", "ai-act:passage:027.004", "gdpr:article:35", "gdpr:passage:035.001", "gdpr:passage:035.002"]),
        dict(id="human-oversight", title="Trace human oversight", start_id="ai-act:article:14",
             question="What does the adopted text say about design, deployment and oversight arrangements?",
             description="Read the different addressees and conditions rather than flattening them into one requirement. Article 27(1)(e) is an assessment-description item; it is not the same provision as Article 14.",
             node_ids=["ai-act:article:14", "ai-act:passage:014.001", "ai-act:article:26", "ai-act:passage:026.002", "ai-act:article:27", "ai-act:passage:027.001:p06"]),
        dict(id="qualified-advice", title="Keep the qualifier", start_id="gdpr:passage:035.002",
             question="What changes if the phrase ‘where designated’ is dropped from a draft?",
             description="Inspect the exact GDPR Article 35(2) wording alongside Articles 37 and 39. The source quote contains ‘where designated’; the graph does not decide whether a particular controller must appoint one.",
             node_ids=["gdpr:article:35", "gdpr:passage:035.002", "gdpr:article:37", "gdpr:article:39"]),
    ]
    for p in presets:
        p["label"] = p["title"]
        for ident in p["node_ids"]:
            if ident not in node_index:
                raise ValueError("Preset refers to absent record: " + ident)
    graph = dict(schema=SCHEMA, meta=dict(
        title="AI governance: an inspectable source graph",
        case_question="Before drafting a high-risk AI deployment-assessment note, which adopted-text provisions, definitions and qualifiers should an analyst inspect?",
        built_on=BUILD_DATE,
        edition_scope="English adopted-text snapshots of the AI Act (2024) and GDPR (2016), not current consolidated legislation or an assessment of present applicability.",
        counts=counts, sources=specs,
        offset_convention="Zero-based Unicode code-point offsets [source_start, source_end) in the pinned sources/{document_id}.txt representation. Whitespace is normalized per XHTML paragraph; paragraphs are separated by two LF characters.",
        presets=presets,
        review_state="Reproducibly extracted public source demonstrator; no legal-expert or human-approval certification.",
        limitations=[
            "A source graph, not a benchmark result, a complete legal ontology, legal advice, or a production compliance decision system.",
            "Adopted editions are intentionally frozen. Later amendments, corrigenda, case law, guidance and phased application dates are not reconciled.",
            "Contains edges reproduce XHTML ancestry. Defined terms are literal definition-opening patterns in AI Act Article 3 and GDPR Article 4, preserving the text's qualifying phrases. No cross-document equivalence is asserted.",
            "Term occurrences are case-insensitive literal singular-phrase matches in operative articles, aggregated by article. They do not establish that a legal definition applies to each usage; morphology, synonyms and semantic entailment are not inferred.",
            "Article-reference extraction is conservative and incomplete. Bare references in operative passages are treated as local to the source document. Explicit foreign instruments other than the two pinned texts are omitted; recitals, footnotes and AI Act amending Articles 99–110 are not reference-parsed.",
            "Article lists are tokenized; ranges record their written endpoints only. ‘Thereof’ antecedents, paragraph and point references are not resolved into additional legal dependencies.",
            "The reading presets are authored inspection questions, kept outside the extracted graph. They do not establish that a real deployment is high-risk or subject to an impact assessment.",
            "Source passages preserve qualifications and exceptions, including ‘where designated’. The graph cannot establish factual accuracy, completeness, or a hallucination reduction on its own.",
            "Normalized text is a derivative representation. The Official Journal and its current legal record remain the authority; inspect the linked official source.",
        ]), nodes=nodes, edges=edges)
    return graph, snapshots


def record_list(graph):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    keys = ("id", "kind", "label", "document_id", "locator", "source_url")
    writer.writerow(keys)
    writer.writerows([n[k] for k in keys] for n in graph["nodes"])
    return stream.getvalue().encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=BASE)
    args = parser.parse_args()
    graph, snapshots = build_graph()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "sources").mkdir(exist_ok=True)
    for name, snapshot in snapshots.items():
        (args.output_dir / "sources" / (name + ".txt")).write_text(snapshot, encoding="utf-8")
    payload = compact(graph)
    (args.output_dir / "graph.json").write_bytes(payload)
    (args.output_dir / "records.csv").write_bytes(record_list(graph))
    print(json.dumps(dict(**graph["meta"]["counts"], bytes=len(payload), sha256=digest(payload)), indent=2))


if __name__ == "__main__":
    main()

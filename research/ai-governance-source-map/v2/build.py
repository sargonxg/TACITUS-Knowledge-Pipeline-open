#!/usr/bin/env python3
"""Build an inspectable source atlas from four EU acts and three CJEU judgments.

Python 3.10+ standard library only. No model, credentials or network are needed.
This is a document/terminology graph, not an automatically validated legal ontology.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
from html.parser import HTMLParser
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
    r"^[\s,]*(?:et\s+seq\.\s*)?(?:(?:points?|paragraphs?)\s+(?:\([a-z0-9]+\)|\d+)"
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


class PublicHTML(HTMLParser):
    """Minimal standard-library DOM for the public CURIA judgment HTML.

    HTMLParser decodes named HTML entities; no scripts, requests or external
    entities execute. EU legislation continues to use strict XML parsing.
    """
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = ET.Element("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        e = ET.SubElement(self.stack[-1], tag, dict(attrs))
        if tag not in self.VOID:
            self.stack.append(e)

    def handle_startendtag(self, tag, attrs):
        ET.SubElement(self.stack[-1], tag, dict(attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                return

    def handle_data(self, data):
        e = self.stack[-1]
        if len(e):
            e[-1].tail = (e[-1].tail or "") + data
        else:
            e.text = (e.text or "") + data


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
        is_case = spec.get("format") == "curia_html"
        if is_case:
            parser = PublicHTML()
            parser.feed(raw.decode("utf-8"))
            parser.close()
            root = parser.root
        else:
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
                        source_url=spec["url"] + ("" if is_case else "#" + anchor),
                        source_start=start, source_end=end)

        if is_case:
            case_ps = [p for p in paragraphs if p.get("class", "").startswith("C")]
            title_ps = case_ps[:2]
            add_node(dict(id=doc + ":document", kind="document", label=spec["title"],
                          layer="structure", record_role="historical_judgment",
                          decision_date=spec["decision_date"],
                          **source_fields(title_ps, "judgment-heading")))

            def case_record(selected, locator, label, role):
                n = add_node(dict(id=doc + ":passage:" + locator, kind="passage", label=label,
                                  layer="structure", record_role=role, parent_id=doc + ":document",
                                  **source_fields(selected, locator)))
                add_edge(doc + ":document", n["id"], "contains", "structure", "published_judgment_structure")
                all_passages.append(n)

            numbered = [(i, p) for i, p in enumerate(case_ps) if p.get("class", "").startswith("C01")]
            for index, p in numbered:
                number = re.match(r"^(\d+)\s", text(p))
                if not number:
                    raise ValueError("Unexpected numbered judgment paragraph: " + doc)
                selected = [p]
                for following in case_ps[index+1:]:
                    if following.get("class", "").startswith(("C01", "C04", "C05", "C06", "C41", "C77")):
                        break
                    selected.append(following)
                case_record(selected, "paragraph:" + number.group(1), spec["title"].split(" · ")[0] + " · Paragraph " + number.group(1), "judgment_paragraph")
            operative_index = next(i for i, p in enumerate(case_ps) if p.get("class", "").startswith("C41"))
            groups = []
            for p in case_ps[operative_index+1:]:
                cls = p.get("class", "")
                if cls.startswith(("C77", "C42")):
                    break
                if cls.startswith("C08") or not groups:
                    groups.append([])
                groups[-1].append(p)
            for i, selected in enumerate(groups, 1):
                case_record(selected, "operative:" + str(i), spec["title"].split(" · ")[0] + " · Operative part " + str(i), "judgment_operative_part")
            continue

        title_p = next((e for e in paragraphs if "oj-doc-ti" in e.get("class", "").split()
                        and any(word in text(e) for word in ("REGULATION", "DIRECTIVE"))), paragraphs[0])
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

    # Article/annex passages and judgment records are scanned. For judgments,
    # only explicitly named included instruments can resolve to article nodes.
    # Recitals, footnotes and inserted amendments are not scope-resolved.
    unresolved = Counter()
    for n in all_passages:
        doc, q = n["document_id"], n["quote"]
        art_match = re.search(r":article:(\d+)$", n["parent_id"])
        spec = next(s for s in specs if s["id"] == doc)
        excluded = list(range(99, 111)) if doc == "ai-act" else spec.get("excluded_reference_articles", [])
        if art_match and int(art_match.group(1)) in excluded:
            continue
        for m in ARTICLE_RE.finditer(q):
            tail = q[m.end():]
            if re.match(r"\s+thereof\b", tail):
                # A legal antecedent must not be guessed from a local article ID.
                continue
            scope = SCOPE_RE.match(tail)
            external = scope if scope and not scope.group(1).startswith(("this Regulation", "this Directive")) else None
            target_doc, method = doc, "lexical_local_article_reference"
            if external:
                instruments = [("gdpr", r"(?:Regulation\s+(?:\(EU\)\s+)?2016/679\b|(?:the\s+)?GDPR\b)"),
                               ("ai-act", r"Regulation\s+(?:\(EU\)\s+)?2024/1689\b"),
                               ("dsa", r"Regulation\s+(?:\(EU\)\s+)?2022/2065\b"),
                               ("led", r"Directive\s+(?:\(EU\)\s+)?2016/680\b")]
                target_doc = next((ident for ident, pattern in instruments if re.match(pattern, external.group(1))), None)
                if target_doc:
                    method = "lexical_explicit_instrument_reference"
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
             description="An editorial reading route, not a finding of applicability. Compare classification, deployer duties, Article 27 scope and exceptions, and the distinct GDPR and Law Enforcement Directive assessment references. The applicable processing regime must be established for the actual activity.",
             node_ids=["ai-act:article:6", "ai-act:passage:006.002", "ai-act:article:26", "ai-act:article:27", "ai-act:passage:027.001", "ai-act:passage:027.004", "gdpr:article:35", "gdpr:passage:035.001", "gdpr:passage:035.002", "led:article:1", "led:article:27", "led:passage:027.001"]),
        dict(id="human-oversight", title="Trace human oversight", start_id="ai-act:article:14",
             question="What does the adopted text say about design, deployment and oversight arrangements?",
             description="Read the different addressees and conditions rather than flattening them into one requirement. Article 27(1)(e) is an assessment-description item; it is not the same provision as Article 14.",
             node_ids=["ai-act:article:14", "ai-act:passage:014.001", "ai-act:article:26", "ai-act:passage:026.002", "ai-act:article:27", "ai-act:passage:027.001:p06"]),
        dict(id="qualified-advice", title="Keep the qualifier", start_id="gdpr:passage:035.002",
             question="What changes if the phrase ‘where designated’ is dropped from a draft?",
             description="Inspect the exact GDPR Article 35(2) wording alongside Articles 37 and 39. The source quote contains ‘where designated’; the graph does not decide whether a particular controller must appoint one.",
             node_ids=["gdpr:article:35", "gdpr:passage:035.002", "gdpr:article:37", "gdpr:article:39"]),
        dict(id="schufa-scoring", title="SCHUFA · When a score shapes a decision", start_id="schufa:passage:operative:1",
             case_id="schufa", decision_date="2023-12-07",
             question="Which condition makes the transmitted probability value part of automated individual decision-making, and what remained for the referring court?",
             description="7 December 2023 · C-634/21, a CJEU preliminary ruling. Keep the operative part's condition that the third party draws strongly on the score. Paragraph 72 leaves national legal-basis and condition checks to the referring court. This is not a finding that every score is prohibited, and it predates the AI Act.",
             node_ids=["schufa:document", "schufa:passage:paragraph:43", "schufa:passage:paragraph:60", "schufa:passage:paragraph:72", "schufa:passage:paragraph:73", "schufa:passage:operative:1", "gdpr:article:5", "gdpr:article:6", "gdpr:article:22"]),
        dict(id="online-declarations", title="Public declarations · What disclosure can reveal", start_id="online-declarations:passage:operative:2",
             case_id="online-declarations", decision_date="2022-08-01",
             question="How do the judgment's proportionality analysis and indirect disclosure of sensitive data constrain a public-interest publication argument?",
             description="1 August 2022 · C-184/20, a CJEU preliminary ruling on the specific online private-interest declaration regime. Read both operative points: the specified publication is precluded in the stated respects, and information liable indirectly to disclose sexual orientation falls within special-category processing. This does not hold that every public declaration is unlawful.",
             node_ids=["online-declarations:document", "online-declarations:passage:paragraph:104", "online-declarations:passage:paragraph:115", "online-declarations:passage:paragraph:120", "online-declarations:passage:paragraph:127", "online-declarations:passage:paragraph:128", "online-declarations:passage:operative:1", "online-declarations:passage:operative:2", "gdpr:article:6", "gdpr:article:9"]),
        dict(id="meta-cooperation-consent", title="Meta · Authority, cooperation and consent", start_id="meta-platforms:passage:operative:1",
             case_id="meta-platforms", decision_date="2023-07-04",
             question="What cooperation condition limits a competition authority's GDPR assessment, and what does market dominance establish about consent?",
             description="4 July 2023 · C-252/21, a CJEU preliminary ruling. The competition authority's assessment is subject to sincere cooperation with data-protection authorities. Dominance does not as such rule out valid consent, but is an important factor and the operator must prove validity. The judgment does not itself resolve every processing operation or a DSA enforcement case.",
             node_ids=["meta-platforms:document", "meta-platforms:passage:paragraph:62", "meta-platforms:passage:paragraph:143", "meta-platforms:passage:paragraph:150", "meta-platforms:passage:operative:1", "meta-platforms:passage:operative:8", "gdpr:article:6", "gdpr:article:7", "gdpr:article:9", "gdpr:article:51"]),
        dict(id="dsa-systemic-risks", title="DSA · Assessment, mitigation and scrutiny", start_id="dsa:article:34",
             question="Which adopted provisions should an analyst inspect before writing about platform systemic-risk assessment and external scrutiny?",
             description="A provision-reading route, not an enforcement finding: inspect the addressees, risk assessment, mitigation, audit and data-access conditions in DSA Articles 34, 35, 37 and 40. The map does not establish designation or breach by any platform.",
             node_ids=["dsa:article:33", "dsa:article:34", "dsa:article:35", "dsa:article:37", "dsa:article:40"]),
    ]
    for p in presets:
        p["label"] = p["title"]
        p["route_kind"] = "editorial_case_reading_route" if "case_id" in p else "editorial_provision_reading_route"
        p["annotation_status"] = "TACITUS-authored guidance; not an extracted link, expert approval or applicability finding"
        for ident in p["node_ids"]:
            if ident not in node_index:
                raise ValueError("Preset refers to absent record: " + ident)
    graph = dict(schema=SCHEMA, meta=dict(
        title="AI governance source atlas · Instruments and real judgments",
        release="v2",
        case_question="How can an analyst connect an adopted provision, the exact judgment that interpreted it, and the conditions a draft must preserve?",
        built_on=BUILD_DATE,
        edition_scope="English adopted-text snapshots of the AI Act (2024), GDPR (2016), DSA (2022) and Law Enforcement Directive (2016), plus English translations of three historical CJEU preliminary-ruling judgments. Not current consolidated law or an assessment of present applicability.",
        counts=counts, sources=specs,
        offset_convention="Zero-based Unicode code-point offsets [source_start, source_end) in the pinned sources/{document_id}.txt representation. Whitespace is normalized per XHTML paragraph; paragraphs are separated by two LF characters.",
        presets=presets,
        cases=[dict(id=s["id"], label=s["title"], title=s["title"], case_number=s["title"].split(" · ")[0], source_document_id=s["id"],
                    decision_date=s["decision_date"], ecli=s["ecli"], celex=s["celex"],
                    event_type="CJEU judgment on a reference for a preliminary ruling",
                    source_url=s["url"], outcome_node_ids=[n["id"] for n in nodes if n["document_id"] == s["id"] and n.get("record_role") == "judgment_operative_part"],
                    route_id=next(p["id"] for p in presets if p.get("case_id") == s["id"]),
                    editorial_summary=next(p["description"] for p in presets if p.get("case_id") == s["id"]),
                    reading_question=next(p["question"] for p in presets if p.get("case_id") == s["id"]),
                    annotation_status="TACITUS-authored reading guidance; not an extracted finding or expert approval",
                    status_note="Historical issued judgment; not an Advocate General opinion. English is a translation. Subsequent national proceedings, later case-law and present applicability are not audited.")
               for s in specs if s.get("format") == "curia_html"],
        review_state="Reproducibly extracted public source demonstrator; no legal-expert or human-approval certification.",
        limitations=[
            "A source graph, not a benchmark result, a complete legal ontology, legal advice, or a production compliance decision system.",
            "All source editions are intentionally frozen. Later amendments, corrigenda, judgments, guidance, national outcomes and phased application dates are not reconciled. These three judgments do not make the instrument collection current consolidated law.",
            "Contains edges reproduce XHTML ancestry or published judgment paragraph/operative structure. Defined terms are literal definition openings in the four instruments. A definition can continue into following source passages. No cross-document equivalence is asserted.",
            "Term occurrences are case-insensitive literal singular-phrase matches in operative articles, aggregated by article. They do not establish that a legal definition applies to each usage; morphology, synonyms and semantic entailment are not inferred.",
            "Article-reference extraction is conservative and incomplete. Bare references in instrument passages are treated as local; judgments resolve only explicitly named included instruments. Other foreign instruments are omitted. Recitals, footnotes, AI Act amending Articles 99–110 and DSA amending Articles 89–90 are not reference-parsed.",
            "Article lists are tokenized; ranges record their written endpoints only. ‘Thereof’ antecedents, paragraph and point references are not resolved into additional legal dependencies.",
            "The reading presets and case descriptions are editorial inspection guidance, kept outside extracted links. They do not establish a real deployment's classification, a platform breach or an organisation's obligations. The historical judgments are not rulings under the later AI Act.",
            "Source passages preserve qualifications and exceptions, including ‘where designated’. The graph cannot establish factual accuracy, completeness, or a hallucination reduction on its own.",
            "Normalized text is a derivative representation. CURIA judgment records preserve the published numbered paragraph together with continuation/list blocks, or an operative point together with its continuation. Only the case-language text is authentic; inspect the linked official source.",
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

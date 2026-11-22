"""Check the fixture's standards mapping and reject omitted lineage or changed modality."""

import argparse
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Literal, Namespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    args = parser.parse_args()
    data = args.export.read_text(encoding="utf-8")
    shapes = Graph().parse(Path(__file__).with_name("shapes.ttl"), format="turtle")
    prov = Namespace("http://www.w3.org/ns/prov#")
    tac = Namespace("https://tacitus.me/ns/reference#")
    graph = Graph().parse(data=data, format="json-ld")
    ok, _, report = validate(graph, shacl_graph=shapes)
    if not ok:
        parser.exit(1, str(report))
    graph.remove((None, prov.wasDerivedFrom, None))
    if validate(graph, shacl_graph=shapes)[0]:
        parser.exit(1, "Missing provenance should fail.\n")
    graph = Graph().parse(data=data, format="json-ld")
    statement = next(graph.subjects(tac.modality))
    graph.set((statement, tac.modality, Literal("obligation")))
    if validate(graph, shacl_graph=shapes)[0]:
        parser.exit(1, "Promoting suggested guidance to an obligation should fail.\n")
    print("NIST standards export conforms. Missing provenance and changed modality were rejected.")


if __name__ == "__main__":
    main()

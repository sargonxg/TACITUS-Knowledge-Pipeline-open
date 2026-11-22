# Define the ontology

Start with `ontology/policy.json`. Its `entity_types` define the objects the application can represent. Each relation declares allowed subject (`domain`) and object (`range`) types. The builder rejects unresolved entities or relations that violate those constraints.

The assessment example distinguishes assessments, review roles, a process and an institution. A statement reifies an attributed interpretation, its predicate, exact evidence, modality, qualifications and proposed review state. It does not directly assert that the legal relationship applies to a particular case.

Add a type only when it supports a real analytical question. Add a relation only with a definition, permitted types and a counterexample. Then add a fixture and a failure case. This application vocabulary is not a universal policy ontology or a complete OWL reasoner. Published RDF/OWL vocabularies can be mapped in a separate reviewed adapter.

The JSON-LD export preserves node identities and references. It is an interchange view of this graph; no downstream importer or PRAXIS compatibility is implied.

The [citation-guidance proof](../examples/citation-guidance/README.md) adds a small release-review vocabulary. `ReleaseDecision` and `ReviewPractice` are distinct types. The `considers_guidance_for` relation expresses the authored interpretation, with its own source edition, suggested-guidance modality and review state. The same action code can refer to different practices in two editions, so the compiler keeps both records and the exact text linking each one.

Published standards play different roles. The [citation-guidance standards export](../examples/citation-guidance/compiled/standards.jsonld) uses SKOS for named review practices and PROV-O to connect versioned sources, exact spans and proposed statements. It retains the TACITUS vocabulary for review status, modality and quote offsets. Its SHACL shapes check those fields and links. [SKOS](https://www.w3.org/TR/skos-reference/) · [PROV-O](https://www.w3.org/TR/prov-o/) · [SHACL](https://www.w3.org/TR/shacl/) · [JSON-LD](https://www.w3.org/TR/json-ld11/)

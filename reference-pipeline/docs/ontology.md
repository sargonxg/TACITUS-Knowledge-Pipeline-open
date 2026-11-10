# Define the ontology

Start with `ontology/policy.json`. Its `entity_types` define the objects the application can represent. Each relation declares allowed subject (`domain`) and object (`range`) types. The builder rejects unresolved entities or relations that violate those constraints.

The assessment example distinguishes assessments, review roles, a process and an institution. A statement reifies an attributed interpretation, its predicate, exact evidence, modality, qualifications and proposed review state. It does not directly assert that the legal relationship applies to a particular case.

Add a type only when it supports a real analytical question. Add a relation only with a definition, permitted types and a counterexample. Then add a fixture and a failure case. This application vocabulary is not a universal policy ontology or a complete OWL reasoner. Published RDF/OWL vocabularies can be mapped in a separate reviewed adapter.

The JSON-LD export preserves node identities and references. It is an interchange view of this graph; no downstream importer or PRAXIS compatibility is implied.

# Build a semantic layer

An ontology defines types and relations. A semantic layer selects the records and review questions relevant to a particular job.

`layers/assessment-evidence.json` chooses three proposed mappings. The conditional complement relationship and the DPO advice condition are required. The template-role mapping can be omitted when the byte budget is too small. Omission is recorded; required evidence is never cut to fit.

To add a layer:

1. Write the analytical question and useful output.
2. Identify complete, version-pinned statements with source evidence.
3. Mark the statements that would change the conclusion as required.
4. Add explicit review checks and distinguish missing case inputs.
5. Test a small budget and source/qualification tampering.

Selection here is explicit and deterministic. It is not semantic embedding search, expert endorsement or automatic extraction. A production retrieval adapter needs access controls, evaluation and a rule for preserving disagreement.

For the [edition-change layer](../layers/citation-guidance-change.json), all three passages are required. The draft and final text answer whether the wording changed. The draft action that shares the final code is the counterexample that makes the interpretation auditable. The layer carries timing qualifiers into the capsule and refuses a budget too small for the complete evidence. A different question about release readiness would use a different layer and include local test and approval records.

The generic team-handoff layer can also use BM25 selection or bounded graph expansion. The selection report records included and omitted statements. Required qualifications stay with each selected statement. [App import](app-import.md)

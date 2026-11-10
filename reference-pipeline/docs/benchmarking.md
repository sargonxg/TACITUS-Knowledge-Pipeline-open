# Benchmark the right thing

`python benchmarks/run.py` uses the same fixed legal-source fixture at four byte budgets. It records source counts, selected/omitted statements, bytes and refusal behavior. Tests separately check source tampering, qualifications, ontology types, stable identity and review boundaries. No language model is called.

This measures assembly behavior, not political understanding, token savings or analyst-time savings. A smaller packet can remove useful information; indexing and review also cost time.

The model-output comparison is work in progress. `benchmarks/model-evaluation-plan.json` specifies matched source pools, held-out tasks and task-only/retrieval/structured-context arms. It requires recorded outputs, model versions, provider usage and blind domain review. No model results are fabricated or prefilled.

TCGC is a separate alpha corpus/scoring project with its own license and limitations: https://github.com/sargonxg/TCGC_TACITUS-Conflict-Grammar-Corpus_BENCHMARK. It does not establish results for this pipeline.

# Benchmark the right thing

`python benchmarks/run.py` uses the same fixed legal-source fixture at four byte budgets. It records source counts, selected/omitted statements, bytes and refusal behavior. Tests separately check source tampering, qualifications, ontology types, stable identity and review boundaries. No language model is called.

This measures assembly behavior, not political understanding, token savings or analyst-time savings. A smaller packet can remove useful information; indexing and review also cost time.

The [model-output protocol](../benchmarks/model-evaluation-plan.json) specifies a fixed model, matched source pools, held-out tasks and three arms using full documents, plain retrieval and structured context. It separates clean task completion, citation support and preserved qualifications from end-to-end costs, including the analyst time needed to review the result. The [edition-change proof](../examples/citation-guidance/README.md) is a development fixture. Model output evaluation is pending.

ALCE motivates separate measures for citation support and coverage. Lost in the Middle motivates a positional stress test for the evidence. The GraphRAG paper motivates comparison against ordinary retrieval when corpus structure matters. Each is a research reference. [ALCE](https://aclanthology.org/2023.emnlp-main.398/) · [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/) · [GraphRAG](https://arxiv.org/abs/2404.16130)

TCGC is a separate alpha corpus/scoring project with its own license and limitations: https://github.com/sargonxg/TCGC_TACITUS-Conflict-Grammar-Corpus_BENCHMARK. It does not establish results for this pipeline.

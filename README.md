# TACITUS Knowledge Pipeline (Open)

![TACITUS network](assets/images/tacitus-network.png)

**Open-source ingestion pipeline for conflict & human-friction analysis.**  
Turn messy text (emails, docs, transcripts) into a **time-aware graph** of actors, events, claims, commitments, and relationships—grounded in a **conflict ontology** designed for disciplined reasoning.

> Repo: https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open  
> Image: https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open/blob/main/assets/images/tacitus-network.png

---

## Why this exists

Most “AI conflict analysis” fails at the same point: **unstructured text**.  
If the system can’t reliably track *who did what, when, and how claims relate to evidence*, you don’t get analysis—you get plausible narration.

This repository open-sources a foundational layer of TACITUS: an ingestion pipeline that produces a **structured, inspectable case graph** you can query, audit, and iterate on.

- Website / broader vision: tacitus.me

---

## What you get (capabilities)

- **Ingest**: load documents and split into stable chunks
- **Extract**: actors, events, claims, relations using LLM prompts aligned to a conflict ontology
- **Normalize**: entity resolution / aliasing (e.g., “UN”, “United Nations”)
- **Persist**: build a graph (Neo4j by default) + embeddings for retrieval
- **Inspect**: diagnostics + sanity checks (counts, connectivity, missing fields)
- **Reproducible runs**: config via env vars; no secrets in notebooks

(See notebooks below.)

---

## Repository contents

- `TACITUS_PIPELINE_Workbench_v8.ipynb` — main development notebook
- `TACITUS_PIPELINE_NoOutput.ipynb` — cleaner notebook for public runs
- `notebooks/` — versioned notebooks
- `assets/images/` — diagrams (including the network image above)
- `REPO_REVIEW.md` — review notes / technical observations

---

## Quickstart (Google Colab)

1) Open the public notebook:  
- (add “Open in Colab” badge/link here)

2) In the setup cell, set environment variables:

```python
import os

os.environ["GCP_PROJECT_ID"] = "your-project-id"
os.environ["GCP_REGION"] = "your-region"

os.environ["NEO4J_URI"] = "neo4j+s://your-instance.databases.neo4j.io"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "your-password"

os.environ["GEMINI_MODEL"] = "gemini-1.5-pro"
os.environ["EMBEDDING_MODEL"] = "text-embedding-004"
```

Run top-to-bottom. You should end with:

- nodes + edges written to Neo4j
- embeddings created
- a “run summary” with counts + basic validation checks

---

## Outputs (what the pipeline produces)

Graph primitives (recommended minimum):

- Actor (person/org/group)
- Event (with time)
- Claim (speaker, content, target, confidence)
- Relationship (ally/adversary/influence/command/etc.)
- Commitment / Constraint (who owes what to whom; limiting conditions)
- Evidence (source pointers; provenance)

Run artifacts:

- `runs/<timestamp>/manifest.json` (config + versions + model IDs)
- `runs/<timestamp>/extractions.jsonl`
- `runs/<timestamp>/entity_resolution.json`
- `runs/<timestamp>/graph_write_report.json`

---

## Configuration (env vars)

Core:

- `GCP_PROJECT_ID`, `GCP_REGION`
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- `GEMINI_MODEL`, `EMBEDDING_MODEL`

Pipeline behavior:

- `TACITUS_CHUNK_SIZE`, `TACITUS_CHUNK_OVERLAP`
- `TACITUS_ER_THRESHOLD` (entity resolution threshold)
- `TACITUS_DEFAULT_DATE`
- `TACITUS_DRY_RUN`

Safety / privacy:

- Do not commit secrets to notebooks.
- For sensitive corpora: run locally, use private storage, and scrub outputs before sharing.

---

## Contributing

PRs welcome. Please:

- keep secrets out of repo
- document schema/prompt changes
- add tests for any new module
- include a small reproducible sample input + expected output

---

## License

(Choose a license: Apache-2.0 or MIT are common defaults; add LICENSE file.)

---

## Codex To-Do List (with acceptance criteria)

### Milestone A — Repo hygiene (make it look serious)
- [ ] **Rename `readme.md` → `README.md`** (GitHub convention).  
  **Accept:** repo root shows rendered README.
- [ ] Add `LICENSE` (MIT or Apache-2.0).  
  **Accept:** GitHub displays license badge/metadata.
- [ ] Add `.gitignore` for notebooks, local outputs, `.env`, `.ipynb_checkpoints/`, `runs/`, etc.  
  **Accept:** running pipeline doesn’t dirty git status with artifacts.
- [ ] Add `SECURITY.md` + “No secrets in notebooks” policy.  
  **Accept:** simple security guidance exists.
- [ ] Add `CITATION.cff` (optional but signals seriousness).  
  **Accept:** GitHub shows “Cite this repository”.

### Milestone B — Make it runnable in 15 minutes (the #1 credibility lever)
- [ ] Add `requirements.txt` (pinned versions) **and** `requirements-colab.txt` if needed.  
  **Accept:** fresh env installs without manual edits.
- [ ] Add `.env.example` listing all env vars with safe placeholders.  
  **Accept:** user can copy→paste and run.
- [ ] Add **one** canonical entry notebook: `notebooks/00_quickstart.ipynb` that runs end-to-end on a small sample corpus.  
  **Accept:** “Run all” completes without errors using sample input.
- [ ] Add `data/sample/` with 2–3 small realistic text files + a minimal “expected outputs” snapshot.  
  **Accept:** quickstart produces same node/edge counts ± small tolerance.

### Milestone C — Separate notebook UI from real pipeline code
Right now, the repo appears notebook-driven. That’s fine, but you need a `src/` so the logic is testable and reusable.
- [ ] Create `src/tacitus_pipeline/` package:
  - `ingest.py` (load files, chunking)
  - `extract.py` (LLM calls, prompt templates)
  - `schema.py` (pydantic models)
  - `resolve.py` (entity resolution)
  - `graph/neo4j_writer.py`
  - `embed.py`
  - `run.py` (orchestrator)
  **Accept:** notebooks import from `src/…` and contain minimal logic.
- [ ] Create a single config object (pydantic) fed by env vars.  
  **Accept:** no hardcoded model IDs or secrets in code.

### Milestone D — Make the “custom ontology” real (and visible)
- [ ] Add `ontology/` with:
  - `ontology.yml` (node/edge types + required fields)
  - `taxonomy.yml` (relationship labels; claim types; evidence types)
  - `validation_rules.yml` (minimum viable graph)
  **Accept:** pipeline validates extracted objects against ontology and reports violations.
- [ ] Add a README section “Ontology” with a 30-line excerpt + link to file(s).  
  **Accept:** a reader understands your primitives without opening notebooks.

### Milestone E — Deterministic, auditable outputs (what makes TACITUS “shine”)
- [ ] Introduce `runs/<run_id>/manifest.json` capturing:
  - git commit hash
  - package versions
  - model IDs
  - config params
  - input file hashes
  **Accept:** two runs are comparable and reproducible.
- [ ] Save raw extractions (`jsonl`) before normalization and after.  
  **Accept:** you can inspect “what the model said” vs “what the system wrote”.
- [ ] Add provenance fields everywhere: `source_doc`, `chunk_id`, `offsets`, `extraction_confidence`, `timestamp`.  
  **Accept:** every node/edge can be traced back to text.

### Milestone F — Quality gates and tests (minimum viable)
- [ ] Add unit tests for:
  - chunker stability
  - schema validation
  - entity-resolution merges/splits
  **Accept:** `pytest` runs green locally.
- [ ] Add one end-to-end test that runs pipeline on sample corpus with mocks for LLM calls (fixture JSON).  
  **Accept:** CI doesn’t require external API keys.
- [ ] Add a “graph sanity check” module:
  - no orphan events
  - events have time or `time_unknown=true`
  - claims have speaker + content
  **Accept:** failing checks stops the run (or flags with severity).

### Milestone G — CI / automation (signals maturity)
- [ ] Add GitHub Actions workflow:
  - lint (ruff)
  - type check (pyright/mypy)
  - tests (pytest)
  - notebook smoke test (optional)
  **Accept:** PR shows green checks.
- [ ] Add pre-commit config (ruff, trailing whitespace, yaml).  
  **Accept:** contributors can’t easily break formatting.

### Milestone H — Neo4j experience (make demo irresistible)
- [ ] Provide a `docker-compose.yml` for local Neo4j + browser.  
  **Accept:** `docker compose up` gives a working local graph.
- [ ] Add `queries/` with ready Cypher:
  - “top actors by mentions”
  - “event timeline”
  - “claim network”
  - “conflict escalation indicators”
  **Accept:** user can run queries immediately after ingest.

### Milestone I — Packaging & CLI (optional but powerful)
- [ ] Add a CLI: `python -m tacitus_pipeline run --input data/sample --output runs/...`  
  **Accept:** works locally without notebooks.
- [ ] Add `Makefile` (or `justfile`) for common tasks: `make install`, `make test`, `make run-sample`.  
  **Accept:** contributors have a paved path.

---

## Suggested target repo structure

```text
.
├─ README.md
├─ LICENSE
├─ requirements.txt
├─ .env.example
├─ src/
│  └─ tacitus_pipeline/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ ingest.py
│     ├─ extract.py
│     ├─ schema.py
│     ├─ resolve.py
│     ├─ embed.py
│     ├─ run.py
│     └─ graph/
│        ├─ neo4j_writer.py
│        └─ cypher_templates.py
├─ ontology/
│  ├─ ontology.yml
│  ├─ taxonomy.yml
│  └─ validation_rules.yml
├─ notebooks/
│  ├─ 00_quickstart.ipynb
│  └─ 01_workbench.ipynb
├─ data/
│  └─ sample/
├─ queries/
├─ tests/
└─ .github/workflows/ci.yml
```

---

## Small but high-impact “shine” tweaks (startup polish)

- Add badges at top of README: “CI”, “License”, “Python version”, “Open in Colab”.
- Add a 30-second demo script section: input → run → Neo4j screenshot → 3 queries.
- Add an “Engineering principles” section: reproducibility, provenance, temporality, auditability.

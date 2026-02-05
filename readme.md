# TACITUS Knowledge Pipeline

```
████████╗ █████╗  ██████╗ ██╗████████╗██╗   ██╗███████╗
╚══██╔══╝██╔══██╗██╔════╝ ██║╚══██╔══╝██║   ██║██╔════╝
   ██║   ███████║██║  ███╗██║   ██║   ██║   ██║███████╗
   ██║   ██╔══██║██║   ██║██║   ██║   ██║   ██║╚════██║
   ██║   ██║  ██║╚██████╔╝██║   ██║   ╚██████╔╝███████║
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚══════╝
```

```
   ┌───────────────────────────────────────────────────┐
   │ TACITUS Knowledge Pipeline                         │
   │ Conflict resolution intelligence, structured       │
   │ for clarity and real world action                  │
   └───────────────────────────────────────────────────┘
```

## Why this exists

TACITUS builds tools that help people reason about conflict with discipline. This repository open sources a key part of that work. It is a knowledge pipeline that turns messy documents into structured cases, actors, events, relationships, and theory aligned insights. The long term mission is to make conflict understanding more rigorous, transparent, and useful for real decisions. While we continue building advanced internal systems, we are sharing this pipeline so the community can learn, extend, and trust the foundations.

Visit tacitus.me for the broader vision, research, and product direction.

## One paragraph, non technical

You drop in text about a conflict. The pipeline extracts who is involved, what happened, and why it matters. It builds a structured graph so people can analyze power, incentives, and escalation risk in a consistent way. It is like a research assistant that converts raw narrative into a clear map you can reason over.

## For engineers and researchers

This pipeline is a Colab friendly, end to end workflow that:

- Ingests documents and splits them into manageable chunks
- Uses large language models to extract entities, events, and relationships
- Normalizes and resolves entity variants
- Builds a graph of actors, events, and theories
- Generates embeddings for semantic retrieval
- Exposes a foundation for downstream analysis and visualization

The design goal is reproducibility. Everything is structured, validated, and ready for iteration, with an emphasis on transparency over black box automation.

## What is in this repository

- `TACITUS_PIPELINE_Workbench_v8.ipynb` is the working notebook used for active development.
- `TACITUS_PIPELINE_NoOutput.ipynb` is a clean, shareable notebook for public use.
- `notebooks/` contains versioned notebooks.
- `REPO_REVIEW.md` contains review notes and technical observations.

## Run it on Colab

Colab notebook link for quick execution:

https://colab.research.google.com/drive/1lBcg0gfu6ok7whkz-InkzUUC7uQwxC24?usp=sharing

Recommended flow:

1. Open the notebook in Colab.
2. Set environment variables in a setup cell.
3. Run the blocks in order.

Example Colab setup cell:

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

## Configuration and customization

The pipeline reads all runtime configuration from environment variables so that credentials and model choices are never hardcoded. The key variables are:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`
- `GEMINI_MODEL`
- `EMBEDDING_MODEL`
- `EMBEDDING_DIMENSIONS`
- `TACITUS_CHUNK_SIZE`
- `TACITUS_CHUNK_OVERLAP`
- `TACITUS_ER_THRESHOLD`
- `TACITUS_DEFAULT_DATE`
- `TACITUS_DRY_RUN`

To customize behavior:

- Change chunk size and overlap to tune extraction granularity.
- Swap models by setting `GEMINI_MODEL` or `EMBEDDING_MODEL`.
- Adjust the entity resolution threshold for stricter or more permissive matching.
- Plug in a different graph backend by adapting the Neo4j sections.

## Architecture overview

```
[Documents] -> [Chunking] -> [Extraction] -> [Entity Resolution]
                     |                |
                     v                v
            [Embeddings]        [Graph Build]
                     \                /
                      \              /
                       -> [Search and Analysis]
```

## Open source stance

We are open sourcing a foundational part of our conflict analysis tooling so that the community can inspect, critique, and extend it. Some advanced capabilities remain internal while we continue development, but this pipeline captures the core mechanics that make TACITUS useful.

## Testing

This repository is notebook driven, so testing is mostly end to end:

- Run the full notebook in Colab.
- Verify that graph connectivity checks pass.
- Confirm that a sample document produces nodes, edges, and embeddings.

If you want automated checks, add a lightweight notebook validation step using `nbclient` or `papermill` in your own environment.

## Contributing

- Keep all secrets out of notebooks and docs.
- Prefer environment variables over inline values.
- Document changes to data schemas or extraction prompts clearly.
- Aim for readable explanations that are useful to researchers and engineers.

## ASCII signals

```
  T A C I T U S
  | | | | | | |
  | | | | | | | -> Conflict intelligence with accountability
```

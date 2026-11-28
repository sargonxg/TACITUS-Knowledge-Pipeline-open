# Reproduce the TACITUS Hugging Face context release

[GitHub pipeline](https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open) · [Hugging Face research profile](https://huggingface.co/Giuliocc)

This release packages the unchanged v2 source atlas and seven verified reading packets for public inspection. The builder copies exact source editions and retains the explicit absence of expert approval. It adds dataset-viewer rows, a release manifest and a standalone offline verifier. It makes zero inference calls.

From the repository root:

```sh
python research/hub-context-capsules/v1/build.py --output /tmp/tacitus-context-release
python /tmp/tacitus-context-release/verify.py
```

Existing output paths are refused. The source graph SHA-256 is fixed; a changed graph requires review and a new release. [Dataset card and scope](DATASET_CARD.md)

The public research dataset is separate from authenticated product storage and the App-import schema. It supplies no quality benchmark, trained model or customer approvals. The source extractor and packet compiler remain the authoritative upstream implementations.

## Publish the reviewed public research

Hub publication is pending. The connected publishing runner returned HTTP 402 without creating a job; browser sign-in was not completed. The source and verified bundle are available from this repository.

An authenticated maintainer can review `publish.py` and run it with UV using an existing Hugging Face publishing credential:

```sh
uv run research/hub-context-capsules/v1/publish.py --publish
```

The publisher verifies the `Giuliocc` account, rebuilds and verifies the pinned public dataset, refuses to overwrite an existing dataset and uses an exact parent commit for each Space update. It replaces only the three owned static research entry pages and their `app_file` metadata; models, datasets, source archives and immutable asset revisions remain available. The landing pages link to authenticated DOXA and Wind Tunnel. It performs no model inference.

If dataset publication succeeds but a Space changed concurrently, inspect the resulting commits before resuming with `--publish --spaces-only`. A conflict is a stop condition, not permission to replace another maintainer's work. Verify the Hub commits and rendered entries before updating product availability claims.

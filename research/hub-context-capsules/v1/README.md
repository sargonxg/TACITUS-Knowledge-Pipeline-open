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

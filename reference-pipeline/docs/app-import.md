# Bring source-linked context into the App

Add `--app-export` to a normal build. The command emits `app-bundle.json` and a PROV-O/SKOS lineage view in `standards.jsonld`. The six existing build outputs retain their formats.

The App package uses `tacitus-pipeline-import/1`. Its SHA-256 digest covers canonical UTF-8 JSON with sorted keys, excluding the top-level `sha256`. It contains the source collection, ontology, task layer, selected capsule and compiler receipt. Keep exact source text with its content hash and declared rights.

In the authenticated App Library, choose **Saved capsules → Import context graph**. Preview the records, then save. The App validates source hashes, quotations, ontology relationships, selected statements and required qualifications. It maps code-point spans to UTF-16 spans against the exact original text. It creates private source objects, a capsule and an artefact. Interpretations enter review as proposals.

The source/capsule/artefact save is one database transaction. Graph staging can resume using the same import when a request is interrupted. Repeating the same import in the same user scope reuses its saved versions. For a project import, explicitly select sharing in the preview to give project members the same versions. Private imports can be shared later through the App’s project-copy action.

The HTTP flow is a scoped `POST` to `/api/v2/profiles/{id}/pipeline-imports/preview` or its `projects` equivalent with `{ "bundle": ... }`. Commit to `/api/v2/profiles/{id}/pipeline-imports/{preview_id}/commit` with the same bundle. Preview does not save objects. Both requests require current authentication, scope access and the App’s origin protections.

The reference compiler supports larger local sources. App import currently accepts a bounded 512 KiB package with at most twelve sources, thirty-two entities and thirty-two statements. Each native source is limited to 64 KB. The mapped graph must fit the App’s 100-node/200-edge limit. Select a smaller task layer when these limits are exceeded.

## Selection and changes

Use `--selection bm25` for lexical passage matching or `--selection graph` for matching with up to two relationship hops. Required layer statements remain selected. `selection.json` records inclusion reasons and omitted statement IDs. The compiler still refuses a byte budget that cannot retain complete required evidence.

```sh
PYTHONPATH=src python -m tacitus_pipeline validate \
  --input examples/team-handoff/collection.json --ontology ontology/team-knowledge.json
PYTHONPATH=src python -m tacitus_pipeline diff --before path/to/earlier/collection.json --after path/to/later/collection.json
```

The diff identifies source edition changes and interpretations requiring review. Saved records retain their historical editions.

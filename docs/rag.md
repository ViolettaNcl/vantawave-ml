# VantaWave RAG

## Knowledge ingestion

Supported local document types:

- Markdown;
- text;
- reStructuredText.

Build a manifest:

```powershell
python scripts/build_knowledge_index.py docs
```

Output:

```text
artifacts/ai/knowledge_manifest.json
```

## Chunking

Documents are split into bounded text chunks while preserving:

- document ID;
- title;
- source path;
- character offsets;
- metadata.

## Retrieval

Default:

- TF-IDF unigram/bigram retrieval.

Optional:

- Sentence Transformers semantic embeddings.

The retrieved chunks are passed to the Security Analyst together with persisted
incident evidence.

## Citation discipline

Concrete findings are tied to citations.

The Analyst is instructed to say when evidence is insufficient rather than
fabricate missing network facts.

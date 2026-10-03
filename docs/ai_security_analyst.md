# AI Security Analyst

## Objective

The VantaWave Security Analyst converts persisted incident evidence and project
knowledge into a grounded, cited explanation.

It is intentionally not an autonomous offensive agent.

## Evidence sources

The analyst can use:

- persisted incident fields;
- persisted incident evidence;
- similar historical incidents;
- retrieved chunks from the VantaWave knowledge base.

Each source receives a stable citation such as:

- `[incident:abc123]`
- `[evidence:abc123]`
- `[document-id-0001]`

## Retrieval

The default retriever is local TF-IDF.

Advantages:

- no cloud dependency;
- deterministic;
- easy to test;
- safe for private project documentation.

An optional Sentence Transformers retriever can provide semantic embeddings.

Install:

```powershell
pip install -e ".[embeddings]"
```

## Grounded prompt contract

`build_grounded_prompt()` creates:

- a system instruction;
- a user question;
- an evidence block;
- an allow-list of valid citations.

The citation guard rejects references that were not supplied as evidence.

## Restricted agent

Allowed actions are read-only/defensive:

- summarize incident;
- retrieve project knowledge;
- compare historical incidents;
- suggest defensive checks;
- generate report;
- refresh read-only monitoring context.

Actions such as packet injection, brute force, credential theft, third-party
targeting and exploit execution are not permitted by the agent planner.

## API

```text
GET /ai/capabilities
GET /ai/analyze/{incident_id}
```

`/ai/analyze/{incident_id}` retrieves the persisted incident and history from
the database and uses configured knowledge paths.

Configure:

```powershell
$env:VANTAWAVE_KNOWLEDGE_PATHS="docs"
```

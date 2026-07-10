# Module Promotion Workflow

This document defines the reviewed promotion path from a private module candidate into the **Lumi Social Intelligence** release doorway.

No private candidate is exported by this document alone. Every real promotion still requires a human-reviewed audit report, a human-reviewed copy plan, an explicit apply command, and a passing release check.

## Airlock sequence

```text
Private candidate
  → read-only audit
  → review-only copy plan
  → explicit reviewed apply
  → doorway release check
  → human release review
```

The airlock exists so private development repositories can remain experimental while the release doorway only receives curated, public-safe files.

## 1. Prepare a private candidate

The candidate source directory should contain only files that are intended for public review. For the first real exports, prefer boring, low-risk surfaces:

- `README.md`
- `pyproject.toml`
- package skeleton files under `src/`
- synthetic tests under `tests/`
- synthetic examples or fixtures only

Do not include raw runs, private memories, diaries, chat logs, local runtime state, scheduler internals, credentials, chat IDs, private coordinates, or unreviewed generated artifacts.

## 2. Run the read-only audit

```bash
python3 scripts/audit_module_export.py \
  --module "Presence" \
  --source /path/to/private/presence-candidate \
  --report /tmp/presence-export-audit.json
```

Expected safe result:

```text
module export audit passed; report written to /tmp/presence-export-audit.json
```

Stop if the report status is `blocked` or if any `blocked_files` are present. Fix the private candidate first; do not hand-edit the audit result to make it pass.

## 3. Generate a review-only copy plan

```bash
python3 scripts/plan_module_export.py \
  --audit-report /tmp/presence-export-audit.json \
  --plan /tmp/presence-export-plan.json
```

Expected safe result:

```text
module export copy plan written to /tmp/presence-export-plan.json; no files copied
```

Review every `source` and `destination` operation before applying. The plan must remain non-mutating and must include:

- `status: ready_for_review`
- `would_copy: false`
- `requires_human_review: true`
- only expected `copy_operations`

## 4. Apply only after review

```bash
python3 scripts/apply_module_export.py \
  --plan /tmp/presence-export-plan.json \
  --apply-reviewed-plan
```

This is the only mutating step. The explicit flag is intentional: without `--apply-reviewed-plan`, the command must refuse to run.

The apply step copies only reviewed operations and writes `.lumi-export-manifest.json` beside the exported files.

## 5. Verify the doorway

After applying a reviewed plan, run the full release gate:

```bash
./scripts/release_check.sh
```

The release gate must pass before committing the promoted files.

## Stop conditions

Stop the promotion if any of these appear:

- audit status is not `pass`;
- audit report contains blocked files;
- copy plan points outside the expected release surface;
- plan contains unexpected source paths, runtime artifacts, generated runs, logs, or secrets;
- apply command would require changing safety guards;
- release check fails;
- the module's public story depends on private Autoresearch evidence or private runtime context.

## First real export recommendation

For the first actual module promotion, start with **Presence** and keep the export intentionally small: public README, package skeleton, synthetic examples, and synthetic tests only. Do not export private behavioral internals until the public surface and release gates are boringly reliable.

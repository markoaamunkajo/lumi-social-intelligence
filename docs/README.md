# Documentation

This directory contains the public-facing documentation for **Lumi Social Intelligence**.

## Start here

- [Product brief](product-brief.md) — concise product framing.
- [Architecture](architecture.md) — how **Lumi Layered Memory**, **Nuances**, and **Presence** work together.
- [Release boundary](release-boundary.md) — what may and may not enter the release repository.
- [Host compatibility](host-compatibility.md) — host-neutral contract and current adapter status.
- [Licensing](licensing.md) — code, documentation, and branding license model.
- [Release checklist](release-checklist.md) — pre-publication gate.
- [Module promotion workflow](module-promotion-workflow.md) — reviewed private-to-doorway airlock.
- [Module release gates](module-release-gates.json) — package names and fail-closed module promotion rules.

## Module export audit

Before promoting a private module candidate into `core/`, run the audit command in
read-only mode and review the JSON report:

```bash
python3 scripts/audit_module_export.py \
  --module "Presence" \
  --source /path/to/private/candidate \
  --report /tmp/presence-export-audit.json
```

The command does **not** copy files. It only compares the candidate tree against
`docs/module-release-gates.json` and blocks raw runs, private runtime state,
logs, secrets, and files outside the public export allowlist.

If the audit passes, generate a review-only copy plan:

```bash
python3 scripts/plan_module_export.py \
  --audit-report /tmp/presence-export-audit.json \
  --plan /tmp/presence-export-plan.json
```

The planner also does **not** copy files. It refuses blocked audit reports and
writes the exact source-to-destination operations for human review.

After reviewing the plan, apply it with the explicit mutation gate:

```bash
python3 scripts/apply_module_export.py \
  --plan /tmp/presence-export-plan.json \
  --apply-reviewed-plan
```

The apply command is the only mutating step. It refuses to run without
`--apply-reviewed-plan`, rejects unsafe path escapes, copies only the reviewed
plan operations, and writes `.lumi-export-manifest.json` beside the exported
module files.

## Naming rule

Public-facing docs should use the product names:

- **Lumi Layered Memory**
- **Nuances**
- **Presence**

Use folder names only when discussing repository paths.

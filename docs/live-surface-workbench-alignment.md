# Live Surface Workbench Alignment

Lumi Social Intelligence is the **public, governed Live Surface layer** for internal/private intelligence workbenches.

This repository should explain the review, confidence, consent, and export behavior that a host can implement. It should **not** publish confidential workbench assumptions, private research policies, customer/source data, local pack internals, or raw evidence.

## Public role

Lumi Social Intelligence owns the public contract for:

```text
Draft · Research · Review · Export · Help
```

These are user-facing surface modes, not engine-room implementation details.

| Surface mode | Public behavior | Boundary |
|---|---|---|
| **Draft** | Shape messy intent into reviewable candidate language. | Drafts remain provisional until reviewed. |
| **Research** | Describe the evidence needed and summarize reviewed source context. | Raw runs, scrape dumps, source graphs, and private ledgers stay outside this repository. |
| **Review** | Check claims, confidence, consent, tone, and export readiness. | Review cards are proposals, not automatic publication or memory promotion. |
| **Export** | Produce narrow, audience-labeled packets after review. | Export is explicit; no silent promotion from private workspaces to public claims. |
| **Help** | Explain what the surface can do and what it will not do. | Help should use product language, not host internals. |

## Engine-room terms stay out of normal UX

Normal users should not have to see or reason about implementation plumbing such as:

```text
models, queues, jobs, agents, packs, memory, source graph, scheduler IDs, chat IDs
```

Public examples, docs, and adapters should translate those concepts into the five surface modes above. Technical docs may mention adapters and release gates when needed, but user-facing examples should keep the surface calm and legible.

## Public/private split

Lumi Social Intelligence may publish:

- review-card schemas and examples;
- fail-closed behavior;
- confidence and consent boundaries;
- synthetic fixtures;
- public-safe release evidence;
- host-adapter contracts;
- export packet structure and labels.

Lumi Social Intelligence must not publish:

- confidential internal workbench workflows;
- private customer/support/source material;
- raw research runs or scrape dumps;
- local pack manifests or pack internals from private workspaces;
- unreviewed generated artifacts;
- private host runtime state, chat IDs, scheduler IDs, queues, credentials, tokens, or connection strings;
- public/customer claims that have not passed source and review checks.

## Promotion ladder

Public behavior should preserve this ladder:

```text
Evidence ≠ insight
Insight ≠ company truth
Company truth ≠ public claim
```

A reviewed export may summarize evidence for a specific audience, but it does not automatically become durable memory, team/company knowledge, or public marketing copy.

## Default export packet

Public-safe exports should be shaped as a narrow packet:

```text
summary.md
sources.md
claims.md
review.md
```

Each packet should declare:

- intended audience;
- review state;
- data sensitivity;
- unsupported claims removed or blocked;
- whether source evidence is synthetic, public, internal, confidential, or unavailable.

## Product principle

Do not extract value from people’s thinking space automatically.

That means private drafting, reactions, comments, and exploratory discussion are not company memory or public truth by default. Promotion requires explicit review, audience selection, and export intent.

## Implementation posture

This public repository defines the **contract**. Host runtimes and private workbenches implement the contract behind their own privacy and permission boundaries.

Good public examples are boring in the best way: synthetic, reviewable, fail-closed, and explicit about what they do **not** claim.

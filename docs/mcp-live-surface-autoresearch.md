# MCP × Live Surface autoresearch

**Status:** evidence-backed, review-only pilot seam
**Date:** 2026-07-13
**Scope:** make capability discovery feel immediate without making trust, connection,
authorization, invocation, memory, or external action implicit.

## Research question

How can Lumi make an MCP capability feel like a natural, low-friction Live Surface
option while preserving a clear, fail-closed separation between:

1. a capability *listing*;
2. explicit connection approval;
3. authorized and auditable invocation; and
4. separately governed side effects, memory, and public claims?

## External evidence

- MCP's [2025-11-25 specification](https://modelcontextprotocol.io/specification/2025-11-25)
  describes a JSON-RPC protocol with distinct host, client, and server roles. A
  listing is therefore not itself a connection or tool execution.
- The official [architecture overview](https://modelcontextprotocol.io/docs/learn/architecture)
  distinguishes tool discovery from tool execution and lifecycle management.
- The official [security guidance](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
  separately addresses confused-deputy risk, token passthrough, SSRF, session
  hijacking, local-server compromise, authorization-URL validation, and scope
  minimization. A friendly surface must not blur those boundaries.

## Local evidence

- `fast_promote.py` already validates a signed manifest before returning a
  metadata-only `listing_preview`, and rejects a failed signature/verifier/manifest
  without a preview.
- Its output is deliberately zero-side-effect: no user-context reads, tool
  invocations, scope grants, durable writes, external actions, or publications.
- `live_surface_controls.py` remains the review-gated natural-language seam;
  this pilot does not connect it to an MCP transport or Hermes configuration.

## Winning pilot: a verified capability review card

A successful Fast Promote preview now emits a small
`lumi.live_surface.mcp_capability_card.v1` card. It contains only the already-safe
listing material needed to answer *“what could this help with?”*:

- human-facing name, summary, category, example prompts, and labelled read/write
  operation types;
- the risk review lane and an explicit human-review requirement;
- one next step: `review_before_connection`; and
- visible gates that connection requires separate approval and invocation is not
  enabled by a listing preview.

The card intentionally excludes transport references, provider identifiers, raw
scopes, capability IDs, manifest identifiers, credentials, user/context payloads,
and any activation control. This is enforced before preview construction: every
card-emitted text field is rejected if it contains a manifest's raw identifier, a
logical reference, or a permission-shaped scope reference such as `mail.read`,
rather than relying on field omission or post-rendering redaction. Invalid
manifests emit no card.

### Why this is the friction win

The Live Surface can present a concrete useful option before users have to learn
MCP plumbing. The system still cannot quietly convert curiosity into a connection,
a scope grant, an invocation, a durable memory write, or an outward action. Nice
little velvet-rope UX: easy to approach, hard to accidentally wander backstage.

## Acceptance checks for this pilot

- [x] The card is emitted only after the existing signed-manifest validation pass.
- [x] The card is metadata/review-only and exposes explicit connection and
  invocation gates.
- [x] The card's safety counters remain all zero.
- [x] Raw transport, provider, scope, and logical-endpoint text are absent from
  the rendered card.
- [x] Invalid signatures produce neither `listing_preview` nor a Live Surface card.

## Deliberately not implemented

- MCP server registration, configuration, connection, OAuth, scope approval,
  tool discovery, tool invocation, persistence, external actions, publication,
  or gateway restart.
- Any automatic promotion from a card into a connected capability.
- Any inference that an MCP server, even a local one, is trusted merely because it
  is discoverable.

## Next research, before any activation work

1. Usability-test the card copy with three representative capability categories
   (read-only context, local creative tooling, and external-action tooling), using
   anonymized fixtures only.
2. Define a separate explicit-connection review record: identity/provenance,
   scoped approval, expiry, revocation, audit receipt, and a no-write dry-run.
3. Keep tool invocation as its own later capability with per-call review context,
   output minimization, and an external-action boundary.

# Fast Promote to Live Surface

**Fast Promote** is a governed shortcut to a **metadata-only Live Surface listing preview**. It turns a reviewed, versioned manifest with a cryptographically verified detached signature into a consistent catalogue candidate and routes that candidate to the appropriate review level.

It is not a connection button, an MCP trust grant, or a permission escalator.

## What this implementation does

The contract validates these manifest declarations before making a preview:

- app identity, publisher ownership/provenance, semantic version, and detached-signature envelope;
- purpose, selected capabilities, declared scopes, and a managed logical MCP transport reference (never a hostname, port, or URL);
- input/output classifications, connection consent, retention/export terms, and rate limit;
- memory authority, trust/review status, revocation/disable path, and effect declarations.

A successful preview contains only public-facing listing metadata, a manifest fingerprint, review route, and zero-side-effect counters. Public listing text is rejected when it contains credential/data markers or transport syntax. A preview never includes a raw transport reference, scope list, input example, user/context payload, credential, endpoint, connection state, or tool result. The caller must provide the trusted-key signature verifier; no verifier or failed verification fails closed without a listing.

## Lifecycle boundaries

| Lifecycle step | This implementation | Separate future gate |
| --- | --- | --- |
| **Promote** | Validates a reviewed manifest and makes a metadata-only preview. | Human review decides whether to list it. |
| **Connect** | Declares that explicit approval is required. | Identity, scope, purpose, retention, and export approval. |
| **Invoke** | Declares that listing does not enable invocation. | Gateway-side per-tool authorization, minimization, provenance, rate limits, audit, and revocation. |
| **Act / publish** | Declares independent gates. | Independent approval for external writes, durable memory, and public claims. |

MCP is a capability transport declaration only. It does not supply consent, public publication, identity trust, authorization, memory authority, or an app’s social judgement.

## Review routing

- **Low risk**: read-only, explicit-user-input-only, only the allowlisted `thread.user_selected.read` scope, minimized ephemeral output, no retention/export, no durable memory, no effects. Route: `expedited_readonly_review`.
- **Sensitive**: identity-sensitive, explicit-location, third-party, broader-scope, or extended-retention/output handling. Route: `stronger_review_required`.
- **High**: a write/action capability, any external effect, durable-memory authority/write, or public-claim effect. Route: `stronger_review_required`.

Even a valid high-risk manifest may only produce a metadata preview. It cannot connect, invoke, write, remember, or publish through this contract.

## First-pilot shape

A suitable first pilot is a read-only `summarize_user_selected_thread` capability that receives only text a person explicitly selected, produces an ephemeral/minimized summary, retains nothing, exports nothing, writes no durable memory, and prepares no external action beyond review.

The following remain intentionally out of scope: broad inbox/DM/social-feed ingestion, background monitoring, relationship scoring, autonomous replies/posts, raw export, device-location inference, silent durable-memory writes, and unreviewed public claims.

> Evidence is not insight; insight is not company truth; company truth is not a public claim.

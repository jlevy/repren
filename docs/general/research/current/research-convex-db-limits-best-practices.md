# Research Brief: Convex Database Limits, Best Practices, and Workarounds

**Last Updated**: 2026-01-09

**Status**: Complete (reviewed January 2026; updated 2026-01-09 with source code
verification and cross-references)

**Legend**:

| Symbol | Meaning |
| --- | --- |
| ✅ | **Verified** - Confirmed against official Convex documentation |
| ⚠️ | **Unverified** - Not confirmed in recent documentation review; may need manual check |
| 📝 | **Anecdotal** - From production experience; not explicitly documented |
| 🔒 | **Hard Limit** - Cannot be changed regardless of plan |
| 🔄 | **Soft Limit** - Can be increased for Professional plan customers (contact support) |
| ❌ | **Not Allowed** - Operation is prohibited or not supported |
| 🔍 | **Undocumented/Discrepancy** - Not in official Convex docs, or source code differs from docs |
| 🛠️ | **Configurable** - Can be changed via environment variable for self-hosted deployments |

**Notation**: Combinations like “✅ 🔒” mean “Verified Hard Limit”

**Related Research**:

- [research-convex-backend-limits-implementation.md](../../../project/research/current/research-convex-backend-limits-implementation.md)
  — Deep dive into source code implementation of limits and configurability for
  self-hosted deployments

* * *

## Executive Summary

Convex enforces a comprehensive set of platform-level limits designed to protect service
stability and ensure predictable performance.
Understanding these limits and their implications is critical for building scalable
applications that avoid runtime errors, performance degradation, and cost overruns.

This document provides a complete reference of Convex’s limits (as of January 2026),
explains the technical constraints behind them, and documents proven workarounds and
best practices. Key topics include: transaction read/write limits (8 MiB cap), document
size constraints (1 MiB max), concurrency quotas, indexing strategies, pagination
patterns, optimistic concurrency control (OCC), and the official Aggregate Component for
maintaining statistics at scale.

**Key Takeaway**: Applications can scale to substantial workloads within Convex by
combining official best practices—selective indexes, pagination, aggregate components,
bounded queries, proper namespacing, and scheduled jobs—with proactive monitoring of
storage and bandwidth quotas.

* * *

## Research Methodology

### Approach

This research synthesizes information from:

1. **Official Documentation Review**: Convex Developer Hub “Limits” page (updated
   October 2025), covering database, function, transaction, and search quotas

2. **Community Best Practices**: Stack Convex articles including “Queries that Scale”
   (February 2024) for practical pagination and indexing guidance

3. **Component Documentation**: Convex Aggregate Component README (November 2025 update)
   detailing interaction with transaction limits and OCC behavior

4. **Real-World Application**: Analysis of common patterns, pitfalls, and production
   scenarios encountered when building scalable applications

### Primary Sources

- [Convex Production Limits](https://docs.convex.dev/production/state/limits) — Official
  limits documentation

- [Convex Best Practices](https://docs.convex.dev/understanding/best-practices) —
  Official best practices guide

- [Indexes and Query Performance](https://docs.convex.dev/database/reading-data/indexes)
  — Index optimization guide

- [Pagination Guide](https://docs.convex.dev/database/pagination) — Official pagination
  patterns

- [Queries that Scale](https://stack.convex.dev/queries-that-scale) — Community best
  practices

- [Convex Aggregate Component](https://github.com/get-convex/aggregate) — Official
  aggregation library

- [Convex Helpers](https://github.com/get-convex/convex-helpers) — Additional utilities
  for pagination and queries

* * *

## Core Limits Reference

### 1. Transaction Read/Write Limits

**Hard Limits (per function invocation)** ✅ 🔒:

| Limit Type | Documented Value | Source Code Default | Status |
| --- | --- | --- | --- |
| **Maximum data read** | 8 MiB per query/mutation | 16 MiB | ✅ 🔒 🔍 🛠️ |
| **Maximum documents scanned** | 16,384 documents per query/mutation | 32,000 | ✅ 🔒 🔍 🛠️ |
| **Maximum data written** | 8 MiB per mutation | 16 MiB | ✅ 🔒 🔍 🛠️ |
| **Maximum documents written** | 8,192 documents per mutation | 16,000 | ✅ 🔒 🔍 🛠️ |
| **Maximum db.get/db.query calls** | 4,096 per transaction | 4,096 | ✅ 🔒 🛠️ |

**🔍 Source Code vs Documentation Discrepancy**:

The source code defaults in `crates/common/src/knobs.rs` are **2x more permissive** than
documented limits:

- `TRANSACTION_MAX_READ_SIZE_BYTES`: 16 MiB (line 355-357)
- `TRANSACTION_MAX_READ_SIZE_ROWS`: 32,000 (line 351-352)
- `TRANSACTION_MAX_USER_WRITE_SIZE_BYTES`: 16 MiB (line 212-214)
- `TRANSACTION_MAX_NUM_USER_WRITES`: 16,000 (line 208-209)
- `TRANSACTION_MAX_READ_SET_INTERVALS`: 4,096 (line 360-361)

**Why the discrepancy?** Convex Cloud likely enforces stricter limits for free/starter
plans while the codebase supports higher values for professional/enterprise customers
and self-hosted deployments.

**🛠️ Self-Hosted Configuration**:

For self-hosted deployments, these limits can be adjusted via environment variables:

```bash
export TRANSACTION_MAX_READ_SIZE_BYTES=33554432  # 32 MiB
export TRANSACTION_MAX_READ_SIZE_ROWS=64000
export TRANSACTION_MAX_NUM_USER_WRITES=32000
export TRANSACTION_MAX_USER_WRITE_SIZE_BYTES=33554432  # 32 MiB
```

**Key Constraint**: The read limit includes **all scanned document bytes**, not just
returned results.
Convex does not support field projection—reading any document reads the
entire document.

**Error Manifestation**: `"transaction exceeded resource limits"` runtime error

**Common Causes**:

- Using `.collect()` on large result sets without pagination

- Scanning tables with large document sizes (e.g., documents approaching the 1 MiB
  limit)

- Counting operations that scan many large documents (even with `.take(limit)`)

- Post-index filtering with `.filter()` instead of using composite indexes

**Sources**:

- [Convex Limits - Database](https://docs.convex.dev/production/state/limits)
- Source: `crates/common/src/knobs.rs:208-214, 351-361`

### 2. Document Size and Structure Limits

**Hard Limits (per document)** ✅ 🔒:

| Limit | Value | Source Location | Status |
| --- | --- | --- | --- |
| **Maximum document size** | 1 MiB (1,048,576 bytes) | `crates/common/src/document.rs:101` | ✅ 🔒 |
| **Maximum fields per document** | 1,024 fields | `crates/value/src/object.rs:30` | ✅ 🔒 |
| **Maximum nesting depth (user)** | 16 levels | `crates/common/src/document.rs:102` | ✅ 🔒 |
| **Maximum nesting depth (system)** | 64 levels | `crates/value/src/size.rs:8` | ✅ 🔒 |
| **Maximum array elements** | 8,192 elements per array | `crates/value/src/array.rs:26` | ✅ 🔒 |
| **Maximum field name length** | 1,024 characters | `crates/sync_types/src/identifier.rs:124` | ✅ 🔒 🔍 |
| **Maximum identifier length** | 64 characters | `crates/sync_types/src/identifier.rs:10` | ✅ 🔒 |

**🔍 Note on Field Name vs Identifier Length**:

The docs say 64 characters for field names, but source code shows **1,024 characters**
for field names (`MAX_FIELD_NAME_LENGTH`) vs **64 characters** for identifiers like
table names (`MAX_IDENTIFIER_LEN`). These are different limits.

**Key Constraints**:

- Field names must be nonempty and cannot start with `$` or `_` (reserved for system
  fields)

- Only “plain old JavaScript objects” are supported (no custom prototypes)

- Strings are stored as UTF-8 and must be valid Unicode sequences

- System fields (`_id`, `_creationTime`) are automatically added and count toward limits

- **These limits are hard-coded** and cannot be changed via configuration—modifying them
  requires code changes to the value serialization layer

**Common Causes of Issues**:

- Storing large text fields (e.g., LLM conversation content, full API responses) in
  documents used for listing/counting

- Deeply nested object structures from external APIs

- Large arrays of embedded objects

- **Returning large query result arrays** - Queries that return >8,192 documents will
  fail even if total data size is under 8 MiB

**Note on 8,192 Array Element Limit**: This limit applies to:

1. Arrays **within** documents (e.g., `tags: string[]`)

2. Arrays **returned** by query functions (the result set itself)

For query results, set explicit limits <8,000 to account for overhead:

```typescript
// SAFE: Explicit limit under 8,192 with margin
const events = await ctx.db.query('events').take(8000);

// DANGEROUS: Could return >8,192 results
const events = await ctx.db.query('events').collect();
```

**Sources**:

- [Convex Limits - Document Size](https://docs.convex.dev/production/state/limits)

### 3. Concurrency and Execution Limits

**Concurrent Execution Limits** ✅ 🔄 🛠️:

| Resource Type | Default (Code) | Source Location | Status |
| --- | --- | --- | --- |
| **Queries** | 16 concurrent | `crates/common/src/knobs.rs:768-773` | ✅ 🔄 🛠️ |
| **Mutations** | 16 concurrent | `crates/common/src/knobs.rs:781-786` | ✅ 🔄 🛠️ |
| **V8 Actions** | 16 concurrent | `crates/common/src/knobs.rs:802-807` | ✅ 🔄 🛠️ |
| **Node Actions** | 16 concurrent | `crates/common/src/knobs.rs:818-823` | ✅ 🔄 🛠️ |
| **HTTP Actions** | 16 concurrent | `crates/common/src/knobs.rs:832-841` | ✅ 🔄 🛠️ |
| **Scheduled Job Parallelism** | 10 concurrent | `crates/common/src/knobs.rs:281-282` | ✅ 🔄 🛠️ |

**🔍 Note on Concurrency Defaults**:

The source code base constant `DEFAULT_APPLICATION_MAX_FUNCTION_CONCURRENCY` is **16**
for all function types.
Convex Cloud overrides these via a “big brain” service for Professional plan customers
(256 queries/mutations, 1000 Node actions, etc.).

**🛠️ Self-Hosted Configuration**:

```bash
export APPLICATION_MAX_CONCURRENT_QUERIES=64
export APPLICATION_MAX_CONCURRENT_MUTATIONS=64
export APPLICATION_MAX_CONCURRENT_V8_ACTIONS=64
export APPLICATION_MAX_CONCURRENT_NODE_ACTIONS=64
export APPLICATION_MAX_CONCURRENT_HTTP_ACTIONS=64
export SCHEDULED_JOB_EXECUTION_PARALLELISM=20
```

*Note: Professional plan limits (256, 1000, etc.)
are enforced by Convex Cloud’s “big brain” service, not by these code defaults.*

**Execution Time Limits** ✅ 🔒 🛠️:

| Limit | Value | Source Location | Status |
| --- | --- | --- | --- |
| **Query/Mutation user timeout** | 1 second | `crates/common/src/knobs.rs:692-693` | ✅ 🔒 🛠️ |
| **Query/Mutation system timeout** | 15 seconds | `crates/common/src/knobs.rs:703-704` | ✅ 🔒 🛠️ |
| **Action timeout** | 10 minutes (600s) | `crates/common/src/knobs.rs:119-120` | ✅ 🔒 🛠️ |
| **V8 action system timeout** | 5 minutes (300s) | `crates/common/src/knobs.rs:745-746` | ✅ 🔒 🛠️ |

**Scheduled Functions** ✅ 🔒 🛠️:

| Limit | Value | Source Location | Status |
| --- | --- | --- | --- |
| **Max scheduled per mutation** | 1,000 | `crates/common/src/knobs.rs:254-255` | ✅ 🔒 🛠️ |
| **Total scheduled args** | 16 MiB | `crates/common/src/knobs.rs:269-275` | ✅ 🔒 🛠️ 🔍 |

**🔍 Note**: The source code default for scheduled args is **16 MiB**, not 8 MiB as
sometimes documented.
Variable: `TRANSACTION_MAX_SCHEDULED_TOTAL_ARGUMENT_SIZE_BYTES`

**Key Constraints**:

- Professional customers can request higher Node action concurrency (>1,000) if needed

- Concurrency limits are per-deployment

- Execution time limits cannot be increased

**Common Issues**:

- Dashboard queries that scan large datasets monopolizing query slots

- Long-running data processing in queries/mutations instead of actions

- Recursive scheduling hitting the 1,000 function limit

**Sources**:

- [Convex Limits - Concurrency](https://docs.convex.dev/production/state/limits)

**Important Notes on Action Timeouts**:

Actions have a hard 10-minute (600-second) timeout that cannot be extended.
For operations that may exceed this limit:

1. **Sampling Strategy**: Process a representative subset of data instead of the entire
   dataset

   - Example: Validate first 100,000 records instead of all records

   - Mark results as “sampled” to indicate incomplete coverage

2. **Resumable Pattern**: Store progress in a database table and resume from last
   checkpoint

   - Use a state table to track:
     `{ operation: string, lastCursor: string, completed: boolean }`

   - Each action invocation processes a batch and updates the state

   - Trigger next batch via scheduled function or manual invocation

3. **Scheduled Functions**: Break large operations into smaller cron jobs

   - Schedule multiple functions to run sequentially

   - Each function processes a manageable chunk within timeout

4. **Optimize Efficiency**: Reduce round-trips and increase batch sizes

   - Use larger `numItems` in pagination (up to database limits)

   - Batch multiple operations within single queries/mutations

   - Minimize logging and console output

### 3.1 Logging Limits

**Limit** ✅ 🔒 🔍: 256 log lines per function execution

**Source Code Verification**: `MAX_LOG_LINES: usize = 256` in
`crates/isolate/src/environment/helpers/mod.rs:29`

This limit is not documented in official Convex docs but is verified in source code.

**Applies To**: All function types (queries, mutations, actions, HTTP actions)

**Error Manifestation**: Logs are silently truncated after 256 lines; no error is thrown

**Common Causes**:

- Verbose progress logging in long-running operations (e.g., logging every page during
  pagination)

- Debug logging in loops that process many items

- Excessive error logging when retrying operations

**Workarounds**:

1. **Log Strategically**: Only log major milestones, not every iteration
   ```typescript
   // Bad: Logs 1000+ times for large datasets
   for (let i = 0; i < items.length; i++) {
     console.log(`Processing item ${i}`);
   }
   
   // Good: Logs ~10 times for same dataset
   for (let i = 0; i < items.length; i++) {
     if (i % 100 === 0) {
       console.log(`Progress: ${i}/${items.length} items processed`);
     }
   }
   ```

2. **Use Log Levels**: Reserve `console.log` for important milestones, use structured
   logging for details

3. **External Logging**: For detailed trace logging, send events to external logging
   services (Datadog, Sentry, etc.)

4. **Return Data Instead**: For validation/analysis, return results in function return
   value instead of logging

**Best Practice for Long-Running Actions**:

- Log start, completion, and every N iterations (where N × iterations < 256)

- Example: For 1000+ pages, log every 100 pages = ~10 logs total

- Always log final summary with totals

**Sources**:

- Production experience and testing (limit not explicitly documented in official docs)

### 3.2 Action Memory Limits

**Limits (per action invocation)** ✅ 🔄 🛠️:

| Runtime | Memory Limit | Source Location | Cold Start | Status |
| --- | --- | --- | --- | --- |
| **Convex Runtime** (default) | 64 MB | `crates/common/src/knobs.rs:849-850` | Faster (no cold start) | ✅ 🔄 🛠️ |
| **Node.js Runtime (static)** | 512 MB | `crates/common/src/knobs.rs:1119-1120` | Slower (cold start possible) | ✅ 🔄 🛠️ |
| **Node.js Runtime (dynamic)** | 4,096 MB | `crates/common/src/knobs.rs:1130-1131` | Build/analyze only | ✅ 🔄 🛠️ |

**🛠️ Self-Hosted Configuration**:

For self-hosted deployments, memory limits can be adjusted via environment variables:

```bash
export ISOLATE_MAX_USER_HEAP_SIZE=134217728        # 128 MB for V8 (default 64 MB)
export ISOLATE_MAX_HEAP_EXTRA_SIZE=67108864        # 64 MB extra (default 32 MB)
export AWS_STATIC_LAMBDA_MEMORY_LIMIT_MB=1024     # 1 GB for Node.js (default 512 MB)
```

**Key Constraints**:

- **Default runtime is Convex Runtime** with 64 MB limit—actions without `"use node";`
  directive run here

- **Node.js runtime requires explicit opt-in** via `"use node";` directive at file top

- **Node.js actions have lower argument size limit**: 5 MiB instead of 8 MiB

- **Node.js versions supported**: 20 and 22 (configurable in `convex.json`)

- **File-level directive**: The `"use node";` directive applies to the entire file—you
  cannot mix runtimes in a single file

- **No queries/mutations in Node.js files**: Files with `"use node";` can only contain
  actions, not queries or mutations

**Error Manifestation**:
`"JavaScript execution ran out of memory (maximum memory usage: 64 MB)"` for Convex
runtime, similar for Node.js at 512 MB

**Common Causes**:

- Processing large API responses or JSON payloads in memory

- Building large data structures for LLM context

- Parsing or transforming large documents

- Memory leaks from accumulating data in loops

**Workaround**: Add `"use node";` directive to switch from 64 MB to 512 MB limit:

```typescript
"use node";

import { internalAction } from "./_generated/server";

export const memoryIntensiveAction = internalAction({
  handler: async (ctx, args) => {
    // Now has 512 MB memory limit instead of 64 MB
    const largeData = await fetchLargePayload();
    return processData(largeData);
  },
});
```

**Trade-offs of Node.js Runtime**:

| Aspect | Convex Runtime | Node.js Runtime |
| --- | --- | --- |
| Memory | 64 MB | 512 MB |
| Cold starts | None | Possible |
| Argument size | 8 MiB | 5 MiB |
| NPM packages | Limited (fetch-based) | Full Node.js ecosystem |
| Performance | Faster startup | Slower startup |

**Best Practice**: Start with Convex runtime (default) for simple actions.
Switch to Node.js runtime only when you need:

- More than 64 MB memory

- Node.js-specific NPM packages

- Node.js APIs not available in Convex runtime

**Limit Configurability**:

These memory limits are **hard limits by default** but can be increased for Professional
plan customers on a case-by-case basis:

| Plan | Default Limits | Can Request Increase? |
| --- | --- | --- |
| **Starter** (Free) | 64 MB / 512 MB | No |
| **Professional** ($25/member/mo) | 64 MB / 512 MB | Yes, contact support |
| **Enterprise** (coming soon) | TBD | Likely customizable |

To request a limit increase, Professional customers can send a support message through
the Convex dashboard or email mailto:support@convex.dev.
Per the docs: “Limits can be lifted for Professional plan customers on a case-by-case
basis … Usually this is only needed if your product has highly bursty traffic.”

**Sources**:

- [Convex Runtimes](https://docs.convex.dev/functions/runtimes) — Runtime comparison and
  `"use node";` directive

- [Convex Actions](https://docs.convex.dev/functions/actions) — Action limits and
  runtime selection

- [Convex Limits](https://docs.convex.dev/production/state/limits) — Official limits
  documentation

- [Convex Contact](https://docs.convex.dev/production/contact) — Support contact for
  limit increases (support@convex.dev)

### 4. Storage and Bandwidth Quotas

*Note: Storage quotas and pricing change periodically.
Verify current values at [Convex Pricing](https://www.convex.dev/pricing).*

**Database Storage** ⚠️ 🔄:

| Plan | Included Storage | Bandwidth/Month | Status |
| --- | --- | --- | --- |
| **Starter** | 0.5 GiB | 1 GiB | ⚠️ 🔄 |
| **Professional** | ~1 GiB+ (verify pricing page) | ~50 GiB (verify) | ⚠️ 🔄 |

*Recent changes (late 2025): Convex updated their pricing model.
Pro plan now includes 1 GB at $0.50/GB/month overage (down from previous $10/GB). Check
official pricing.*

**File Storage** ⚠️ 🔄:

| Plan | Included Storage | Bandwidth/Month | Status |
| --- | --- | --- | --- |
| **Starter** | 1 GiB | 1 GiB | ⚠️ 🔄 |
| **Professional** | (verify pricing page) | (verify) | ⚠️ 🔄 |

**Key Constraints**:

- Database storage includes all tables **and indexes** (indexes are not free)

- Bandwidth includes data transfer for queries, mutations, and file downloads

- Backups consume file storage bandwidth

**Common Issues**:

- Underestimating index storage overhead (especially on large tables)

- Retaining historical data indefinitely without archival strategy

- High-frequency queries on large result sets consuming bandwidth

**Sources**:

- [Convex Limits - Storage](https://docs.convex.dev/production/state/limits)

### 5. Index and Schema Limits

**Index Limits (per table)** ✅ 🔒:

| Limit | Documented | Source Code | Source Location | Status |
| --- | --- | --- | --- | --- |
| **Maximum indexes per table** | 32 | **64** | `crates/common/src/schemas/mod.rs:64` | ✅ 🔒 🔍 |
| **Maximum fields per index** | 16 | 16 | `crates/common/src/bootstrap_model/index/mod.rs:42` | ✅ 🔒 |
| **Maximum index name length** | 64 chars | 64 chars | `crates/sync_types/src/identifier.rs:10` | ✅ 🔒 |

**🔍 Index Count Discrepancy**:

The source code constant `MAX_INDEXES_PER_TABLE` is **64**, not 32 as documented.
This is the total across all index types (database indexes, text indexes, and vector
indexes).

**Schema Limits (per deployment)** ✅ 🔒:

| Limit | Value | Source Location | Status |
| --- | --- | --- | --- |
| **Maximum tables** | 10,000 | `crates/database/src/bootstrap_model/table.rs:62` | ✅ 🔒 |
| **Maximum user modules** | 4,096 | `crates/common/src/knobs.rs:1329-1330` | ✅ 🔒 🛠️ |

**Full-Text Search Indexes** ✅ 🔒:

| Limit | Value | Source Location | Status |
| --- | --- | --- | --- |
| **Maximum full-text indexes per table** | 4 | Docs (within 64 total) | ✅ 🔒 |
| **Maximum filters per full-text index** | 16 | `crates/common/src/bootstrap_model/index/mod.rs:43` | ✅ 🔒 |
| **Maximum results per query** | 1,024 | `crates/search/src/constants.rs:18` | ✅ 🔒 |

**Vector Search Indexes** ✅ 🔒:

| Limit | Value | Source Location | Status |
| --- | --- | --- | --- |
| **Maximum vector indexes per table** | 4 | Docs (within 64 total) | ✅ 🔒 |
| **Maximum filters per vector index** | 16 | `crates/common/src/bootstrap_model/index/mod.rs:44` | ✅ 🔒 |
| **Maximum dimensions** | 4,096 | `crates/common/src/bootstrap_model/index/vector_index/dimensions.rs:6` | ✅ 🔒 |
| **Maximum results per query** | 256 (default 10) | `crates/vector/src/lib.rs:64` | ✅ 🔒 |
| **Maximum indexed documents** | 100,000 per vector index | Docs | ✅ 🔒 |

**Key Constraints**:

- Index fields must be queried in the same order they are defined

- To query `field1` then `field2` AND `field2` then `field1`, you need two separate
  indexes

- Indexes add overhead during document insertion

- All index types (database, text, vector) share the 64 total indexes per table limit

**Sources**:

- [Convex Limits - Indexes](https://docs.convex.dev/production/state/limits)
- Source: `crates/common/src/schemas/mod.rs`,
  `crates/common/src/bootstrap_model/index/mod.rs`

### 6. Function and Code Limits

**Function Invocation Limits** ✅ 🔄:

| Resource | Starter Plan | Professional Plan | Status |
| --- | --- | --- | --- |
| **Function Calls/Month** | 1,000,000 | 25,000,000 | ✅ 🔄 |
| **Action Execution** | 20 GiB-hours | 250 GiB-hours | ⚠️ 🔄 |

**Code and Argument Limits** ⚠️ 🔒:

- **Maximum deployment code size**: 32 MiB ⚠️ (not verified in recent search)

- **Maximum argument size**: 8 MiB per function call ✅ (Convex Runtime); 5 MiB (Node.js)

- **Maximum return value size**: 8 MiB per function call ✅

**Team Limits** ✅ 🔄:

- **Starter**: 1–6 developers ✅

- **Professional**: Up to 25 developers per month ⚠️

**Environment Variables** ✅ 🔒:

| Limit | Documented | Source Code | Source Location | Status |
| --- | --- | --- | --- | --- |
| **Maximum environment variables** | 100 | **1,000** | `crates/common/src/knobs.rs:1537-1538` | ✅ 🔒 🔍 🛠️ |
| **Maximum variable name length** | 40 chars | 40 chars | `crates/common/src/types/environment_variables.rs:66` | ✅ 🔒 |
| **Maximum variable value length** | N/A | 8,192 bytes | `crates/common/src/types/environment_variables.rs:69` | ✅ 🔒 |

**🔍 Env Var Count Discrepancy**:

The source code default `ENV_VAR_LIMIT` is **1,000**, not 100 as documented.
This is configurable via the `ENV_VAR_LIMIT` environment variable for self-hosted
deployments.

**Sources**:

- [Convex Limits - Functions](https://docs.convex.dev/production/state/limits)
- Source: `crates/common/src/knobs.rs:1537-1538`,
  `crates/common/src/types/environment_variables.rs`

### 7. Runtime Architecture and Isolation Model

Understanding how Convex executes functions is critical for designing concurrent
workloads like experiments running multiple agent threads.

#### 7.1 V8 Isolate Architecture ✅

Convex uses **V8 JavaScript isolates** rather than containerized serverless functions
(like AWS Lambda). This provides:

- **Fast cold starts**: ~10ms to spin up an isolate vs 500ms–10s for Lambda

- **Low-latency database I/O**: No network hop between function and database

- **Memory isolation**: Each isolate has completely isolated memory

**Key constraint**: V8 has a limit of 128 threads per process, which led Convex to
create the Funrun service for horizontal scaling (see below).

**Sources**:

- [How We Horizontally Scaled Function Execution](https://stack.convex.dev/horizontally-scaling-functions)

- [How Convex Works](https://stack.convex.dev/how-convex-works)

#### 7.2 Function Execution Model ✅

**Per-invocation isolation**:

| Aspect | Behavior | Status |
| --- | --- | --- |
| **Memory per invocation** | 64 MB (Convex Runtime) or 512 MB (Node.js) | ✅ |
| **Isolate reuse** | Isolates reused only for same backend; contexts never reused between requests | ✅ |
| **Security boundary** | Fresh isolate context per request for security | ✅ |

**What this means for concurrent experiments**:

When you run an experiment with multiple threads, each calling actions/mutations:

1. **Each action invocation gets its own isolate context** with its own memory limit (64
   MB or 512 MB depending on runtime)

2. **Memory limits are per-invocation, not shared** - Thread A’s action using 50 MB
   doesn’t reduce Thread B’s available memory

3. **Isolates are pooled within the backend** - The scheduler picks an existing isolate
   from the same backend when possible, otherwise creates new

4. **Each `ctx.runAction()` call is a separate invocation** - Calling runAction creates
   a new function invocation with its own memory quota

#### 7.3 Funrun: Horizontal Scaling Service ✅

Before Funrun (pre-March 2024):

- Functions ran inside the backend process in V8 isolates

- Limited to 128 concurrent threads per deployment

- Scaling was constrained by V8’s threading model

After Funrun (March 2024+):

- Function execution is a separate multi-tenant service ("Funrun")

- Backend sends function requests to any Funrun instance

- Funrun executes, returns results to backend for conflict checking

- **Professional customers can run 10x more concurrent functions**

**Architecture diagram** (simplified):

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │────▶│   Backend    │────▶│   Funrun     │
│  (your app)  │     │  (per-deploy)│     │ (multi-tenant)│
└──────────────┘     └──────────────┘     └──────────────┘
                            │                    │
                            ▼                    ▼
                     ┌──────────────┐     ┌──────────────┐
                     │  Database    │     │ V8 Isolates  │
                     │  (commits)   │     │ (execution)  │
                     └──────────────┘     └──────────────┘
```

**Sources**:

- [How We Horizontally Scaled Function Execution](https://stack.convex.dev/horizontally-scaling-functions)

#### 7.4 Local Development vs Cloud vs Self-Hosted ✅

| Deployment Mode | Architecture | Memory Limits | Scaling |
| --- | --- | --- | --- |
| **Local (`npx convex dev`)** | Backend runs as subprocess, SQLite storage | Same 64/512 MB limits | Single process, V8 threading limits |
| **Cloud (Convex Cloud)** | Funrun service, managed infrastructure | Same 64/512 MB limits | Horizontal scaling via Funrun |
| **Self-Hosted** | Same OSS code as cloud, single machine by default | Same 64/512 MB limits | Single machine unless you modify Funrun |

**Key insight**: Memory limits (64 MB / 512 MB) are enforced at the V8 isolate level, so
they apply **identically** across all deployment modes.
The difference is in concurrency scaling, not per-function memory.

**Local development specifics**:

- Backend runs as subprocess of `npx convex dev`

- Database stored locally (SQLite by default)

- Function calls don’t count against cloud quotas

- Same isolation model, just running locally

**Self-hosted specifics**:

- Same open-source code as cloud service

- By default, runs on single machine (no Funrun scaling)

- Can be modified to scale horizontally

**Sources**:

- [Local Deployments for Development](https://docs.convex.dev/cli/local-deployments)

- [Self-Hosting with Convex](https://stack.convex.dev/self-hosted-develop-and-deploy)

- [Self-Hosting Documentation](https://docs.convex.dev/self-hosting)

#### 7.5 Implications for Multi-Threaded Experiments 📝

When running experiments with multiple concurrent agent threads:

1. **Each action invocation is independent** - Memory limits apply per-action, not
   shared across your experiment threads

2. **Concurrency limits matter more than memory** - On Starter plan, you’re limited to
   ~~64 concurrent actions; Professional gets ~~256+ with Funrun scaling

3. **OCC conflicts are the bigger concern** - Multiple threads writing to the same
   documents will cause retry loops (see Pitfall 5)

4. **Scheduled functions have separate limits** - If you schedule many functions from
   one mutation, you hit the 1,000 function / 8 MiB argument limit per mutation

**Practical example**:

Running 10 agent threads, each doing parallel actions:

```
Thread 1 ─▶ Action (64 MB isolate) ─▶ Query + Mutation
Thread 2 ─▶ Action (64 MB isolate) ─▶ Query + Mutation
...
Thread 10 ─▶ Action (64 MB isolate) ─▶ Query + Mutation
```

Each thread’s action has its own 64 MB (or 512 MB if `"use node";`). They don’t share
memory. But they do compete for:

- Concurrency slots (Professional: 256 actions)

- Database OCC (if writing same documents)

- Function call quotas (monthly limit)

* * *

## Function Calling Rules and Composition Patterns

Understanding which Convex functions can call other functions is critical for designing
correct architectures.
Violating these rules leads to runtime errors or architectural issues.

### Function Type Call Matrix

| Caller Type | Can Call | Method | Use Case |
| --- | --- | --- | --- |
| **Query** | Helper functions | Direct call | Extract shared read logic |
| **Query** | Other queries | ❌ **NO** | No `ctx.runQuery` in queries |
| **Query** | Mutations | ❌ **NO** | Queries are read-only |
| **Mutation** | Helper functions | Direct call | Extract shared write logic |
| **Mutation** | Other mutations | ❌ **NO** | No `ctx.runMutation` in mutations |
| **Mutation** | Queries | ❌ **NO** | Use helper functions instead |
| **Action** | Queries | Yes | `ctx.runQuery(internal.*)` |
| **Action** | Mutations | Yes | `ctx.runMutation(internal.*)` |
| **Action** | Other actions | Yes | `ctx.runAction(internal.*)` |
| **Action** | Schedule functions | Yes | `ctx.scheduler.runAfter(...)` |

### Key Principles

1. **Queries and mutations cannot call other queries/mutations**

   - They can only call helper functions that take their context as an argument

   - This enforces single-transaction semantics

2. **Actions are the orchestration layer**

   - Actions coordinate between queries and mutations

   - Multiple `runQuery`/`runMutation` calls execute in separate transactions

3. **Transactional boundaries**

   - Each query/mutation is one transaction

   - Actions can compose multiple transactions

   - No guarantees of consistency across action-orchestrated calls

4. **Avoid nested action calls within the same runtime** ✅

   - While `ctx.runAction()` is technically allowed, Convex officially recommends
     against calling actions from actions **in the same runtime**

   - Use `ctx.runAction()` **only** when crossing runtimes (V8 → Node.js)

   - For same-runtime calls, extract shared code into plain TypeScript helper functions

   - **Official guidance**
     ([Convex Actions Docs](https://docs.convex.dev/functions/actions)):
     > “If you want to call an action from another action that’s in the same runtime,
     > which is the normal case, the best way to do this is to pull the code you want to
     > call into a TypeScript helper function and call the helper instead.”

   - **Observed behavior**: Nested same-runtime action calls can silently timeout at ~5
     minutes (undocumented implementation detail)

### Pattern: Helper Functions for Shared Logic

**Correct pattern for sharing logic within queries/mutations**:

```typescript
// Helper function - takes context as parameter
async function getCompletedRecords(ctx: QueryCtx, userId: Id<'users'>) {
  return await ctx.db
    .query('records')
    .withIndex('by_user', q => q.eq('userId', userId))
    .filter(q => q.eq(q.field('status'), 'completed'))
    .collect();
}

// Use helper in multiple queries
export const getUserStats = query({
  handler: async (ctx, { userId }) => {
    const records = await getCompletedRecords(ctx, userId); // Helper call
    return { totalRecords: records.length };
  },
});

export const getUserHistory = query({
  handler: async (ctx, { userId }) => {
    const records = await getCompletedRecords(ctx, userId); // Reuse helper
    return records.map(r => ({ id: r._id, date: r.createdAt }));
  },
});
```

### Pattern: Actions Orchestrating Queries and Mutations

**Correct pattern for composing operations across transactions**:

```typescript
// Action orchestrates query + mutation
export const processData = internalAction({
  handler: async (ctx, { recordId }) => {
    // 1. Read data (separate transaction)
    const data = await ctx.runQuery(internal.data.getData, { recordId });

    // 2. Process data (JavaScript, no transaction)
    const processed = transform(data);

    // 3. Write results (separate transaction)
    await ctx.runMutation(internal.data.updateStats, {
      recordId,
      stats: processed,
    });
  },
});
```

**Important**: The query and mutation above are **not atomic**. Another mutation could
modify data between the query and mutation calls.

### Pattern: Atomic Operations in Single Mutations

**When you need atomicity, consolidate into one mutation**:

```typescript
// WRONG: Action with race condition
export const incrementCounter = internalAction({
  handler: async (ctx, { counterId }) => {
    const counter = await ctx.runQuery(internal.getCounter, { counterId });
    await ctx.runMutation(internal.updateCounter, {
      counterId,
      value: counter.value + 1  // Race condition!
    });
  },
});

// CORRECT: Single atomic mutation
export const incrementCounter = mutation({
  args: { counterId: v.id('counters') },
  handler: async (ctx, { counterId }) => {
    const counter = await ctx.db.get(counterId);
    if (!counter) throw new Error('Counter not found');

    await ctx.db.patch(counterId, {
      value: counter.value + 1, // Atomic - no race condition
    });
  },
});
```

### Sources

- [Convex Functions Documentation](https://docs.convex.dev/functions)

- [Actions Documentation](https://docs.convex.dev/functions/actions)

- [Query Functions](https://docs.convex.dev/functions/query-functions)

- [Mutation Functions](https://docs.convex.dev/functions/mutation-functions)

* * *

## Common Pitfalls and Workarounds

This section catalogs frequent issues encountered when building applications on Convex,
along with proven mitigation strategies.

### Pitfall 1: Exceeding 8 MiB Read Limit with `.collect()`

**Symptom**: Runtime error `"transaction exceeded resource limits"` when querying tables
with many documents or large documents.

**Root Cause**: Using `.collect()` on queries that return large result sets.
Since Convex reads entire documents (no field projection), even seemingly small document
counts can exceed 8 MiB if individual documents are large.

**Example Scenario**:

```typescript
// DANGEROUS: Will fail if events table is large
const allEvents = await ctx.db.query('events').collect();
```

**Workarounds**:

1. **Use `.take(n)` for fixed limits**:

   ```typescript
   // Safe: Only reads first 100 documents
   const recentEvents = await ctx.db
     .query('events')
     .order('desc')
     .take(100);
   ```

2. **Use `.paginate(paginationOpts)` for cursor-based pagination**:

   ```typescript
   export const listEvents = query({
     args: { paginationOpts: paginationOptsValidator },
     handler: async (ctx, args) => {
       return await ctx.db
         .query('events')
         .order('desc')
         .paginate(args.paginationOpts);
     },
   });
   ```

3. **Use head+1 pattern for “N+” labels**:
   ```typescript
   const events = await ctx.db.query('events').take(limit + 1);
   const hasMore = events.length > limit;
   const displayLabel = hasMore ? `${limit}+` : `${events.length}`;
   ```

**Best Practice**: Never use `.collect()` on tables that can grow unbounded.
Always use `.take()` or `.paginate()`.

**Sources**:

- [Pagination Guide](https://docs.convex.dev/database/pagination)

- [Queries that Scale](https://stack.convex.dev/queries-that-scale)

### Pitfall 2: Large Documents Causing Read Limit Issues Even with `.take()`

**Symptom**: Queries fail with read limit error even when using `.take(n)` with small
values of `n`.

**Root Cause**: Individual documents are large (approaching 1 MiB limit), so reading
even 10–15 documents exceeds the 8 MiB transaction limit.

**Example Scenario**:

```typescript
// Can still fail if message documents have ~900KB content fields
const rows = await ctx.db
  .query('messages')
  .withIndex('by_parent', (q) => q.eq('parentId', parentId))
  .take(10); // 10 × 900KB = 9 MiB > 8 MiB limit
```

**Workarounds**:

1. **Separate large payloads into detail tables**:

   ```typescript
   // Keep main table light for listing/counting
   messages: {
     parentId: v.id('threads'),
     timestamp: v.number(),
     role: v.string(),
     contentSummary: v.string(), // Small snippet
     detailId: v.id('messageDetails'), // Link to full content
   }
   
   // Store large content separately
   messageDetails: {
     fullContent: v.string(), // Large field
     metadata: v.object({ ... }),
   }
   ```

2. **Pre-aggregate counters instead of scanning**:

```typescript
// Maintain counts at write time instead of scanning large documents
const count = thread.messageCount; // Pre-computed
// Instead of:
// const count = (await ctx.db.query(...).collect()).length; // SLOW
```

3. **Use the Convex Aggregate Component** (see Pitfall 3): Official library for
   maintaining statistics without scanning source tables.

**Best Practice**: Keep documents used for listing, counting, and filtering small
(<10KB). Store large payloads in separate detail tables fetched on-demand.

**Sources**:

- [Convex Limits - Document Size](https://docs.convex.dev/production/state/limits)

### Pitfall 3: Counting and Aggregating Over Large Datasets

**Symptom**: Need accurate counts, sums, or other aggregates over thousands to millions
of records, but scanning exceeds read limits.

**Root Cause**: Computing aggregates at query time by scanning all records is
incompatible with 8 MiB read limit for large datasets.

**Example Scenario**:

```typescript
// SLOW and will fail at scale
const errorCount = (await ctx.db.query('events')
  .withIndex('by_type', q => q.eq('eventType', 'error'))
  .collect()).length;
```

**Workarounds**:

1. **Use the official Convex Aggregate Component**:

   The [Convex Aggregate Component](https://github.com/get-convex/aggregate) provides
   O(log n) queries for counts and sums using an internal B-tree structure.

   ```typescript
   import { Aggregate } from '@convex-dev/aggregate';
   
   // Define aggregate
   const eventAggregate = new Aggregate<typeof schema.events>(components.aggregate, {
     filterKey: (event) => event.parentId,
     sumFields: { tokenCount: 0 },
   });
   
   // Query aggregates efficiently
   const stats = await eventAggregate.count(ctx, {
     prefix: parentId,
     bounds: { lower: ['error'], upper: ['error'] },
   });
   ```

**Key Features**:

- **Namespaces**: Isolate aggregates by entity (per-user, per-project, etc.)

- **Structured Keys**: Multi-level keys for flexible filtering

- **Sum Fields**: Track numeric aggregates (tokens, costs, etc.)

- **Batch Operations**: `countBatch()`, `sumBatch()`, `atBatch()` for efficient
  multi-query operations

- **Automatic Atomicity**: Handles concurrent writes correctly

- **TableAggregate wrapper**: Keeps aggregates in sync with table writes automatically

2. **Maintain counters at write time**:

```typescript
// Update counters when inserting events
await ctx.db.patch(entityId, {
 errorCount: (record.errorCount ?? 0) + 1,
 totalTokens: (record.totalTokens ?? 0) + tokens,
});
```

**Limitation**: Requires careful handling of concurrent updates and doesn’t support
ad-hoc filtering.

3. **Statistical sampling for approximate counts**:
   ```typescript
   const sample = await ctx.db.query('events').take(1000);
   const errorRate = sample.filter((e) => e.type === 'error').length / sample.length;
   const estimatedTotal = errorRate * totalEvents;
   ```
   **Limitation**: Not exact, unsuitable for critical metrics.

**Best Practice**: Use the Convex Aggregate Component for any aggregation over datasets
that can grow beyond a few hundred documents.

**Sources**:

- [Convex Aggregate Component](https://github.com/get-convex/aggregate)

### Pitfall 4: Post-Index Filtering Instead of Composite Indexes

**Symptom**: Queries are slow or hit read limits even when using indexes.

**Root Cause**: Using `.withIndex()` to narrow results by one field, then using
`.filter()` to narrow by another field.
This causes Convex to read all documents matching the index, including those filtered
out.

**Example Scenario**:

```typescript
// INEFFICIENT: Reads all items for parentId, then filters
const items = await ctx.db
  .query('items')
  .withIndex('by_parent', (q) => q.eq('parentId', parentId))
  .filter((q) => q.eq(q.field('status'), 'active'))
  .take(100);
```

**Workaround**: Create composite indexes that include all filter conditions.

```typescript
// schema.ts
items: defineTable({
  parentId: v.id('parents'),
  status: v.string(),
  ...
}).index('by_parent_and_status', ['parentId', 'status'])

// Query using composite index
const items = await ctx.db
  .query('items')
  .withIndex('by_parent_and_status', q =>
    q.eq('parentId', parentId).eq('status', 'active')
  )
  .take(100);
```

**Best Practice**: Design indexes to match your query patterns.
Prefer composite indexes over post-index filtering.

**Sources**:

- [Indexes and Query Performance](https://docs.convex.dev/database/reading-data/indexes)

- [Queries that Scale](https://stack.convex.dev/queries-that-scale)

### Pitfall 5: Optimistic Concurrency Control (OCC) Conflicts

**Symptom**: Mutations fail or retry frequently with errors related to conflicting
writes, especially under high concurrency.

**Root Cause**: Multiple mutations trying to read and update the same documents
concurrently. Convex uses Optimistic Concurrency Control—if a mutation reads a document
that another mutation modifies before the first completes, it retries.

**Example Scenario**:

```typescript
// Multiple concurrent mutations updating the same counter
const record = await ctx.db.get(recordId);
await ctx.db.patch(recordId, {
  eventCount: record.eventCount + 1, // OCC conflict if another mutation updates this
});
```

**Workarounds**:

1. **Consolidate related writes into single mutations**:

   Combine operations that update the same document into a single atomic mutation
   instead of calling multiple mutations from an action.

```typescript
// WRONG: Action calls two mutations - race condition
export const startWorkflow = internalAction(async (ctx, args) => {
  const sessionId = await ctx.runMutation(internal.createSession, ...);
  const workflowId = await ctx.runMutation(internal.createWorkflow, ...); // Race!
});

// CORRECT: Single mutation does both operations atomically
export const createSessionAndWorkflow = mutation({
  handler: async (ctx, args) => {
    const sessionId = await ctx.db.insert('sessions', ...);
    const workflowId = await ctx.db.insert('workflows', { sessionId, ... });
    return { sessionId, workflowId };
  },
});
```

2. **Batch create operations in single mutations**:

   When creating many related entities, do it in a single mutation instead of a loop:

   ```typescript
   // WRONG: Loop calling mutation - OCC conflicts possible
   for (const config of configs) {
     await ctx.runMutation(internal.createEntity, config);
   }
   
   // CORRECT: Single mutation creates all entities
   export const createEntities = internalMutation({
     handler: async (ctx, { configs }) => {
       const ids = [];
       for (const config of configs) {
         ids.push(await ctx.db.insert('entities', config));
       }
       return ids;
     },
   });
   ```

3. **Stagger concurrent scheduled mutations**:

   When scheduling multiple mutations that may write to related documents, add small
   delays:

   ```typescript
   // Schedule mutations with stagger to reduce simultaneous writes
   for (let i = 0; i < items.length; i++) {
     await ctx.scheduler.runAfter(
       100 * i, // 100ms delay per item
       internal.processItem,
       { itemId: items[i] }
     );
   }
   ```

4. **Use namespacing to isolate writes**:

   Ensure different entities write to different documents.
   For example, use per-entity aggregates instead of global counters.

5. **Use the Aggregate Component with namespaces**:

   The Aggregate Component handles concurrency internally and supports per-entity
   namespaces to minimize contention.

   ```typescript
   // Each entity has its own aggregate namespace - no cross-entity conflicts
   await eventAggregate.insert(ctx, {
     namespace: entityId,
     value: event,
   });
   ```

6. **Avoid wide aggregate reads**:

   Reading without bounds can create large read dependency sets, amplifying reactivity
   and OCC conflicts. Always use tight bounds:

   ```typescript
   // WIDE: Triggers reruns on any aggregate change
   const count = await aggregate.count(ctx, { prefix: entityId });
   
   // BOUNDED: Only reruns when matching records change
   const count = await aggregate.count(ctx, {
     prefix: entityId,
     bounds: { lower: ['error'], upper: ['error'] },
   });
   ```

7. **Lazy root evaluation**: Configure aggregates with `rootLazy: true` to reduce write
   contention at the cost of slightly slower reads.

**Best Practices Summary**:

- Consolidate related database operations into single atomic mutations

- Batch create operations instead of loops calling mutations

- Design mutations to minimize shared write dependencies

- Use namespacing and bounded reads extensively

- Stagger scheduled mutations that may conflict

**Workflow-Specific Idempotency**:

When using `@convex-dev/workflow` or `@convex-dev/workpool`, additional idempotency
requirements apply beyond OCC conflict handling:

- **Workflow retries are automatic**: Even successful actions may re-run if the
  scheduler has a transient failure recording the return value

- **Check before executing**: Workflow step actions should query for existing results
  before performing work (e.g., check for summary event by step index)

- **Write-through pattern**: Write results to DB inside actions, return only IDs to
  avoid re-processing on retry

**See Also**:
- [research-durable-workflows-agent-conversations.md](../../../project/research/current/research-durable-workflows-agent-conversations.md)
  § “Idempotency Requirements for Workflow Steps” for idempotency patterns
- [plan-2026-01-09-durable-workflows-agent-conversations-v3.md](../../../project/specs/active/plan-2026-01-09-durable-workflows-agent-conversations-v3.md)
  § “Idempotency Contract” for implementation-ready details

**🛠️ OCC Configuration (Self-Hosted)**:

The OCC retry behavior is configurable via environment variables:

| Setting | Default | Env Var | Source |
| --- | --- | --- | --- |
| Max retries | 4 | `UDF_EXECUTOR_OCC_MAX_RETRIES` | `knobs.rs:146-147` |
| Initial backoff | 10ms | `UDF_EXECUTOR_OCC_INITIAL_BACKOFF_MS` | `knobs.rs:150-151` |
| Max backoff | 2,000ms | `UDF_EXECUTOR_OCC_MAX_BACKOFF_MS` | `knobs.rs:154-155` |

Self-hosted deployments with lower contention could reduce retries; high-contention
scenarios might benefit from longer backoffs:

```bash
export UDF_EXECUTOR_OCC_MAX_RETRIES=8
export UDF_EXECUTOR_OCC_INITIAL_BACKOFF_MS=20
export UDF_EXECUTOR_OCC_MAX_BACKOFF_MS=5000
```

**Sources**:

- [Convex Aggregate Component](https://github.com/get-convex/aggregate)

- [@convex-dev/workpool](https://www.npmjs.com/package/@convex-dev/workpool) — “you
  should ensure that each step is an idempotent Convex action”

- Source: `crates/common/src/knobs.rs:146-155`

### Pitfall 6: Storage and Bandwidth Overages

**Symptom**: Unexpected costs from exceeding included storage or bandwidth quotas.

**Root Cause**: Retaining historical data indefinitely, underestimating index overhead,
or high-frequency queries on large result sets.

**Example Scenario**:

- Application stores detailed logs for every record indefinitely

- Indexes on large tables consume significant storage

- Dashboard queries transfer large amounts of data on every refresh

**Workarounds**:

1. **Implement data archival policies**:

   ```typescript
   // Archive completed runs to external storage (S3, etc.)
   export const archiveOldRuns = internalAction({
     handler: async (ctx, args) => {
      const oldRecords = await ctx.runQuery(internal.records.getCompleted, {
         beforeDate: Date.now() - 90 * 24 * 60 * 60 * 1000, // 90 days
       });
   
      for (const record of oldRecords) {
         // Export to S3
        await exportRecordToS3(record);
         // Delete from Convex
        await ctx.runMutation(internal.records.delete, { recordId: record._id });
       }
     },
   });
   ```

2. **Monitor storage and bandwidth proactively**:

   - Set up alerts at 75-80% of quota limits

   - Review Convex dashboard metrics monthly

   - Track growth trends to project future costs

3. **Optimize indexes**:

   - Remove unused indexes

   - Consider whether all composite index combinations are necessary

   - Index storage counts toward database storage quota

4. **Reduce bandwidth consumption**:

   - Use pagination to limit result set sizes

   - Cache frequently-accessed read-only data on the client

   - Avoid polling with reactive queries; use Convex’s real-time subscriptions instead

**Best Practice**: Design archival strategy before hitting quota limits.
Monitor usage monthly and set up automated alerts.

**Sources**:

- [Convex Limits - Storage](https://docs.convex.dev/production/state/limits)

### Pitfall 7: Pagination Loops in Queries and Mutations

**Symptom**: Pagination loops (do-while with cursor) hang in tests, timeout in
migrations, or fail with execution time limits.

**Root Cause**: Convex queries and mutations have limited execution time (1 second for
JS execution) and cannot safely iterate with pagination loops.
Additionally, pagination mocks in test environments can cause infinite loops.

**Example Scenario**:

```typescript
// PROBLEMATIC: Pagination loop in query
export const countAllTurns = query({
  handler: async (ctx, args) => {
    let total = 0;
    let cursor = null;
    do {
      const page = await ctx.db
        .query('conversationTurns')
        .paginate({ cursor, numItems: 100 });
      total += page.page.length;
      cursor = page.continueCursor;
    } while (cursor !== null); // Can loop forever or timeout!
    return total;
  },
});
```

**Problems with this pattern**:

1. **Test hanging**: Pagination mocks in `convex-test` can cause infinite loops

2. **Timeout risk**: Query/mutation execution time limit (1 second JS time)

3. **No progress guarantee**: If loop iteration fails, entire function retries from
   beginning

4. **Migration timeouts**: Validation queries using pagination loops hit 600-second
   timeout

**Workarounds**:

1. **Use `.take(limit)` instead of pagination loops**:

   ```typescript
   // CORRECT: Use take() with appropriate limit
   export const countTurns = query({
     handler: async (ctx, { conversationId }) => {
       const turns = await ctx.db
         .query('conversationTurns')
         .withIndex('by_conversation', (q) => q.eq('conversationId', conversationId))
         .take(1000); // Safe limit
       return turns.length;
     },
   });
   ```

2. **Move pagination to actions for large datasets**:

   Actions can safely loop because they have a 10-minute execution limit and don’t use
   mocked pagination in tests.

   ```typescript
   // CORRECT: Action can paginate safely
   export const processAllTurns = internalAction({
     handler: async (ctx, args) => {
       let cursor = null;
       let totalProcessed = 0;
   
       do {
         // Call mutation to process one batch
         const result = await ctx.runMutation(
           internal.processTurnsBatch,
           { cursor, numItems: 100 }
         );
   
         totalProcessed += result.processed;
         cursor = result.continueCursor;
       } while (cursor !== null);
   
       return { totalProcessed };
     },
   });
   
   // Mutation processes one batch
   export const processTurnsBatch = internalMutation({
     args: { cursor: v.union(v.string(), v.null()), numItems: v.number() },
     handler: async (ctx, args) => {
       const page = await ctx.db
         .query('conversationTurns')
         .paginate({ cursor: args.cursor, numItems: args.numItems });
   
       // Process page.page here
       const processed = page.page.length;
   
       return {
         processed,
         continueCursor: page.continueCursor,
       };
     },
   });
   ```

3. **For migrations: Use action-based validation**:

   ```typescript
   // Validation in action (not query)
   export const validateMigration = internalAction({
     handler: async (ctx, args) => {
       let cursor = null;
       let totalValidated = 0;
   
       do {
         const batch = await ctx.runQuery(internal.validateBatch, {
           cursor,
           numItems: 500,
         });
   
         totalValidated += batch.count;
         cursor = batch.continueCursor;
       } while (cursor !== null);
   
       return { totalValidated };
     },
   });
   ```

**Common Mistakes**:

1. **Declaring cursor as const**: `const cursor = null` in loop header means cursor
   never updates, causing infinite loop

2. **Not checking for null cursor**: Missing null check can cause issues

3. **Using in migrations**: Migration validation queries especially prone to timeouts

**Best Practices**:

- **Never use pagination loops in queries/mutations** - risk of timeouts and test hangs

- **Use `.take(n)` for bounded queries** - safer and faster than pagination

- **Use actions for pagination loops** - 10-minute limit allows safe iteration

- **For migrations: action-based validation** - query-based validation hits limits

- **Always update cursor in loops** - ensure cursor variable is mutable

**Sources**:

- [Convex Actions](https://docs.convex.dev/functions/actions)

- [Convex Pagination](https://docs.convex.dev/database/pagination)

### Pitfall 8: Bucket Timestamp Keys to Avoid Monotonic Writes

**Symptom**: High write contention when using aggregate keys based on `_creationTime` or
other monotonically increasing values.

**Root Cause**: Monotonically increasing keys cause all concurrent writes to target the
same B-tree leaf nodes, creating contention and OCC conflicts.

**Example Scenario**:

```typescript
// BAD: All events with similar timestamps hit same leaf node
await eventAggregate.insert(ctx, {
  namespace: entityId,
  key: [event._creationTime, event.type], // Monotonic first key
  value: event,
});
```

**Workaround**: Bucket timestamps to distribute writes across nodes.

```typescript
// GOOD: Bucket to nearest minute to spread writes
const bucketedTime = Math.floor(event._creationTime / 60000) * 60000;
await eventAggregate.insert(ctx, {
  namespace: entityId,
  key: [bucketedTime, event.type],
  value: event,
});
```

**Best Practice**: When using time-based keys in aggregates or indexes, bucket to
appropriate granularity (minute, hour, day) based on write frequency.

**Sources**:

- [Convex Aggregate Component](https://github.com/get-convex/aggregate)

### Pitfall 9: Dangling Promises in Actions

**Symptom**: Console warnings showing “1 unawaited operation” in Convex logs, or
intermittent errors in action invocations that seem unrelated to the current operation.

**Root Cause**: Fire-and-forget async patterns like `void fn()` or `fn().catch()` create
unawaited promises. When an action returns, any promises still running may or may not
complete. Since Convex reuses Node.js execution environments between action calls,
dangling promises can cause errors in subsequent action invocations.

**Convex Documentation Warning**:

> “Make sure to await all promises created within an action.
> Async tasks still running when the function returns might or might not complete.
> In addition, since the Node.js execution environment might be reused between action
> calls, dangling promises might result in errors in subsequent action invocations.”

**Example Scenarios**:

```typescript
// BAD: Fire-and-forget with void (promise may not complete)
export const processData = internalAction({
  handler: async (ctx, args) => {
    void logger.trackEvent({ event: 'started', ...args }); // Dangling!

    const result = await doWork(args);

    void logger.trackEvent({ event: 'completed', result }); // Dangling!
    return result;
  },
});

// BAD: Fire-and-forget with .catch() (still dangling)
export const processData = internalAction({
  handler: async (ctx, args) => {
    logger.trackEvent({ event: 'started' }).catch((err) => {
      console.error('Logging failed:', err);
    }); // Dangling! The promise is not awaited

    const result = await doWork(args);
    return result;
  },
});
```

**Workaround**: Always await async operations, even “fire-and-forget” logging calls.

```typescript
// CORRECT: All promises awaited
export const processData = internalAction({
  handler: async (ctx, args) => {
    await logger.trackEvent({ event: 'started', ...args }); // Properly awaited

    const result = await doWork(args);

    await logger.trackEvent({ event: 'completed', result }); // Properly awaited
    return result;
  },
});

// CORRECT: With error handling that still awaits
export const processData = internalAction({
  handler: async (ctx, args) => {
    try {
      await logger.trackEvent({ event: 'started' });
    } catch (err) {
      console.error('Logging failed:', err);
      // Continue execution even if logging fails
    }

    const result = await doWork(args);
    return result;
  },
});
```

**Key Patterns to Avoid**:

| Pattern | Issue | Fix |
| --- | --- | --- |
| `void asyncFn()` | Promise not awaited | `await asyncFn()` |
| `asyncFn().catch(...)` | Promise not awaited (catch returns new Promise) | `await asyncFn()` with try/catch |
| `setTimeout(() => asyncFn(), 0)` | Promise escapes action scope | Use `ctx.scheduler.runAfter(0, ...)` |
| Returning before awaiting | Promise orphaned | Ensure all awaits complete before return |

**Common Affected Operations**:

- Logging and telemetry calls

- Background analytics tracking

- Non-critical side effects (notifications, metrics)

- Cleanup operations at end of actions

**Best Practices**:

1. **Always await every async call** in actions, even for “non-critical” operations

2. **Use try/catch if the operation can fail** and you want to continue:
   ```typescript
   try {
     await optionalOperation();
   } catch (err) {
     console.warn('Optional operation failed:', err);
   }
   ```

3. **Use `ctx.scheduler.runAfter`** for truly fire-and-forget operations that should run
   independently:
   ```typescript
   // If you truly don't need to wait and want it to run separately
   await ctx.scheduler.runAfter(0, internal.logging.trackEvent, { event: 'completed' });
   ```

4. **Audit existing code** for `void` keyword and `.catch()` patterns in actions

**Sources**:

- [Convex Actions Documentation](https://docs.convex.dev/functions/actions) — Section on
  awaiting promises

### Pitfall 10: Nested Same-Runtime Action Calls ✅

**Symptom**: Actions that call other actions via `ctx.runAction()` within the same
runtime (both Node.js or both V8) silently timeout at ~5 minutes, well before the
documented 10-minute action timeout.

**Root Cause**: Convex officially recommends against nested action calls within the same
runtime. While technically allowed, this pattern has efficiency issues (parent action
wastes resources waiting idle) and observed timeout behavior that differs from
documented limits.

**Convex Official Guidance:**

From [Actions Documentation](https://docs.convex.dev/functions/actions):

> “If you want to call an action from another action that’s in the same runtime, which
> is the normal case, the best way to do this is to pull the code you want to call into
> a TypeScript helper function and call the helper instead.”

From [Best Practices](https://docs.convex.dev/understanding/best-practices/):

> “It counts as an extra function call with its own memory and CPU usage, while the
> parent action is doing nothing except waiting for the result.
> Therefore, runAction should almost always be replaced with calling a plain TypeScript
> function.”

**Example Scenario**:

```typescript
// BAD: Nested action call within same Node.js runtime
"use node";

export const parentAction = internalAction({
  handler: async (ctx, args) => {
    // This call may silently timeout at ~5 minutes!
    const result = await ctx.runAction(internal.childAction, { data: args.data });
    return result;
  },
});

export const childAction = internalAction({
  handler: async (ctx, args) => {
    // Long-running operation...
    return await processData(args.data);
  },
});
```

**Workaround**: Extract shared logic into plain TypeScript helper functions.

```typescript
// CORRECT: Use helper function instead of nested action
"use node";

// Plain TypeScript helper - NOT a Convex action
async function processDataHelper(data: DataType): Promise<ResultType> {
  // Shared logic lives here
  return await processData(data);
}

export const parentAction = internalAction({
  handler: async (ctx, args) => {
    // Call helper directly - no nested action, no timeout issue
    const result = await processDataHelper(args.data);
    return result;
  },
});

// childAction can still exist for direct invocation if needed
export const childAction = internalAction({
  handler: async (ctx, args) => {
    return await processDataHelper(args.data);
  },
});
```

**When `ctx.runAction()` IS Appropriate**:

| Scenario | Appropriate? | Reason |
| --- | --- | --- |
| V8 action calling Node.js action | ✅ Yes | Cross-runtime call (different isolates) |
| Node.js action calling V8 action | ✅ Yes | Cross-runtime call (different isolates) |
| Node.js action calling Node.js action | ❌ No | Same runtime - use helper function |
| V8 action calling V8 action | ❌ No | Same runtime - use helper function |
| Workflow `step.runAction()` | ✅ Yes | Workflow orchestration (V8 → Node) |

**Key Distinction**:

| Aspect | Documented by Convex | Observed in Production |
| --- | --- | --- |
| **Reason to avoid** | Efficiency (wasted resources) | Silent ~5 min timeout |
| **Recommended alternative** | Plain TypeScript helper functions | Same |
| **Valid use case** | Cross-runtime calls only | Same |

**Impact on Durable Workflows**:

When using `@convex-dev/workflow`, workflow step actions (called via `step.runAction()`)
must be **leaf actions** that do not call `ctx.runAction()` internally.
The workflow orchestrator runs in V8 and calls Node.js actions, which is a valid
cross-runtime pattern.
But if those Node.js actions then call other Node.js actions, you recreate the
problematic nested same-runtime pattern.

**See Also**:
- [research-durable-workflows-agent-conversations.md](../../../project/research/current/research-durable-workflows-agent-conversations.md)
  § “Nested Action Timeout Issue” for detailed analysis
- [plan-2026-01-09-durable-workflows-agent-conversations-v3.md](../../../project/specs/active/plan-2026-01-09-durable-workflows-agent-conversations-v3.md)
  § “Leaf Action Requirement” for implementation guidance

**Best Practices**:

1. **Search codebase for `ctx.runAction`** and verify each call crosses runtimes

2. **Extract shared logic** into plain TypeScript helper functions

3. **Use dependency injection** to pass context to helpers when needed

4. **For workflows**: Ensure all `step.runAction()` targets are leaf actions

**Sources**:

- [Convex Actions Documentation](https://docs.convex.dev/functions/actions)

- [Convex Best Practices](https://docs.convex.dev/understanding/best-practices/)

* * *

## Best Practices Checklist

### Query Design

1. **Never use `.collect()` on unbounded tables**

   - Use `.take(n)` for fixed-size results

   - Use `.paginate(paginationOpts)` for cursor-based pagination

   - Use head+1 pattern (`.take(limit + 1)`) for “N+” labels

2. **Use composite indexes over post-index filtering**

   - Design indexes to match query patterns

   - Include all filter fields in index definition

   - Avoid `.withIndex()` followed by `.filter()`

3. **Keep scanned documents small**

   - Separate large payloads (>10KB) into detail tables

   - Fetch detail documents only when needed (on-demand)

   - Design listing/counting tables with minimal fields

4. **Index fields in query order**

   - Match index field order to query equality/range conditions

   - Create separate indexes for different query orders if needed

### Aggregation and Counting

5. **Use Aggregate Component for statistics at scale**

   - Leverage official
     [Convex Aggregate Component](https://github.com/get-convex/aggregate) for
     counts/sums over large datasets

   - Design aggregate namespaces for isolation (per-entity aggregates)

   - Use batch operations (`countBatch`, `sumBatch`, `atBatch`) for efficiency

6. **Bound all aggregate reads**

   - Always specify `bounds: { lower, upper }` to limit reactivity

   - Combine `prefix` with bounds for targeted queries

   - Avoid reading entire namespace without bounds

7. **Bucket timestamp keys**

   - Bucket `_creationTime` to appropriate granularity (minute/hour/day)

   - Avoid monotonically increasing first keys in aggregates

   - Distribute writes across B-tree nodes

### Concurrency and Performance

8. **Namespace to avoid write contention**

   - Use per-entity namespacing (e.g., per-run, per-user)

   - Isolate unrelated writes to different documents

   - Minimize shared write dependencies

9. **Use actions for long-running operations**

   - Move data exports, backfills, and heavy processing to actions

   - Keep queries/mutations under 1-second execution time

   - Break work into chunks that finish within 10-minute action limit

10. **Await all promises in actions**

    - Never use `void asyncFn()` or `asyncFn().catch()` patterns

    - Use try/catch for non-critical operations that can fail

    - Use `ctx.scheduler.runAfter` for truly independent operations

11. **Limit scheduled job fan-out**

    - Schedule at most 1,000 functions per mutation

    - Keep total scheduled arguments under 8 MiB

    - Use batch processing for larger workloads

12. **Avoid nested action calls within same runtime** ✅

    - Use `ctx.runAction()` **only** for cross-runtime calls (V8 → Node.js)

    - Extract shared logic into plain TypeScript helper functions

    - Audit codebase for `ctx.runAction` and verify each call crosses runtimes

    - For durable workflows: ensure step actions are “leaf actions” (no nested calls)

### Storage and Cost Management

13. **Monitor storage and bandwidth proactively**

    - Set up alerts at 75-80% of quota limits

    - Review Convex dashboard metrics monthly

    - Track growth trends to project costs

14. **Implement data archival policies**

    - Export historical data to external storage (S3, etc.)

    - Delete archived data from Convex to free quota

    - Define archival criteria before hitting limits

15. **Optimize index usage**

    - Remove unused indexes

    - Evaluate whether all composite index combinations are necessary

    - Remember: indexes consume storage quota

### Code Organization

16. **Use proper function visibility**

    - Use `internalQuery`/`internalMutation`/`internalAction` for private functions

    - Use `query`/`mutation`/`action` only for public API

    - Follow file-based routing conventions

17. **Always include validators**

    - Add `args` and `returns` validators to all functions

    - Use `v.null()` for functions with no return value

    - Leverage TypeScript types generated from validators

* * *

## References

### Official Convex Documentation

- [Convex Production Limits](https://docs.convex.dev/production/state/limits) — Complete
  limits reference (verified January 2026)

- [Convex Pricing](https://www.convex.dev/pricing) — Current plan limits and pricing

- [Convex Best Practices](https://docs.convex.dev/understanding/best-practices) —
  Official best practices guide

- [Convex Runtimes](https://docs.convex.dev/functions/runtimes) — Runtime comparison
  (Convex vs Node.js)

- [Indexes and Query Performance](https://docs.convex.dev/database/reading-data/indexes)
  — Index optimization and query patterns

- [Pagination Guide](https://docs.convex.dev/database/pagination) — Cursor-based and
  offset pagination

- [Query Functions](https://docs.convex.dev/functions/query-functions) — Query design
  and patterns

- [Full Text Search](https://docs.convex.dev/search/text-search) — Search index limits

- [Vector Search](https://docs.convex.dev/search/vector-search) — Vector index limits

- [Scheduled Functions](https://docs.convex.dev/scheduling/scheduled-functions) —
  Scheduling limits

- [Environment Variables](https://docs.convex.dev/production/environment-variables) —
  Environment variable limits

### Community Resources

- [Queries that Scale](https://stack.convex.dev/queries-that-scale) — Community article
  on scalable query patterns (February 2024)

### Official Libraries and Tools

- [Convex Aggregate Component](https://github.com/get-convex/aggregate) — Official
  library for maintaining denormalized aggregates

- [Convex Helpers](https://github.com/get-convex/convex-helpers) — Utilities for
  pagination, filtering, and common patterns

* * *

## Quick Reference Tables

### Limit Quick Reference (January 2026)

**Note**: Limits marked ✅ are verified against official documentation as of January
2026\. Limits marked 🔍 have source code values that differ from documentation.
Professional plan customers can request increases on a case-by-case basis by contacting
mailto:support@convex.dev.

| Category | Limit Type | Documented | Source Code | Status |
| --- | --- | --- | --- | --- |
| **Transaction Read** | Maximum data read | 8 MiB | **16 MiB** | ✅ 🔒 🔍 🛠️ |
|  | Maximum documents scanned | 16,384 | **32,000** | ✅ 🔒 🔍 🛠️ |
|  | Maximum db.get/db.query calls | 4,096 | 4,096 | ✅ 🔒 🛠️ |
| **Transaction Write** | Maximum data written | 8 MiB | **16 MiB** | ✅ 🔒 🔍 🛠️ |
|  | Maximum documents written | 8,192 | **16,000** | ✅ 🔒 🔍 🛠️ |
| **Document** | Maximum size | 1 MiB | 1 MiB | ✅ 🔒 |
|  | Maximum fields | 1,024 | 1,024 | ✅ 🔒 |
|  | Maximum nesting depth | 16 levels | 16 levels | ✅ 🔒 |
|  | Maximum array elements | 8,192 | 8,192 | ✅ 🔒 |
|  | Maximum field name length | 64 chars | **1,024 chars** | ✅ 🔒 🔍 |
| **Execution Time** | Query/Mutation user timeout | 1 second | 1 second | ✅ 🔒 🛠️ |
|  | Query/Mutation system timeout | N/A | 15 seconds | ✅ 🔒 🛠️ |
|  | Action execution | 10 minutes | 10 minutes | ✅ 🔒 🛠️ |
| **Action Memory** | Convex Runtime | 64 MB | 64 MB | ✅ 🔄 🛠️ |
|  | Node.js Runtime | 512 MB | 512 MB | ✅ 🔄 🛠️ |
| **Function Arguments** | Convex Runtime | 8 MiB | **16 MiB** | ✅ 🔒 🔍 🛠️ |
|  | Node.js Runtime | 5 MiB | 5 MiB (error msg) | ✅ 🔒 |
| **Scheduled Functions** | Max functions per mutation | 1,000 | 1,000 | ✅ 🔒 🛠️ |
|  | Total argument size | 8 MiB | **16 MiB** | ✅ 🔒 🔍 🛠️ |
| **Logging** | Log lines per execution | N/A | 256 | ✅ 🔒 🔍 |
| **Concurrency (default)** | Queries | 16 | 16 | ✅ 🔄 🛠️ |
|  | Mutations | 16 | 16 | ✅ 🔄 🛠️ |
|  | V8/Node/HTTP Actions | 16 | 16 | ✅ 🔄 🛠️ |
|  | Scheduled Job Parallelism | 10 | 10 | ✅ 🔄 🛠️ |
| **Indexes** | Indexes per table | 32 | **64** | ✅ 🔒 🔍 |
|  | Fields per index | 16 | 16 | ✅ 🔒 |
|  | Full-text indexes per table | 4 | 4 | ✅ 🔒 |
|  | Vector indexes per table | 4 | 4 | ✅ 🔒 |
|  | Vector index max documents | 100,000 | 100,000 | ✅ 🔒 |
| **Search Results** | Full-text search results | 1,024 | 1,024 | ✅ 🔒 |
|  | Vector search results | 256 | 256 | ✅ 🔒 |
| **Environment Vars** | Maximum count | 100 | **1,000** | ✅ 🔒 🔍 🛠️ |
|  | Name length | 40 chars | 40 chars | ✅ 🔒 |
|  | Value length | N/A | 8,192 bytes | ✅ 🔒 |

**Key**: 🔍 = Source code differs from docs; 🛠️ = Configurable via env var for
self-hosted

### Common Error Messages and Solutions

| Error Message | Likely Cause | Solution |
| --- | --- | --- |
| `"transaction exceeded resource limits"` | Read limit (8 MiB) or document count (16,384) exceeded | Use `.take()` or `.paginate()` instead of `.collect()`; separate large fields into detail tables |
| `"document too large"` | Document exceeds 1 MiB | Split large fields into separate documents; compress or truncate large text |
| `"JavaScript execution ran out of memory (maximum memory usage: 64 MB)"` | Action exceeded Convex Runtime 64 MB limit | Add `"use node";` directive to file to switch to Node.js runtime (512 MB limit) |
| Action timeout (no error, just stops) | Action exceeded 600s limit | Use sampling strategy; implement resumable pattern; break into scheduled jobs |
| Logs truncated silently | Exceeded 256 log lines | Log less frequently (every 100 iterations instead of every 5); use external logging |
| High OCC retry rates | Write contention on shared documents | Use namespacing; avoid wide aggregate reads; isolate entity writes |
| Slow query performance | Table scan without index | Create composite index matching query pattern; avoid post-index `.filter()` |
| Storage overage charges | Data retention without archival | Implement archival policy; export historical data; delete old records |
| `"1 unawaited operation"` warning | Dangling promises from `void fn()` or `fn().catch()` | Await all async operations; use try/catch for error handling |

### Decision Matrix: When to Use Each Pattern

| Use Case | Recommended Pattern | Alternative |
| --- | --- | --- |
| **Count/sum over <100 records** | Direct query with `.collect()` | N/A |
| **Count/sum over 100–1000 records** | `.take(limit)` with head+1 pattern | Aggregate Component |
| **Count/sum over >1000 records** | Convex Aggregate Component | Pre-computed counters (limited flexibility) |
| **List 10–100 records** | `.take(n)` | `.paginate()` if client needs multiple pages |
| **List unbounded records** | `.paginate(paginationOpts)` | Never use `.collect()` |
| **Large text fields (>10KB)** | Separate detail table | Compression (if feasible) |
| **High-frequency counters** | Aggregate Component with namespaces | Write-time counters (OCC risk) |
| **Long-running processing (< 10 min)** | Action with progress logging (every 100 iterations) | Break into scheduled mutations |
| **Long-running processing (> 10 min)** | Resumable action pattern or scheduled jobs | Sampling strategy for validation |
| **Historical data retention** | Archive to S3/external storage | Accept storage costs |

### Recommended Limit Values for Common Scenarios

This table provides practical limit values based on real-world usage patterns and Convex
constraints:

| Scenario | Recommended Limit | Rationale |
| --- | --- | --- |
| **Log/event queries** | 8,000 max return | Stays under 8,192 array limit with formatting overhead |
| **Activity tracking scans** | 10,000 max scan | Prevents 8 MiB read with typical record sizes (0.5-1KB each) |
| **Large text collection queries** | 1,000 per parent | Combined with 900KB content limit prevents excessive reads |
| **Dashboard tab counts** | 50-100 with head+1 | Balances UX clarity with query performance |
| **Truncated text fields** | 500 characters | Prevents 8 MiB return limit with thousands of records |
| **Large content fields** | 900 KB max | Leaves 100KB+ headroom below 1 MiB document limit |
| **Relational data queries** | 10,000-20,000 | Typical collection sizes stay well under limits |
| **File storage content** | 50 KB before compression | Use Brotli compression (3:1 ratio) for larger content |

### When to Use File Storage vs. Document Fields

| Content Size | Strategy | Implementation |
| --- | --- | --- |
| **<1 KB** | Store in document field | Direct field storage |
| **1-10 KB** | Store in document field | Consider if used for listing/counting |
| **10-50 KB** | Separate document or file storage | Use detail tables for on-demand fetch |
| **50-900 KB** | **Must** use detail table or file storage | Approaching 1 MiB document limit |
| **>900 KB** | **Must** use file storage with compression | Brotli compression for HTML/text (3:1 ratio) |

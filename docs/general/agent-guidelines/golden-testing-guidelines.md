# Golden Testing Guidelines

**Author**: Joshua Levy (github.com/jlevy) with about 5 LLMs

**Last Updated**: 2025-12-31

**Related**:

- `docs/general/agent-guidelines/general-tdd-guidelines.md`

* * *

## TL;DR (What to do)

- Define a session schema (events) with stable vs unstable fields.

- Capture full execution for scenarios (inputs, outputs, side effects) as YAML.

- Normalize or remove unstable fields at serialization time.

- Provide a mock mode for all nondeterminism and slow dependencies.

- Add a CLI to run scenarios, update goldens, and print diffs.

- Keep scenarios few but end-to-end; tests must run fast in CI (<100ms each).

- Prefer many small artifacts (shard by scenario/phase) over monolithic traces.

- Layer domain-focused assertions alongside raw diffs for critical invariants.

- Review and commit session files with code; treat them as behavioral specs.

**Why this approach**:

## When to Use Golden Tests

When not to use: if output is trivially stable and unit tests are enough, use snapshots
or unit tests only. Golden session testing excels for complex systems where writing and
maintaining hundreds of unit or integration tests is burdensome, even for coding agents.
Traditional unit tests struggle to capture the full behavior of systems with many
interacting components, non-deterministic outputs, and complex state transitions.
Session-level testing provides complete visibility into what the system actually does
*inside and outside* both when it conforms and when it changes.

### Terminology Note

The industry uses “golden file tests,” “approval tests,” “snapshot tests,” and
“characterization tests” for related ideas.
We use “golden tests” or “golden session tests” to mean tests with full detailed session
checks—capturing complete execution traces (not just final output) with explicit
stable-field filtering.

## Overview

Golden testing captures the complete execution trace, which we call a **session**, of a
system—inputs, outputs, and intermediate states—serializes it to a human-readable file,
and uses it as a reference for detecting behavioral regressions.
This document presents an opinionated approach to golden testing optimized for
AI-assisted development and fast CI pipelines.

Sessions are a testing construct, not an application requirement.
Any application can be tested using sessions by treating a sequence of operations
(commands, API calls, user actions) as a session.
A stateless CLI is just as testable as a stateful web app—you define a session as “run
these commands in order and capture setup state, intermediate states, and final
outputs.”

The approach draws on established work (snapshot testing, approval testing, VCR) but
extends it with explicit data modeling of events, unified CLI/GUI abstractions, and
developer workflows designed for modern AI-assisted development.

The entire approach rests on the idea of modeling and using serialized sessions, then
checking them into your version control system as “golden” references and examining when
and how they change.

### Transparent Box Testing

Golden session testing is “transparent box” testing: you capture *every* meaningful
detail of execution, not just inputs and outputs.
The goal is full visibility into system behavior so that any change—intentional or
accidental—shows up in diffs.
And it does this without the maintenance burden of writing numerous unit or integration
tests.

Sessions should be serialized in a clean text format.
Generally, YAML is a good choice, but other text formats are also acceptable.
Do *not* make session data you record abstract or high-level.
The practical goal is to make the serialized session:

- *as detailed as possible within a reasonable size budget* (small enough to manually
  review in PRs and commit to git, e.g. <2000 lines of YAML session data per test)

- *stable and deterministic* across runs and environments (we get into this later)

- *in a clean format that is easy to diff* to see changes and regressions when reviewing
  PRs

You should aim to capture everything meaningful that happens in the code within the size
budget. Concretely: include full payloads for requests/responses that change state, the
complete stdout/stderr for commands, and the contents (or checksums) of files that are
read or written.

**What to capture depends on your application:**

**CLI Tools**: Log the full command with all arguments, environment variables that
affect behavior, working directory, complete stdout/stderr (not truncated), exit code,
files read and written (with contents or checksums), timing for performance-sensitive
operations. Even for a “stateless” CLI, the session captures multiple commands in
sequence with the full filesystem state changes.

**Web Applications**: Log every HTTP request/response (method, headers, body, status),
database queries executed, cache hits/misses, session state changes, user actions with
full payloads, server-side computations with inputs and outputs, external API calls with
request/response bodies.
The session shows the complete data flow from user click to database write.

**Agent Frameworks**: Log the full user message, the complete system prompt, every LLM
call with full request (including all messages in context) and full response (including
token counts, finish reason), every tool call with complete arguments, every tool result
with complete return value, internal reasoning/chain-of-thought if available, final
response with all metadata.
When an agent’s behavior changes—different tool choice, different reasoning, different
phrasing—the session diff shows exactly what changed.

**Why capture everything?**

- Debugging: When something breaks, the session file shows exactly what happened

- Regression detection: Subtle changes (reordered operations, changed formats) are
  visible in diffs

- Documentation: Session files serve as executable specifications

- AI-assisted development: Agents can read session diffs to understand behavioral
  changes right away and understand failures writing new tests or adding log messages to
  tests

**Prerequisites for reproducibility:**

This approach only works if you have:

1. **Stable/unstable field classification**: Every field in your event schema must be
   classified. Stable fields (actions, quantities, configurations) are compared exactly.
   Unstable fields (timestamps, generated IDs, random values, durations) are filtered or
   normalized before comparison.
   Without this classification, tests will be flaky.

2. **Full mocking for nondeterministic dependencies**: Anything that produces
   nondeterministic output must be mockable—LLM APIs, external services, database
   sequences, random number generators, system clocks.
   If you can’t mock it, you can’t get reproducible sessions.

3. **Full mocking for slow dependencies**: Network calls, database queries, and external
   APIs should run against mocks in CI. The same test code runs in “live” mode (real
   services) for debugging and in “mocked” mode (recorded/stubbed responses) for fast
   CI. Without this, tests are too slow to run on every commit.

The filtering of unstable fields happens at serialization time—you capture the full
data, but normalize non-deterministic values so diffs are meaningful.
For example, replace `transactionId: "abc123"` with `transactionId: "[GENERATED]"`
before writing the session file.

* * *

## Related Work

The core concepts have established precedents:

- **Golden Master Testing** (Nat Pryce & Steve Freeman): Captures current behavior as a
  “golden master” reference for regression testing.
  Records complete system behavior and filters out unstable/non-deterministic elements.

- **Characterization Testing** (Michael Feathers, *Working Effectively with Legacy
  Code*): Write tests characterizing current behavior before refactoring.
  Helps understand complex systems through their outputs and protects against unintended
  changes during refactoring.

- **Approval Testing** (Llewellyn Falco, ApprovalTests): Focuses on whole-system
  behavior verification with “scrubbers” to filter unstable values.
  Uses diff tools for comparison and treats test output as living documentation.

- **Snapshot Testing** (Jest, Vitest, Playwright): Serializes component output to files
  committed to version control.
  Widely adopted in frontend development but often criticized for brittleness when
  overused.

- **VCR / Cassette Testing** (Ruby VCR, vcrpy, nock): Records HTTP interactions to
  “cassettes” for deterministic replay.

- **Record-Replay Testing** (BitDive, iReplayer): Captures full execution traces for
  debugging and testing.

- **Trace-Based Testing** (Academic): Uses execution traces for testing complex systems
  including compilers, distributed systems, and state machines.

Our approach combines these ideas: the behavioral specification of golden master
testing, the characterization of complex systems from Feathers’ work, the scrubber
concept from approval testing, the recording pattern from VCR, and the trace depth of
record-replay—unified into a single methodology.

* * *

## Core Principles

### 1. Model Events Formally

All events in the system should be modeled with type-safe schemas (Zod, Pydantic,
TypeScript interfaces).
Events are serialized to YAML for human readability.

```typescript
// Example: a user action event
const UserActionSchema = z.object({
  type: z.literal('user_action'),
  timestamp: z.number(),       // unstable - will be filtered
  requestId: z.string(),       // unstable - generated
  action: z.string(),          // stable
  payload: z.record(z.unknown()), // stable
});
```

**Why**: Schemas provide documentation, enable validation, and make filtering and
migration tractable.
YAML is preferred over JSON for diff readability.

### 2. Classify Fields as Stable or Unstable

Every field in an event schema must be classified:

- **Stable**: Deterministic values that must match exactly (symbols, actions,
  quantities, configuration)

- **Unstable**: Non-deterministic values filtered during comparison (timestamps,
  generated IDs, random values, durations)

Filter unstable fields before writing session files.
Options:

- Replace with placeholders: `"[TIMESTAMP]"`, `"[GENERATED_ID]"`

- Omit entirely from serialization

- Normalize to canonical form (sort arrays, trim whitespace)

Example filter function:

```typescript
const UNSTABLE = ['timestamp', 'requestId', 'transactionId', 'duration'];

function filterEvent(event: Record<string, unknown>) {
  return Object.fromEntries(
    Object.entries(event).filter(([k]) => !UNSTABLE.includes(k))
  );
}
```

**Why**: Unstable fields cause flaky tests.
Centralizing the filtering logic prevents ad-hoc workarounds scattered across tests.

### 3. Use Switchable Mock Modes

Implement two execution modes using the same test code:

- **Live mode**: Calls real external services for debugging and updating golden files

- **Mocked mode**: Uses recorded/stubbed responses for fast, deterministic CI

```typescript
const mockMode = process.env.MOCK_MODE ?? 'mocked';

const paymentClient = mockMode === 'live'
  ? new StripeClient(process.env.STRIPE_KEY)
  : new MockPaymentClient(loadFixtures('payments'));
```

**Why**: CI needs speed and determinism (mocked).
Development needs real behavior for validation (live).
The same tests must run in both modes.

**Hermeticity**: For full determinism, inject everything that varies—clocks, random
generators, network, database sequences.
If a value can differ between runs, it must be controlled or filtered.

### 4. Build CLI for Token-Efficient Agent Testing

Build a CLI that runs scenarios and produces structured YAML output.
This enables AI agents to:

- Run golden tests in tight feedback loops

- Read text-based session diffs (token-efficient vs screenshots)

- Make precise assertions on structured output

Example commands:

```bash
my-app test golden --scenario checkout-flow
my-app test golden --scenario checkout-flow --update
git diff tests/golden/
```

**Why**: AI agents work better with structured text than screenshots.
A CLI with structured output enables efficient agent testing loops.

Recommended directory layout:

```
tests/
  golden/
    scenarios/
      checkout-flow.yaml
      refunds.yaml
    fixtures/
      payments.json
    README.md
```

### 5. Unify Session Abstractions Across CLI and GUI

*This principle applies to projects with a UI/app layer.
Skip if CLI-only.*

The CLI should use identical code paths as the GUI. The same event types and session
structures should power:

- Backend execution

- Web frontend

- CLI tools

- GUI applications

```
┌─────────────┐     ┌─────────────┐
│   Web UI    │     │   CLI       │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 │
          ┌──────▼──────┐
          │   Shared    │
          │   Codebase  │
          └──────┬──────┘
                 │ writes
                 ▼
          ┌─────────────┐          ┌─────────────┐
          │   Session   │          │   Golden    │
          │   Files     │◄─────────│   Files     │
          │  (actual)   │  compare │   (in git)  │
          └─────────────┘          └──────┬──────┘
                                          │
                                   ┌──────▼──────┐
                                   │   Tests     │
                                   │  (fail if   │
                                   │   differ)   │
                                   └─────────────┘
```

**Why**: When UI and CLI share the same codebase that emits session events, you can test
complex UI logic without browser automation.
Tests compare actual session output against committed golden files and fail on any diff.

### 6. Design for Fast CI

Golden tests should run in under 100ms per scenario:

- Run in mocked mode (no network, no external services)

- Use in-memory mocks over file-based fixtures

- Parallelize independent scenarios

- Cache expensive setup (parsed configs, initialized state)

Define canonical scenarios that maximize coverage:

- Each scenario exercises a complete user flow

- Prefer fewer comprehensive scenarios over many narrow tests

- Supplement with unit tests for edge cases

**Why**: Tests that don’t run on every commit don’t catch regressions.
Speed is non-negotiable.

### 7. Layer Domain-Focused Assertions

In addition to raw diff comparison, layer targeted programmatic assertions for critical
invariants:

- **Shape/contract checks**: Validate event structure matches schemas

- **Ordering invariants**: Assert events appear in expected sequence

- **Aggregate constraints**: Verify totals, counts, or derived values are consistent

- **Cross-event relationships**: Check that IDs referenced in one event exist in another

```typescript
// Example: combine diff with targeted assertions
const session = runScenario('checkout-flow');
compareToGolden(session, 'checkout-flow.yaml');

// Additional invariants beyond raw diff
assert(session.events.filter(e => e.type === 'payment').length === 1);
assert(session.events.find(e => e.type === 'order_created')?.total > 0);
```

**Why**: Raw diffs catch unexpected changes; targeted assertions catch semantic
violations that might not appear as diff noise.
The combination provides maximum signal with minimal brittleness.

### 8. Establish Session Management Workflows

The developer workflow for golden tests:

1. **Make changes**: Modify business logic, fix bugs, add features

2. **Run tests**: `pnpm test:golden` — tests fail if behavior changed

3. **Regenerate**: `pnpm test:golden --update` — update golden files

4. **Review diffs**: `git diff tests/golden/` — verify changes are intentional

5. **Commit**: Session files committed alongside code changes

6. **PR review**: Reviewers see both code and behavioral changes

For AI agents, this workflow is the same but automated:

1. Agent runs tests, reads structured failure output

2. Agent decides: fix code or update golden files

3. Agent reviews diffs, commits with explanation

**Why**: Session files are behavioral specifications.
They deserve the same review rigor as code.

### Minimum Viable Implementation (30–60 min)

1. Pick 3–5 end‑to‑end scenarios that cover major flows.

2. Define event schemas and mark unstable fields.

3. Add a filter/normalizer that runs before writing YAML.

4. Introduce `MOCK_MODE` (`mocked` by default; `live` for updates).

5. Implement a CLI:

   - `test golden --scenario <name>` → run, compare, fail on diff

   - `test golden --scenario <name> --update` → rewrite YAML

6. Add CI job to run all scenarios in mocked mode in parallel.

7. Document the review workflow in `tests/golden/README.md`.

### Do / Don’t

- Do capture full payloads and side effects that influence behavior.

- Do normalize/remap unstable values at write time, not in comparisons.

- Do keep scenarios few, representative, and fast.

- Do prefer many small artifacts over monolithic traces—shard by scenario, phase, or
  subsystem.

- Do layer targeted assertions for critical invariants alongside raw diff comparison.

- Do find ways to log text fields that matter, even if they are long: consider
  truncating after a length or truncating in the middle of a long string, so you can see
  part of it for quick debugging.
  Or use short hashes of the value.

- Don’t depend on real clocks, random, network, or database in CI—inject mocks/fixtures
  for full hermeticity.

- Don’t hide differences with overly broad placeholders; prefer precise normalization.

- Don’t fork logic for tests vs production; share code paths.

- Don’t let artifacts grow unbounded—add lint checks to warn on size thresholds.

### Common Pitfalls

- Missing unstable field classification → flaky diffs.

- File I/O captured without contents/checksums → silent regressions.

- GUI and CLI use different code paths → untestable UI logic.

- Slow or network‑bound scenarios → skipped in practice, regressions leak.

- LLM output not recorded or scrubbed → non‑deterministic sessions.

- Monolithic traces that grow unbounded → hard to review, slow to diff.

- Over-approval without careful review → tests pass but behavior is wrong.

* * *

## Reading Session Diffs

When behavior changes, session diffs show exactly what changed:

```diff
  - type: discount_applied
    code: "SAVE10"
-   discount: 7.50
+   discount: 10.00
+   reason: "loyalty_bonus"
```

Well-structured session files have these properties:

- Human-readable YAML (easy to review in PRs)

- Unstable fields removed or replaced with placeholders like `"[GENERATED]"`

- Events in execution order

- Complete trace from input to final state

Review diffs as behavioral changes: if diffs are intentional, update the golden; if not,
fix the code or mocks.

* * *

## Implementation Checklist

When implementing golden testing for a new project:

- [ ] Define event schemas with Zod/Pydantic before implementation

- [ ] Mark each field as stable or unstable in schema documentation

- [ ] Implement stable field filtering by having it in the event data model from the
  start

- [ ] Add mock mode toggle via environment variable

- [ ] Create API client abstraction that switches on mock mode

- [ ] Build CLI that shares code with main application

- [ ] Define 3-5 canonical scenarios covering major user flows

- [ ] Create `tests/golden/` with `scenarios/` and `fixtures/` folders

- [ ] Add `test:golden` and `test:golden --update` scripts

- [ ] Add artifact lint checks (size thresholds, unstable field detection)

- [ ] If appropriate, add configurable comparison strictness (strict/lenient/partial)

- [ ] If appropriate, support multi-format outputs (YAML, text files, log files, etc.)

- [ ] Add targeted assertions for critical invariants alongside diff comparison

- [ ] Be sure to confirm CI fails due to golden test failures on unexpected golden diffs

- [ ] Document the session review workflow for the team

- [ ] Consider complementary testing approaches (property-based, contract testing)

* * *

## Comparison with Alternatives

### By Use Case and Suitability

| Approach | Scope | Stability | Maintenance | Debugging | AI Suitability |
| --- | --- | --- | --- | --- | --- |
| Golden Sessions | Full session traces | High (stable fields) | Medium | Excellent | Excellent |
| ApprovalTests | Whole value outputs | Medium-High | Medium | Good | Very Good |
| Jest Snapshots | Component outputs | Low (brittle) | High | Poor | Poor |
| VCR/Cassettes | HTTP only | Medium | Low | Limited | Limited |
| Unit Tests | Individual functions | High | Low | Good | Limited |

### By Artifact Form and Workflow

| Approach | Artifact Form | Update Flow | Primary Risk |
| --- | --- | --- | --- |
| Golden Sessions | Execution trace (YAML) | Regenerate + review diff | Trace bloat if unmanaged |
| ApprovalTests | Approved artifact | Re-approve on change | Over-approval without review |
| Jest Snapshots | Serialized component | Update snapshots | Brittleness from noise |
| VCR/Cassettes | HTTP interaction trace | Re-record cassette | Drift vs real service behavior |
| Golden Files (Go/Bazel) | Text/binary output | Regenerate golden | Bloat if unmanaged |

**When to use simpler alternatives**:

- Pure snapshot testing: Simple UIs with stable output

- VCR-only: API-heavy apps where internal state doesn’t matter

- Screenshot testing: Visual regression where pixels matter

### Complementary Approaches

Golden session testing works well alongside other testing strategies:

- **Property-based testing**: Use for edge case exploration and invariant validation.
  Golden tests capture expected behavior; property tests explore unexpected inputs.

- **Contract testing**: For API boundary validation between services.
  Golden tests verify internal behavior; contract tests verify interface agreements.

- **Unit tests**: For isolated function logic and edge cases.
  Golden tests provide end-to-end coverage; unit tests provide granular verification.

* * *

## References

**Books**:

- Feathers, Michael. *Working Effectively with Legacy Code*. Prentice Hall, 2004.

- Pryce, Nat & Freeman, Steve.
  *Growing Object-Oriented Software, Guided by Tests*. Addison-Wesley, 2009.

**Articles**:

- Mitchell Hashimoto, “Testing with Golden Files”:
  https://mitchellh.com/writing/golden-files

- Llewellyn Falco, Approval Testing methodology: https://approvaltests.com/

- Characterization Testing (Wikipedia):
  https://en.wikipedia.org/wiki/Characterization_test

**Tools and Frameworks**:

- Jest Snapshot Testing: https://jestjs.io/docs/snapshot-testing

- Playwright Snapshots (non-image): https://playwright.dev/docs/test-snapshots

- Go “testdata/” convention: https://pkg.go.dev/cmd/go#hdr-Test_packages

- Bazel diff-based golden tests:
  https://bazelbuild.github.io/rules_testing/overview.html

- VCR (Ruby): https://github.com/vcr/vcr

- vcrpy (Python): https://vcrpy.readthedocs.io/

- PollyJS (Netflix): https://netflix.github.io/pollyjs/

- WireMock (service virtualization): https://wiremock.org/docs/record-playback/

- insta (Rust): https://github.com/mitsuhiko/insta

- Verify (.NET): https://github.com/VerifyTests/Verify

- ScalaTest Matchers: https://www.scalatest.org/user_guide/using_matchers

- Concordion (Java): https://concordion.org/

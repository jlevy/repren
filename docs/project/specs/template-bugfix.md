# Bugfix Spec: [Description of Bug]

## Purpose

This is a bugfix template, used for planning and implementing a fix to a bug.

It should be updated during the bugfix process, then kept as a record for later context
once implementation is complete.

> AGENT INSTRUCTIONS:
> 
> This is a template. It has pre-filled sections you must fill in as you progress.
> You will fill in the bug template and then the rest of this template based on user’s
> instructions, proceeding one stage at a time:
> 
> - Stage 1: Clarifying the Bug
>
> - Stage 2: Debugging Environment and Tools
>
> - Stage 3: Investigation and Reproduction
>
> - Stage 4: Planning Stage
>
> - Stage 5: Implementation Stage
>
> - Stage 6: Validation Stage
>
> - Stage 7: Release Stage

## Background

> AGENT INSTRUCTIONS:
> 
> - Describe the relevant background on the product and why this bugfix is needed.
>
> - Reference other documentation or previous specs.

## Bug Template

> AGENT INSTRUCTIONS:
> 
> Fill in answers to the following questions, using user’s input as needed.

1. In what scenarios does this bug apply?

2. What is the current behavior?

3. What is the desired behavior?

4. Is it reproducible? If so, what are the data records, inputs, or steps to reproduce
   it?

5. Could this bug appear in other situations?

6. Should this be a complete, more systematic fix or a faster, lower-risk patch?

7. Should we make a deployment plan?
   Are there any other requirements to deploy a fix?

## Stage 1: Clarifying the Bug

> AGENT INSTRUCTIONS:
> 
> Carefully describe each of the items below based on the answers to the bug template.
> If information is incomplete, note explicit assumptions and list open questions to
> resolve.

### Current Behavior

> What is the current behavior scenario?

### Desired Behavior

> What is the desired behavior scenario?

### Ambiguities

> Are there any ambiguities in the desired behavior or the nature of the bug?

### Nature of the Fix

> Should this be a complete, more systematic fix or a faster, lower-risk patch?
> Are there any other constraints on how the fix is made?

### Scope of Testing

> What is the scope of the testing effort needed to validate the fix?

### Other Scenarios

> Are there other scenarios to consider or include in testing when making this fix?

### Questions to Investigate

> Based on the information above, are there any questions that should be investigated
> before a fix is identified?

## Stage 2: Debugging Environment and Tools

> AGENT INSTRUCTIONS:
> 
> Identify where and how to reproduce, and what instrumentation is available.
> Keep this generic; use the project’s standard tooling without naming specific
> commands.
> 
> Be sure to read all project documentation for context on setup, environments, unit
> tests, integration tests, end-to-end tests, linting, type-checking, and formatting.

### Environments and Data

> Which environments are needed (local, staging, production)?
> What data state or datasets are required (snapshots, fixtures, seed data)?
> Are any feature flags or configuration toggles relevant?

### Observability and Instrumentation

> What logs, metrics, traces, profiling tools, or DB query logs will you use?
> Do you need to add temporary instrumentation?

### Reproduction Data/Records

> List concrete inputs, records, or flows that reproduce the bug.
> Include identifiers or minimal payloads as needed.

## Stage 3: Investigation and Reproduction

> AGENT INSTRUCTIONS:
> 
> Build a minimal, reliable reproduction and gather evidence to understand scope and
> root cause candidates.

### Minimal Reproduction Steps

> Provide precise, repeatable steps to reproduce the issue.
> Aim for the smallest case that still fails.

### Evidence Collected

> Summarize logs, traces, metrics, screenshots, or other artifacts that characterize the
> failure.

### Scope and Impact

> What components, endpoints, or user flows are affected?
> Estimate severity and blast radius.

### Hypotheses and Experiments

> List suspected root causes and small experiments run to confirm/deny them.

### Further Information Needed

> What information is missing to fully understand the bug?
> How will you gather it (e.g., add logs, capture traces, inspect data)?

### Isolation Strategy

> How did you isolate the fault to a component, change, or data condition?
> What tools or techniques did you use to isolate and reproduce reliably?

## Stage 4: Fix Planning

> AGENT INSTRUCTIONS:
> 
> Compare viable fixes, weigh tradeoffs, and select a plan with clear mitigations.

### Candidate Fixes (Options)

> Option A …
> 
> Option B …

### Decision and Rationale

> State the chosen approach and why it is preferred (correctness, risk, effort,
> maintainability).

### Risks and Mitigations

> Enumerate risks (regressions, performance, data correctness) and how you will mitigate
> them (feature flag, progressive rollout, additional tests).

### Data Changes or Migrations

> Note any data corrections or migrations needed, and how they will be validated and
> rolled back if necessary.

### Compatibility Expectations

> Define backward/forward compatibility expectations if applicable, or explicitly note
> that compatibility is not required.

## Stage 5: Implementation (TDD)

> AGENT INSTRUCTIONS:
> 
> Start by writing a failing test, implement the fix, then iterate until all checks pass
> using the project’s standard testing, linting, and type-checking workflows.

### Minimal Test Case

> Describe the minimal failing test that reproduces the bug prior to the fix.
> Keep the test focused and independent from unrelated behavior.

### Tests Added or Updated

> List unit/integration tests added or updated to reproduce and guard the fix.

### Code Changes (Files to Touch)

> List files/modules to modify.
> Keep edits minimal and targeted.

### Feature Flags / Config Toggles

> Note any temporary guards or kill switches and how they are controlled.

### Documentation Updates

> Update relevant docs, comments, or runbooks.

### Confirmation of Fix

> Show that the minimal test now passes and the original failure is no longer
> reproducible. Include any additional checks performed.

## Stage 6: Validation

> AGENT INSTRUCTIONS:
> 
> Validate the fix end-to-end and ensure quality criteria are met.

### Validation Plan

> Outline final checks: automated tests, manual E2E, regression passes, performance and
> security smoke tests.

### Test Results Summary

> Summarize outcomes of the validation activities.

### Additional Tests to Prevent Recurrence

> Identify and add tests that would prevent similar regressions (e.g., edge cases,
> negative tests, property-based tests where applicable).

## Stage 7: Release

> AGENT INSTRUCTIONS:
> 
> Plan rollout, monitor post-release, and ensure you can rollback safely.

### Release Plan

> Describe rollout strategy (immediate, staged, or behind a flag) and any required
> coordination.

### Monitoring Plan

> Define dashboards/alerts to watch and specific signals of success/failure.

### Rollback Plan

> Provide a clear, quick rollback path if issues arise.
> Include data rollback if applicable.

### Approvals / Sign-offs

> Record any required approvals (code review, QA, product, operations).

### Reference Examples

> Link to previous feature specs or bugfix docs consulted as examples for style or
> process.

## Supplemental Sections

### Triage and Severity

> Severity level, priority, and SLA. Link to incident/ticket if applicable.

### Affected Versions / Components

> Versions, services, packages, or platforms impacted.

### Stakeholders and Owners

> Engineering owner, reviewers, QA, product, and any external partners.

### Out of Scope (do NOT do now)

> Explicitly list related issues or refactors not addressed by this fix to avoid scope
> creep.

### Assumptions and Open Questions

> Track assumptions and questions to resolve; update as you learn.

### Postmortem / Follow-ups

> If this was an incident, link to the postmortem and list follow-up tasks.

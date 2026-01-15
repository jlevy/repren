# Implementation Spec: [Feature or Task Title]

## Purpose

This is an implementation spec, used to track and record the implementation of a feature
or task.

This should be filled in after a Plan Spec is written.
The Plan Spec covers Stage 1 and 2 and this Implementation Spec covers Stage 3.

It should be updated during the development process, then kept as a record for later
context once implementation is complete.

**Feature Plan:** [plan-YYYY-MM-DD-feature-description.md]

## Stage 3: Implementation Stage

> AGENT INSTRUCTIONS:
> 
> - Break down to implementation and small feedback loops, with tests and features.
>
> - Clarify if any changes require backward compatibility (DO NOT preserve backward
>   compatibility unless confirmed in the spec).
>
> - Always follow test-driven development (TDD) following the Red → Green → Refactor
>   cycle. See `@tdd-guidelines.md` for complete TDD and Tidy First methodology.
>
> - Implement simplest version with working testing and then iterate.
>
> - Architecture review step post implementation
>
> - Rules:
>   
>   1. Explicitly look for duplicated code and consolidate
>
>   2. Explicitly look for dead code and remove
> 
> Add implementation plans below.
> Begin with Phases.

### Implementation Phases

> AGENT INSTRUCTIONS:
> 
> The implementation includes ongoing TDD (Test Driven Development) so should include
> testing at each phase and whenever possible.
> 
> - If there are a lot of changes required, break the changes into a few separate
>   commits, each testable and reviewable by the user, so ideally at most a few thousand
>   lines of code.
>
> - If the feature is small enough, it can be just one phase.
>   A large feature may be 3-4 phases.
>
> - The user may supply Phase breakdowns.
>   If they are not provided, you should pick 1 to 4 phases, depending on the scope of
>   the work. Small features can be one phase.

The implementation is broken into phases that may be committed and tested separately:

- Phase 1: …

- Phase 2: …

## Phase 1

### Files to Touch

> List files to be modified below.

- path1/file1.txt

- …

### Automated Testing Strategy

> Describe the steps to test this feature below.
> 
> Be sure to read the project README.md for context on formatting, linting, building,
> and testing steps for this project.

- Testing steps…

### Libraries Used

> List any new libraries that will be used in this feature below.

### Open Questions (resolve now)

> List any open questions that need to be resolved before starting work on this feature,
> then delete these instructions.

- [ ] …

### Out of Scope (do NOT do now)

> List features or aspects that are NOT part of the work described in this doc.
> List only likely next steps that are not being addressed here, to avoid accidentally
> adding features or scope creep.

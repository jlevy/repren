# Plan Spec: [Feature or Task Title]

## Purpose

This is a technical design doc used for assembling full context for feature or task and
to plan its implementation, including architecture and all key technical choices.

It should be updated during the planning process, then kept as a record for later
context once implementation is begun.

> AGENT INSTRUCTIONS:
> 
> This is a template. It has pre-filled sections you must fill in as you progress.
> 
> - You will fill this in based on user’s instructions, proceeding one stage at a time:
>   
>   - Stage 1: Planning Stage
>
>   - Stage 2: Architecture Stage
>
>   - Stage 3: Implementation Stage
>     
>     - This Stage uses test-driven development (TDD)
>
>     - Implementation may be broken into Phases
>
>     - In each Phase track progress using Markdown checkboxes for TODOs and outstanding
>       questions
>
>   - Stage 4: Validation Stage
>
> - If possible, look for a previous example of a feature spec for this project for an
>   illustration of what a complete spec looks like.

## Background

> AGENT INSTRUCTIONS:
> 
> - Describe the relevant background on the product and why this task or feature is
>   needed.
>
> - Reference other documentation or previous specs.

## Summary of Task

> AGENT INSTRUCTIONS:
> 
> - Give a concise and detailed description of the task or feature to be implemented.

## Backward Compatibility

> AGENT INSTRUCTIONS:
> 
> - Fill out this section by reading `@backward-compatibility-rules.md` for the
>   template, definitions, and guidance.
>
> - Copy the template from that file and fill in the appropriate values for each area
>   based on the feature requirements.

## Stage 1: Planning Stage

> AGENT INSTRUCTIONS:
> 
> Steps to plan this feature:
> 
> - Stage one context gathering and strategizing.
>
> - Go through project and get an understanding of current state of the features at a
>   product level
>
> - Clearly define whether to maintain backwards compatibility or not - ask users what
>   should be included in feature
>
> - Define minimum feature, make sure u have a list of not to implement, include scale
>   and scope include acceptance criteria
>
> - Review with user and clarify ambiguity.
>   Specifically around what are the feature requirements.
>   Do not add extra features unless confirmed with user
>
> - Output of this is a feature doc from product level
> 
> Add planning notes below.

## Stage 2: Architecture Stage

> AGENT INSTRUCTIONS:
> 
> - Review codebase and current technical implementation.
>   With goal of putting relevant technical context in one area either in memory or
>   current doc
>
> - List and research latest SDKs that will be relevant that we currently use as well as
>   potential ones we have to add
>
> - Read through feature doc come up with architecture design
>
> - Review with User on implementation and architecture
>
> - Update feature doc with relevant context
> 
> Add architecture plans below.

## Stage 3: Refine Architecture

> AGENT INSTRUCTIONS:
> 
> **Goal:** Find reuse opportunities to minimize new code before implementation.
> 
> **Steps:**
> 
> 1. **Find Reusable Components**
>    
>    - Search codebase for existing components, utilities, and APIs that solve similar
>      problems
>
>    - Review recent similar feature specs for patterns to follow
>
>    - Document what you found with file paths and how you’ll use them
>
> 2. **Verify Performance**
>    
>    - Check all database queries use existing indexes (no table scans)
>
>    - Estimate data transfer sizes and rendering costs
>
>    - Identify any N+1 query patterns and how to avoid them
>
> 3. **Simplify Architecture**
>    
>    - Update Stage 2 architecture to leverage reusable components found in Step 1
>
>    - Remove any planned new code that duplicates existing functionality
>
>    - Document why changes were made and code saved

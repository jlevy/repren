---
description: General Comment Rules
globs:
alwaysApply: true
---
# General Comment Rules

## Comment Usage

These are language-agnostic rules on comments:

- Keep all comments concise and clear and suitable for inclusion in final production.

- DO use comments whenever the intent of a given piece of code is subtle or confusing or
  avoids a bug or is not obvious from the code itself.

- DO NOT repeat in comments what is obvious from the names of functions or variables or
  types.

- DO NOT make any other obvious comments that duplicate messages, such as a comment that
  repeats what is in a log message.
  Do NOT DO things like this as the comment is superfluous:

  ```typescript
    // Log LLM response details
    await logger.info('llm-response', 'LLM response received', {
      contentLength: content.length,
      toolCalls: result.toolCalls?.length || 0,
      ...
  ```

- DO NOT include comments that reflect what you did, such as “Added this function” as
  this is meaningless to anyone reading the code later.
  (Instead, describe in your message to the user any other contextual information.)

- DO NOT use fancy or needlessly decorated headings like “===== MIGRATION TOOLS =====”
  in comments

- DO NOT number steps in comments.
  These are hard to maintain if the code changes.
  NEVER DO THIS: “// Step 3: Fetch the data from the cache”\
  This is fine: “// Now fetch the data from the cache”

- DO NOT use emojis or special unicode characters like ① or • or – or — in comments.

- DO NOT leave comments about code changes that have been completed.
  DO NOT leave comments like:

  ```typescript
  // BAD:
  // NOTE: Runtime context types (CoreExecCtx, AgentExecCtx, TradeCtx) have been moved to
  // convex/exec/runtimeContext.ts.
  ```

- DO NOT put values of constants in comments:

  ```typescript
  // BAD:
  const MAX_RETRIES = 5; // Maximum number of retries is 5
  
  // BAD:
  /**
   * Get current paper trading timestamp using the configured 9:00 AM ET settings.
   */
  export function getCurrentPaperTradingTimestamp(): number {
    return getPaperTradingTimestamp(new Date(), PAPER_TIMESTAMP_CONFIG);
  }
  ```

  This is redundant and clutters the code.

- DO NOT leave straggling comments that refer to past implementations or refactors.
  Remove comments that describe old behavior after code changes are complete.

  ```typescript
  // BAD:
  expect.objectContaining({
    runId: mockRunId,
    agentId: mockAgentId,
    // other fields are now removed
  });
  
  // GOOD:
  expect.objectContaining({
    runId: mockRunId,
    agentId: mockAgentId,
  });
  ```

## Comment Syntax

- Use appropriate syntax for IDE-compatible comments whenever possible, e.g. TypeScript,
  prefer `/** ... */` comments wherever appropriate on variables, functions, methods,
  and at the top of files.

- See language-specific comment rules for more details.

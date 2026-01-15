---
description: General Guidelines
globs: *.ts
alwaysApply: true
---
# TypeScript Rules

## Coding Style

- Use clear lowerCamelCase or UpperCamelCase names for functions and variables, per
  usual TypeScript conventions.

- DO NOT use fully uppercase abbreviations: Use names like `mapHistoryToLlmMessages`. DO
  NOT use names like `mapHistoryToLLMMessages`.

- DO NOT use underscore prefixes for variables that are actually used.
  Underscore prefixes should only be used for genuinely unused parameters (like
  framework callbacks).

## Docstrings

- All major functions and types should have a *concise* docstring explaining their
  purpose. They should use `\**` … `*/` style comments.

  - Focus on any rationale or purpose.

  - Do NOT state obvious things about the code.

  This should cover

  - Public types

  - Major functions

  - Convex schemas, functions, actions, mutations, and queries

  It should NOT cover:

  - Test functions

  - Trivial internal helper functions

  Example:

  ```ts
  /**
   * Render a ContextSummary as readable markdown for both LLMs and users.
   */
  export function formatContextMarkdown(
    summary: ContextSummary,
    options?: { maxHoldings?: number },
  ): string {
    ...
  }
  ```

- **Document fields in type definitions, not at usage sites.** Place documentation
  directly on type/interface fields as the single source of truth.
  Reference the type documentation elsewhere using `@see TypeName.fieldName`.

  ```ts
  // GOOD: Documentation on type definition
  interface RunConfig {
    /** When true, logs full LLM request/response payloads for debugging. */
    logLlmCalls: boolean;
    /**
     * TEST ONLY: Disables automatic scheduling of backtest steps.
     * NEVER use in production.
     */
    testSkipScheduling?: boolean;
  }
  
  // Reference it elsewhere
  export const runConfigValidator = v.object({
    logLlmCalls: v.optional(v.boolean()),
    /** @see RunConfig.testSkipScheduling for documentation */
    testSkipScheduling: v.optional(v.boolean()),
  });
  
  // BAD: Documentation duplicated at multiple usage sites
  export const runConfigValidator = v.object({
    /** When true, logs full LLM request/response payloads for debugging. */
    logLlmCalls: v.optional(v.boolean()),
    /** TEST ONLY: Disables automatic scheduling... */
    testSkipScheduling: v.optional(v.boolean()),
  });
  ```

## Type Annotations

- Don’t use `any` to types unless absolutely necessary!
  Do not add `any` types to get type checking to pass.
  Use more precise types instead.
  Then make sure type checking passes.

- Avoid `as any` and unsafe casts.
  Prefer overloads or precise types at boundaries.

  ```ts
  // BAD: Silences type safety
  const logger = createAgentLogger(ctx, agentCtx as any);
  
  // GOOD: Provide a precise input shape or overload that matches
  const logger = createAgentLogger(ctx, {
    runId: runId as Id<'runs'>,
    agentId: agentId as Id<'agents'>,
    conversationId: conversationId as Id<'conversations'>,
    experimentRunId: experimentRunId,
  });
  // Or define overloads to accept both Id<> and string shared types, and narrow internally.
  ```

- **Extract and name inline object types.** DO NOT use anonymous inline types for
  complex structures that appear in multiple places.
  Create named types in shared locations.

  ```ts
  // BAD: Inline anonymous type duplicated across functions
  interface ExecutionResults {
    tradesSummary: {
      totalTrades: number;
      successfulTrades: number;
      trades: { symbol: string; action: 'buy' | 'sell'; price: number }[];
    };
  }
  
  // GOOD: Named type in shared location
  interface FullTradeSummary {
    stats: TradeSummaryStats;
    trades: TradeDetail[];
  }
  interface ExecutionResults {
    tradesSummary: FullTradeSummary;
  }
  ```

- **Consolidate duplicate calculation logic.** DO NOT duplicate calculations of related
  metrics. Create a single function that computes all related values together.

  ```ts
  // BAD: Same calculations scattered across files
  const totalBuyValue = trades
    .filter((t) => t.action === 'buy')
    .reduce((sum, t) => sum + t.value, 0);
  const totalSellValue = trades
    .filter((t) => t.action === 'sell')
    .reduce((sum, t) => sum + t.value, 0);
  
  // GOOD: Single shared function computes all related metrics
  function computeTradeSummaryStats(trades: Trade[]): TradeSummaryStats {
    return {
      totalBuyValue: trades.filter((t) => t.action === 'buy').reduce((sum, t) => sum + t.value, 0),
      totalSellValue: trades
        .filter((t) => t.action === 'sell')
        .reduce((sum, t) => sum + t.value, 0),
      uniqueTickers: new Set(trades.map((t) => t.symbol)).size,
    };
  }
  ```

## Exhaustiveness Checks

- **Always add exhaustiveness checks to `switch` statements on discriminated union
  types.** When switching on unions (like `field.kind` or `action.type`), include a
  `default` branch that assigns to `never`. This forces a compile-time error if a new
  variant is added but not handled.

  ```ts
  // GOOD: Exhaustiveness check catches missing cases at compile time
  switch (field.kind) {
    case 'string':
      return handleString(field);
    case 'number':
      return handleNumber(field);
    // ... all cases ...
    default: {
      const _exhaustive: never = field;
      throw new Error(`Unhandled field kind: ${(_exhaustive as { kind: string }).kind}`);
    }
  }
  
  // BAD: Missing cases silently fall through or return undefined
  switch (field.kind) {
    case 'string':
      return handleString(field);
    case 'number':
      return handleNumber(field);
    // New field kinds won't cause compile errors!
  }
  
  // BAD: Default that masks missing cases
  switch (field.kind) {
    case 'string':
      return handleString(field);
    default:
      return null; // Silently handles unknown cases
  }
  ```

  This pattern ensures that when new variants are added to a union type, every `switch`
  that handles that type will fail to compile until updated.

## Function Parameters

- **Avoid optional parameters in methods where accidental omission of a value can lead
  to bugs:** This is especially true for factory functions.
  It’s better to be explicit about all parameters to ensure we don’t accidentally omit
  important context.

  Prefer explicit `| null` instead of optional parameters (`?`) when a value can be
  intentionally absent.

  Example: Don’t create default context objects as it’s easy to have them use
  misconfigured defaults!

  ```ts
  // GOOD: Explicit parameters with clear null semantics
  export function createAgentExecCtx(
    ctx: any,
    params: {
      executionType: 'live' | 'experiment';
      experimentRunId: Id<'experimentRuns'> | null; // null for live, required for experiment
      agentId: Id<'agents'>;
      runId: Id<'runs'>;
      conversationId: Id<'conversations'>;
      runConfig: RunConfig | null;
      paperTimestamp: number; // Unix timestamp in milliseconds (Date.now() format)
    },
  ): Promise<AgentExecCtx>;
  
  // BAD: Optional parameters that can lead to accidental omission
  export function createAgentExecCtx(
    ctx: any,
    type: 'live' | 'experiment',
    options?: {
      agentId?: Id<'agents'>;
      paperTimestamp?: number;
      runConfig?: RunConfig;
      experimentRunId?: Id<'experimentRuns'>;
    },
  ): Promise<AgentExecCtx>;
  ```

- Remove unused parameters after refactors.
  Do not keep placeholder params like `_ctx` unless required by a framework.

  ```ts
  // BAD: Legacy unused parameter kept
  export function doWork(_ctx: any, params: X): Y {
    /* _ctx unused */
  }
  
  // GOOD: Remove unused param and update callers
  export function doWork(params: X): Y {
    /* ... */
  }
  ```

## File Naming

- **Do NOT use non-descriptive filenames:** Avoid duplicate filenames `index.ts` for
  source modules. Prefer unique, purpose-revealing names that state what the file does.

  - Examples: Instead of `tools/index.ts`, use `tools/tool-registry.ts` (or a similarly
    descriptive name that matches its purpose).

- **Avoid creating multiple source files with the same name and different purposes:** Do
  not use the filename in different directories with different logic.
  Use unique, descriptive names to avoid confusion and make code easier to remember and
  search for.

  - For example, don’t have two files like `shared/types/runtimeTypes.ts` and
    `convex/models/runtimeTypes.ts`. Give them different names, such as
    `shared/types/appRuntimeTypes.ts` and `convex/models/runtimeValidators.ts`.

## Imports and Exports

- **Avoid dynamic imports!** Prefer static imports over dynamic imports.
  Dynamic `import()` calls are not supported in many runtime environments and make code
  less readable. ALWAYS use static imports at the top of the file unless dynamic imports
  are explicitly required and known to be supported.

  ```ts
  // BAD: Dynamic import (not supported in many runtimes)
  export const myFunction = async (args) => {
    const { helper } = await import('./helpers.js');
    return helper(args);
  };
  
  // GOOD: Static import at top of file
  import { helper } from './helpers.js';
  
  export const myFunction = async (args) => {
    return helper(args);
  };
  ```

- **Do not use inline imports** like `import('../path').Type` in function parameters.
  Import types at the top of the file.
  Again, this is better for readability and consistency.

- **Avoid re-exporting functions or types** unless explicitly done for consumers of a
  library (such as a top-level `index.ts`).

  - If a function or type is moved from one file to another, ALWAYS update all imports
    in the codebase to the location.
    DO NOT re-export types a type or other value from its old location:

    ```ts
    // BAD: Do not re-export imports for re-import elsewhere:
    export { backtestStep } from './experimentExecution';
    
    // GOOD: Import directly from the new location:
    import { backtestStep } from './experimentExecution';
    ```

- **Barrel files:** The rules differ for libraries vs applications.

  **For libraries:** Use exactly ONE barrel file — the root `index.ts` that defines the
  public API. This is essential for consumers who `import { X } from 'your-library'`. Do
  NOT create module-level barrels (like `utils/index.ts` or `harness/index.ts`).
  Internal code should import directly from source files.

  ```ts
  // BAD: Module-level barrel that just re-exports siblings
  // src/harness/index.ts
  export { FormHarness } from './harness.js';
  export { MockAgent } from './mockAgent.js';
  
  // BAD: Importing through module barrel
  import { FormHarness } from '../harness';
  
  // GOOD: Import directly from source file
  import { FormHarness } from '../harness/harness.js';
  
  // GOOD: Root index.ts for public API is fine
  // src/index.ts (package entry point)
  export { FormHarness } from './harness/harness.js';
  ```

  **For applications:** Avoid barrel files entirely.
  Apps have no public API, so barrels only add indirection.
  Import directly from source files throughout.
  If you find yourself wanting a barrel for “convenience,” that’s often a sign of
  incomplete refactors or poor module structure.

## Exceptions

- **Do not use pointless try/catch blocks:** Look for try/catch blocks like this:

  ```ts
  try {
    // ...
  } catch (error) {
    // Re-throw errors
    throw error;
  }
  ```

  Then decide which is best: (1) REMOVE them the block entirely or (2) wrap the
  exception with better message and relevant context:

  ```ts
  try {
    // ...
  } catch (error) {
    throw new Error(`Failed to do X because of Y: ${localVar.infoDetails}: ${error.message}`);
  }
  ```

## File Operations

- **Use `atomically` for writing files:** When writing files to disk, use the
  `atomically` library instead of `fs.writeFile` or `fs.writeFileSync`. This prevents
  partial or corrupted files if the process crashes mid-write.

  The `atomically` library writes to a temp file first, then renames atomically to the
  final path. This guarantees you never have half-written files.
  (`atomically` is TypeScript-native, zero third-party dependencies, slightly faster,
  has more robust error handling and retry logic than `write-file-atomic`.)

  ```ts
  // BAD: Can leave corrupted file if process crashes mid-write
  import { writeFileSync } from 'fs';
  writeFileSync(filePath, content);
  
  // GOOD: Modern TypeScript-native with zero dependencies
  import { writeFile } from 'atomically';
  await writeFile(filePath, content);
  ```

---
description: Rules and patterns for developing LLM-usable tools
applies_to: All tool development tasks
---
# Tool Development Rules

## Universal Patterns

Every tool implementation must follow these patterns:

1. **Tool Structure**

   - Use AI SDK `tool()` function from ‘ai’ package

   - Define Zod schema with `.describe()` on every field

   - Support mock mode via `runConfig?.mockApis` or feature-specific mock flag

   - Return structured response: `{ success: boolean, data: any, message: string }`

   - Handle errors with clear, actionable messages

2. **LLM-Optimized Descriptions**

   - Start with action verb: “Get...”, “Search...”, “Execute …”

   - Include usage context: “Use this to …”

   - Provide concrete examples in parameter descriptions

   - Avoid technical jargon or ambiguous terms

   - Example: “Get RSI indicator values for given symbols on a specific date.
     Use this to identify overbought/oversold conditions in backtests.”

3. **Parameter Descriptions**

   - Every Zod field must have `.describe()` with clear explanation

   - Include format examples: “Date in YYYY-MM-DD format (example: ‘2024-01-15’)”

   - Specify constraints: “Array of 1-10 stock ticker symbols”

   - Explain purpose: “Why this parameter affects the result”

4. **Backtest-Safe Tools** (for tools that support historical queries)

   - Must have date/timestamp parameter for point-in-time queries

   - Never return data from future dates

   - Must be wrapped by cutoffTimestampWrapper in toolResolver

   - Set `supportsBacktest: true` in tool registry

   - Validate all date parameters follow YYYY-MM-DD format

5. **Mock Mode Support**

   - Check `runConfig?.mockApis` for global mock mode

   - OR check feature-specific flag (e.g., `runConfig?.mockPrice`)

   - Return realistic mock data that matches real response schema

   - Document mock behavior in tool’s unit tests

## Tool Categories

Tools are categorized for UI organization and filtering:

- **market-data**: Stock prices, technical indicators, options data, fundamentals

- **news**: News search, article retrieval, sentiment analysis

- **trading**: Buy/sell execution, portfolio queries, order management

- **search**: Web search, external APIs, research tools

## Tool Registry Pattern

Every new tool requires updates in 3 locations:

1. **Tool ID Declaration** (`convex/models/toolTypes.ts`):

   ```typescript
   // Add to FUNCTION_TOOL_IDS (for custom tools) or PROVIDER_TOOL_IDS (for native tools)
   export const FUNCTION_TOOL_IDS = [
     'stock_prices_current',
     'stock_prices_historical',
     // ... existing tools
     'new_tool_id', // ← Add here
   ] as const;
   ```

2. **Tool Metadata** (`convex/models/toolRegistry.ts`):

   ```typescript
   export const TOOL_REGISTRY: Record<ToolId, ToolMetadata> = {
     // ... existing tools
     new_tool_id: {
       id: 'new_tool_id',
       name: 'Human Readable Name',
       description: 'Brief description for UI display',
       category: 'market-data', // or 'news', 'trading', 'search'
       supportsBacktest: true, // or false
       skipCutoffValidation: false, // set true only for forward-looking data (earnings dates)
     },
   };
   ```

3. **Tool Resolver** (`convex/tools/toolResolver.ts`):

   ```typescript
   import { createNewTool } from './newTool';
   
   // In resolveTools() switch statement:
   case 'new_tool_id':
     tools.new_tool_id = createNewTool(runConfig);
     break;
   ```

## Testing Requirements

Minimum test coverage for every tool:

1. **Schema Validation Tests**

   - Valid parameters accepted

   - Invalid parameters rejected with clear errors

   - Required fields enforced

   - Type checking works correctly

2. **Mock Mode Tests**

   - Returns mock data when configured

   - Mock data matches real response schema

   - Can be used in tests without API calls

3. **API Integration Tests**

   - Successful API responses parsed correctly

   - API errors handled gracefully

   - Rate limiting handled (if applicable)

   - Authentication works (if applicable)

4. **Backtest Safety Tests** (if `supportsBacktest: true`)

   - Future dates blocked by cutoff wrapper

   - Historical dates allowed

   - Date parameter validation works

5. **LLM Evaluation Tests**

   - LLM can discover when to use tool

   - LLM can construct valid parameters

   - LLM can interpret results correctly

   - LLM handles errors gracefully

   - **Target: >90% success rate across all test types**

## Common Pitfalls

Avoid these frequent mistakes:

1. **Ambiguous Tool Description**

   - Problem: LLM doesn’t know when to use tool

   - Fix: Add concrete usage examples and context

2. **Confusing Parameter Names**

   - Problem: LLM sends wrong data or guesses format

   - Fix: Use clear names and detailed `.describe()` with examples

3. **Missing Error Messages**

   - Problem: LLM doesn’t know what went wrong

   - Fix: Throw errors with specific details about what failed and why

4. **No Format Examples**

   - Problem: LLM guesses date/time formats incorrectly

   - Fix: Include explicit format in description with example

5. **Future Data Leakage**

   - Problem: Backtest results invalid due to lookahead bias

   - Fix: Validate all date params, use cutoff wrapper, test thoroughly

6. **Overly Complex Schemas**

   - Problem: LLM struggles with many optional parameters

   - Fix: Keep schemas simple, use sensible defaults, make intent clear

## Code Examples

### Basic Tool Implementation Pattern

```typescript
'use node';

import { tool } from 'ai';
import { z } from 'zod';
import { fetchExternalApi } from '../apis/externalProvider';
import type { RunConfig } from '../../shared/types/runtimeTypes';

/**
 * Creates a tool for [purpose].
 * [Brief explanation of what it does and when to use it].
 */
export function createMyTool(runConfig: RunConfig | null) {
  return tool({
    description: 'Get [what] for [inputs] [constraints]. Use this to [when/why].',
    inputSchema: z.object({
      symbols: z
        .array(z.string())
        .describe('Stock ticker symbols (e.g., ["AAPL", "MSFT"]). Provide 1-10 symbols.'),
      date: z
        .string()
        .describe('Date in YYYY-MM-DD format (example: "2024-01-15"). Must be a historical date.'),
      // ... other parameters
    }),
    execute: async ({ symbols, date }) => {
      // Check for mock mode
      if (runConfig?.mockApis) {
        return {
          success: true,
          data: {
            /* mock data matching real schema */
          },
          message: `Mock data returned for ${symbols.length} symbols`,
        };
      }

      // Real API call
      try {
        const data = await fetchExternalApi({ symbols, date });

        return {
          success: true,
          data,
          message: `Successfully fetched data for ${symbols.length} symbols as of ${date}`,
        };
      } catch (apiError) {
        const errorMessage = apiError instanceof Error ? apiError.message : String(apiError);
        throw new Error(
          `MyTool API failed for symbols [${symbols.join(', ')}] on ${date}: ${errorMessage}`,
        );
      }
    },
  });
}
```

### Test Pattern

```typescript
import { describe, test, expect } from 'vitest';
import { createMyTool } from './myTool';

describe('MyTool', () => {
  describe('Schema Validation', () => {
    test('accepts valid parameters', async () => {
      const tool = createMyTool({ mockApis: true });
      const result = await tool.execute({
        symbols: ['AAPL'],
        date: '2024-01-15',
      });
      expect(result.success).toBe(true);
    });

    test('rejects invalid date format', async () => {
      const tool = createMyTool({ mockApis: true });
      await expect(
        tool.execute({ symbols: ['AAPL'], date: '2024-01-15T00:00:00Z' }),
      ).rejects.toThrow();
    });
  });

  describe('Mock Mode', () => {
    test('returns mock data when configured', async () => {
      const tool = createMyTool({ mockApis: true });
      const result = await tool.execute({
        symbols: ['AAPL'],
        date: '2024-01-15',
      });
      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
    });
  });
});
```

## References

- Existing tool implementations: `convex/tools/stockPricesHistorical.ts`,
  `convex/tools/gdeltSearch.ts`

- Tool registry: `convex/models/toolRegistry.ts`

- Tool resolver: `convex/tools/toolResolver.ts`

- Tool documentation example: `web/docs/gdelt_tool.md`

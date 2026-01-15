## Dependency Injection Guidelines

### Overview

Convex uses a **context-passing pattern** instead of traditional dependency injection
containers. Dependencies are provided through factory functions and context objects,
aligning with Convex’s emphasis on plain TypeScript functions and functional
composition.

### Core Principles

1. **Interface-Based Design**: Always define clear interfaces for dependencies

2. **Factory Pattern**: Use factory functions to create contexts with injected
   dependencies

3. **Method Injection**: Inject functions/capabilities when creating context objects

4. **Context Passing**: Pass dependencies through context parameters, not global state

5. **Plain Functions**: Keep business logic in regular TypeScript functions with minimal
   Convex wrappers

### Dependency Injection Patterns

#### ✅ CORRECT: Factory Pattern with Method Injection

```typescript
// 1. Define interface for the dependency
interface ExecutionCtx {
  agentId: string;
  runId: string;
  timestamp: number;
  executeAction: (action: Action) => Promise<Result>;
}

// 2. Factory function creates context with injected Convex operations
function createExecutionCtx(
  ctx: ActionCtx, 
  agentId: string,
  runId: string
): ExecutionCtx {
  return {
    agentId,
    runId,
    timestamp: Date.now(),
    executeAction: async (action: Action) => {
      // Inject Convex database operations
      return await ctx.runMutation(internal.actions.execute, { 
        agentId, 
        runId, 
        action 
      });
    }
  };
}

// 3. Use in functions by accepting pre-created context
async function processAgent(ctx: ActionCtx, agentId: string) {
  const executionCtx = createExecutionCtx(ctx, agentId, runId);

  // Business logic uses the injected capabilities
  const result = await executionCtx.executeAction(someAction);
  return result;
}
```

#### ❌ FORBIDDEN: Direct Database Access in Business Logic

```typescript
// NEVER do this - business logic coupled to Convex database
async function processAgent(ctx: ActionCtx, agentId: string) {
  // Bad: Direct database access mixed with business logic
  const result = await ctx.runMutation(internal.trades.execute, { 
    agentId, 
    trades: computedTrades 
  });

  // Bad: Hard to test, tightly coupled
  return result;
}
```

#### ❌ FORBIDDEN: Global State or Service Locators

```typescript
// NEVER do this - global state breaks Convex's function model
let globalExecutor: ExecutionService;

// NEVER do this - service locator pattern
const ServiceLocator = {
  getExecutor: () => globalExecutor,
  getLogger: () => globalLogger,
};
```

### Testing with Dependency Injection

#### ✅ CORRECT: Mock Dependencies through Factory

```typescript
// Test by providing mock implementation
function createMockExecutionCtx(agentId: string): ExecutionCtx {
  return {
    agentId,
    runId: 'test-run',
    timestamp: 1234567890,
    executeAction: async (action: Action) => {
      // Mock implementation for testing
      return { success: true, result: 'mocked' };
    }
  };
}

// Test becomes simple
test('processAgent handles actions', async () => {
  const mockCtx = createMockExecutionCtx('test-agent');
  const result = await processAgentLogic(mockCtx, someAction);
  expect(result.success).toBe(true);
});
```

### Common Patterns

#### Context Creation in Entry Points

```typescript
// Entry point (public action) creates context and calls business logic
export const startAgentExecution = action({
  args: { agentId: v.id('agents'), config: v.object({...}) },
  handler: async (ctx, args) => {
    // Create context with injected Convex operations
    const executionCtx = createExecutionCtx(ctx, args.agentId, config);

    // Call plain TypeScript business logic
    return await executeAgentWorkflow(executionCtx, args.config);
  }
});

// Business logic is pure TypeScript with dependency injection
async function executeAgentWorkflow(
  ctx: ExecutionCtx, 
  config: Config
): Promise<Result> {
  // Uses injected capabilities, not direct Convex calls
  const result = await ctx.executeAction(computeAction(config));
  return result;
}
```

#### Multiple Dependencies Pattern

```typescript
interface ToolContext {
  agentId: string;
  executeQuery: (query: string) => Promise<QueryResult>;
  executeTrade: (trade: Trade) => Promise<TradeResult>;
  logEvent: (event: Event) => Promise<void>;
}

function createToolContext(ctx: ActionCtx, agentId: string): ToolContext {
  return {
    agentId,
    executeQuery: (query) => ctx.runQuery(internal.data.query, { query }),
    executeTrade: (trade) => ctx.runMutation(internal.trades.execute, { trade }),
    logEvent: (event) => ctx.runMutation(internal.logs.create, { event }),
  };
}
```

### Integration with Convex Best Practices

1. **Thin Wrappers**: Keep `action`/`mutation`/`query` functions minimal - they create
   contexts and call business logic

2. **Plain Functions**: Most logic lives in regular TypeScript functions that accept
   injected contexts

3. **No Action Chaining**: Avoid `ctx.runAction` calls; use direct function composition
   instead

4. **Function Organization**: Place business logic in `convex/lib/` or similar, Convex
   wrappers in `convex/`

### When to Use Dependency Injection

#### ✅ USE for:

- Database operations that business logic needs to perform

- External API calls or integrations

- Tool capabilities that need to be mockable for testing

- Cross-cutting concerns like logging or metrics

- Operations that vary between environments (live vs test)

#### ❌ DON’T USE for:

- Simple parameter passing (just use function parameters)

- Pure computation that doesn’t need external dependencies

- Convex context objects themselves (they’re already dependency injection)

### Key Benefits

1. **Testability**: Easy to provide mock implementations for testing

2. **Separation of Concerns**: Business logic separated from infrastructure

3. **Type Safety**: Full TypeScript inference and validation

4. **Convex Alignment**: Works naturally with Convex’s function-based architecture

5. **Flexibility**: Different contexts for different execution modes (live, test,
   experiment)

```typescript

// ========== Dependency Injection Architecture ==========

/**
 * DEPENDENCY INJECTION IN TYPESCRIPT & CONVEX: BACKGROUND & RATIONALE
 * 
 * This section documents the approach used for trade execution dependency injection,
 * explaining the patterns chosen and why they align with TypeScript and Convex best practices.
 */

/**
 * TYPESCRIPT DEPENDENCY INJECTION PATTERNS (2024-2025)
 * 
 * Modern TypeScript DI follows these key principles:
 * 
 * 1. **Interface-Based Design**: Define clear contracts between components
 * 2. **Loose Coupling**: Components receive dependencies rather than creating them
 * 3. **Method vs Constructor Injection**: 
 *    - Constructor injection: Dependencies injected at class creation (traditional)
 *    - Method injection: Dependencies provided when methods are called (functional)
 * 4. **Testability**: Easy to mock dependencies with test doubles
 * 5. **Modularity**: Promotes separation of concerns and clean architecture
 * 
 * Popular approaches include container-based DI (TypeDI, Awilix, Inversify) or
 * lightweight functional approaches using factory functions and context passing.
 */

/**
 * CONVEX FRAMEWORK APPROACH TO DEPENDENCY INJECTION
 * 
 * Convex differs from traditional frameworks by emphasizing:
 * 
 * 1. **Context Passing**: Dependencies provided through context objects (QueryCtx, MutationCtx, ActionCtx)
 * 2. **Plain TypeScript Functions**: Business logic in regular functions, thin Convex wrappers
 * 3. **Function Composition**: Direct function calls rather than action chaining
 * 4. **No Traditional DI Containers**: Uses factory functions and context injection instead
 * 
 * This approach avoids the complexity of DI containers while maintaining loose coupling
 * and testability through context abstraction and plain function composition.
 */

/**
 * TRADE EXECUTION DEPENDENCY INJECTION PATTERN
 * 
 * Our implementation uses Method Injection with Factory Pattern:
 * 
 * 1. **TradeExecutionCtx Interface**: Defines the contract for trade operations
 * 2. **createTradeExecutionCtx Factory**: Creates context with injected Convex operations  
 * 3. **Method Injection**: executeTrades function injected when context is created
 * 4. **Tool Integration**: Tools receive pre-configured execution context
 * 
 * This pattern provides:
 * - Clean separation between tool logic and database operations
 * - Easy testing via mock executeTrades functions
 * - Type safety with TypeScript interfaces
 * - Convex-native approach using context passing
 */

// Trade Context Implementation
interface TradeExecutionCtx {
  agentId: string;
  runId?: string;
  conversationTurnId?: string;
  timestamp: number;
  executeTrades: (trades: TradeWithPrice[]) => Promise<{ cashBalance: number }>;
}

// Factory function creates context with injected Convex operations
function createTradeExecutionCtx(ctx: ConvexContext, ...params): TradeExecutionCtx {
  return {
    // ... context data
    executeTrades: async (trades) => {
      // Injected implementation using Convex ctx.runMutation
      return ctx.runMutation(internal.trading.trading.applyTrades, { trades });
    }
  };
}
```

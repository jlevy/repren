# Shortcut: Update Docstrings

## Instructions

Review all major functions and types and ensure they have a concise docstring explaining
their purpose.

## What to Document

Document the following:

- Public types and interfaces

- Major functions and methods

- Convex schemas, functions, actions, mutations, and queries

- Non-obvious helper functions

## What NOT to Document

Do not add docstrings to:

- Test functions

- Trivial internal helper functions where purpose is obvious from the name

- Private implementation details that are self-explanatory

## Docstring Guidelines

1. **Focus on rationale and purpose**: It is more important to explain the “why” than
   the “what”. Only include the “what” if it is not obvious from the code.

2. **Do NOT state obvious things**: If a function is called `getUserById(id)`, do not
   write “Gets a user by ID”. Instead explain any non-obvious behavior, side effects, or
   constraints.

3. **Keep it concise**: One to three sentences is usually sufficient.
   Avoid verbose documentation that repeats parameter names or return types.

4. **Use proper syntax**: For Typescript or JavaScript, use `/** ... */` style comments
   for IDE compatibility.

5. **Use backticks**: Use `backticks` around variable names and inline code.

## Example

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

## Process

1. Scan all source files (excluding test files)

2. Identify major functions and types lacking docstrings

3. Add concise docstrings following the guidelines above

4. Review existing docstrings and remove any that are redundant or obvious

5. Run linting to ensure no syntax errors

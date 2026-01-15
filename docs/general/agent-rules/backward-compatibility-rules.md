---
description: Backward Compatibility Guidelines
globs:
alwaysApply: true
---
## Backward Compatibility Guidelines

### Types of Backward Compatibility

When making code changes, you should be aware of compatibility requirements for:

- Code compatibility internal to a single application (types and method or function
  signatures)

- API compatibility for libraries (types and method or function signatures)

- Server API compatibility (REST, GraphQL, gRPC, etc.)

- File format compatibility

- Database schema compatibility

### Backward Compatibility Template

> Use the following template when clarifying backward compatibility requirements:

For the following areas:

- “DO NOT MAINTAIN” means simply make the changes and DO NOT preserve any old stubs or
  add comments about past changes

- “KEEP DEPRECATED” means to add new features but also preserve support, function stubs,
  and comments about past changes

- “SUPPORT BOTH” means to add new features but also preserve support, function

- “MIGRATE” means to add new features but also document and use database migrations or
  automated tasks to migrate to new formats or schemas

- “N/A” means this area isn’t applicable

**BACKWARD COMPATIBILITY REQUIREMENTS:**

- **Code types, methods, and function signatures**:
  [DO NOT MAINTAIN or KEEP DEPRECATED, additional notes if necessary]

- **Library APIs**:
  [DO NOT MAINTAIN or KEEP DEPRECATED or N/A, plus any additional notes]

- **Server APIs**:
  [DO NOT MAINTAIN or KEEP DEPRECATED or N/A, plus any additional notes]

- **File formats**: [DO NOT MAINTAIN or SUPPORT BOTH or N/A, plus any additional notes]

- **Database schemas**: [DO NOT MAINTAIN or MIGRATE or N/A, plus any additional notes]

### Always Clarify Backward Compatibility Requirements

- ALWAYS be clear on backward compatibility requirements when making changes.
  These should ALWAYS be clear in any specification.

- If they are not clear, stop and ask the user for clarification.

### When Backward Compatibility Is Important

- In general, compatibility for libraries, servers, file formats and database schemas is
  VERY IMPORTANT. Compatibility and migration should be planned carefully.

- Backward compatibility and legacy support *within* a single application is usually NOT
  important and should NOT be done if it needlessly complicates code changes.
  But if not specified, it also should be clarified to be sure it is not needed.

### Single Application Code Backward Compatibility

- Unless stated in the spec or stated by the user, deprecated and backward compatibility
  code support should NOT be left after refactors to a single application repository.

- When doing normal refactoring or reorganizing code, REMOVE deprecated functions,
  methods, classes, or files completely if backward compatibility is not needed.

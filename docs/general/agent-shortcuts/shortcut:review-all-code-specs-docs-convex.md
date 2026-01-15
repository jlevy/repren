Shortcut: Review Code, Specs, and Docs (including Convex)

Instructions:

Help me walk through the codebase together to follow the flow of execution and validate
all logic is correct and that the internal specs and docs are consistent with the
current code.

Create a to-do list with the following items then perform all of them:

1. Review the architecture docs in @docs/project/architecture/ to understand the overall
   behavior of execution and persistence.

2. Review the historic specs in @docs/project/specs/done/ to understand the more about
   intent and requirements, in historic order.

3. Review the schema in web/convex/schema.ts for the Convex database schema.
   Documentation on database schema should be in comments here, to keep them close to
   the code. Reference teh tables as needed in the specs and docs.

4. Review the code, especially relevant files in web/convex to identify current
   behavior.

During all of this be sure we are following best practices as documented in the Convex
rules in @docs/general/agent-rules/ and the Convex docs and Convex best practices here:
https://docs.convex.dev/understanding/best-practices/

Then:

1. Make any suggestions to conform with Convex best practices at all times.

2. If you find inconsistencies, suggest changes to the specs or the code as appropriate.

3. If unsure of desired behavior let me know so we can clarify and update the specs.

4. Add comments close to code when possible and ensure comments are up to date and clear
   and include correct rationale.
   Avoid putting info in docs if it is in the comments.

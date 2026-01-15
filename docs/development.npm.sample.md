## Developer Workflows

> This is a sample `development.md` file describing developer workflows for agents and
> humans, using a simple npm/node project as an example.
> 
> Fill this in or adjust as needed with all information agents should routinely need
> (such as what you’d put in CLAUDE.md).

### Initial Setup

Install dependencies:

```bash
# Install all dependencies (npm workspaces installs for both root and web/)
npm install     # Installs dependencies + git hooks via prepare script
```

### Development Environment Variables

For local development, the single source of truth for secrets is `.env` (optionally
override with `.env.local`).

### Running Tests

```bash
# View all test-related scripts
npm run help | grep test

# Formatting and linting
npm run format           # Format all files
npm run lint             # Lint all files

# Common test commands
npm run precommit        # Full precommit check (codegen, format, lint, unit, integration)
npm test                 # Same as precommit
npm run test:unit        # Unit tests only
npm run test:integration # Integration tests only
npm run test:e2e         # End-to-end tests
npm run test:coverage    # Run with coverage report
```

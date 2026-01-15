# Research Brief: Modern TypeScript CLI Architecture Patterns

**Last Updated**: 2025-12-30

**Status**: Complete

**Related**:

- [Modern Python CLI Patterns](research-modern-python-cli-patterns.md) — Equivalent
  patterns for Python CLIs (Typer, Rich, UV)

- [CLI Tool Development Rules](../../agent-rules/typescript-cli-tool-rules.md) —
  Actionable rules for CLI development

- [Modern TypeScript Monorepo Package](research-modern-typescript-monorepo-patterns.md)
  — Build tooling, package structure, CI/CD

- [Commander.js Documentation](https://github.com/tj/commander.js)

- [picocolors Documentation](https://github.com/alexeyraspopov/picocolors)

- [@clack/prompts Documentation](https://github.com/bombshell-dev/clack)

* * *

## Executive Summary

This research brief documents proven architectural patterns for building maintainable
TypeScript CLI applications using Commander.js.
These patterns emerged from production CLI tools and address common challenges: code
duplication across commands, dual output modes (human-readable vs machine-parseable),
consistent error handling, and testability.

The recommended architecture uses a **Base Command pattern** with an **OutputManager**
for dual-mode output, **Handler + Command separation** for clean organization, and
**git-based versioning** for accurate version strings.

**Research Questions**:

1. How should CLI commands be structured to minimize code duplication?

2. What patterns support both human-readable and JSON output modes?

3. How should version information be derived for CLI tools?

4. What directory structure best organizes CLI code in a library/CLI hybrid package?

* * *

## Research Methodology

### Approach

Patterns were extracted from production TypeScript CLI tools, analyzed for common
solutions to recurring problems, and documented with complete implementation examples.

### Sources

- Production CLI implementations in TypeScript monorepos

- Commander.js best practices and documentation

- Unix philosophy for output handling (stdout vs stderr)

- npm versioning conventions and semver sorting requirements

* * *

## Research Findings

### 1. Directory Structure

**Status**: Recommended

**Details**:

Organize CLI code for maintainability with clear separation between commands, shared
utilities, and type definitions:

```
scripts/cli/
├── cli.ts                  # Main entry point, program setup
├── commands/               # Command implementations (one file per command group)
│   ├── my-feature.ts       # Command with subcommands
│   └── simple-cmd.ts       # Simple single command
├── lib/                    # Shared utilities and base classes
│   ├── baseCommand.ts      # Base class for handlers
│   ├── outputManager.ts    # Unified output handling
│   ├── commandContext.ts   # Global option management
│   ├── *Formatters.ts      # Domain-specific formatters
│   └── shared.ts           # General utilities
└── types/
    └── commandOptions.ts   # Named types for command options
```

**Assessment**: This structure scales well from small CLIs to large ones with many
commands.
The `lib/` directory prevents code duplication, while `types/` keeps TypeScript
interfaces organized.

* * *

### 2. Agent & Automation Compatibility

**Status**: Strongly Recommended

**Details**:

Modern CLIs must work reliably in three execution contexts:

| Mode | Context | Behavior |
| --- | --- | --- |
| **Interactive (TTY)** | Human at terminal | Prompts, spinners, colored output allowed |
| **Non-interactive (headless)** | CI, scripts, agent runners | No prompts, deterministic output, fail-fast |
| **Protocol mode** | MCP/JSON-RPC adapters | Structured I/O only (future extension) |

**Key flags for automation**:

```ts
program
  .option('--non-interactive', 'Disable all prompts, fail if input required')
  .option('--yes', 'Assume yes to confirmation prompts')
  .option('--format <format>', 'Output format: text, json, or jsonl', 'text');
```

**Behavior contract**:

- If `--non-interactive` is set, stdin is not a TTY, or `CI` env var is set, **never
  prompt**

- If required values are missing, exit with code `2` and a structured error:

```ts
// Exit with actionable error for missing required input
if (!options.name && !process.stdin.isTTY) {
  console.error(JSON.stringify({
    error: 'Missing required input',
    missing: ['name'],
    hint: 'Provide --name or run interactively'
  }));
  process.exit(2);
}
```

- `--yes` skips confirmations but does **not** conjure missing required fields

- Respect `CI` environment variable (set by GitHub Actions, GitLab CI, CircleCI, Travis,
  and most CI systems):

```ts
function isCI(): boolean {
  return Boolean(process.env.CI);
}

function isInteractive(): boolean {
  return process.stdin.isTTY && !isCI();
}
```

- Support `NO_COLOR` environment variable (see [no-color.org](https://no-color.org/)):

```ts
function shouldColorize(colorOption: 'auto' | 'always' | 'never'): boolean {
  if (process.env.NO_COLOR) return false;  // Respect NO_COLOR
  if (colorOption === 'always') return true;
  if (colorOption === 'never') return false;
  return process.stdout.isTTY ?? false;
}
```

**Self-documentation for agents** (optional but high-value):

```ts
// Machine-readable command schema
const schemaCommand = new Command('schema')
  .argument('<command>', 'Command to describe')
  .description('Output JSON Schema for command inputs')
  .action((commandName) => {
    const schema = getCommandSchema(commandName);
    console.log(JSON.stringify(schema, null, 2));
  });

// Machine-readable examples
const examplesCommand = new Command('examples')
  .argument('<command>', 'Command to show examples for')
  .description('Output example invocations as JSON')
  .action((commandName) => {
    const examples = getCommandExamples(commandName);
    console.log(JSON.stringify(examples, null, 2));
  });
```

**Critical: Disable spinners and progress output for agents**

Spinners and progress indicators are a severe antipattern in non-interactive contexts.
When an AI coding agent (Claude Code, Cursor, Copilot, etc.)
invokes a CLI, any spinner output—even partial line rewrites via ANSI escape codes—gets
captured as text and floods the agent’s context window.
A single long-running command with an active spinner can generate thousands of lines of
captured output, rapidly exhausting context and degrading agent performance.

```ts
// ALWAYS check TTY before showing progress
if (!process.stderr.isTTY) {
  // No spinners, no progress bars, no animations
}

// Provide explicit flag for agent-driven invocations
program.option('--no-progress', 'Disable all progress output (for agent/script use)');

// In OutputManager, respect both TTY detection AND explicit flag
spinner(message: string): Spinner {
  if (this.noProgress || !process.stderr.isTTY) {
    return { message: () => {}, stop: () => {} };  // Silent no-op
  }
  // ...create actual spinner
}
```

Key requirements:

- **Always check `isTTY`** before any spinner/progress output

- **Provide `--no-progress` flag** for explicit disabling (agents may run in
  pseudo-TTYs)

- **Default to silent** when in doubt—missing progress output is far better than flooded
  context

- **Never use carriage returns (`\r`) or ANSI cursor movement** in non-TTY mode

**Assessment**: Explicit automation support enables CLIs to work reliably with AI
agents, CI pipelines, and scripted workflows without TTY hacks or brittle parsing.

* * *

### 3. Base Command Pattern

**Status**: Strongly Recommended

**Details**:

Use a base class to eliminate duplicate code across commands.
This pattern centralizes:

- Command context extraction

- Output management initialization

- Client/API connection handling

- Error handling with consistent formatting

- Dry-run checking

```ts
// lib/errors.ts
export class CLIError extends Error {
  constructor(
    message: string,
    public exitCode: number = 1
  ) {
    super(message);
    this.name = 'CLIError';
  }
}

export class ValidationError extends CLIError {
  constructor(message: string) {
    super(message, 2);  // Exit code 2 for usage/validation errors
  }
}

// lib/baseCommand.ts
export abstract class BaseCommand {
  protected ctx: CommandContext;
  protected output: OutputManager;
  private client?: HttpClient;

  constructor(command: Command, format: OutputFormat) {
    this.ctx = getCommandContext(command);
    this.output = new OutputManager({ format, ...this.ctx });
  }

  protected getClient(): HttpClient {
    if (!this.client) {
      this.client = new HttpClient(getApiUrl());
    }
    return this.client;
  }

  // Throws CLIError instead of calling process.exit - handled at entrypoint
  protected async execute<T>(
    action: () => Promise<T>,
    errorMessage: string
  ): Promise<T> {
    try {
      return await action();
    } catch (error) {
      this.output.error(errorMessage, error);
      throw new CLIError(errorMessage);
    }
  }

  protected checkDryRun(message: string, details?: object): boolean {
    if (this.ctx.dryRun) {
      logDryRun(message, details);
      return true;
    }
    return false;
  }

  abstract run(options: unknown): Promise<void>;
}

// CLI entrypoint - single place for exit handling
async function main() {
  try {
    await program.parseAsync(process.argv);
  } catch (error) {
    if (error instanceof CLIError) {
      process.exit(error.exitCode);
    }
    console.error('Unexpected error:', error);
    process.exit(1);
  }
}

// Handle SIGINT (Ctrl+C)
process.on('SIGINT', () => {
  console.error('\nInterrupted');
  process.exit(130);  // 128 + SIGINT(2)
});

main();
```

**Exit code conventions** (aligned with Unix standards):

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | Operational error (API failed, file not found) |
| 2 | Validation/usage error (missing argument, invalid option) |
| 130 | Interrupted (SIGINT / Ctrl+C) |

**Assessment**: The Base Command pattern dramatically reduces boilerplate.
New commands inherit consistent behavior for error handling, dry-run support, and output
formatting. Throwing typed errors instead of calling `process.exit()` improves
testability and ensures proper resource cleanup.

* * *

### 4. Dual Output Mode (Text + JSON)

**Status**: Strongly Recommended

**Details**:

Support both human-readable and machine-parseable output through an OutputManager class
that handles format switching transparently:

```ts
// lib/outputManager.ts
export class OutputManager {
  private format: 'text' | 'json';
  private quiet: boolean;
  private verbose: boolean;

  // Structured data - always goes to stdout
  data<T>(data: T, textFormatter?: (data: T) => void): void {
    if (this.format === 'json') {
      console.log(JSON.stringify(data, null, 2));
    } else if (textFormatter) {
      textFormatter(data);
    }
  }

  // Status messages - text mode only, stdout
  success(message: string): void {
    if (this.format === 'text' && !this.quiet) {
      p.log.success(message);
    }
  }

  // Errors - always stderr, always shown
  error(message: string, err?: Error): void {
    if (this.format === 'json') {
      console.error(JSON.stringify({ error: message, details: err?.message }));
    } else {
      console.error(colors.error(`Error: ${message}`));
    }
  }

  // Spinner - returns no-op in JSON/quiet mode or non-TTY
  spinner(message: string): Spinner {
    if (this.format === 'text' && !this.quiet && process.stderr.isTTY) {
      const s = p.spinner();
      s.start(message);
      return { message: (m) => s.message(m), stop: (m) => s.stop(m) };
    }
    return { message: () => {}, stop: () => {} };
  }
}
```

**Key principles**:

| Output Type | Destination | When Shown |
| --- | --- | --- |
| Data (results) | stdout | Always |
| Success messages | stdout | Text mode, not quiet |
| Errors | stderr | Always |
| Warnings | stderr | Always |
| Spinners/progress | stderr | Text mode, TTY only |

**Note**: Spinners and progress indicators go to **stderr** to keep stdout clean for
pipeable data. Disable them entirely when stdout is not a TTY (prevents corruption in
`my-cli list | jq ...` scenarios).

**Assessment**: This pattern enables Unix pipeline compatibility
(`my-cli list --format json | jq '.items[]'`) while providing rich interactive output
for terminal users.

* * *

### 5. Handler + Command Structure

**Status**: Recommended

**Details**:

Separate command definitions from implementation for cleaner code organization:

```ts
// commands/my-feature.ts

// 1. Handler class (extends BaseCommand)
class MyFeatureListHandler extends BaseCommand {
  async run(options: MyFeatureListOptions): Promise<void> {
    // Implementation
  }
}

// 2. Subcommand definition
const listCommand = withColoredHelp(new Command('list'))
  .description('List resources')
  .option('--limit <number>', 'Maximum results', '20')
  .action(async (options, command) => {
    setupDebug(getCommandContext(command));
    const format = validateFormat(options.format);
    const handler = new MyFeatureListHandler(command, format);
    await handler.run(options);
  });

// 3. Main command export (aggregates subcommands)
export const myFeatureCommand = withColoredHelp(new Command('my-feature'))
  .description('Manage resources')
  .addCommand(listCommand)
  .addCommand(showCommand)
  .addCommand(createCommand);
```

**Assessment**: This separation keeps command registration concise while allowing
complex handler logic.
The handler class is testable in isolation.

* * *

### 6. Named Option Types

**Status**: Recommended

**Details**:

Use named interfaces for command options to get TypeScript type checking:

```ts
// types/commandOptions.ts
export interface MyFeatureListOptions {
  limit: number;  // Coerced at parse time, not string
  status: string | null;
  verbose: boolean;
}

export interface MyFeatureCreateOptions {
  name: string;
  description: string | null;
}
```

**Option coercion** (parse values in Commander, not handlers):

```ts
// lib/parsers.ts - Wrapper needed because parseInt takes 2 args
const parseIntOption = (value: string): number => {
  const parsed = parseInt(value, 10);
  if (isNaN(parsed)) {
    throw new InvalidArgumentError('Not a number');
  }
  return parsed;
};

// commands/my-feature.ts
const listCommand = new Command('list')
  .option('--limit <number>', 'Maximum results', parseIntOption, 20)
  .option('--status <status>', 'Filter by status')
  .action(async (options: MyFeatureListOptions) => {
    // options.limit is already a number, no parsing needed
    const handler = new MyFeatureListHandler(command, format);
    await handler.run(options);
  });
```

**Assessment**: Named option types catch typos at compile time and provide autocomplete
in editors. Parsing options at the Commander layer (via coercion functions) keeps
handlers clean and ensures consistent validation across commands.

* * *

### 7. Formatter Pattern

**Status**: Recommended

**Details**:

Pair text and JSON formatters for each domain.
Text formatters handle human-readable display; JSON formatters structure data for
machine consumption:

```ts
// lib/myFeatureFormatters.ts

// Text formatter - for human-readable output
export function displayMyFeatureList(items: Item[], ctx: CommandContext): void {
  if (items.length === 0) {
    p.log.info('No items found');
    return;
  }

  const table = createStandardTable(['ID', 'Name', 'Status']);
  for (const item of items) {
    table.push([item.id, item.name, formatStatus(item.status)]);
  }
  p.log.message('\n' + table.toString());
}

// JSON formatter - structured data for machine consumption
export function formatMyFeatureListJson(items: Item[]): object {
  return {
    total: items.length,
    items: items.map(item => ({
      id: item.id,
      name: item.name,
      status: item.status,
    })),
  };
}

// Usage in handler:
this.output.data(
  formatMyFeatureListJson(items),  // JSON format
  () => displayMyFeatureList(items, this.ctx)  // Text format
);
```

**Assessment**: Separating formatters makes them reusable and testable.
The JSON formatter defines the contract for machine consumers.

* * *

### 8. Version Handling

**Status**: Recommended

**Details**:

CLI tools should display accurate version information via `--version`. Use the `VERSION`
constant injected at build time via dynamic git-based versioning.

For the complete versioning implementation (format, rationale, and `getGitVersion()`
function), see
[Dynamic Git-Based Versioning](research-modern-typescript-monorepo-patterns.md#dynamic-git-based-versioning)
in the monorepo patterns doc.

**CLI integration**:

```ts
// Import the build-time injected VERSION constant
import { VERSION } from '../index.js';

const program = new Command()
  .name('my-cli')
  .version(VERSION, '--version', 'Show version number')
  // ...
```

**Key points**:

- Use the exported `VERSION` constant from your library entry point

- Commander.js reserves `-V` and `--version` by default

- Avoid `-v` alias for other options (conflicts with version in some setups)

**Assessment**: Centralizing version in the library (injected at build time) ensures CLI
and programmatic consumers see the same version.

* * *

### 9. Global Options

**Status**: Recommended

**Details**:

Define global options once at the program level, not on individual commands:

```ts
// cli.ts
const program = new Command()
  .name('my-cli')
  .version(getVersionInfo().version)
  .option('--dry-run', 'Show what would be done without making changes')
  .option('--verbose', 'Enable verbose output')
  .option('--quiet', 'Suppress non-essential output')
  .option('--format <format>', 'Output format: text, json, or jsonl', 'text')
  .option('--color <when>', 'Colorize output: auto, always, never', 'auto')
  .option('--non-interactive', 'Disable all prompts, fail if input required')
  .option('--yes', 'Assume yes to confirmation prompts');

// Access via getCommandContext() in any command:
export function getCommandContext(command: Command): CommandContext {
  const opts = command.optsWithGlobals();
  const isCI = Boolean(process.env.CI);
  return {
    dryRun: opts.dryRun ?? false,
    verbose: opts.verbose ?? false,
    quiet: opts.quiet ?? false,
    format: opts.format ?? 'text',
    color: opts.color ?? 'auto',
    nonInteractive: opts.nonInteractive ?? !process.stdin.isTTY ?? isCI,
    yes: opts.yes ?? false,
  };
}
```

**Color output handling:**

The `--color` option follows the Unix convention used by `git`, `ls`, `grep`:

- `auto` (default): Enable colors when stdout is a TTY, disable when piped/redirected

- `always`: Force colors (useful for `less -R` or capturing colored output)

- `never`: Disable colors entirely

Also respect the `NO_COLOR` environment variable (see
[no-color.org](https://no-color.org/)):

```ts
// lib/colors.ts
export function shouldColorize(colorOption: 'auto' | 'always' | 'never'): boolean {
  // NO_COLOR takes precedence (unless --color=always explicitly set)
  if (process.env.NO_COLOR && colorOption !== 'always') return false;
  if (colorOption === 'always') return true;
  if (colorOption === 'never') return false;
  return process.stdout.isTTY ?? false;
}
```

**Alternative: `--json` flag:**

Some CLIs use a simpler `--json` boolean flag instead of `--format`. This is less
extensible but more concise for the common case:

```ts
.option('--json', 'Output as JSON')
```

**Assessment**: Centralizing global options ensures consistency and prevents option name
conflicts across commands.

* * *

### 10. Avoid Single-Letter Option Aliases

**Status**: Recommended (with exceptions)

**Details**:

Use full option names to prevent conflicts in large CLIs:

```ts
// GOOD: Full names only
program
  .option('--dry-run', 'Show what would be done')
  .option('--verbose', 'Enable verbose output')
  .option('--quiet', 'Suppress output')

// AVOID: Single-letter aliases
program
  .option('-d, --dry-run', 'Show what would be done')  // -d might conflict
  .option('-v, --verbose', 'Verbose output')           // -v used by --version
```

**Exception: Backward compatibility**

When building a drop-in replacement for an existing CLI, preserve single-letter aliases
to maintain compatibility with existing scripts and muscle memory:

```ts
// OK when matching existing CLI (e.g., replacing `bd` with `cead`)
.option('-t, --type <type>', 'Issue type')      // Matches original CLI
.option('-p, --priority <n>', 'Priority level') // Matches original CLI
```

Document which aliases exist for compatibility vs which are native to your CLI.

**Assessment**: Single-letter aliases seem convenient but cause conflicts as CLIs grow.
Full names are self-documenting and avoid collisions.
However, backward compatibility with an existing CLI is a valid reason to use them.

* * *

### 11. Show Help After Errors

**Status**: Recommended

**Details**:

Configure Commander.js to display help after usage errors.
This helps users understand what went wrong and how to correctly use the command:

```ts
// In program setup (affects all commands)
const program = new Command()
  .name('my-cli')
  .showHelpAfterError()  // Show full help after errors
  // ... other options

// Or with a custom hint message (more concise)
program.showHelpAfterError('(add --help for additional information)');
```

This provides a better user experience when required arguments are missing or options
are invalid:

```console
$ my-cli research
error: missing required argument 'input'

Usage: my-cli research [options] <input>

Fill a form using a web-search-enabled model

Options:
  --model <provider/model>  Model to use (required)
  -h, --help                display help for command
```

When configured on the root program, this behavior propagates to all subcommands
automatically.

**Assessment**: This small configuration change significantly improves user experience
when commands are misused.

* * *

### 12. Stdout/Stderr Separation

**Status**: Essential

**Details**:

Route output appropriately for Unix pipeline compatibility:

```ts
// Data/success → stdout (can be piped)
console.log(JSON.stringify(data));
this.output.success('Operation complete');

// Errors/warnings → stderr (visible even when piped)
console.error('Error: something failed');
this.output.warn('Deprecated option');

// This enables: my-cli list --format json | jq '.items[]'
```

**Assessment**: Proper stdout/stderr separation is fundamental to Unix philosophy and
enables CLI tools to be composed in pipelines.

* * *

### 13. Testing with Dry-Run

**Status**: Recommended

**Details**:

Design commands to be testable via `--dry-run`:

```ts
class MyCommandHandler extends BaseCommand {
  async run(options: Options): Promise<void> {
    // Check dry-run early and return
    if (this.checkDryRun('Would create resource', {
      name: options.name,
      config: options.config,
    })) {
      return;
    }

    // Actual implementation only runs if not dry-run
    await this.createResource(options);
  }
}

// Test script can verify all commands with:
// my-cli resource create --name test --dry-run
// my-cli resource delete --id res-123 --dry-run
```

**Assessment**: Dry-run support enables safe testing of destructive commands and helps
users verify what a command will do before executing it.

* * *

### 14. Preaction Hooks

**Status**: Situational

**Details**:

Use Commander.js hooks for cross-cutting concerns like codegen or logging setup:

```ts
program.hook('preAction', (thisCommand) => {
  const commandName = thisCommand.name();

  // Run codegen before commands that need it
  if (!['help', 'docs', 'version'].includes(commandName)) {
    runCodegenIfNeeded({ silent: true });
  }

  // Set up logging based on verbose flag
  if (thisCommand.optsWithGlobals().verbose) {
    process.env.DEBUG = 'true';
  }
});
```

**Assessment**: Preaction hooks are useful for setup that should run before any command
but shouldn’t be duplicated in each command handler.

* * *

### 15. Documentation Command

**Status**: Recommended

**Details**:

Add a `docs` command that shows comprehensive help for all commands:

```ts
const docsCommand = new Command('docs')
  .description('Show full documentation for all commands')
  .action(async () => {
    let output = '';
    output += formatMainHelp(program);

    for (const cmd of program.commands) {
      output += formatCommandHelp(cmd);
      for (const subcmd of cmd.commands) {
        output += formatCommandHelp(subcmd);
      }
    }

    // Use pager for long output
    await showInPager(output);
  });
```

**Assessment**: A docs command provides a single reference for all CLI functionality,
which is especially valuable for CLIs with many subcommands.

* * *

### 16. Testing CLI Commands

**Status**: Recommended

**Details**:

Test CLI commands by invoking them as subprocesses and verifying exit codes, stdout, and
stderr:

```ts
// tests/cli.test.ts
import { execSync, spawnSync } from 'child_process';
import { describe, it, expect } from 'vitest';  // or node:test

describe('CLI', () => {
  const cli = (args: string) =>
    spawnSync('node', ['./dist/cli.js', ...args.split(' ')], {
      encoding: 'utf-8',
    });

  it('returns exit code 0 on success', () => {
    const result = cli('list --format json');
    expect(result.status).toBe(0);
  });

  it('outputs valid JSON in json format', () => {
    const result = cli('list --format json');
    expect(result.status).toBe(0);
    const data = JSON.parse(result.stdout);
    expect(data).toHaveProperty('items');
  });

  it('returns exit code 2 for missing required args', () => {
    const result = cli('create');  // Missing --name
    expect(result.status).toBe(2);
  });

  it('outputs errors to stderr while keeping stdout parseable', () => {
    const result = cli('show --id invalid-id --format json');
    expect(result.stderr).toContain('error');
    // stdout should still be valid (empty or error JSON)
    if (result.stdout.trim()) {
      expect(() => JSON.parse(result.stdout)).not.toThrow();
    }
  });

  it('respects --dry-run flag', () => {
    const result = cli('delete --id test-123 --dry-run');
    expect(result.status).toBe(0);
    expect(result.stdout).toContain('DRY-RUN');
  });
});
```

**Assessment**: Testing CLIs as subprocesses validates the full user experience
including argument parsing, exit codes, and output streams.
Use `--format json` for assertions to avoid brittle text parsing.

* * *

## Best Practices Summary

1. **Support agent/automation modes** with `--non-interactive`, `--yes`, and
   `--no-progress` flags; also respect `CI` env var

2. **Disable spinners/progress in non-TTY** — agent context window flooding is a severe
   antipattern

3. **Use Base Command pattern** to eliminate boilerplate across commands

4. **Support dual output modes** (text, JSON, jsonl) through OutputManager

5. **Throw typed errors** (CLIError), handle exits only at entrypoint

6. **Use standard exit codes**: 0 success, 1 error, 2 validation, 130 interrupted

7. **Route output correctly**: data to stdout, spinners/errors to stderr

8. **Separate handlers from command definitions** for testability

9. **Use named option types** with coercion for TypeScript safety

10. **Pair text and JSON formatters** for each data domain

11. **Use build-time VERSION constant** from library (see
    [monorepo patterns](research-modern-typescript-monorepo-patterns.md#dynamic-git-based-versioning))

12. **Define global options at program level** only

13. **Support `--color auto|always|never`** and respect `NO_COLOR` env var

14. **Avoid single-letter aliases** to prevent conflicts (exception: backward compat)

15. **Show help after errors** for better UX

16. **Support --dry-run** for safe testing of destructive commands

17. **Test CLI as subprocess** verifying exit codes, stdout JSON validity, stderr errors

18. **Add docs/schema/examples commands** for human and machine documentation

* * *

## References

### Documentation

- [Commander.js](https://github.com/tj/commander.js) — CLI framework

- [picocolors](https://github.com/alexeyraspopov/picocolors) — Terminal colors

- [@clack/prompts](https://github.com/bombshell-dev/clack) — Interactive prompts

- [cli-table3](https://github.com/cli-table/cli-table3) — Table formatting

### Related Documentation

- [Modern Python CLI Patterns](research-modern-python-cli-patterns.md) — Equivalent
  patterns for Python CLIs (Typer, Rich, UV)

- [CLI Tool Development Rules](../../agent-rules/typescript-cli-tool-rules.md) —
  Actionable rules for CLI development

- [Modern TypeScript Monorepo Package](research-modern-typescript-monorepo-patterns.md)
  — Build tooling, package exports, CI/CD

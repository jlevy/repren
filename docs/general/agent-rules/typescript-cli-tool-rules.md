---
description: CLI Tool Development Rules
globs: scripts/cli/**/*.ts, scripts/test-*.ts, scripts/*-cli.ts
alwaysApply: false
---
# CLI Tool Development Rules

These rules apply to all CLI tools, command-line scripts, and terminal utilities.

## Color and Output Formatting

- **ALWAYS use picocolors for terminal colors:** Import `picocolors` (aliased as `pc`)
  for all color and styling needs.
  NEVER use hardcoded ANSI escape codes like `\x1b[36m` or `\033[32m`.

  ```ts
  // GOOD: Use picocolors
  import pc from 'picocolors';
  console.log(pc.green('Success!'));
  console.log(pc.cyan('Info message'));
  
  // BAD: Hardcoded ANSI codes
  console.log('\x1b[32mSuccess!\x1b[0m');
  console.log('\x1b[36mInfo message\x1b[0m');
  ```

- **Use shared color utilities:** Create a shared formatting module for consistent color
  application across commands.

  ```ts
  // lib/cliFormatting.ts - shared color utilities
  import pc from 'picocolors';
  
  export const colors = {
    success: (s: string) => pc.green(s),
    error: (s: string) => pc.red(s),
    info: (s: string) => pc.cyan(s),
    warn: (s: string) => pc.yellow(s),
    muted: (s: string) => pc.gray(s),
  };
  
  // Usage in commands:
  import { colors } from '../lib/cliFormatting.js';
  console.log(colors.success('Operation completed'));
  ```

- **Trust picocolors TTY detection:** Picocolors automatically detects when stdout is
  not a TTY (e.g., piped to `cat` or redirected to a file) and disables colors.
  DO NOT manually check `process.stdout.isTTY` unless you need special non-color
  behavior.

  Picocolors respects:

  - `NO_COLOR=1` environment variable (disables colors)

  - `FORCE_COLOR=1` environment variable (forces colors)

  - `--no-color` and `--color` command-line flags (if implemented)

  - TTY detection via `process.stdout.isTTY`

  ```ts
  // GOOD: Let picocolors handle it automatically
  import pc from 'picocolors';
  console.log(pc.green('This works correctly in all contexts'));
  
  // BAD: Manual TTY checking (redundant with picocolors)
  const useColors = process.stdout.isTTY;
  const msg = useColors ? '\x1b[32mSuccess\x1b[0m' : 'Success';
  console.log(msg);
  ```

## Commander.js Patterns

- **Use Commander.js for all CLI tools:** Import from `commander` and follow established
  patterns for command registration and option handling.

- **Apply colored help to all commands:** Use `withColoredHelp()` wrapper from shared
  utilities to ensure consistent help text formatting.

  ```ts
  import { Command } from 'commander';
  import { withColoredHelp } from '../lib/shared.js';
  
  export const myCommand = withColoredHelp(new Command('my-command'))
    .description('Description here')
    .action(async (options, command) => {
      // Implementation
    });
  ```

- **Use shared context helpers:** Create utilities like `getCommandContext()`,
  `setupDebug()`, and `logDryRun()` in a shared module for consistent behavior.

  ```ts
  import { getCommandContext, setupDebug, logDryRun } from '../lib/shared.js';
  
  .action(async (options, command) => {
    const ctx = getCommandContext(command);
    setupDebug(ctx);
  
    if (ctx.dryRun) {
      logDryRun('Would perform action', { details: 'here' });
      return;
    }
  
    // Actual implementation
  });
  ```

- **Support `--dry-run`, `--verbose`, and `--quiet` flags:** These are global options
  defined at the program level.
  Access them via `getCommandContext()`.

## Progress and Feedback

- **Use @clack/prompts for interactive UI:** Import `@clack/prompts` as `p` for
  spinners, prompts, and status messages.

  ```ts
  import * as p from '@clack/prompts';
  
  p.intro('🧪 Starting test suite');
  
  const spinner = p.spinner();
  spinner.start('Processing data');
  // ... work ...
  spinner.stop('✅ Data processed');
  
  p.outro('All done!');
  ```

- **Use consistent logging methods:**

  - `p.log.info()` for informational messages

  - `p.log.success()` for successful operations

  - `p.log.warn()` for warnings

  - `p.log.error()` for errors

  - `p.log.step()` for step-by-step progress

- **Use appropriate emojis for status:** Follow emoji conventions from
  `@docs/general/agent-rules/general-style-rules.md`:

  - ✅ for success

  - ❌ for failure/error

  - ⚠️ for warnings

  - ⏰ for timing information

  - 🧪 for tests

## Timing and Performance

- **Display timing for long operations:** For operations that take multiple seconds,
  display timing information using the ⏰ emoji and colored output.

  ```ts
  const start = Date.now();
  // ... operation ...
  const duration = ((Date.now() - start) / 1000).toFixed(1);
  console.log(colors.cyan(`⏰ Operation completed: ${duration}s`));
  ```

- **Show total time for multi-step operations:** For scripts that run multiple phases
  (like test suites), show individual phase times and a total.

  ```ts
  console.log(colors.cyan(`⏰ Phase 1: ${phase1Time}s`));
  console.log(colors.cyan(`⏰ Phase 2: ${phase2Time}s`));
  console.log('');
  console.log(colors.green(`⏰ Total time: ${totalTime}s`));
  ```

## Script Structure

- **Use TypeScript for all CLI scripts:** Write scripts as `.ts` files with proper
  types. Use `#!/usr/bin/env tsx` shebang for executable scripts.

  ```ts
  #!/usr/bin/env tsx
  
  /**
   * Script description here.
   */
  
  import { execSync } from 'node:child_process';
  import * as p from '@clack/prompts';
  
  async function main() {
    // Implementation
  }
  
  main().catch((err) => {
    p.log.error(`Script failed: ${err}`);
    process.exit(1);
  });
  ```

- **Handle errors gracefully:** Always catch errors at the top level and provide clear
  error messages before exiting.

  ```ts
  main().catch((err) => {
    p.log.error(`Operation failed: ${err.message || err}`);
    process.exit(1);
  });
  ```

- **Exit with proper codes:** Use `process.exit(0)` for success and `process.exit(1)`
  for failures. This is important for CI/CD pipelines and shell scripts.

## File Naming

- **Use descriptive kebab-case names:** CLI script files should use kebab-case with
  clear purpose indicators.

  - Examples: `test-with-timings.ts`, `test-all-commands.ts`, `generate-config-data.ts`

- **Organize commands in a `commands/` directory:** Keep command implementations
  organized with one file per command or command group.

## Documentation

- **Document CLI scripts with file-level comments:** Include a brief description of what
  the script does at the top of the file.

  ```ts
  /**
   * Test Runner with Timing
   *
   * Runs the full test suite (codegen, format, lint, unit, integration)
   * and displays timing information for each phase.
   */
  ```

- **Add help text to all commands and options:** Use `.description()` for commands and
  options to provide clear help text.

  ```ts
  .option('--mode <mode>', 'Mock mode: real or full_fixed')
  .option('--output-dir <path>', 'Output directory', './runs')
  ```

## Environment Variables

When supporting environment variables, especially those used by SDK libraries (like
`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.), also support `.env` loading so CLIs work
seamlessly in local dev and in remote environments.

- **Add dotenv as a dependency:** Add `dotenv` to your project dependencies for `.env`
  file loading.

- **Load `.env.local` and `.env` automatically (recommended):** Support both
  `.env.local` and `.env` automatically, with `.env.local` taking precedence over
  `.env`.

- **Manual dotenv loading:** For standalone scripts that don’t use `vite-node`, load
  environment files manually with explicit precedence:

  ```ts
  import dotenv from 'dotenv';
  import { existsSync } from 'node:fs';
  
  // Load .env.local first (higher priority), then .env (lower priority).
  // Note: dotenv does NOT override existing values by default, so load higher-priority
  // first.
  if (existsSync('.env.local')) {
    dotenv.config({ path: '.env.local' });
  }
  if (existsSync('.env')) {
    dotenv.config({ path: '.env' });
  }
  ```

- **Fail fast with clear errors:** If a required env var is missing, throw immediately
  with a message listing all accepted variable names.

- **Document required variables:** List required environment variables in the command’s
  help text or a README.

- **Never commit secrets:** Use `.env.local` for secrets (it’s typically gitignored).
  `.env` should only contain non-sensitive defaults.

## Best Practices

- **Don’t reinvent the wheel:** Use established patterns from existing CLI commands in
  this project or best practices from other modern open source CLI tools in Typescript.

- **Test with pipes:** Verify that scripts work correctly when output is piped (e.g.,
  `npm test | cat` should have no ANSI codes).

- **Respect environment variables:**

  - `NO_COLOR` - disable colors

  - `FORCE_COLOR` - force colors

  - `DEBUG` or `VERBOSE` - enable verbose logging

  - `QUIET_MODE` - suppress non-essential output

- **Make scripts composable:** Design scripts to work well in pipelines and automation.
  Consider how they’ll be used in CI/CD and shell scripts.

## Library/CLI Hybrid Packages

When building a package that functions as both a library and a CLI tool, isolate all
Node.js dependencies to CLI-only code.
This allows the core library to be used in non-Node environments (browsers, edge
runtimes, Cloudflare Workers, etc.).

**Key rules:**

- Core library entry point (`index.ts`) must have no `node:` imports

- All `node:` imports must be in `cli/` directory only

- Configuration constants go in node-free files

- Build-time values use bundler `define` injection

- Add guard tests to prevent future regressions

For detailed patterns, directory structure, and implementation examples, see
[Modern TypeScript Monorepo Patterns](../research/current/research-modern-typescript-monorepo-patterns.md#13-librarycli-hybrid-packages).

## CLI Architecture Patterns

For architectural patterns when building CLI applications, see
[Modern TypeScript CLI Patterns](../research/current/research-modern-typescript-cli-patterns.md).

**Key patterns covered:**

- **Base Command Pattern** — Eliminate boilerplate with a base class

- **Dual Output Mode** — Support both text and JSON output via OutputManager

- **Handler + Command Structure** — Separate definitions from implementation

- **Formatter Pattern** — Pair text and JSON formatters for each domain

- **Version Handling** — Git-based dynamic versioning (`X.Y.Z-dev.N.hash`)

- **Global Options** — Define `--dry-run`, `--verbose`, `--quiet`, `--format` at program
  level

- **Stdout/Stderr Separation** — Data to stdout, errors to stderr for pipeline
  compatibility

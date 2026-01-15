# Research Brief: Golden Testing for CLI Applications

**Last Updated**: 2025-12-31

**Status**: Complete

**Related**:

- [Golden Testing Guidelines](../../agent-guidelines/golden-testing-guidelines.md)

- [Modern TypeScript CLI Patterns](research-modern-typescript-cli-patterns.md)

- [repren test suite](https://github.com/jlevy/repren/tree/master/tests) — Simple
  reference implementation in Bash

* * *

## Executive Summary

Golden testing (also called snapshot testing or characterization testing) is a powerful
approach for testing CLI applications end-to-end without writing verbose unit tests.
Instead of asserting on individual values, you capture the complete output of a CLI
session—stdout, stderr, exit codes, and file system changes—and compare it against a
known-good “golden” file checked into version control.

This approach is particularly effective for CLI tools because:

1. CLIs have well-defined text-based outputs that are easy to capture and diff

2. File system side effects can be captured and verified

3. Tests can grow incrementally as script-like sequences of commands

4. Reviewing golden file diffs in PRs reveals behavioral changes

This research examines existing tools, patterns, and a proposed design for a modern CLI
golden testing framework that integrates well with TypeScript/JavaScript and Python
ecosystems.

**Research Questions**:

1. What existing tools support golden/snapshot testing for CLI applications?

2. What script format best balances readability, expressiveness, and tooling support?

3. How should stdout/stderr be captured and interleaved deterministically?

4. What normalization/scrubbing patterns are needed for stable, reproducible tests?

5. What is a minimal viable design for a modern CLI golden testing framework?

* * *

## Research Methodology

### Approach

Examined existing implementations, including:

- The repren Bash-based test harness as a reference “poor man’s” implementation

- Web searches for established CLI testing frameworks across multiple language
  ecosystems

- Analysis of golden testing patterns in the broader testing literature

### Sources

- Production CLI testing implementations (repren, various open source projects)

- Documentation for bats-core, oclif/test, shrun, CLI Testing Library

- Golden testing literature (ApprovalTests, Jest snapshots, VCR)

- Characterization testing concepts (Michael Feathers)

* * *

## Research Findings

### 1. Existing Tools and Frameworks

#### Bash-Based Approaches

**bats-core (Bash Automated Testing System)**

- TAP-compliant testing framework for Bash

- Tests are Bash scripts with `@test` annotations

- Good for testing other Bash scripts or simple CLI tools

- No built-in golden file support (assertions are manual)

- URL: https://github.com/bats-core/bats-core

**repren test harness (Reference Implementation)**

- Simple but effective pattern: `tests.sh` runs commands, `run.sh` captures and scrubs
  output

- Uses `set -v` to echo commands as executed

- Perl-based scrubbing to remove timestamps, line numbers, and platform differences

- Compares cleaned output against `tests-clean.log` via `git diff`

- Minimal dependencies (Bash, Perl)

**Assessment**: The repren approach demonstrates the core pattern elegantly.
Its simplicity is both a strength (easy to understand) and limitation (no structured
test organization, no parallel execution).

#### Python Tools

**pytest with pytest-snapshot**

- Adds snapshot testing to pytest

- Good for testing Python CLIs via subprocess

- Requires Python ecosystem

**cram (Historical)**

- Pioneering doctest-style CLI testing tool

- Format: commands prefixed with `$`, expected output follows

- No longer actively maintained

**Assessment**: Python tools integrate well with Python CLIs but add ecosystem overhead
for non-Python projects.

#### TypeScript/JavaScript Tools

**@gmrchk/cli-testing-library** *(Recommended for TypeScript projects)*

- Creates isolated environment for each test (temp directories, filesystem)

- Tests CLIs written in *any language* (works via shell)

- Normalizes system-specific differences automatically

- Supports both `execute` (run to completion) and `spawn` (interactive) modes

- Works with any JavaScript test framework (Jest, Vitest, etc.)

- ~63 stars, actively maintained (last update mid-2024)

- URL: https://www.npmjs.com/package/@gmrchk/cli-testing-library

Example:

```typescript
const { execute, cleanup, ls } = await prepareEnvironment();

await execute('node', './my-cli.js generate-file file.txt');

expect(ls('./')).toContain('file.txt');

await cleanup();
```

**Assessment**: This is the most promising TypeScript option for golden-style testing.
It provides the isolation and normalization needed, though you’d still need to add your
own golden file comparison layer on top.
Best suited for programmatic test assertions rather than pure golden file workflows.

**@oclif/test**

- Testing utilities for oclif-based CLIs

- Captures stdout/stderr programmatically

- Integrates with Mocha/Jest

- Limited to oclif framework

- URL: https://oclif.io/docs/testing/

**shrun**

- Modern CLI testing in Docker containers

- Uses Jest as test runner

- Provides isolation via containerization

- URL: https://www.cdevn.com/shrun-a-modern-cli-testing-framework/

**Assessment**: @oclif/test is framework-specific.
shrun’s Docker approach provides strong isolation but adds complexity.

#### Rust Tools

**trycmd + snapbox** *(Best-in-class golden testing, Rust-only)*

- Part of the assert-rs project, inspired by cram

- Two test formats:

  - `.trycmd` / `.md`: Markdown with fenced `console` blocks for inline tests

  - `.toml` + `.stdout/.stderr`: Structured format with separate expected outputs

- Built-in elision patterns: `[..]` (any text), `...` (any lines), `[EXE]`, `[ROOT]`,
  `[CWD]`

- Automatic golden update via `TRYCMD=overwrite cargo test`

- Supports file system verification (`.in/` and `.out/` directories)

- Used by major Rust projects: typos, cargo-edit, clap

- URL: https://crates.io/crates/trycmd

Example `.trycmd` format:

````markdown
```console
$ my-cli --help
my-cli [VERSION]

Usage: my-cli [OPTIONS] <COMMAND>

Commands:
  init    Initialize a new project
  build   Build the project
...

```
````

**Limitation**: trycmd is designed for testing Rust binaries built by Cargo.
It uses `bin.name` from Cargo.toml to locate the binary.
Testing arbitrary external CLIs requires workarounds or using the lower-level `snapbox`
crate directly.

**insta**

- General snapshot testing for Rust

- Can be used for CLI output capture via subprocess

- Excellent UX: `cargo insta review` for interactive approval

- URL: https://github.com/mitsuhiko/insta

**assert_cmd + assert_fs**

- Lower-level building blocks for CLI testing

- `assert_cmd`: Run commands and assert on exit status, stdout, stderr

- `assert_fs`: Create temp directories and verify file contents

- More flexible than trycmd but requires more code

**Assessment**: Rust has the most mature CLI golden testing ecosystem.
trycmd’s design is excellent and worth emulating in other languages.
However, these tools are Rust-specific and cannot directly test CLIs written in other
languages.

#### Go Tools

**Golden file convention (testdata/)**

- Standard Go pattern: expected outputs in `testdata/` directory

- Built into testing culture but not a specific tool

**Assessment**: Go’s convention-over-configuration approach is elegant but requires
manual implementation.

#### Summary: Language-Agnostic Tools

Most CLI testing tools are language-specific (trycmd for Rust, @oclif/test for oclif).
Tools that can test *any* CLI:

| Tool | Language | Golden Support | Interactive | Maturity |
| --- | --- | --- | --- | --- |
| **@gmrchk/cli-testing-library** | TypeScript | Manual | Yes | Medium |
| **bats-core** | Bash | Manual | No | High |
| **repren-style Bash** | Bash | Yes | No | Low (DIY) |
| **cram** (unmaintained) | Python | Yes | No | Historical |

**Recommendation**: For testing non-Rust/non-Go CLIs with golden files:

1. **Quick start**: Use repren-style Bash scripts (minimal dependencies)

2. **TypeScript projects**: Use `@gmrchk/cli-testing-library` with custom golden
   comparison

3. **Interactive CLIs**: `@gmrchk/cli-testing-library` supports `spawn` with
   `waitForText`/`writeText`

4. **Inspiration**: Study trycmd’s format and elision patterns for a custom
   implementation

* * *

### 2. Script Format Analysis

#### Option A: Raw Bash (repren style)

```bash
#!/bin/bash
set -e -o pipefail
set -v

# Commands are echoed as executed
my-cli create --name test
ls -la
my-cli delete --id test-123
```

**Pros**: Simple, familiar, uses real shell **Cons**: No structured expectations,
scrubbing is external, hard to extend

#### Option B: Doctest-style (cram-inspired)

```
Create a new resource:

  $ my-cli create --name test
  Created resource: test-123

  $ ls -la output/
  total 0
  -rw-r--r--  1 user  group  0 Jan  1 00:00 test.txt
```

**Pros**: Self-documenting, expectations inline **Cons**: Complex parsing,
indentation-sensitive

#### Option C: YAML/TOML Configuration

```yaml
tests:
  - name: create-resource
    commands:
      - run: my-cli create --name test
        expect_stdout: "Created resource: *"
        expect_exit: 0
      - run: ls -la output/
        expect_files:
          - name: test.txt
            exists: true
```

**Pros**: Structured, extensible, tooling-friendly **Cons**: Verbose, less readable than
shell scripts

#### Option D: Markdown with Fenced Blocks (trycmd-inspired)

````markdown
# Test: Create Resource

Run the create command:

```console
$ my-cli create --name test
Created resource: test-123
````

Verify the file was created:

```console
$ ls -la output/
-rw-r--r--  1 user  group  0 test.txt
```
````

**Pros**: Human-readable, can include prose, renders nicely on GitHub
**Cons**: Complex parsing, markdown limitations

#### Recommendation

**Hybrid approach**: Use a simple line-by-line command format (like repren) with an
optional YAML header for metadata. The golden output file is separate and compared via
diff.

```bash
# test: create-resource
# description: Test resource creation flow
# setup: mkdir -p output

my-cli create --name test
ls -la output/
my-cli show test
````

The separate `.golden` file captures the expected output, making diffs easy to review.

* * *

### 3. Stdout/Stderr Capture and Interleaving

The challenge: stdout and stderr are separate streams with no guaranteed ordering when
interleaved. Different approaches:

#### Approach 1: Merge at Source

```bash
my-cli command 2>&1
```

**Pros**: Simple, deterministic **Cons**: Loses ability to distinguish stdout from
stderr

#### Approach 2: Sequential Capture

```bash
stdout=$(my-cli command 2>/dev/null)
stderr=$(my-cli command 2>&1 >/dev/null)
echo "STDOUT:"
echo "$stdout"
echo "STDERR:"
echo "$stderr"
```

**Pros**: Preserves distinction **Cons**: Runs command twice, doesn’t capture true
interleaving

#### Approach 3: Use PTY (pseudo-terminal)

Use libraries like `node-pty` or `script` command to capture output as it would appear
in a terminal.

**Pros**: Most accurate representation **Cons**: Complex, platform-specific behavior

#### Recommendation

For most cases, **merge at source (`2>&1`)** is the pragmatic choice.
For tests that need to verify specific error handling, capture stderr separately with
labeled sections:

```
[stdout]
Created resource: test-123

[stderr]
Warning: deprecated option used

[exit: 0]
```

* * *

### 4. Output Normalization (Scrubbing)

Unstable content must be normalized before comparison.
Common patterns:

#### Timestamps

```perl
# ISO timestamps
s/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[.Z\d]*/[TIMESTAMP]/g

# Unix timestamps
s/\d{10,13}/[TIMESTAMP]/g

# Relative times
s/\d+ (seconds?|minutes?|hours?|days?) ago/[RELATIVE_TIME]/g
```

#### Generated IDs

```perl
# UUIDs
s/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/[UUID]/g

# Common ID patterns
s/[a-z]+_[a-zA-Z0-9]{8,}/[GENERATED_ID]/g
```

#### File Paths

```perl
# Home directory
s|/Users/[^/]+/|/HOME/|g
s|/home/[^/]+/|/HOME/|g

# Temp directories
s|/tmp/[a-zA-Z0-9._-]+|/tmp/[TEMP]|g
s|/var/folders/[^/]+/[^/]+/T/|/tmp/[TEMP]/|g
```

#### Line Numbers and Stack Traces

```perl
# Python tracebacks
s/File ".*\/([a-zA-Z0-9._]+\.py)", line \d+/File "...\/\1", line XX/g

# Node.js stack traces
s/at .+:\d+:\d+/at [LOCATION]/g
```

#### Durations and Timing

```perl
s/\d+(\.\d+)?ms/[DURATION]ms/g
s/took \d+(\.\d+)? seconds/took [DURATION] seconds/g
```

#### Best Practice: Centralized Scrubber Configuration

Define scrubbing rules in a configuration file:

```yaml
# .golden-scrub.yaml
scrubbers:
  - name: timestamps
    pattern: '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
    replace: '[TIMESTAMP]'

  - name: uuids
    pattern: '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    replace: '[UUID]'

  - name: home_dir
    pattern: '/Users/[^/]+/'
    replace: '/HOME/'
```

* * *

### 5. File System Verification

CLI tools often create, modify, or delete files.
Approaches to verify:

#### Option A: Include File Contents in Output

```bash
my-cli generate config
echo "=== Generated Files ==="
cat output/config.yaml
```

**Pros**: Simple, full visibility **Cons**: Verbose for large/binary files

#### Option B: File Manifest with Hashes

```bash
my-cli generate config
find output -type f -exec sha256sum {} \; | sort
```

Output:
```
abc123...  output/config.yaml
def456...  output/schema.json
```

**Pros**: Compact, detects any content change **Cons**: Hard to debug what changed

#### Option C: Hybrid with Size/Hash Summary

```bash
my-cli generate config
ls -la output/
sha256sum output/* 2>/dev/null | cut -c1-16
```

**Recommendation**: Use the hybrid approach—list files with sizes and first 16
characters of hash. For important files, include content directly or in separate golden
files.

* * *

### 6. Test Organization

#### Directory Structure

```
tests/
├── golden/
│   ├── README.md
│   ├── fixtures/              # Input files for tests
│   │   └── sample-input.txt
│   ├── scenarios/             # Test scripts
│   │   ├── basic-usage.sh
│   │   ├── error-handling.sh
│   │   └── file-operations.sh
│   └── expected/              # Golden output files
│       ├── basic-usage.golden
│       ├── error-handling.golden
│       └── file-operations.golden
├── scrubbers.yaml             # Output normalization rules
└── run-golden.sh              # Test runner
```

#### Naming Conventions

- Test scripts: `<feature>-<scenario>.sh`

- Golden files: `<feature>-<scenario>.golden`

- One script per logical test scenario

- Keep scripts small (<100 lines) and focused

* * *

### 7. CLI Design Requirements

For effective golden testing, CLIs should support:

#### Required

1. **Non-interactive mode**: Skip prompts, use defaults or flags
   ```bash
   my-cli create --name test --yes  # Skip confirmation
   ```

2. **Color control**: Disable color codes
   ```bash
   my-cli --no-color list
   # Or via environment
   NO_COLOR=1 my-cli list
   ```

3. **Deterministic output**: Same inputs produce same outputs

   - Avoid random ordering (sort lists)

   - Use stable IDs where possible

#### Recommended

4. **Quiet/verbose modes**: Control output detail level
   ```bash
   my-cli --quiet create  # Minimal output
   my-cli --verbose list  # Maximum detail
   ```

5. **Machine-readable output**: JSON mode for structured output
   ```bash
   my-cli list --format json
   ```

6. **Dry-run mode**: Show what would happen without side effects
   ```bash
   my-cli --dry-run delete --all
   ```

7. **Exit codes**: Use meaningful exit codes (0 success, 1 user error, 2 system error)

* * *

## Proposed Design: CLI Golden Test Framework

### Overview

A minimal framework for golden testing CLI tools, inspired by repren’s simplicity with
modern conveniences.

### Components

#### 1. Test Runner (`golden-test`)

```bash
# Run all tests
golden-test run

# Run specific test
golden-test run scenarios/basic-usage.sh

# Update golden files after review
golden-test update scenarios/basic-usage.sh

# Show diff without updating
golden-test diff scenarios/basic-usage.sh
```

#### 2. Test Script Format

Simple Bash with optional metadata header:

```bash
#!/usr/bin/env bash
# @name: basic-usage
# @description: Test basic CLI operations
# @setup: mkdir -p work && cd work
# @teardown: rm -rf work

# Commands run sequentially, output captured
my-cli init
my-cli add item --name "Test Item"
my-cli list
my-cli show item-1
```

#### 3. Golden File Format

Captured output with labeled sections:

```
# Command: my-cli init
Initialized empty project in /tmp/[TEMP]/work

# Command: my-cli add item --name "Test Item"
Added item: item-1

# Command: my-cli list
Items:
  - item-1: Test Item

# Command: my-cli show item-1
Item: item-1
  Name: Test Item
  Created: [TIMESTAMP]

# Exit: 0
```

#### 4. Configuration (`.golden.yaml`)

```yaml
# CLI to test
cli: ./dist/my-cli

# Environment setup
env:
  NO_COLOR: "1"
  TZ: "UTC"

# Output scrubbing
scrubbers:
  - pattern: '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
    replace: '[TIMESTAMP]'
  - pattern: '/tmp/golden-test-[a-zA-Z0-9]+'
    replace: '/tmp/[TEMP]'

# Directories
scenarios: tests/golden/scenarios
expected: tests/golden/expected
fixtures: tests/golden/fixtures

# Options
merge_stderr: true
show_exit_codes: true
show_command_echo: true
```

#### 5. Implementation Sketch (TypeScript)

```typescript
interface GoldenConfig {
  cli: string;
  env: Record<string, string>;
  scrubbers: Array<{ pattern: string; replace: string }>;
  scenarios: string;
  expected: string;
  mergeStderr: boolean;
}

interface TestResult {
  name: string;
  passed: boolean;
  output: string;
  expected: string;
  diff?: string;
}

async function runScenario(
  scenarioPath: string,
  config: GoldenConfig
): Promise<string> {
  const script = await readFile(scenarioPath, 'utf-8');
  const commands = parseCommands(script);

  let output = '';
  for (const cmd of commands) {
    output += `# Command: ${cmd}\n`;
    const result = await exec(cmd, {
      env: { ...process.env, ...config.env },
      shell: true,
    });
    output += scrub(result.stdout + result.stderr, config.scrubbers);
    output += '\n';
  }
  output += `# Exit: ${lastExitCode}\n`;

  return output;
}

function scrub(text: string, scrubbers: Scrubber[]): string {
  let result = text;
  for (const { pattern, replace } of scrubbers) {
    result = result.replace(new RegExp(pattern, 'g'), replace);
  }
  return result;
}
```

#### 6. Implementation Sketch (Python)

```python
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass
import yaml

@dataclass
class GoldenConfig:
    cli: str
    env: dict[str, str]
    scrubbers: list[dict[str, str]]
    scenarios: Path
    expected: Path
    merge_stderr: bool = True

def run_scenario(scenario_path: Path, config: GoldenConfig) -> str:
    script = scenario_path.read_text()
    commands = parse_commands(script)

    output_lines = []
    for cmd in commands:
        output_lines.append(f"# Command: {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, **config.env}
        )
        combined = result.stdout + result.stderr if config.merge_stderr else result.stdout
        output_lines.append(scrub(combined, config.scrubbers))

    output_lines.append(f"# Exit: {result.returncode}")
    return "\n".join(output_lines)

def scrub(text: str, scrubbers: list[dict[str, str]]) -> str:
    result = text
    for scrubber in scrubbers:
        result = re.sub(scrubber["pattern"], scrubber["replace"], result)
    return result
```

* * *

## Comparative Analysis

| Feature | repren-style Bash | bats-core | shrun | Proposed Design |
| --- | --- | --- | --- | --- |
| Language | Bash | Bash | JavaScript | TypeScript/Python |
| Golden files | Manual | None | Optional | First-class |
| Scrubbing | External Perl | Manual | N/A | Configured YAML |
| Parallel execution | No | Yes | Yes | Planned |
| CI integration | Manual | TAP output | Jest | Built-in |
| Setup complexity | Minimal | Low | Medium (Docker) | Low |
| Cross-platform | Partial | Bash-only | Docker-based | Full |

**Strengths/Weaknesses Summary**:

- **repren-style**: Simple but manual; good for small projects

- **bats-core**: Mature ecosystem but no golden file support

- **shrun**: Docker isolation is powerful but adds complexity

- **Proposed Design**: Balances simplicity with modern conveniences

* * *

## Design: TypeScript Port of trycmd (`tryscript`)

> **Full implementation plan**: See
> [plan-2025-01-01-tryscript-cli-golden-testing.md](../../../project/specs/active/plan-2025-01-01-tryscript-cli-golden-testing.md)
> for the complete phased implementation plan with TDD approach.

A minimal TypeScript implementation inspired by trycmd’s design, but language-agnostic
(can test any CLI binary).

### Goals

1. **Language-agnostic**: Test any CLI, not just TypeScript/Node binaries

2. **trycmd-compatible format**: Same markdown syntax and elision patterns

3. **Minimal dependencies**: Node.js only, no Docker

4. **Self-bootstrapping**: tryscript tests tryscript

### Test File Format (`.tryscript.md`)

Inspired by trycmd’s markdown format:

````markdown
# Test: Basic Usage

Test the help command:

```console
$ my-cli --help
my-cli v[..]

Usage: my-cli [OPTIONS] <COMMAND>

Options:
  --verbose    Enable verbose output
  --help       Show this help

Commands:
  init         Initialize a new project
  build        Build the project
...

```

Test initialization:

```console
$ my-cli init my-project
Created project: my-project
? 0
```

Verify files were created:

```console
$ ls my-project/
config.json
src/
? 0
```

Check file contents:

```console
$ cat my-project/config.json
{
  "name": "my-project",
  "version": "1.0.0",
  "created": "[TIMESTAMP]"
}
? 0
```
````

### Format Specification

**Command blocks**:

- Fenced code blocks with `console` or `bash` info string

- `$ ` prefix starts a command

- `> ` prefix continues a multi-line command

- `? <status>` indicates expected exit code (default: `? 0`)

- All other lines are expected output

**Elision patterns** (trycmd-compatible):

- `[..]` — Match any characters on this line

- `...` — Match zero or more lines

- `[EXE]` — `.exe` on Windows, empty otherwise

- `[ROOT]` — Test root directory

- `[CWD]` — Current working directory

- `[TIMESTAMP]` — ISO timestamp pattern (custom)

- `[UUID]` — UUID pattern (custom)

**Metadata header** (optional YAML front matter):

```yaml
---
# Binary to test (required)
bin: ./dist/my-cli

# Or use a command that will be resolved via PATH
command: my-cli

# Environment variables
env:
  NO_COLOR: "1"
  MY_CLI_CONFIG: /dev/null

# Working directory (default: temp dir)
cwd: .

# Timeout per command in ms (default: 30000)
timeout: 5000

# Custom elision patterns
patterns:
  TIMESTAMP: '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
  VERSION: 'v\d+\.\d+\.\d+'
---
```

### Directory Structure

```
tests/
├── tryscript.config.ts      # Global config
├── cmd/
│   ├── help.tryscript.md    # Test file
│   ├── help.in/             # Input files (optional)
│   │   └── sample.txt
│   ├── help.out/            # Expected output files (optional)
│   │   └── result.txt
│   ├── init.tryscript.md
│   └── build.tryscript.md
└── README.md
```

### Configuration (`tryscript.config.ts`)

```typescript
import { defineConfig } from 'tryscript';

export default defineConfig({
  // Binary to test (can be overridden per-test)
  bin: './dist/my-cli',

  // Test file patterns
  tests: ['tests/cmd/**/*.tryscript.md'],

  // Global environment
  env: {
    NO_COLOR: '1',
    TZ: 'UTC',
  },

  // Custom elision patterns
  patterns: {
    TIMESTAMP: /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/,
    UUID: /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/,
    DURATION: /\d+(\.\d+)?ms/,
  },

  // Normalize paths for cross-platform
  normalizePaths: true,

  // Timeout per command
  timeout: 30_000,
});
```

### CLI Interface

```bash
# Run all tests
npx tryscript

# Run specific test
npx tryscript tests/cmd/help.tryscript.md

# Update golden files (like TRYCMD=overwrite)
npx tryscript --update

# Dump actual output without comparing
npx tryscript --dump

# Show diff on failure
npx tryscript --diff

# Run in parallel
npx tryscript --parallel

# Filter by name pattern
npx tryscript --filter "init"
```

### Key Differences from trycmd

| Feature | trycmd | tryscript |
| --- | --- | --- |
| Language | Rust | TypeScript |
| Target binaries | Cargo binaries | Any CLI |
| Test format | .trycmd/.toml | .tryscript.md |
| Config | Cargo.toml integration | tryscript.config.ts |
| Elision patterns | Same | Same (compatible) |
| File verification | .in/.out dirs | Same |
| Update command | TRYCMD=overwrite | --update flag |
| Binary discovery | bin.name in Cargo | Explicit path/command |

* * *

## Best Practices

1. **Start simple**: Begin with a few high-value scenarios covering core functionality,
   not exhaustive coverage

2. **Keep scenarios focused**: Each test script should test one logical flow (3-10
   commands)

3. **Review golden diffs carefully**: Treat golden file changes as behavioral
   specifications in PRs

4. **Use meaningful scrubbers**: Only scrub genuinely unstable content; over-scrubbing
   hides regressions

5. **Run tests in CI**: Golden tests should run on every commit in mocked/deterministic
   mode

6. **Separate live vs mocked modes**: Use real services for updating goldens, mocks for
   CI speed

7. **Document test intent**: Add comments in test scripts explaining what behavior is
   being verified

8. **Fail fast**: Exit on first failure in CI; in development, continue to show all
   failures

9. **Version control golden files**: They are specifications; changes should be reviewed
   and committed intentionally

10. **Keep golden files small**: If a single test produces >500 lines, consider
    splitting into multiple scenarios

* * *

## Open Research Questions

1. **Cross-platform normalization**: How to handle platform-specific path separators and
   behavior differences consistently?

2. **Binary file handling**: What’s the best approach for CLIs that produce binary
   output (checksums vs separate files)?

3. **Interactive testing**: How to test interactive prompts while maintaining golden
   file compatibility?

4. **Performance regression detection**: Can timing be captured in a way that’s useful
   but not flaky?

* * *

## Recommendations

### Summary

For new CLI projects, implement a golden testing approach using:

1. Simple Bash test scripts with metadata headers

2. Separate `.golden` files for expected output

3. YAML-configured scrubbers for output normalization

4. A thin test runner in your project’s primary language

### Recommended Approach

Start with the **minimal Bash-based approach** (like repren) for immediate value:

```bash
# tests/golden/run.sh
#!/bin/bash
set -euo pipefail

./tests/golden/scenarios.sh 2>&1 \
  | perl -pe 's/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/[TIMESTAMP]/g' \
  | perl -pe 's|/tmp/[a-zA-Z0-9]+|/tmp/[TEMP]|g' \
  > tests/golden/output.actual

diff tests/golden/output.expected tests/golden/output.actual
```

Then evolve to the **full framework** as needs grow:

- Add YAML configuration for scrubbers

- Implement parallel test execution

- Add `--update` command for regenerating goldens

- Integrate with CI reporting

### Alternative Approaches

- **For Bash-heavy projects**: Use bats-core with custom golden file helpers

- **For Docker-based workflows**: Consider shrun for guaranteed isolation

- **For Python CLIs**: pytest-snapshot provides similar functionality

- **For Rust CLIs**: Use trycmd for idiomatic integration

* * *

## References

### Tools

- [bats-core](https://github.com/bats-core/bats-core) — Bash Automated Testing System

- [@oclif/test](https://oclif.io/docs/testing/) — Testing utilities for oclif CLIs

- [shrun](https://www.cdevn.com/shrun-a-modern-cli-testing-framework/) — CLI testing in
  Docker

- [CLI Testing Library](https://cli-testing.com/) — Framework-agnostic CLI testing

- [trycmd](https://github.com/assert-rs/trycmd) — Rust CLI snapshot testing

- [insta](https://github.com/mitsuhiko/insta) — Rust snapshot testing

### Reference Implementations

- [repren tests](https://github.com/jlevy/repren/tree/master/tests) — Simple Bash-based
  golden testing

### Literature

- [Golden Testing Guidelines](../../agent-guidelines/golden-testing-guidelines.md) —
  Session-level golden testing principles

- [Characterization Test (Wikipedia)](https://en.wikipedia.org/wiki/Characterization_test)
  — Foundational concepts

- [ApprovalTests](https://approvaltests.com/) — Approval testing methodology

- Michael Feathers, *Working Effectively with Legacy Code* — Characterization testing
  concepts

* * *

## Appendix A: Complete repren Test Harness Analysis

The repren project provides an excellent minimal reference implementation.
Key components:

### `run.sh` — Test Orchestrator

```bash
# 1. Clean up and prepare
rm -rf "$dir/tmp-dir"
cp -a $dir/work-dir $dir/tmp-dir

# 2. Run tests, capture output
$dir/tests.sh 2>&1 | tee $full_log | ...

# 3. Scrub unstable content (Perl one-liners)
| perl -pe 's/([a-zA-Z0-9._]+.py):[0-9]+/\1:xx/g'
| perl -pe 's/File ".*\/([a-zA-Z0-9._]+.py)", line [0-9]*/File "...\/\1", line __X/g'
| perl -pe 's/[0-9.:T-]*Z/__TIMESTAMP/g'
> $clean_log

# 4. Compare against checked-in golden file
git diff $clean_log > $final_diff
```

### `tests.sh` — Test Script

```bash
set -e -o pipefail  # Exit on error
set -v               # Echo commands (key for output capture)

# Helper for expected errors
expect_error() {
  echo "(got expected error: status $?)"
}

# Helper for portable ls
ls_portable() {
  ls -lF "$@" | tail -n +2 | awk '{gsub(/@/, "", $1); print $1, $NF}'
}

# Actual tests
run --from Humpty --to Dumpty test1/humpty-dumpty.txt
diff -r original test1
```

### Key Insights

1. `set -v` echoes commands, creating a natural “test transcript”

2. Error handling via trap and helper function

3. Portable helpers abstract platform differences

4. Scrubbing happens in pipeline, not inline

5. `git diff` provides familiar diff output

* * *

## Appendix B: Scrubber Pattern Library

Common patterns for output normalization:

```yaml
# .golden-scrubbers.yaml

patterns:
  # Timestamps
  iso_timestamp:
    pattern: '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?'
    replace: '[TIMESTAMP]'

  unix_timestamp:
    pattern: '\b1[67]\d{8}\b'  # 2020-2030 range
    replace: '[UNIX_TS]'

  relative_time:
    pattern: '\d+ (second|minute|hour|day|week|month|year)s? ago'
    replace: '[TIME_AGO]'

  # IDs
  uuid:
    pattern: '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    replace: '[UUID]'

  nanoid:
    pattern: '[A-Za-z0-9_-]{21}'
    replace: '[NANOID]'

  # Paths
  home_macos:
    pattern: '/Users/[^/\s]+'
    replace: '/HOME'

  home_linux:
    pattern: '/home/[^/\s]+'
    replace: '/HOME'

  temp_macos:
    pattern: '/var/folders/[^/]+/[^/]+/T/[^/\s]+'
    replace: '/tmp/[TEMP]'

  temp_generic:
    pattern: '/tmp/[a-zA-Z0-9._-]+'
    replace: '/tmp/[TEMP]'

  # Stack traces
  python_traceback_line:
    pattern: 'File "[^"]+/([^"]+\.py)", line \d+'
    replace: 'File ".../\1", line XX'

  node_stack_frame:
    pattern: 'at [^\n]+:\d+:\d+'
    replace: 'at [LOCATION]'

  # Memory addresses
  python_object_id:
    pattern: ' at 0x[0-9a-f]+'
    replace: ' at 0x[ADDR]'

  # Duration/timing
  duration_ms:
    pattern: '\d+(\.\d+)?ms'
    replace: '[N]ms'

  duration_s:
    pattern: '\d+(\.\d+)?s\b'
    replace: '[N]s'

  # Version numbers (be careful - sometimes you want these!)
  semver:
    pattern: 'v?\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?'
    replace: '[VERSION]'
```

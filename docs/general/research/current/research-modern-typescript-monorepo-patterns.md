# Research Brief: Modern TypeScript Monorepo Architecture Patterns

**Last Updated**: 2026-01-05 (Updated all tool versions, fixed section numbering)

**Status**: Complete

**Related**:

- [pnpm Workspaces Documentation](https://pnpm.io/workspaces)

- [Changesets Documentation](https://github.com/changesets/changesets)

- [tsdown Documentation](https://tsdown.dev/)

- [publint Documentation](https://publint.dev/docs/)

* * *

## Updating This Document

### Last Researched Versions

| Tool / Package | Version | Check For Updates |
| --- | --- | --- |
| **Node.js** | 24 (LTS "Krypton") | [nodejs.org/releases](https://nodejs.org/en/about/previous-releases) — Active LTS until Oct 2026 |
| **pnpm** | 10.27.0 | [github.com/pnpm/pnpm/releases](https://github.com/pnpm/pnpm/releases) |
| **TypeScript** | ^5.9.0 | [github.com/microsoft/TypeScript/releases](https://github.com/microsoft/TypeScript/releases) — 5.9 adds `import defer`, `--module node20` |
| **tsdown** | ^0.18.0 | [github.com/rolldown/tsdown/releases](https://github.com/rolldown/tsdown/releases) — 0.19.x in beta |
| **publint** | ^0.3.0 | [npmjs.com/package/publint](https://www.npmjs.com/package/publint) |
| **@changesets/cli** | ^2.29.0 | [github.com/changesets/changesets/releases](https://github.com/changesets/changesets/releases) |
| **@types/node** | ^24.0.0 | Should match Node.js major version (^25.0.0 also available) |
| **actions/checkout** | v5 | [github.com/actions/checkout/releases](https://github.com/actions/checkout/releases) — v6 available, uses Node 24 |
| **actions/setup-node** | v6 | [github.com/actions/setup-node/releases](https://github.com/actions/setup-node/releases) |
| **pnpm/action-setup** | v4 | [github.com/pnpm/action-setup/releases](https://github.com/pnpm/action-setup/releases) |
| **changesets/action** | v1 | [github.com/changesets/action](https://github.com/changesets/action) |
| **lefthook** | ^2.0.0 | [github.com/evilmartians/lefthook/releases](https://github.com/evilmartians/lefthook/releases) |
| **npm-check-updates** | ^19.0.0 | [npmjs.com/package/npm-check-updates](https://www.npmjs.com/package/npm-check-updates) |
| **tsx** | ^4.21.0 | [github.com/privatenumber/tsx/releases](https://github.com/privatenumber/tsx/releases) |
| **prettier** | ^3.0.0 | [github.com/prettier/prettier/releases](https://github.com/prettier/prettier/releases) |
| **eslint-config-prettier** | ^10.0.0 | [github.com/prettier/eslint-config-prettier/releases](https://github.com/prettier/eslint-config-prettier/releases) |

### Reminders When Updating

1. **Check each version** in the table above using the linked release pages

2. **Update the table** with new versions and any relevant notes

3. **Search and update code examples** — version numbers appear in:

   - GitHub Actions workflows (CI and Release sections)

   - `tsdown.config.ts` examples (`target: "node24"`)

   - `tsconfig.base.json` examples (`target`/`lib` should match Node.js ES version)

   - `package.json` examples (`engines`, `packageManager`, `devDependencies`)

   - Appendices A, B, and D (complete examples)

4. **Verify compatibility** — check that tools still work together (e.g., new
   pnpm/action-setup versions may change caching behavior)

5. **Update the “Last Updated” date** at the top of the document

6. **Review “Open Research Questions”** section for any resolved items

* * *

## Executive Summary

This research brief provides a comprehensive guide for setting up a modern TypeScript
package that can start as a single package and grow into a multi-package monorepo.
The architecture prioritizes fast iteration during early development while maintaining a
clear path to split packages later without breaking changes.

The recommended stack uses **pnpm workspaces** for dependency management, **tsdown** for
building ESM/CJS dual outputs with TypeScript declarations, **Changesets** for
versioning and release automation, **publint** for validating package publishability,
and **lefthook** for fast local git hooks.
This approach supports private development via GitHub Packages or direct GitHub
installs, with a seamless transition to public npm publishing when ready.

**Research Questions**:

1. What is the optimal monorepo structure for a TypeScript package that may grow from
   one to many packages?

2. How should modern TypeScript packages handle dual ESM/CJS output with proper type
   declarations?

3. What tooling provides the best developer experience for versioning, publishing, and
   CI/CD automation?

4. How can packages support optional peer dependencies (like AI SDKs or protocol
   integrations) without forcing them on users?

* * *

## Research Methodology

### Approach

Research was conducted through documentation review, web searches for current best
practices (2025), analysis of popular open-source monorepos, and evaluation of tooling
recommendations from the TypeScript and JavaScript ecosystem maintainers.

### Sources

- Official documentation (pnpm, TypeScript, Node.js, GitHub)

- Tool-specific documentation (tsdown, publint, Changesets)

- Developer blog posts and migration guides

- GitHub discussions and issue threads

- Real-world monorepo implementations (Effect-TS, TresJS)

* * *

## Research Findings

### 1. Package Manager & Workspace Structure

#### pnpm Workspaces

**Status**: Recommended

**Details**:

- pnpm offers disk space efficiency through content-addressable storage with symlinks

- Built-in workspace support without additional tools

- Strict `node_modules` prevents phantom dependencies (packages not explicitly declared)

- `workspace:` protocol ensures local packages are always used during development

- `pnpm deploy` command enables isolated production deployments for Docker

**Assessment**: pnpm is the consensus choice for TypeScript monorepos in 2025, offering
superior disk efficiency and stricter dependency management than npm or yarn.

**Key Configuration** (`pnpm-workspace.yaml`):
```yaml
packages:
  - "packages/*"
  - "apps/*"
```

**Root `.npmrc`**:
```ini
save-workspace-protocol=true
prefer-workspace-packages=true
```

**References**:

- [pnpm Workspaces](https://pnpm.io/workspaces)

- [Complete Monorepo Guide 2025](https://jsdev.space/complete-monorepo-guide/)

* * *

#### Monorepo Structure Strategy

**Status**: Recommended

**Details**:

The “start mono, stay sane” approach places packages in `packages/` from day one, even
if there’s only one package initially.
This prevents restructuring when adding new packages later.

**Recommended Directory Structure**:
```
project-root/
  .changeset/
    config.json
    README.md
  .github/
    workflows/
      ci.yml
      release.yml
  packages/
    package-name/
      src/
        core/           # Future: package-name-core
        cli/            # Future: package-name-cli
        adapters/       # Future: package-name-adapters
        bin.ts
        index.ts
      package.json
      tsconfig.json
      tsdown.config.ts
  .gitignore
  .npmrc
  eslint.config.js
  package.json
  pnpm-workspace.yaml
  tsconfig.base.json
```

**Assessment**: Starting with a monorepo structure from day one has minimal overhead and
prevents painful restructuring later.
Internal code organization (`core/`, `cli/`, `adapters/`) creates natural split points.

**References**:

- [Setting up a monorepo with pnpm and
  TypeScript](https://brockherion.dev/blog/posts/setting-up-a-monorepo-with-pnpm-and-typescript/)

- [Wisp CMS: How to Bootstrap a Monorepo with
  PNPM](https://www.wisp.blog/blog/how-to-bootstrap-a-monorepo-with-pnpm-a-complete-guide)

* * *

### 2. TypeScript Configuration

#### Base Configuration

**Status**: Recommended

**Details**:

Modern TypeScript monorepos use a shared base configuration extended by each package.

**`tsconfig.base.json`**:
```json
{
  "compilerOptions": {
    "target": "ES2024",
    "lib": ["ES2024"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "resolveJsonModule": true,
    "strict": true,
    "skipLibCheck": true,
    "noUncheckedIndexedAccess": true,
    "forceConsistentCasingInFileNames": true,
    "verbatimModuleSyntax": true
  }
}
```

**Package-level `tsconfig.json`**:
```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "types": ["node"],
    "noEmit": true
  },
  "include": ["src"]
}
```

**Assessment**: Using `moduleResolution: "Bundler"` is appropriate when a bundler
(tsdown) handles the final output.
For maximum Node.js compatibility without a bundler, `NodeNext` would be preferred.
Since tsdown generates proper ESM and CJS with correct extensions, `Bundler` mode works
well.

**References**:

- [TypeScript: Choosing Compiler
  Options](https://www.typescriptlang.org/docs/handbook/modules/guides/choosing-compiler-options.html)

- [Is nodenext right for
  libraries?](https://blog.andrewbran.ch/is-nodenext-right-for-libraries-that-dont-target-node-js/)

* * *

#### moduleResolution: Bundler vs NodeNext

**Status**: Situational

**Details**:

| Aspect | `Bundler` | `NodeNext` |
| --- | --- | --- |
| File extensions | Not required in imports | Required (.js extension) |
| Use case | When bundler handles output | Direct Node.js execution |
| Library compatibility | Requires bundler-aware consumers | Works everywhere |
| Type generation | Must ensure .d.ts aligns with output | Naturally aligned |

**Key insight**: `NodeNext` is “infectious” in a good way—code that works in Node.js
typically works in bundlers too.
However, `Bundler` is acceptable when using tsdown since it handles file extensions
correctly.

**Assessment**: Use `Bundler` for simplicity during development when tsdown generates
the final output. The bundler handles the complexity of module resolution.

**References**:

- [TypeScript moduleResolution documentation](https://www.typescriptlang.org/tsconfig/moduleResolution.html)

- [Live types in a TypeScript
  monorepo](https://colinhacks.com/essays/live-types-typescript-monorepo)

* * *

### 3. Build Tooling

#### tsdown

**Status**: Strongly Recommended

**Details**:

tsdown is the modern successor to tsup, built on Rolldown (the Rust-based bundler from
the Vite ecosystem).
Key advantages:

- **ESM-first**: Properly handles file extensions in ESM output (a pain point with tsup)

- **Dual format output**: Generates both ESM (`.js`) and CJS (`.cjs`) from the same
  source

- **TypeScript declarations**: Built-in `.d.ts` and `.d.cts` generation

- **Multi-entry support**: Build multiple entry points (library, CLI, adapters) in one
  config

- **Plugin ecosystem**: Compatible with Rollup, Rolldown, and most Vite plugins

- **Fast**: Powered by Rust-based Oxc and Rolldown

- **Isolated declarations**: Supports TypeScript 5.5+ `--isolatedDeclarations` for
  faster type generation

**Migration from tsup**: tsdown provides a `migrate` command and is compatible with most
tsup configurations.

**Configuration (`tsdown.config.ts`)**:
```typescript
import { defineConfig } from "tsdown";

export default defineConfig({
  entry: {
    index: "src/index.ts",
    cli: "src/cli/index.ts",
    adapter: "src/adapters/index.ts",
    bin: "src/bin.ts"
  },
  format: ["esm", "cjs"],
  platform: "node",
  target: "node24",
  sourcemap: true,
  dts: true,
  clean: true,
  banner: ({ fileName }) =>
    fileName.startsWith("bin.") ? "#!/usr/bin/env node\n" : ""
});
```

**Assessment**: tsdown is the recommended choice for new TypeScript library projects.
It has official backing from the Vite/Rolldown team and will become the foundation for
Rolldown Vite’s Library Mode.

**Note on tsup**: tsup is no longer actively maintained.
The project recommends migrating to tsdown.

**References**:

- [tsdown Introduction](https://tsdown.dev/guide/)

- [Switching from tsup to tsdown](https://alan.norbauer.com/articles/tsdown-bundler/)

- [Migrate from tsup](https://tsdown.dev/guide/migrate-from-tsup)

- [TresJS tsdown Migration](https://tresjs.org/blog/tresjs-tsdown-migration)

- [Dual publish ESM and CJS with
  tsdown](https://dev.to/hacksore/dual-publish-esm-and-cjs-with-tsdown-2l75)

* * *

### 4. Package Exports & Dual Module Support

#### Subpath Exports

**Status**: Essential

**Details**:

The `exports` field in `package.json` enables:

- Multiple entry points (`./cli`, `./adapter`)

- Conditional exports (ESM vs CJS, types vs runtime)

- Package encapsulation (only expose intended APIs)

**Critical rule**: The `"types"` condition must come first in each export block.

**Example `package.json` exports**:
```json
{
  "name": "@scope/package-name",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.js"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    },
    "./cli": {
      "import": {
        "types": "./dist/cli.d.ts",
        "default": "./dist/cli.js"
      },
      "require": {
        "types": "./dist/cli.d.cts",
        "default": "./dist/cli.cjs"
      }
    },
    "./package.json": "./package.json"
  },
  "bin": {
    "package-name": "./dist/bin.js"
  },
  "files": ["dist"]
}
```

**Assessment**: Subpath exports are essential for future-proofing.
They allow splitting packages later without breaking the API surface—`@scope/pkg/cli`
can remain stable even if internals move to `@scope/pkg-cli`.

**References**:

- [Guide to package.json exports field](https://hirok.io/posts/package-json-exports)

- [Node.js Packages documentation](https://nodejs.org/api/packages.html)

- [Ship ESM & CJS in one Package](https://antfu.me/posts/publish-esm-and-cjs)

- [Building npm package compatible with ESM and CJS in
  2024](https://snyk.io/blog/building-npm-package-compatible-with-esm-and-cjs-2024/)

* * *

#### Separate Declaration Files for ESM/CJS

**Status**: Required

**Details**:

Each entry point needs separate declaration files for ESM (`.d.ts`) and CJS (`.d.cts`).
TypeScript interprets declaration files as ESM or CJS based on file extension and the
package’s `type` field.

Using a single `.d.ts` for both formats will cause TypeScript errors for consumers using
one of the module systems.

**Assessment**: tsdown handles this automatically when `dts: true` is configured.

**References**:

- [TypeScript Modules Reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html)

- [Publishing dual ESM+CJS packages](https://mayank.co/blog/dual-packages/)

* * *

### 5. Optional Peer Dependencies

#### Strategy for Optional Integrations

**Status**: Recommended

**Details**:

For packages that optionally integrate with external SDKs (AI SDKs, MCP servers, etc.),
use:

1. **Optional peer dependencies**: Don’t force installation

2. **Subpath exports**: Isolate optional code in separate entry points

3. **Dynamic imports**: Only load the SDK when the subpath is actually imported

**`package.json` configuration**:
```json
{
  "peerDependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "ai": "^5.0.0"
  },
  "peerDependenciesMeta": {
    "@modelcontextprotocol/sdk": { "optional": true },
    "ai": { "optional": true }
  }
}
```

**Implementation pattern** (`src/adapters/mcp/index.ts`):
```typescript
export async function createMcpServer(options: McpServerOptions) {
  // Dynamic import only when this code path is executed
  const { Server } = await import("@modelcontextprotocol/sdk/server");
  return new Server(options);
}
```

**Assessment**: This pattern ensures the main package remains lightweight while
providing rich integrations for users who need them.

**References**:

- [tsdown Dependencies handling](https://tsdown.dev/options/dependencies)

- [npm peer dependencies
  documentation](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#peerdependenciesmeta)

* * *

### 6. Package Validation

#### publint

**Status**: Essential

**Details**:

publint validates that packages will work correctly across different environments (Vite,
Webpack, Rollup, Node.js).
It checks:

- Export field validity

- File existence for declared exports

- ESM/CJS format correctness

- Type declaration alignment

- Common configuration mistakes

**Integration**:
```json
{
  "scripts": {
    "publint": "publint",
    "prepack": "pnpm build"
  },
  "devDependencies": {
    "publint": "^0.3.0"
  }
}
```

**CI Integration**: Run `pnpm publint` after build in CI to catch publishing issues
before release.

**Assessment**: publint catches issues that would only surface after users install the
package. Essential for any published package.

**References**:

- [publint documentation](https://publint.dev/docs/)

- [publint rules](https://publint.dev/rules)

* * *

### 7. Versioning & Release Automation

#### Changesets

**Status**: Strongly Recommended

**Details**:

Changesets provides:

- **Intent-based versioning**: Developers declare the impact (patch/minor/major) when
  making changes

- **Automated changelogs**: Generated from changeset descriptions

- **Monorepo-aware**: Handles inter-package dependencies automatically

- **CI integration**: GitHub Action opens release PRs and publishes automatically

**Setup**:

1. Initialize: `pnpm add -Dw @changesets/cli && pnpm changeset init`

2. Configure `.changeset/config.json`:
```json
{
  "$schema": "https://unpkg.com/@changesets/config/schema.json",
  "changelog": "@changesets/changelog-github",
  "commit": false,
  "fixed": [],
  "linked": [],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch"
}
```

3. Root scripts:
```json
{
  "scripts": {
    "changeset": "changeset",
    "version-packages": "changeset version",
    "release": "pnpm build && pnpm publint && changeset publish"
  }
}
```

**Workflow**:

1. Developer runs `pnpm changeset` and describes changes

2. PR includes the changeset file

3. On merge to main, GitHub Action either:

   - Opens a “Version Packages” PR (accumulating changesets)

   - Publishes to npm when that PR is merged

**Assessment**: Changesets is the de facto standard for monorepo versioning.
It integrates seamlessly with pnpm and GitHub Actions.

**References**:

- [Using Changesets with pnpm](https://pnpm.io/using-changesets)

- [Changesets GitHub repository](https://github.com/changesets/changesets)

- [Frontend Handbook: Changesets](https://infinum.com/handbook/frontend/changesets)

* * *

#### Dynamic Git-Based Versioning

**Status**: Recommended for dev builds

**Details**:

While Changesets handles release versioning, development builds benefit from dynamic
git-based version strings.
This provides traceability during development without manual version bumps.

**Format**: `X.Y.Z-dev.N.hash`

| State | Format | Example |
| --- | --- | --- |
| On tag | `X.Y.Z` | `1.2.3` |
| After tag | `X.Y.Z-dev.N.hash` | `1.2.4-dev.12.a1b2c3d` |
| Dirty working dir | `X.Y.Z-dev.N.hash-dirty` | `1.2.4-dev.12.a1b2c3d-dirty` |
| No tags | `0.0.0-dev.0.hash` | `0.0.0-dev.0.a1b2c3d` |

**Key design decisions**:

1. **Bump patch for dev versions**: Ensures correct semver sorting—dev versions sort
   *before* the next release, not after the current one

2. **Hash in pre-release, not metadata**: npm strips build metadata (`+hash`), so embed
   the hash in the pre-release identifier (`-dev.N.hash`)

3. **Dirty marker**: Identifies uncommitted changes during development

**Implementation in tsdown.config.ts**:

```ts
import { execSync } from 'node:child_process';
import { defineConfig } from 'tsdown';
import pkg from './package.json' with { type: 'json' };

function getGitVersion(): string {
  try {
    const git = (args: string) =>
      execSync(`git ${args}`, { encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();

    const tag = git('describe --tags --abbrev=0');
    const tagVersion = tag.replace(/^v/, '');
    const [major, minor, patch] = tagVersion.split('.').map(Number);
    const commitsSinceTag = parseInt(git(`rev-list ${tag}..HEAD --count`), 10);
    const hash = git('rev-parse --short=7 HEAD');

    let dirty = false;
    try {
      git('diff --quiet');
      git('diff --cached --quiet');
    } catch {
      dirty = true;
    }

    if (commitsSinceTag === 0 && !dirty) {
      return tagVersion;
    }

    const bumpedPatch = (patch ?? 0) + 1;
    const suffix = dirty ? `${hash}-dirty` : hash;
    return `${major}.${minor}.${bumpedPatch}-dev.${commitsSinceTag}.${suffix}`;
  } catch {
    return pkg.version;
  }
}

export default defineConfig({
  // ...
  define: {
    __VERSION__: JSON.stringify(getGitVersion()),
  },
});
```

**Library usage**:

```ts
// src/index.ts
declare const __VERSION__: string;
export const VERSION: string =
  typeof __VERSION__ !== 'undefined' ? __VERSION__ : 'development';
```

**Comparison with Python (uv-dynamic-versioning)**:

| Aspect | npm (this approach) | Python (PEP 440) |
| --- | --- | --- |
| Format | `1.2.4-dev.12.a1b2c3d` | `1.2.4.dev12+a1b2c3d` |
| Metadata handling | In pre-release (preserved) | Local version `+` (may be stripped) |
| Sorting | Standard semver | PEP 440 compliant |
| Configuration | In bundler config | In `pyproject.toml` |

**Assessment**: Dynamic versioning complements Changesets—use Changesets for releases
and git-based versioning for development builds.
This provides full traceability without manual intervention.

* * *

### 8. CI/CD Configuration

#### GitHub Actions: CI Workflow

**Status**: Recommended

**`.github/workflows/ci.yml`**:
```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - uses: pnpm/action-setup@v4
        with:
          version: 10

      - uses: actions/setup-node@v6
        with:
          node-version: 24
          cache: pnpm

      - run: pnpm install --frozen-lockfile
      - run: pnpm format:check
      - run: pnpm lint:check
      - run: pnpm build
      - run: pnpm publint
      - run: pnpm test
```

**Key points**:

- Node.js 24 is the current LTS ("Krypton", active until Oct 2026, maintained until Apr
  2028\)

- `actions/checkout@v5` requires Actions Runner v2.327.1+ (node24 runtime)

- `pnpm/action-setup@v4` includes built-in caching

- `actions/setup-node@v6` with `cache: pnpm` provides additional caching

- `--frozen-lockfile` ensures CI uses exact versions from lockfile

**References**:

- [pnpm action-setup](https://github.com/pnpm/action-setup)

- [pnpm Continuous Integration](https://pnpm.io/continuous-integration)

* * *

#### GitHub Actions: Release Workflow

**Status**: Recommended

**`.github/workflows/release.yml`**:
```yaml
name: Release

on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0

      - uses: pnpm/action-setup@v4
        with:
          version: 10

      - uses: actions/setup-node@v6
        with:
          node-version: 24
          cache: pnpm
          registry-url: "https://registry.npmjs.org"

      - run: pnpm install --frozen-lockfile

      - name: Create Release PR or Publish
        uses: changesets/action@v1
        with:
          publish: pnpm release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**Repository settings required**:

- Settings → Actions → General → Workflow permissions → **Read and write**

- Add `NPM_TOKEN` secret when ready to publish to npm

**References**:

- [Changesets GitHub Action](https://github.com/changesets/action)

- [Using Changesets with pnpm](https://pnpm.io/using-changesets)

* * *

### 9. Code Formatting

#### Prettier

**Status**: Essential

**Details**:

Prettier provides consistent code formatting across the project.
Configure it once and let it handle all formatting decisions automatically.

**Installation**:
```bash
pnpm add -Dw prettier eslint-config-prettier
```

**`.prettierrc`**:
```json
{
  "$schema": "https://json.schemastore.org/prettierrc",
  "printWidth": 100,
  "singleQuote": true,
  "trailingComma": "all",
  "semi": true,
  "arrowParens": "always",
  "tabWidth": 2,
  "useTabs": false
}
```

**`.prettierignore`**:
```
dist
node_modules
pnpm-lock.yaml
*.min.js
*.min.css
coverage
```

**Key configuration choices**:

| Option | Recommended | Rationale |
| --- | --- | --- |
| `printWidth` | 100 | Wider than default 80; fits modern screens |
| `singleQuote` | true | Common in JS ecosystem, less visual noise |
| `trailingComma` | "all" | Cleaner diffs, easier reordering |
| `semi` | true | Explicit; avoids ASI edge cases |

**Assessment**: Prettier eliminates formatting debates and ensures consistency.
Use `eslint-config-prettier` to disable ESLint rules that conflict with Prettier.

**References**:

- [Prettier Documentation](https://prettier.io/docs/)

- [eslint-config-prettier](https://github.com/prettier/eslint-config-prettier)

* * *

#### Format Scripts Pattern

**Status**: Recommended

**Details**:

Structure format and lint scripts to support both auto-fix and CI verification modes.

**Root `package.json` scripts**:
```json
{
  "scripts": {
    "format": "prettier --write --log-level warn .",
    "format:check": "prettier --check --log-level warn .",
    "lint": "eslint . --fix && pnpm typecheck && eslint . --max-warnings 0",
    "lint:check": "pnpm typecheck && eslint . --max-warnings 0",
    "typecheck": "tsc -b",
    "build": "pnpm format && pnpm lint:check && <build-command>"
  }
}
```

**Script purposes**:

| Script | Purpose | When to use |
| --- | --- | --- |
| `format` | Auto-format changed files (quiet for unchanged) | Local development |
| `format:check` | Verify formatting (quiet for valid files) | CI |
| `lint` | Lint with auto-fix, then verify zero warnings | Local development |
| `lint:check` | Lint without fix, zero warnings | CI, pre-build |
| `build` | Format, lint, then build | Production builds |

**Key insight**: The `lint` script runs ESLint twice: first with `--fix` to auto-fix
issues, then again with `--max-warnings 0` to catch any unfixable warnings.
This ensures auto-fix doesn’t mask problems that require manual attention.

**Key insight**: Using `--log-level warn` with Prettier suppresses the verbose output
that lists every unchanged file.
This keeps output clean—only files that were actually changed (or have issues in check
mode) are shown.

**Key insight**: The `build` script runs `format` before `lint:check`. This ensures
formatting is applied before linting, catching any formatting issues that would fail the
lint check.

**Assessment**: Separating `--fix` variants (for local use) from `--check` variants (for
CI) provides the best developer experience while ensuring CI catches issues.

* * *

### 10. Git Hooks & Local Validation

#### Lefthook

**Status**: Recommended

**Details**:

Lefthook is a fast, cross-platform Git hooks manager written in Go.
It provides a better developer experience than Husky + lint-staged while being faster
and having no Node.js runtime dependency for the hook runner itself.

**Why Lefthook over Husky + lint-staged**:

| Aspect | Lefthook | Husky + lint-staged |
| --- | --- | --- |
| Runtime | Go binary (fast) | Node.js (slower startup) |
| Configuration | Single YAML file | Multiple config files |
| Parallel execution | Built-in | Requires configuration |
| Staged files | Native support | Via lint-staged |
| Monorepo support | Excellent (`root:` option) | Requires workarounds |

**Installation**:
```bash
pnpm add -Dw lefthook
npx lefthook install
```

**References**:

- [Lefthook Documentation](https://github.com/evilmartians/lefthook)

- [Lefthook vs Husky](https://evilmartians.com/chronicles/lefthook-knock-your-teams-code-back-into-shape)

* * *

#### Pre-commit Hooks Strategy

**Status**: Recommended

**Details**:

Pre-commit hooks should be **fast** (target: 2-5 seconds) to avoid disrupting developer
flow.
Run checks in parallel, operate only on staged files, and use caching aggressively.

**Key principles**:

1. **Parallel execution**: Run independent checks simultaneously

2. **Staged files only**: Don’t waste time checking unchanged code

3. **Auto-fix and re-stage**: Fix formatting/linting issues automatically

4. **Incremental type checking**: Use TypeScript’s `--incremental` flag

5. **Cache everything**: ESLint cache, TypeScript build info, etc.

**Example `lefthook.yml` (pre-commit)**:
```yaml
pre-commit:
  parallel: true

  commands:
    # Auto-format with prettier (~500ms)
    format:
      glob: "*.{js,ts,tsx,json}"
      run: npx prettier --write --log-level warn {staged_files}
      stage_fixed: true
      priority: 1

    # Lint with auto-fix and caching (~1s first, ~200ms cached)
    lint:
      glob: "*.{js,ts,tsx}"
      run: >
        npx eslint
        --cache
        --cache-location node_modules/.cache/eslint
        --fix {staged_files}
      stage_fixed: true
      priority: 2

    # Type check with incremental mode (~2s)
    typecheck:
      glob: "*.{ts,tsx}"
      run: npx tsc --noEmit --incremental
      priority: 3
```

**Monorepo considerations**: Use `root:` to scope commands to specific packages:
```yaml
commands:
  lint:
    root: "packages/core/"
    glob: "*.{ts,tsx}"
    run: npx eslint --fix {staged_files}
```

**Assessment**: Fast pre-commit hooks catch issues early without slowing down commits.
The auto-fix pattern reduces friction—developers don’t need to manually format code.

* * *

#### Pre-push Hooks Strategy

**Status**: Recommended

**Details**:

Pre-push hooks can be **slower** (target: 3-5s with cache, <30s without) since pushes
are less frequent. Use these for comprehensive validation that would be too slow for
pre-commit.

**Key principles**:

1. **Run full test suite**: Not just changed files

2. **Use commit-hash caching**: Skip tests if already passed for this commit

3. **Detect uncommitted changes**: Re-run tests if working tree is dirty

4. **Provide clear escape hatch**: Document `--no-verify` for emergencies

**Example `lefthook.yml` (pre-push)**:
```yaml
pre-push:
  commands:
    verify-tests:
      run: |
        echo "🔍 Checking test status for push..."

        COMMIT_HASH=$(git rev-parse HEAD)
        CACHE_DIR="node_modules/.test-cache"
        CACHE_FILE="$CACHE_DIR/$COMMIT_HASH"

        # Check for uncommitted changes
        if ! git diff --quiet || ! git diff --cached --quiet; then
          echo "⚠️  Uncommitted changes detected"
          echo "📊 Running test suite..."
          pnpm test
          exit $?
        fi

        # Check cache
        if [ -f "$CACHE_FILE" ]; then
          SHORT_HASH=$(echo "$COMMIT_HASH" | cut -c1-8)
          echo "✓ Tests already passed for commit $SHORT_HASH"
          exit 0
        fi

        # No cache, run tests
        echo "📊 Running test suite..."
        pnpm test

        # Cache on success
        if [ $? -eq 0 ]; then
          mkdir -p "$CACHE_DIR"
          touch "$CACHE_FILE"
          echo "✅ Tests cached for commit $(echo $COMMIT_HASH | cut -c1-8)"
        else
          echo "❌ Tests failed - push blocked"
          echo "Bypass with: git push --no-verify"
          exit 1
        fi
```

**Assessment**: Commit-hash caching ensures tests only run once per commit, making
repeated push attempts instant.
This is especially valuable when rebasing or when a push fails for non-test reasons.

* * *

#### CI vs Local Hook Relationship

**Status**: Best Practice

**Details**:

Local hooks and CI should complement each other:

| Check | Pre-commit | Pre-push | CI |
| --- | --- | --- | --- |
| Format | ✅ Auto-fix | — | ✅ Verify |
| Lint | ✅ Auto-fix | — | ✅ Verify |
| Typecheck | ✅ Incremental | — | ✅ Full |
| Unit tests | ⚠️ Changed only | ✅ Full | ✅ Full |
| Integration tests | — | ⚠️ Optional | ✅ Full |
| Build | — | — | ✅ Full |
| publint | — | — | ✅ Full |

**Key insight**: Pre-commit hooks fix issues, CI verifies correctness.
Never skip CI because hooks passed—hooks can be bypassed with `--no-verify`.

**Root `package.json` integration**:
```json
{
  "scripts": {
    "prepare": "lefthook install"
  },
  "devDependencies": {
    "lefthook": "^2.0.0"
  }
}
```

**References**:

- [Lefthook Configuration](https://github.com/evilmartians/lefthook/blob/master/docs/configuration.md)

- [Git Hooks Best Practices](https://pre-commit.com/#introduction)

* * *

### 11. Dependency Upgrade Management

#### npm-check-updates (ncu)

**Status**: Recommended

**Details**:

npm-check-updates (`ncu`) provides a safe, structured approach to keeping dependencies
current. It supports upgrade targets that let you control how aggressively to upgrade,
making it easy to separate low-risk minor/patch updates from potentially breaking major
updates.

**Installation**:
```bash
pnpm add -Dw npm-check-updates
```

**Key flags**:

| Flag | Description |
| --- | --- |
| `--target minor` | Only upgrade to latest minor/patch (safe) |
| `--target patch` | Only upgrade to latest patch (safest) |
| `--target latest` | Upgrade to latest version (includes major) |
| `--format group` | Group output by update type (major/minor/patch) |
| `--interactive` | Select which packages to upgrade |
| `-u` | Update package.json (otherwise just reports) |

**Upgrade Targets Explained**:

- **patch**: Only upgrade `1.0.0` → `1.0.x` (bug fixes only)

- **minor**: Upgrade `1.0.0` → `1.x.x` (new features, backwards compatible)

- **latest**: Upgrade to latest published version (may include breaking changes)

- **newest**: Upgrade to newest version, even if not latest (e.g., prereleases)

- **greatest**: Upgrade to greatest version number

**Assessment**: Using upgrade targets separates routine maintenance (minor/patch) from
potentially breaking changes (major), enabling a safer, more frequent upgrade cadence.

**References**:

- [npm-check-updates documentation](https://www.npmjs.com/package/npm-check-updates)

- [ncu GitHub repository](https://github.com/raineorshine/npm-check-updates)

* * *

#### Upgrade Scripts Pattern

**Status**: Recommended

**Details**:

Add structured upgrade scripts to your root `package.json` that encode your upgrade
workflow. This makes upgrades consistent and discoverable.

**Root `package.json` scripts**:
```json
{
  "scripts": {
    "upgrade:check": "ncu --format group",
    "upgrade": "ncu --target minor -u && pnpm install && pnpm test",
    "upgrade:patch": "ncu --target patch -u && pnpm install && pnpm test",
    "upgrade:major": "ncu --target latest --interactive --format group"
  }
}
```

**Script descriptions**:

| Script | Purpose |
| --- | --- |
| `upgrade:check` | Show available updates grouped by type (no changes) |
| `upgrade` | Safe upgrade: minor+patch versions, install, and test |
| `upgrade:patch` | Conservative upgrade: patch versions only |
| `upgrade:major` | Interactive selection for major version changes |

**Workflow**:

1. **Check for updates**: `pnpm upgrade:check` — see what’s available without changing
   anything

2. **Safe upgrade**: `pnpm upgrade` — upgrade minor/patch versions and run tests to
   verify nothing breaks

3. **Major upgrades**: `pnpm upgrade:major` — interactively review major version bumps,
   select which to apply, then test and review changelogs

**Key insight**: Running tests after `upgrade` catches regressions immediately.
If tests fail, you can `git checkout package.json pnpm-lock.yaml && pnpm install` to
rollback before investigating.

**Assessment**: This pattern enables frequent, low-risk dependency updates while
maintaining control over potentially breaking changes.

* * *

#### Monorepo Considerations

**Status**: Best Practice

**Details**:

In a pnpm monorepo, run ncu from the workspace root to update all packages consistently:

```bash
# Check all workspace packages
pnpm ncu --format group -ws

# Upgrade minor versions in all packages
pnpm ncu --target minor -u -ws && pnpm install && pnpm test
```

For selective package updates:
```bash
# Upgrade specific packages only
pnpm ncu --filter "@scope/*" --target minor -u
```

**Handling peer dependency conflicts**:

Some packages may have strict peer dependency requirements that conflict during
upgrades. Options:

1. **Use `--legacy-peer-deps`** (npm): `npm install --legacy-peer-deps`

2. **Pin conflicting versions**: Lock specific versions in `pnpm.overrides`:
   ```json
   {
     "pnpm": {
       "overrides": {
         "react": "^18.3.0"
       }
     }
   }
   ```

3. **Staged upgrades**: Upgrade conflicting packages together in one commit

**References**:

- [pnpm overrides documentation](https://pnpm.io/package_json#pnpmoverrides)

* * *

### 12. CLI Development Workflow

#### Running CLI from Source

**Status**: Strongly Recommended

**Details**:

During development, CLI commands should run directly from TypeScript source rather than
requiring a build step.
This ensures developers always work with the current code and eliminates the common
frustration of debugging stale builds.

**The dual-script pattern**:

```json
{
  "scripts": {
    "cli-name": "tsx packages/package-name/src/cli/bin.ts",
    "cli-name:bin": "node packages/package-name/dist/bin.mjs"
  }
}
```

| Script | Purpose | When to use |
| --- | --- | --- |
| `cli-name` | Runs source via tsx | Development—always current, no build needed |
| `cli-name:bin` | Runs built binary | Pre-release verification of published output |

**Why this matters**:

1. **No stale builds**: Developers never accidentally run old code while debugging

2. **Faster iteration**: No build step between code changes and testing

3. **Reduced confusion**: “Did I forget to build?”
   is never the answer

4. **Still verifiable**: The `:bin` variant ensures the production build works correctly

* * *

#### tsx vs vite-node vs ts-node

**Status**: tsx Recommended

**Details**:

For running TypeScript CLI commands directly, **tsx** is the recommended choice:

| Aspect | tsx | vite-node | ts-node |
| --- | --- | --- | --- |
| **Speed** | 5-10x faster than ts-node | Fast (esbuild) | Slow |
| **Startup time** | Single-digit milliseconds | Fast | Noticeable delay |
| **Configuration** | Zero-config | Requires Vite familiarity | Often needs config |
| **Use case** | CLI and scripts | Vite ecosystem projects | Legacy projects |
| **Maintenance** | Active | Active | Active but slower |

**When to choose each**:

- **tsx**: Default choice for CLI development, scripts, and simple TypeScript execution

- **vite-node**: When you need Vite’s plugin ecosystem (e.g., CSS imports, asset
  handling)

- **ts-node**: Only for legacy projects already using it

**Example implementation**:

```json
{
  "scripts": {
    "markform": "tsx packages/markform/src/cli/bin.ts",
    "markform:bin": "node packages/markform/dist/bin.mjs"
  },
  "devDependencies": {
    "tsx": "^4.21.0"
  }
}
```

**Assessment**: tsx provides the best developer experience for CLI development.
It uses esbuild for near-instant compilation while maintaining compatibility with all
modern TypeScript features.
Reserve vite-node for projects that specifically need Vite’s transformation pipeline.

**References**:

- [tsx documentation](https://tsx.is/)

- [TSX vs ts-node
  comparison](https://betterstack.com/community/guides/scaling-nodejs/tsx-vs-ts-node/)

- [ts-runtime-comparison benchmarks](https://github.com/privatenumber/ts-runtime-comparison)

* * *

### 13. Private Package Distribution

#### Option A: GitHub Packages (Recommended)

**Status**: Recommended for teams

**Details**:

GitHub Packages provides a private npm registry with standard npm semantics.

**Requirements**:

- Package must be scoped (`@org/package-name`)

- Repository name should match organization/scope

**Publisher `.npmrc`**:
```ini
@your-org:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
```

**Consumer `.npmrc`**:
```ini
@your-org:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=YOUR_GITHUB_TOKEN
```

**Install command**: `pnpm add @your-org/package-name`

**Assessment**: Lowest-friction option for teams.
Works exactly like npm but private.
No build-on-install quirks.

**References**:

- [GitHub npm registry
  documentation](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-npm-registry)

- [Publish NPM Package to GitHub Packages
  Registry](https://www.neteye-blog.com/2024/09/publish-npm-package-to-github-packages-registry-with-github-actions/)

* * *

#### Option B: Direct GitHub Install (pnpm)

**Status**: Viable for development

**Details**:

pnpm v9+ supports installing from a monorepo subdirectory:

```bash
pnpm add github:org/repo#path:packages/package-name
```

**Caveats**:

- Requires the package to be pre-built (dist must exist) OR lifecycle scripts must build
  it

- Less reliable than registry-based installs

- Version pinning is less precise

**Assessment**: Good for rapid development and testing.
Use GitHub Packages or npm for production.

**References**:

- [pnpm discussion: Add dependency from git
  monorepo](https://github.com/orgs/pnpm/discussions/8194)

* * *

#### Option C: Local Linking

**Status**: Best for development

**Details**:

For active development across repositories:

```bash
# In consumer project
pnpm add ../path-to-monorepo/packages/package-name
```

Or use `pnpm link`:
```bash
# In package directory
pnpm link --global

# In consumer project
pnpm link --global @scope/package-name
```

**Assessment**: Essential for local development iteration.
Not suitable for distribution.

* * *

#### Bun Compatibility Note

**Status**: Limited

**Details**:

Bun supports GitHub dependencies but has limited support for monorepo subdirectory
installs. For Bun consumers, GitHub Packages or npm publishing provides the smoothest
experience.

**References**:

- [Bun: Add a Git dependency](https://bun.sh/docs/guides/install/add-git)

- [Bun issue: Support installing Git dependency from
  subdirectory](https://github.com/oven-sh/bun/issues/15506)

* * *

### 14. Library/CLI Hybrid Packages

#### Node-Free Core Pattern

**Status**: Recommended

**Details**:

When building a package that functions as both a library and a CLI tool, **isolate all
Node.js dependencies to CLI-only code**. This allows the core library to be used in
non-Node environments (browsers, edge runtimes, Cloudflare Workers, Convex, etc.).

Node.js-specific imports like `node:path`, `node:fs`, or `node:module` will cause
bundler errors or runtime failures in non-Node environments.
Even if only the CLI uses these imports, if they’re in shared code, the entire library
becomes Node-dependent.

**Directory Structure for Isolation**:

Keep CLI code in a dedicated subdirectory:

```
src/
├── index.ts           # Library entry point (NO node: imports)
├── settings.ts        # Configuration constants (NO node: imports)
├── engine/            # Core library code (NO node: imports)
├── cli/               # CLI-only code (node: imports OK here)
│   ├── cli.ts         # CLI entry point
│   ├── commands/      # Command implementations
│   └── lib/           # CLI utilities (path resolution, etc.)
└── integrations/      # Optional integrations (NO node: imports)
```

**Assessment**: This pattern is essential for libraries targeting multiple runtimes.
The directory structure creates clear boundaries that are easy to enforce with automated
tests.

* * *

#### Pattern: Move Node.js Utilities to CLI

**Status**: Recommended

**Details**:

Configuration constants belong in node-free files; functions that use Node.js APIs
belong in CLI-specific code:

```ts
// BAD: Node.js import in shared settings
// src/settings.ts
import { resolve } from 'node:path';

export const DEFAULT_OUTPUT_DIR = './output';

export function getOutputDir(override?: string): string {
  return resolve(process.cwd(), override ?? DEFAULT_OUTPUT_DIR);
}

// GOOD: Constant in settings, function in CLI
// src/settings.ts (node-free)
export const DEFAULT_OUTPUT_DIR = './output';

// src/cli/lib/paths.ts (node: imports OK)
import { resolve } from 'node:path';
import { DEFAULT_OUTPUT_DIR } from '../../settings.js';

export { DEFAULT_OUTPUT_DIR };  // Re-export for CLI convenience

export function getOutputDir(override?: string): string {
  return resolve(process.cwd(), override ?? DEFAULT_OUTPUT_DIR);
}
```

**Assessment**: This pattern keeps the core library portable while providing full
Node.js functionality in CLI contexts.

* * *

#### Pattern: Build-Time Constants

**Status**: Recommended

**Details**:

For values that need Node.js at build time (like reading `package.json`), use bundler
`define` options to inject them as compile-time constants:

```ts
// tsdown.config.ts / esbuild / rollup config
import pkg from './package.json' with { type: 'json' };

export default {
  define: {
    __VERSION__: JSON.stringify(pkg.version),
  },
};

// src/index.ts (node-free)
declare const __VERSION__: string;

export const VERSION: string =
  typeof __VERSION__ !== 'undefined' ? __VERSION__ : 'development';
```

**Assessment**: Build-time injection eliminates runtime Node.js dependencies for values
that are constant at build time.
This is cleaner than dynamic requires or filesystem reads.

* * *

#### Guard Tests for Node-Free Core

**Status**: Strongly Recommended

**Details**:

Add automated tests to prevent Node.js dependency leaks:

```ts
// tests/node-free-core.test.ts
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const SRC_DIR = 'src';
const NODE_ALLOWED_DIRS = ['cli'];  // Only CLI can use node:
const NODE_IMPORT_PATTERN = /from\s+['"]node:/g;

function getAllTsFiles(dir: string): string[] { /* recursive scan */ }

describe('Node-free core library', () => {
  it('source files outside cli/ should not import from node:', () => {
    const violations: string[] = [];

    for (const file of getAllTsFiles(SRC_DIR)) {
      const rel = relative(SRC_DIR, file);
      if (NODE_ALLOWED_DIRS.some(d => rel.startsWith(d + '/'))) continue;

      const content = readFileSync(file, 'utf-8');
      if (NODE_IMPORT_PATTERN.test(content)) {
        violations.push(rel);
      }
    }

    expect(violations).toHaveLength(0);
  });

  it('dist/index.mjs should not reference node: modules', () => {
    const content = readFileSync('dist/index.mjs', 'utf-8');
    expect(content).not.toMatch(NODE_IMPORT_PATTERN);
  });
});
```

**Assessment**: Guard tests catch accidental node: imports during development rather
than discovering them when users try to use the library in browser/edge contexts.

* * *

#### Checklist for Library/CLI Packages

**Status**: Best Practice

**Checklist**:

- [ ] Core library entry point (`index.ts`) has no `node:` imports

- [ ] All `node:` imports are in `cli/` directory only

- [ ] Configuration constants are in node-free files

- [ ] Build-time values use bundler `define` injection

- [ ] Guard tests prevent future regressions

- [ ] Built output (`dist/*.mjs`) has no `node:` references

**References**:

- [CLI Tool Development Rules](../../agent-rules/typescript-cli-tool-rules.md) —
  CLI-specific patterns using Commander.js, picocolors, and @clack/prompts

* * *

## Comparative Analysis

### Build Tools Comparison

| Criteria | tsdown | tsup | unbuild | Rollup |
| --- | --- | --- | --- | --- |
| Active maintenance | Yes | No (abandoned) | Yes | Yes |
| ESM-first | Yes | No (CJS-first) | Yes | Yes |
| DTS generation | Built-in | Built-in | Built-in | Plugin required |
| Multi-entry | Yes | Yes | Yes | Yes |
| Config simplicity | Excellent | Good | Good | Complex |
| Speed | Fast (Rust) | Fast (esbuild) | Moderate | Moderate |
| Plugin ecosystem | Rolldown/Rollup/Vite | esbuild | unbuild | Rollup |

**Recommendation**: tsdown for new projects; migrate from tsup if currently using it.

* * *

### Package Manager Comparison

| Criteria | pnpm | npm | yarn |
| --- | --- | --- | --- |
| Disk efficiency | Excellent | Poor | Moderate |
| Workspace support | Built-in | Built-in (v7+) | Built-in |
| Strict mode | Yes (default) | No | Optional |
| Speed | Fast | Moderate | Fast |
| Monorepo tooling | Excellent | Basic | Good |

**Recommendation**: pnpm for monorepos.

* * *

## Best Practices

1. **Scope your package names**: Use `@org/package-name` format for easier GitHub
   Packages integration and namespace clarity.

2. **Structure for splitting**: Organize internal code (`core/`, `cli/`, `adapters/`) to
   make future package splits painless.

3. **Use subpath exports from day one**: Define `./cli`, `./adapter` exports even in
   v0.1 to stabilize the API surface.

4. **Types first in exports**: Always put `"types"` condition before `"default"` in
   export conditions.

5. **Optional peer deps for integrations**: Don’t force SDK dependencies on users who
   don’t need them.

6. **Validate before publish**: Run publint in CI and before every release.

7. **Changeset per PR**: Require changesets for user-facing changes to maintain accurate
   changelogs.

8. **Lock your tooling versions**: Pin exact versions in `packageManager` field and CI
   configurations.

9. **Test both ESM and CJS**: Ensure both module formats work correctly, especially for
   CLI tools.

10. **Keep the monorepo root private**: The root `package.json` should have `"private":
    true` and only contain workspace tooling.

11. **Use type-aware ESLint**: Configure `recommendedTypeChecked` for comprehensive bug
    detection, especially promise safety rules.
    See Appendix C for detailed configuration.

12. **Enforce code style consistency**: Use `curly: 'all'` and `brace-style: '1tbs'` to
    prevent subtle bugs and improve readability.

13. **Use fast pre-commit hooks**: Run formatting and linting with auto-fix on staged
    files only. Target 2-5 seconds total.
    Use lefthook for better monorepo support.

14. **Cache test results by commit hash**: In pre-push hooks, skip test runs if the
    current commit has already passed tests.
    This makes repeated pushes instant.

15. **Use structured upgrade scripts**: Add `upgrade:check`, `upgrade`, and
    `upgrade:major` scripts to make dependency updates consistent and safe.
    Separate minor/patch from major upgrades.

16. **Separate format and lint script variants**: Provide `format`/`format:check` and
    `lint`/`lint:check` scripts.
    Use `--fix` variants for local development and `--check`/zero-warnings variants for
    CI.

17. **Run format before lint in builds**: The `build` script should run `format` then
    `lint:check` to ensure formatting is applied before linting.

18. **Use dynamic git-based versioning**: Inject version at build time using
    `X.Y.Z-dev.N.hash` format.
    This provides traceability during development without manual version bumps.
    See “Dynamic Git-Based Versioning” section for implementation.

19. **Run CLI from source during development**: Use the dual-script pattern with tsx to
    run CLI commands directly from TypeScript source.
    Provide a separate `:bin` script for verifying the built output.
    This eliminates “did I forget to build?”
    confusion.

* * *

## Open Research Questions

1. **Rolldown Vite Library Mode**: tsdown is positioned to become the foundation for
   Rolldown Vite’s Library Mode.
   Monitor for announcements that may affect best practices.

2. **TypeScript 6.0/7.0 Transition**: TypeScript 7.0 will be a complete rewrite in Go,
   promising up to 10x faster builds.
   TypeScript 6.0 will serve as a transition point.
   Monitor for migration guidance and breaking changes.

3. **Native TypeScript Execution**: TypeScript 5.8+ supports `--erasableSyntaxOnly`
   flag, enabling direct execution in Node.js 23.6+ without transpilation.
   This may reduce the need for tsx in some workflows.
   Monitor for broader adoption and tooling support.

4. **ESLint v10 multi-config**: ESLint v10 promises stable support for multiple config
   files in monorepos. Currently, a single root config is recommended but has
   limitations.

* * *

## Recommendations

### Summary

Use a pnpm monorepo with tsdown for building, Changesets for versioning, publint for
validation, Prettier for code formatting, lefthook for fast local git hooks, and
npm-check-updates for structured dependency upgrades.
Structure code internally for future splits while exposing a stable API through subpath
exports.
Start with GitHub Packages for private distribution, then transition to npm when
ready for public release.

### Recommended Approach

1. **Initialize workspace** with pnpm and a single package in `packages/`

2. **Configure tsdown** for dual ESM/CJS output with TypeScript declarations

3. **Set up subpath exports** for main entry and any adapters/integrations

4. **Add Changesets** for version management

5. **Configure Prettier** with eslint-config-prettier for consistent formatting

6. **Configure lefthook** for pre-commit (format, lint, typecheck) and pre-push (tests)

7. **Add upgrade scripts** for structured dependency management

8. **Configure CI** with format:check, lint:check, typecheck, build, publint, and test

9. **Configure release workflow** with Changesets GitHub Action

10. **Validate with publint** before every release

**Rationale**:

- Minimal overhead to start, clear path to scale

- Industry-standard tooling with active maintenance

- Supports both private and public distribution

- Enables fast iteration without accumulating technical debt

### Alternative Approaches

- **Nx or Turborepo**: For larger monorepos with complex dependency graphs, consider
  adding Nx or Turborepo for caching and task orchestration.
  The pnpm + Changesets foundation integrates well with both.

- **unbuild**: If Rolldown/Vite ecosystem alignment isn’t important, unbuild is another
  solid choice with a different plugin ecosystem.

- **Single-package repo**: For truly simple packages that will never grow, a
  non-monorepo structure is fine.
  However, the monorepo structure overhead is minimal and provides flexibility.

* * *

## References

### Official Documentation

- [pnpm Workspaces](https://pnpm.io/workspaces)

- [pnpm Using Changesets](https://pnpm.io/using-changesets)

- [pnpm Continuous Integration](https://pnpm.io/continuous-integration)

- [tsdown Documentation](https://tsdown.dev/)

- [publint Documentation](https://publint.dev/docs/)

- [Prettier Documentation](https://prettier.io/docs/)

- [Changesets GitHub](https://github.com/changesets/changesets)

- [Node.js Packages (exports)](https://nodejs.org/api/packages.html)

- [TypeScript Module Documentation](https://www.typescriptlang.org/docs/handbook/modules/reference.html)

- [GitHub Packages npm
  registry](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-npm-registry)

- [Node.js Releases](https://nodejs.org/en/about/previous-releases)

### Guides & Articles

- [Complete Monorepo Guide 2025](https://jsdev.space/complete-monorepo-guide/)

- [Guide to package.json exports field](https://hirok.io/posts/package-json-exports)

- [Ship ESM & CJS in one Package](https://antfu.me/posts/publish-esm-and-cjs)

- [Building npm package compatible with ESM and CJS in
  2024](https://snyk.io/blog/building-npm-package-compatible-with-esm-and-cjs-2024/)

- [TypeScript in 2025: ESM and CJS
  publishing](https://lirantal.com/blog/typescript-in-2025-with-esm-and-cjs-npm-publishing)

- [Switching from tsup to tsdown](https://alan.norbauer.com/articles/tsdown-bundler/)

- [Live types in a TypeScript
  monorepo](https://colinhacks.com/essays/live-types-typescript-monorepo)

- [Is nodenext right for
  libraries?](https://blog.andrewbran.ch/is-nodenext-right-for-libraries-that-dont-target-node-js/)

### GitHub Actions

- [pnpm/action-setup](https://github.com/pnpm/action-setup)

- [changesets/action](https://github.com/changesets/action)

* * *

## Appendices

### Appendix A: Complete package.json Example

```json
{
  "name": "@scope/package-name",
  "version": "0.1.0",
  "description": "Package description",
  "license": "MIT",
  "type": "module",
  "sideEffects": false,
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.js"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    },
    "./cli": {
      "import": {
        "types": "./dist/cli.d.ts",
        "default": "./dist/cli.js"
      },
      "require": {
        "types": "./dist/cli.d.cts",
        "default": "./dist/cli.cjs"
      }
    },
    "./package.json": "./package.json"
  },
  "bin": {
    "package-name": "./dist/bin.js"
  },
  "files": ["dist"],
  "engines": {
    "node": ">=24"
  },
  "scripts": {
    "build": "tsdown",
    "dev": "tsdown --watch",
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "test": "node --test",
    "publint": "publint",
    "prepack": "pnpm build"
  },
  "dependencies": {},
  "peerDependencies": {
    "optional-sdk": "^1.0.0"
  },
  "peerDependenciesMeta": {
    "optional-sdk": { "optional": true }
  },
  "devDependencies": {
    "@types/node": "^24.0.0",
    "publint": "^0.3.0",
    "tsdown": "^0.18.0",
    "typescript": "^5.9.0"
  }
}
```

### Appendix B: Root package.json Example

```json
{
  "name": "project-workspace",
  "private": true,
  "packageManager": "pnpm@10.27.0",
  "engines": {
    "node": ">=24"
  },
  "scripts": {
    "build": "pnpm -r build",
    "typecheck": "pnpm -r typecheck",
    "test": "pnpm -r test",
    "publint": "pnpm -r publint",
    "format": "prettier --write --log-level warn .",
    "format:check": "prettier --check --log-level warn .",
    "lint": "eslint . --fix && pnpm typecheck && eslint . --max-warnings 0",
    "lint:check": "pnpm typecheck && eslint . --max-warnings 0",
    "prepare": "lefthook install",
    "changeset": "changeset",
    "version-packages": "changeset version",
    "release": "pnpm build && pnpm publint && changeset publish",
    "upgrade:check": "ncu --format group",
    "upgrade": "ncu --target minor -u && pnpm install && pnpm test",
    "upgrade:major": "ncu --target latest --interactive --format group"
  },
  "devDependencies": {
    "@changesets/cli": "^2.29.0",
    "@changesets/changelog-github": "^0.5.0",
    "@eslint/js": "^9.0.0",
    "eslint": "^9.0.0",
    "eslint-config-prettier": "^10.0.0",
    "lefthook": "^2.0.0",
    "npm-check-updates": "^19.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.9.0",
    "typescript-eslint": "^8.0.0"
  }
}
```

### Appendix C: ESLint Flat Config Example

#### Minimal Configuration

For projects just getting started, a minimal configuration:

```javascript
// eslint.config.js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  prettier, // Must be last to override conflicting rules
  {
    ignores: ["**/dist/**", "**/node_modules/**", "**/.pnpm-store/**"],
  },
];
```

#### Strict Type-Aware Configuration (Recommended)

For production projects, use type-aware linting with strict rules.
This catches more bugs but requires tsconfig integration:

```javascript
// eslint.config.js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier";

// Type-aware ESLint configuration using flat config.
// Uses TypeScript's project service for precise, cross-project type information.

// Apply type-checked configs only to TypeScript files
const typedRecommended = tseslint.configs.recommendedTypeChecked.map((cfg) => ({
  ...cfg,
  files: ["**/*.ts", "**/*.tsx"],
  languageOptions: {
    ...(cfg.languageOptions ?? {}),
    parserOptions: {
      ...(cfg.languageOptions?.parserOptions ?? {}),
      projectService: true,
      tsconfigRootDir: import.meta.dirname,
    },
  },
}));

const typedStylistic = tseslint.configs.stylisticTypeChecked.map((cfg) => ({
  ...cfg,
  files: ["**/*.ts", "**/*.tsx"],
  languageOptions: {
    ...(cfg.languageOptions ?? {}),
    parserOptions: {
      ...(cfg.languageOptions?.parserOptions ?? {}),
      projectService: true,
      tsconfigRootDir: import.meta.dirname,
    },
  },
}));

export default [
  // Global ignores
  {
    ignores: [
      "**/dist/**",
      "**/node_modules/**",
      "**/.pnpm-store/**",
      "eslint.config.*",
    ],
  },

  // Base JS rules
  js.configs.recommended,

  // Type-aware TypeScript rules
  ...typedRecommended,
  ...typedStylistic,

  // Prettier config must be last to override conflicting rules
  prettier,

  // TypeScript-specific rules
  {
    files: ["**/*.ts", "**/*.tsx"],
    rules: {
      // === Code Style ===
      // Enforce curly braces for all control statements (prevents bugs)
      curly: ["error", "all"],
      // Consistent brace style: opening on same line, closing on new line
      "brace-style": ["error", "1tbs", { allowSingleLine: false }],

      // === Unused Variables ===
      // Allow underscore prefix for intentionally unused vars/args
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],

      // === Promise Safety (Critical for Node.js) ===
      // Catch unhandled promises (common source of silent failures)
      "@typescript-eslint/no-floating-promises": "error",
      // Prevent passing promises where void is expected (e.g., event handlers)
      "@typescript-eslint/no-misused-promises": [
        "error",
        { checksVoidReturn: { attributes: false } },
      ],
      // Catch awaiting non-promise values
      "@typescript-eslint/await-thenable": "error",
      // Prevent confusing void expressions in unexpected places
      "@typescript-eslint/no-confusing-void-expression": "error",

      // === Type Import Consistency ===
      // Enforce `import type` for type-only imports (better tree-shaking)
      "@typescript-eslint/consistent-type-imports": [
        "error",
        {
          prefer: "type-imports",
          fixStyle: "separate-type-imports",
          disallowTypeAnnotations: true,
        },
      ],
      // Prevent side effects in type-only imports
      "@typescript-eslint/no-import-type-side-effects": "error",

      // === Restricted Patterns ===
      // Forbid inline import() type expressions (prefer proper imports)
      "no-restricted-syntax": [
        "error",
        {
          selector: "TSImportType",
          message:
            "Inline import() type expressions are not allowed. Use a proper import statement at the top of the file instead.",
        },
      ],
    },
  },

  // === File-Specific Overrides ===
  // Relax rules for test files where dynamic behavior is expected
  {
    files: ["**/*.test.ts", "**/*.spec.ts", "**/tests/**/*.ts"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unsafe-assignment": "off",
      "@typescript-eslint/no-unsafe-member-access": "off",
      "@typescript-eslint/no-unsafe-call": "off",
    },
  },

  // Relax rules for scripts/tooling
  {
    files: ["**/scripts/**/*.ts", "**/tools/**/*.ts"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "no-console": "off",
    },
  },
];
```

#### ESLint Best Practices

**Type-Aware vs Basic Linting**:

| Aspect | `recommended` | `recommendedTypeChecked` |
| --- | --- | --- |
| Setup complexity | Simple | Requires tsconfig |
| Performance | Fast | Slower (type analysis) |
| Bug detection | Basic | Comprehensive |
| Promise safety | Limited | Full coverage |
| Best for | Quick setup, small projects | Production code |

**Key Rules Explained**:

1. **`no-floating-promises`**: Catches unhandled promises—a common source of silent
   failures in Node.js:
   ```typescript
   // Bad: Promise result ignored, errors swallowed
   saveData();
   // Good: Explicitly handle or void
   await saveData();
   void saveData(); // Intentionally fire-and-forget
   ```

2. **`consistent-type-imports`**: Enforces `import type` for type-only imports, enabling
   better tree-shaking and clearer intent:
   ```typescript
   // Bad: Runtime import for type-only usage
   import { SomeType } from "./types";
   // Good: Explicit type import
   import type { SomeType } from "./types";
   ```

3. **`curly: ['error', 'all']`**: Prevents bugs from missing braces:
   ```typescript
   // Bad: Easy to introduce bugs when adding lines
   if (condition) doSomething();
   // Good: Always use braces
   if (condition) {
     doSomething();
   }
   ```

4. **Underscore prefix for unused vars**: Convention for intentionally unused
   parameters:
   ```typescript
   // Clear intent: we don't use the error parameter
   .catch((_error) => handleDefaultCase())
   ```

**Common Gotcha with `noUncheckedIndexedAccess`**:

When using `noUncheckedIndexedAccess: true` in tsconfig (recommended for safety),
ESLint’s `no-unnecessary-type-assertion` may incorrectly flag necessary assertions:

```typescript
// With noUncheckedIndexedAccess, array[0] returns T | undefined
const first = array[0]!; // ESLint may wrongly flag this as unnecessary
```

If you encounter false positives, consider disabling the rule:
```javascript
rules: {
  "@typescript-eslint/no-unnecessary-type-assertion": "off",
}
```

**Naming Convention Rules (Optional)**:

For teams wanting consistent naming, add naming convention rules:

```javascript
"@typescript-eslint/naming-convention": [
  "error",
  {
    selector: "parameter",
    format: ["camelCase", "PascalCase"],
    leadingUnderscore: "forbid",
    filter: { regex: "^_", match: false }, // Allow _ prefix for unused
  },
  {
    selector: "parameter",
    format: ["camelCase", "PascalCase"],
    leadingUnderscore: "allow",
    modifiers: ["unused"],
  },
  {
    selector: "variable",
    format: ["camelCase", "PascalCase", "UPPER_CASE"],
    leadingUnderscore: "forbid",
    filter: { regex: "^(__filename|__dirname)$", match: false },
  },
],
```

**CLI-Specific Rules**:

For CLI packages, consider restricting console usage to centralized output functions:

```javascript
{
  files: ["**/cli/**/*.ts"],
  rules: {
    "no-console": ["warn", { allow: ["error"] }],
    "no-restricted-imports": [
      "error",
      {
        patterns: [
          {
            group: ["chalk"],
            message: "Use picocolors for CLI output (smaller, faster).",
          },
        ],
      },
    ],
  },
}
```

### Appendix D: tsdown Config Example

```typescript
// tsdown.config.ts
import { defineConfig } from "tsdown";

export default defineConfig({
  entry: {
    index: "src/index.ts",
    cli: "src/cli/index.ts",
    bin: "src/bin.ts"
  },
  format: ["esm", "cjs"],
  platform: "node",
  target: "node24",
  sourcemap: true,
  dts: true,
  clean: true,
  banner: ({ fileName }) =>
    fileName.startsWith("bin.") ? "#!/usr/bin/env node\n" : ""
});
```

### Appendix E: Complete lefthook.yml Example

```yaml
# lefthook.yml
# Git hooks for code quality
# Pre-commit: Fast checks with auto-fix (target: 2-5 seconds)
# Pre-push: Full test validation with caching (target: 3-5s cached, <30s uncached)

# PHASE 1: Fast pre-commit checks
pre-commit:
  parallel: true

  commands:
    # Auto-format with prettier (~500ms)
    format:
      glob: "*.{js,ts,tsx,json,yaml,yml}"
      run: npx prettier --write --log-level warn {staged_files}
      stage_fixed: true
      priority: 1

    # Lint with auto-fix and caching (~1s first, ~200ms cached)
    lint:
      glob: "*.{js,ts,tsx}"
      run: >
        npx eslint
        --cache
        --cache-location node_modules/.cache/eslint
        --fix {staged_files}
      stage_fixed: true
      priority: 2

    # Type check with incremental mode (~2s)
    typecheck:
      glob: "*.{ts,tsx}"
      run: npx tsc --noEmit --incremental
      priority: 3

    # Test only changed files (optional, ~1-3s)
    # test-changed:
    #   glob: "*.{test,spec}.{ts,tsx}"
    #   run: npx vitest --changed --run
    #   priority: 4

# PHASE 2: Pre-push validation with test caching
pre-push:
  commands:
    verify-tests:
      run: |
        echo "🔍 Checking test status for push..."

        # Get current commit hash
        COMMIT_HASH=$(git rev-parse HEAD)
        CACHE_DIR="node_modules/.test-cache"
        CACHE_FILE="$CACHE_DIR/$COMMIT_HASH"

        # Check for uncommitted changes
        if ! git diff --quiet || ! git diff --cached --quiet; then
          echo "⚠️  Uncommitted changes detected"
          echo "📊 Running test suite..."
          pnpm test
          exit $?
        fi

        # Check cache
        if [ -f "$CACHE_FILE" ]; then
          SHORT_HASH=$(echo "$COMMIT_HASH" | cut -c1-8)
          echo "✓ Tests already passed for commit $SHORT_HASH"
          exit 0
        fi

        # No cache, run tests
        echo "📊 Running test suite..."
        pnpm test

        # Cache on success
        if [ $? -eq 0 ]; then
          mkdir -p "$CACHE_DIR"
          touch "$CACHE_FILE"
          SHORT_HASH=$(echo "$COMMIT_HASH" | cut -c1-8)
          echo "✅ Tests passed and cached for commit $SHORT_HASH"
          exit 0
        else
          echo "❌ Tests failed - push blocked"
          echo "Fix tests and try again, or bypass with: git push --no-verify"
          exit 1
        fi
```

**Monorepo variant** (scope commands to packages):
```yaml
pre-commit:
  parallel: true

  commands:
    format-core:
      root: "packages/core/"
      glob: "*.{ts,tsx}"
      run: npx prettier --write --log-level warn {staged_files}
      stage_fixed: true

    lint-core:
      root: "packages/core/"
      glob: "*.{ts,tsx}"
      run: npx eslint --cache --fix {staged_files}
      stage_fixed: true

    typecheck-core:
      root: "packages/core/"
      glob: "*.{ts,tsx}"
      run: npx tsc -p tsconfig.json --noEmit --incremental
```

### Appendix F: Upgrade Scripts with Documentation

For projects with many scripts, a `scripts-info` field provides inline documentation
that can be queried programmatically:

```json
{
  "scripts": {
    "upgrade:check": "ncu --format group",
    "upgrade": "ncu --target minor -u && pnpm install && pnpm test",
    "upgrade:patch": "ncu --target patch -u && pnpm install && pnpm test",
    "upgrade:major": "ncu --target latest --interactive --format group",
    "help": "tsx scripts/help.ts"
  },
  "scripts-info": {
    "upgrade:check": "Check for outdated packages grouped by type (no changes)",
    "upgrade": "Safe upgrade: minor+patch versions, install, and test",
    "upgrade:patch": "Conservative upgrade: patch versions only, install, and test",
    "upgrade:major": "Interactive upgrade for major version changes"
  }
}
```

**Simple help script** (`scripts/help.ts`):
```typescript
import { readFileSync } from "node:fs";

const pkg = JSON.parse(readFileSync("package.json", "utf-8"));
const info = pkg["scripts-info"] ?? {};

console.log("\nAvailable scripts:\n");
for (const [name, desc] of Object.entries(info)) {
  console.log(`  ${name.padEnd(20)} ${desc}`);
}
```

**Additional ncu options for complex projects**:

```json
{
  "scripts": {
    "upgrade:check": "ncu --format group",
    "upgrade:check:all": "ncu --format group -ws",
    "upgrade": "ncu --target minor -u && pnpm install && pnpm test",
    "upgrade:all": "ncu --target minor -u -ws && pnpm install && pnpm test",
    "upgrade:major": "ncu --target latest --interactive --format group",
    "upgrade:filter": "ncu --filter"
  },
  "scripts-info": {
    "upgrade:check": "Check root package for updates (grouped by type)",
    "upgrade:check:all": "Check all workspace packages for updates",
    "upgrade": "Safe upgrade root: minor+patch, install, test",
    "upgrade:all": "Safe upgrade all workspaces: minor+patch, install, test",
    "upgrade:major": "Interactive major version upgrades",
    "upgrade:filter": "Filter upgrades by pattern, e.g.: pnpm upgrade:filter '@radix-ui/*'"
  }
}
```

**Useful ncu filter patterns**:

```bash
# Upgrade only Radix UI packages
ncu --filter "@radix-ui/*" --target minor -u

# Upgrade everything except React (held for compatibility)
ncu --reject "react,react-dom" --target minor -u

# Check only dev dependencies
ncu --dep dev --format group

# Upgrade with peer dependency handling
ncu --target minor -u && pnpm install --force
```

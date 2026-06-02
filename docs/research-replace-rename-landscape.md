# Search, Replace, and Rename: Tooling Landscape and Agent Gaps

Last updated: 2026-06-02.

This is a research note on the landscape of command-line search-and-replace and renaming
tools, on how AI coding agents apply edits today, and on where repren fits. It exists to
inform repren's positioning and roadmap. Popularity and maintenance figures are a
snapshot from mid-2026 and will drift; treat them as rough signal, not exact values.

## Scope and Method

The question was twofold: which tools compete with or complement repren for bulk
search-and-replace and renaming, and what ideas from agent-driven editing are worth
adopting. Findings were gathered from each tool's official repository, documentation, and
release history, plus published benchmarks and engineering write-ups from the agent
ecosystem. Sources are linked inline and collected at the end.

For context, repren is a single-file, zero-runtime-dependency Python CLI that does
multi-file search-and-replace and file and directory renaming in one pass. Its
distinctive features are simultaneous multi-pattern replacement including swaps
(`foo` to `bar` and `bar` to `foo` at once), case-variant-preserving rewrites
(camelCase, snake_case, PascalCase, UPPER_CASE together), full regex with capture groups,
combined content-and-path renames, atomic writes with automatic `.orig` backups, dry-run
and undo, and an installable coding-agent skill.

## Text Search-and-Replace CLIs

These tools edit file contents. The first group is already in repren's comparison table;
the second is the wider field.

| Tool | Edits | Standout | Case-preserving | Swaps / multi-pattern | Status |
| --- | --- | --- | --- | --- | --- |
| sed / awk / perl | Contents | Ubiquitous one-liners | No | No / No | Stable |
| sd | Contents | Simple, fast sed replacement | No | No / No | Active |
| fastmod | Contents | Interactive per-match prompts (default) | No | No / No | Active |
| ast-grep | Contents | AST structural search/replace | No | No / No | Very active |
| comby | Contents | Structural matching with holes | No | No / No | Active |
| ruplacer | Contents | `--preserve-case` (snake/Pascal/UPPER) | Yes (no kebab) | No / No | Archived, moved to Codeberg |
| scooter | Contents | Full TUI, per-match toggle, `$EDITOR`, batch `--no-tui` | No | No / No | Very active |
| sad | Contents | fzf diff-preview before commit | No | No / No | Active |
| repgrep (rgr) | Contents | ripgrep-powered TUI | No | No / No | Moderate |
| serpl | Contents | VS Code-style TUI, AST-grep mode, a preserve-case mode | Partial (depth undocumented) | No / No | Active, seeking maintainers |
| amber | Contents | Interactive confirm (y/n/a/q) | No | No / No | Active |
| ripgrep `--replace` | Neither | Prints replaced output only; never writes files | No | No / No | n/a by design |
| fnr | Contents (Windows) | GUI and CLI | No | No / No | Abandoned (2018) |

Notes:

- **ripgrep does not edit files.** `rg --replace` substitutes only in printed output; the
  maintainer has repeatedly declined in-place editing. It is a search engine, paired with
  a separate replacer.
- **Only ruplacer also does case-preserving replacement**, and it omits kebab-case, has no
  simultaneous swaps, no multi-pattern files, and no file renaming. It is archived and has
  moved to Codeberg.
- **None of these tools do simultaneous swaps or multi-pattern-from-file.** Several modern
  ones (scooter, sad, repgrep, serpl) compete on interactive terminal review rather than on
  transformation power.

## Batch Renamers

These tools rename files and directories. None of them edit file contents, which is the
line that separates them from repren.

| Tool | Regex + captures | Dry run | Undo | Cyclic a/b | Editor-based | Status |
| --- | --- | --- | --- | --- | --- | --- |
| f2 | Yes (`$1`) | Yes (default) | Yes | Auto-suffix only | No | Active |
| massren | Via `$EDITOR` | Yes | Yes | No | Yes | Active |
| brename | Yes (`${1}`) | Yes | Yes (last op) | No | No | Active |
| nomino | Yes (`{1}`) | Yes | No | No | No | Active |
| mmv | Wildcards (`#1`) | Yes | No | Yes | No | Active (niche) |
| rnr | Yes (`${1}`) | Yes (default) | Yes (dump file) | No | No | Active |
| Perl rename | Yes (full Perl) | Yes (`-n`) | No | No | No | Stable |
| util-linux rename | No (literal) | Yes (`-n`) | No | No | No | Active |
| vidir (moreutils) | Via `$EDITOR` | No | No | Via line swap | Yes | Stable |
| vimv | Via Vim | No | No | Yes | Yes | Semi-active |
| renameutils (qmv) | Via `$EDITOR` | No | No | No | Yes | Unmaintained |
| pyRenamer | Limited (GUI) | n/a | n/a | n/a | n/a | Abandoned |

The most capable modern renamers are **f2** (dry-run by default, undo, regex, EXIF and ID3
variables) and **massren** (editor-based, undo, cross-platform). repren overlaps these
when a rename is part of a content change, but a dedicated renamer is a reasonable choice
for filename-only work. The key point for the comparison is that repren does the
content-and-path rename together, which no pure renamer does.

## Structural and Semantic Refactoring

This category trades language-agnostic regex for parser-backed precision. It is the "more
correct, more setup" end of the spectrum.

| Tool | Matching model | Languages | Type-aware | Backer |
| --- | --- | --- | --- | --- |
| GritQL / grit | Tree-sitter AST | 12+ | No | Biome (donated by Grit/Honeycomb) |
| Semgrep autofix | AST plus metavariables | 30+ | Partial (commercial) | Semgrep Inc. |
| OpenRewrite | Lossless Semantic Tree | Java, Kotlin, Groovy, JS/TS | Yes (Java) | Moderne |
| jscodeshift | Babel AST plus recast | JS/TS | No | Meta |
| ts-morph | TypeScript compiler API | TS/JS | Yes | Community |
| retrie | GHC parser, equations as rewrites | Haskell | Partial | Meta (archived; fork active) |
| Coccinelle | Semantic Patch Language over CFG | C, some C++/Rust | No | INRIA |
| gofmt -r | Go AST expression rewrites | Go | No | Go team |
| IntelliJ SSR | PSI tree, IDE-only | JVM languages | Yes | JetBrains |

The most important general-purpose structural alternative to be aware of is **GritQL**: it
has the broadest practical language coverage of the AST tools through tree-sitter, a low
learning curve (any code snippet is a valid query), and an active home in Biome.
**Semgrep** has the largest user base, though autofix is secondary to its security
mission. **OpenRewrite** is the gold standard for type-aware Java migrations but needs
build context and is JVM-centric. These tools handle things regex cannot: scope-aware
rename, import management, and type-correct transforms. They cost a parser dependency,
per-language coverage, and setup, and most are single-language.

## How AI Agents Apply Edits Today

Understanding agent editing explains where a deterministic tool helps. The ecosystem has
converged on a few patterns and learned a few hard lessons.

**Edit formats vary widely in reliability, independent of the model.** Aider supports
whole-file, search/replace block ("diff"), diff-fenced, and unified-diff ("udiff")
formats. Its unified-diff format took GPT-4 Turbo from 20% to 61% on its laziness
benchmark and cut placeholder "lazy" edits roughly threefold. A later content-hash line
addressing scheme ("hashline") raised 15 models by 5 to 64 percentage points by changing
only the interface, not the model. The lesson: the mechanical edit format is a first-class
engineering problem.

**Exact string matching is both the safest and the most brittle approach.** Claude Code's
`str_replace` requires the search string to match exactly one location, which prevents
wrong-location edits but fails on the first attempt roughly 15 to 20 percent of the time
because of tab-versus-space conversion, CRLF differences, formatter drift, and ambiguous
duplicate matches. OpenAI's Codex `apply_patch` (the V4A format) uses context anchors
instead of line numbers and a three-tier fuzzy fallback, precisely because models
hallucinate line numbers and indentation.

**Line numbers are unreliable for model-generated edits.** Every successful format avoids
them: search/replace blocks, context-anchored hunks, and content hashes. Models hallucinate
line numbers, and counts shift after each edit.

**Separating planning from applying improves reliability.** Fast-apply services (Morph,
Relace) and Cursor's speculative apply take a compact edit sketch from a frontier model
and merge it into the file with a fast specialized model. Aider's architect-and-editor
split does the same with two roles. Vendor-reported numbers put Morph near 98% first-pass
merge accuracy at high throughput, with the planning model freed to describe intent rather
than format diffs.

**Symbol-level beats line-level.** Tools like Serena and LSP-based rename
(`textDocument/rename`) let agents edit named symbols with scope-correct, cross-file
results, at the cost of a running language server. Claude Code added native LSP support in
late 2025.

**Hybrid and orchestration patterns are emerging.** codemod.com 2.0 pairs deterministic
ast-grep detection with LLM rewriting. Sourcegraph Batch Changes separates the change
engine (any script or tool) from orchestration (which repos, PR creation, tracking). A
good change engine is tool-agnostic and composable.

## Agent Editing Tools and Services

- **Fast-apply models** (Morph, Relace) and **Cursor's apply model** solve the speed and
  accuracy of merging an edit sketch into a large file. They exist because full rewrites
  are slow and model-generated diffs are error-prone.
- **Serena** is an MCP server that exposes LSP symbol operations (find symbol, find
  references, rename, replace symbol body) to agents across 40-plus languages.
- **ast-grep's MCP server** exposes structural search and rule-based rewrite to agents
  through tree-sitter, with tools to dump syntax trees and test rules before applying.
- **Editing-oriented MCP servers** (Desktop Commander, text-editor servers, agent-LSP)
  provide diff-based edits, terminal control, and speculative in-memory edits.
- **Orchestration layers** (Sourcegraph Batch Changes, the codemod CLI) run a change
  across many repositories and manage the resulting pull requests.

## Where repren Fits

repren is the deterministic, zero-dependency, auditable apply-layer for changes that are
expressible as patterns. It is more reliable than a model free-typing edits when the change
is mechanical, and weaker when the change needs semantic understanding.

repren is **more reliable** than free-form LLM edits in specific ways:

- No hallucinated line numbers and no "lazy" placeholder output. The class of format
  failures above does not apply.
- Exact and regex matching is a feature when a human or agent specifies the pattern: the
  brittleness of `str_replace` comes from a model failing to reproduce a string, not from
  a user-specified pattern.
- Dry-run, automatic backups, and undo give verifiable, reversible operations.
- One transformation applies across many files atomically, avoiding the inconsistent
  intermediate state an agent can leave when it edits file by file and fails partway.
- No token or context limits: it processes arbitrarily large files and trees.

repren is **weaker** where semantics matter:

- It cannot act on intent like "add error handling to all database calls" or do a
  type-correct, cross-boundary rename. It matches only what a regex can express.
- It puts the pattern-authoring burden on the user or agent. For novel one-off refactors
  that follow no mechanical pattern, an LLM agent is the practical option.
- Its failure mode is silent non-application (a pattern that does not match), which is a
  different risk profile from an agent's misapplication, and calls for dry-run discipline.

The honest framing is that repren is **identifier-aware but not scope-aware**. Its
`--word-breaks` and `--preserve-case` modes capture much of the value of a symbol rename
across naming conventions without a parser, but it does not resolve scope, imports, or
types. It complements AST and LSP tools rather than competing with them.

## Strategic Insights: Where Agents Need Better Tools

The research points to concrete gaps in the agent editing stack that a deterministic tool
is well placed to fill.

1. **Reliable mechanical application is underserved.** Agents routinely spend tokens and
   retries hand-typing bulk edits that are really a single find-and-replace. A safe,
   scriptable, pattern-based tool removes that whole failure class. The opportunity for
   repren is to be the obvious choice an agent reaches for on any multi-file, mechanical
   change, which is what the installable skill is for.
2. **Reviewability is inconsistent at the tool layer.** Agents apply edits speculatively
   and lean on git or retries to recover. Tools that present changes as a diff and support
   undo make agent verification loops cheap. repren has dry-run and JSON output but not a
   true unified-diff output, which is the clearest gap to close.
3. **Multi-file atomicity and reproducibility are rare.** LLM edits are neither atomic
   across files nor reproducible run to run. Deterministic transforms that either fully
   apply or cleanly back out are valuable for CI and for agent self-checking.
4. **Language-agnostic, identifier-aware rename has no clean home.** AST and LSP renames
   are precise but heavy and per-language; raw regex is too blunt and error-prone on
   identifiers. A case-aware, word-boundary-aware, cross-file rename that also fixes the
   matching file names sits in a real gap, and it is exactly repren's niche.
5. **Composability between detection and application is undervalued.** The strongest
   emerging pattern is deterministic detection (ast-grep) plus targeted rewrite. Clean,
   machine-readable interfaces let tools compose inside agent loops and orchestration
   layers. repren benefits from leaning into this rather than trying to add a parser.

### Candidate Directions for repren

These follow from the gaps above and stay within repren's zero-dependency, deterministic
character. They are options to weigh, not commitments.

- **Add a unified-diff output mode.** Let repren print standard diffs for agent review and
  for piping to `git apply --check`. This is the highest-value, lowest-cost item, and it
  matches what every agent-friendly tool offers.
- **Name and document the identifier-aware niche.** `--word-breaks` and `--preserve-case`
  already deliver the cheap majority of a symbol rename. Make this an explicit, documented
  position rather than an incidental feature.
- **Document and support pairing with ast-grep.** ast-grep finds structural matches,
  repren applies the text replacement. Accepting match locations to scope replacements
  would make the hybrid pattern first-class.
- **Tighten agent-loop input and output.** Accept patterns on stdin or as JSON, and enrich
  `--format=json` with per-replacement before-and-after text and counts so an agent can
  verify and iterate.
- **Extend renames to references (ambitious).** When `--full` renames a file, optionally
  fix import or include paths that reference that file name, which is much of what
  module-aware codemods do, without a parser.

## Bottom Line

No surveyed tool replicates repren's combination of case-preserving replacement,
simultaneous swaps, multi-pattern files, combined content-and-path renames, and built-in
safety, at zero dependencies. The competitive field is best read as complementary: pure
renamers do half the job, modern interactive replacers compete on review rather than
transformation power, and structural tools trade setup and language coverage for semantic
precision. The agent ecosystem's main lesson is that deterministic, reviewable application
of mechanical changes is both valuable and underbuilt, which is the niche repren should own
and where a unified-diff mode and explicit positioning would help most.

## Sources

Text search-and-replace CLIs:
[ruplacer](https://github.com/your-tools/ruplacer),
[scooter](https://github.com/thomasschafer/scooter),
[sad](https://github.com/ms-jpq/sad),
[repgrep](https://github.com/acheronfail/repgrep),
[serpl](https://github.com/yassinebridi/serpl),
[amber](https://github.com/dalance/amber),
[ripgrep issue #147 (no in-place edit)](https://github.com/BurntSushi/ripgrep/issues/147),
[sd](https://github.com/chmln/sd),
[fastmod](https://github.com/facebookincubator/fastmod),
[ast-grep](https://ast-grep.github.io/),
[comby](https://comby.dev/).

Batch renamers:
[f2](https://github.com/ayoisaiah/f2),
[massren](https://github.com/laurent22/massren),
[brename](https://github.com/shenwei356/brename),
[nomino](https://github.com/yaa110/nomino),
[mmv](https://github.com/rrthomas/mmv),
[rnr](https://github.com/ismaelgv/rnr),
[Perl File::Rename](https://metacpan.org/dist/File-Rename),
[renameutils](https://www.nongnu.org/renameutils/),
[vidir (moreutils)](https://manpages.debian.org/testing/moreutils/vidir.1.en.html),
[vimv](https://github.com/thameera/vimv).

Structural and semantic refactoring:
[GritQL (Biome)](https://github.com/biomejs/gritql),
[Grit language docs](https://docs.grit.io/language/overview),
[Semgrep autofix](https://semgrep.dev/docs/writing-rules/autofix),
[OpenRewrite](https://docs.openrewrite.org/),
[jscodeshift](https://github.com/facebook/jscodeshift),
[ts-morph](https://ts-morph.com/),
[retrie](https://engineering.fb.com/2020/07/06/open-source/retrie/),
[Coccinelle](https://coccinelle.gitlabpages.inria.fr/website/),
[gofmt -r](https://pkg.go.dev/cmd/gofmt),
[IntelliJ SSR](https://www.jetbrains.com/help/idea/structural-search-and-replace.html),
[Sourcegraph Batch Changes](https://sourcegraph.com/batch-changes).

Agent edit formats and reliability:
[Aider edit formats](https://aider.chat/docs/more/edit-formats.html),
[Aider unified diffs](https://aider.chat/docs/unified-diffs.html),
[Aider code editing leaderboard](https://aider.chat/docs/leaderboards/edit.html),
[Aider architect/editor](https://aider.chat/2024/09/26/architect.html),
[Anthropic text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool),
[Claude Code hashline proposal (#25775)](https://github.com/anthropics/claude-code/issues/25775),
[OpenAI apply_patch](https://developers.openai.com/api/docs/guides/tools-apply-patch),
[The Harness Problem](https://blog.can.ac/2026/02/12/the-harness-problem/).

Agent editing tools and services:
[Morph fast apply](https://www.morphllm.com/fast-apply-model),
[Relace](https://relace.ai/),
[Cursor instant apply](https://cursor.com/blog/instant-apply),
[Serena](https://github.com/oraios/serena),
[ast-grep MCP](https://github.com/ast-grep/ast-grep-mcp),
[codemod 2.0](https://codemod.com/blog/codemod2),
[LSP specification](https://microsoft.github.io/language-server-protocol/).

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose before editing. -->

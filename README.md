# myelinate

[![CI](https://github.com/AnubhavLakra10/myelinate/actions/workflows/ci.yml/badge.svg)](https://github.com/AnubhavLakra10/myelinate/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/myelinate)](https://pypi.org/project/myelinate/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Knowledge graphs show you what's in your files. myelinate shows you what's in your head.**

Drop in code, papers, markdown, screenshots, diagrams, whiteboard photos — myelinate extracts concepts and relationships into a knowledge graph, finds what you know and what you're missing, then quizzes you on the connections until they stick. Spaced repetition powered by [FSRS](https://github.com/open-spaced-repetition/fsrs4anki), the same algorithm behind modern Anki.

> Andrej Karpathy keeps a `/raw` folder where he drops papers, tweets, screenshots, and notes. Other tools turn that into a graph you look at once. myelinate turns it into a graph that **teaches you** — it tracks what you've reviewed, schedules what you're about to forget, and tells you which connections you haven't explored yet.

```
myelinate ingest .                  # any folder — code, papers, notes, images
myelinate graph                     # build + visualize the knowledge graph
myelinate gaps                      # what's missing from your understanding?
myelinate quiz                      # spaced repetition from graph edges
myelinate path "attention" "RLHF"   # trace connections between concepts
```

```
myelinate-out/
├── graph.html         interactive graph — click nodes, search, filter by community
├── REPORT.md          god nodes, gaps, surprising connections, suggested questions
├── graph.json         persistent graph — query weeks later without re-reading
├── learn.db           spaced repetition state — what you know, what's due, what you forgot
└── cache/             SHA256 cache — re-runs only process changed files
```

## Why this exists

Knowledge graph tools build a map. Then you close the tab and forget everything.

myelinate builds the map **and walks you through it**. Every edge in the graph becomes a potential flashcard. The spaced repetition engine schedules reviews based on how well you actually recall each connection — not how recently you read about it. Over time, the graph isn't just a visualization of your files. It's a model of **your understanding**.

## Install

**Requires:** Python 3.10+

```bash
pip install myelinate
```

## How it works

myelinate runs in three stages:

**1. Extract** — A deterministic AST pass via tree-sitter extracts structure from code (classes, functions, imports, call graphs) with no LLM. Claude processes docs, papers, and images in parallel to extract concepts, relationships, and design rationale.

**2. Build** — Results merge into a NetworkX graph. Leiden community detection (via graspologic) clusters related concepts. Analysis identifies god nodes, cross-community bridges, and structural gaps.

**3. Learn** — Graph edges become review cards. FSRS schedules reviews based on your actual recall performance. Gap detection compares what's in the graph against what you've reviewed, surfacing blind spots you didn't know you had.

Every relationship is tagged `EXTRACTED` (found directly in source), `INFERRED` (reasonable deduction), or `AMBIGUOUS` (flagged for review). You always know what was found vs guessed.

## What makes this different

| Other knowledge graph tools | myelinate |
|---|---|
| Build a graph, stop | Build a graph, then **teach you the graph** |
| Static visualization you look at once | Living system that tracks your retention |
| File-centric — one node per file | Concept-centric — same idea from a tweet, paper, and code merged into one node |
| "Here's what's connected" | "Here's what's connected **and you haven't learned this part yet**" |
| Report output | Gap detection — compares graph structure against your review history |
| No memory between sessions | Persistent learning state in SQLite |

## Commands

```bash
# Ingest
myelinate ingest <path|url>         # add files, URLs, screenshots to corpus
myelinate ingest . --update         # re-extract only changed files, merge into graph

# Graph
myelinate graph                     # build/rebuild knowledge graph
myelinate graph --watch             # auto-rebuild on file changes
myelinate graph --directed          # build directed graph (preserves edge direction)

# Learn
myelinate quiz                      # spaced repetition session (due cards first)
myelinate quiz --topic "attention"  # quiz on specific subgraph
myelinate quiz --count 20           # number of cards per session
myelinate gaps                      # find knowledge gaps
myelinate stats                     # learning progress dashboard

# Navigate
myelinate path <A> <B>             # shortest path between two concepts
myelinate explain <concept>         # explain at your current understanding level

# Export
myelinate export --obsidian         # export to Obsidian vault
myelinate export --wiki             # generate wiki articles per community
myelinate export --svg              # export graph.svg
myelinate export --neo4j            # generate Cypher for Neo4j
```

## File support

| Type | Extensions | Extraction |
|------|-----------|------------|
| Code | `.py .ts .js .go .rs .java .c .cpp .rb .cs .kt .scala .php` | AST via tree-sitter + call-graph pass |
| Docs | `.md .txt .rst` | Concepts + relationships via Claude |
| Papers | `.pdf` | Citation mining + concept extraction |
| Images | `.png .jpg .webp .gif` | Claude vision — screenshots, diagrams, any language |

## What you get

**God nodes** — highest-degree concepts. What everything connects through.

**Knowledge gaps** — concepts adjacent to things you know well but that you've never reviewed. "You understand attention mechanisms, but you haven't explored positional encoding which connects to 4 concepts you've mastered."

**Surprising connections** — ranked by composite score. Cross-community and cross-filetype edges rank higher. Each result includes a plain-English why.

**Spaced repetition** — every graph edge is a potential flashcard. FSRS schedules reviews based on your actual recall — not just "show it again tomorrow." Cards you struggle with appear more often. Cards you nail get pushed out further.

**Review history** — persistent SQLite database tracks every review. Your learning state survives across sessions, machines (just copy `learn.db`), and graph rebuilds.

**Suggested questions** — 4-5 questions the graph is uniquely positioned to answer, generated from topology, not keywords.

## The quiz loop

```
$ myelinate quiz

  Card 1/10
  ─────────
  What connects "Attention" to "Gradient Flow"?

  > The attention mechanism's softmax output creates gradient paths
    that bypass deep layer chains, allowing gradients to flow
    directly to earlier layers.

  Rate your recall:
  [1] Again  [2] Hard  [3] Good  [4] Easy

  > 3

  ✓ Next review in 2.5 days

  Card 2/10
  ─────────
  ...
```

## Privacy

Code files are processed **locally** via tree-sitter AST — no file contents leave your machine for code. Docs, papers, and images are sent to Claude's API for semantic extraction (using your own API key). No telemetry, no analytics, no tracking. The only network calls are to the model API during extraction.

## Tech stack

NetworkX + Leiden (graspologic) + tree-sitter + Claude + FSRS + SQLite + vis.js. No server, no database server, runs entirely locally.

## Project status

**Alpha.** The scaffolding is complete — pipeline architecture, CLI, data models, spaced repetition engine, graph construction, analysis, and export all have working code with tests (86% coverage). Extraction is the next implementation target: tree-sitter AST for code, Claude API calls for docs/images. Benchmarks will come from real corpus runs.

## Contributing

**Worked examples** are the most trust-building contribution. Run `myelinate ingest` on a real corpus, save the output, write an honest review of what the graph got right and wrong, and submit a PR.

**Extraction bugs** — open an issue with the input file, the cache entry, and what was missed or invented.

## License

[MIT](LICENSE)

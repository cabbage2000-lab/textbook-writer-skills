# textbook-writer-skills

[中文](README.md) | **English**

[![CI](https://github.com/cabbage2000-lab/textbook-writer-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/cabbage2000-lab/textbook-writer-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](CHANGELOG.md)

A Claude Code skill suite for writing textbooks, aimed at STEM subjects where worked examples can be verified — mathematics, physics, computer science. It packs established instructional-design method into an AI workflow: first pin down what students should walk away with, then work backwards to chapters and exercises, then write chapter by chapter into a coherent textbook with a through-line, a cognitive gradient, and worked examples whose answers you can trust. Interrupt it anytime and pick up where you left off.

> **Output language: Chinese.** These skills produce Chinese-language textbooks. The section headings are hard-coded Chinese strings that the template forbids renaming (`## N.1 概念讲解`, `## N.2 示范例题`, …), the Bloom verb tables are Chinese, and the prose style guide encodes Chinese typography rules. The instructional-design machinery — UbD, Bloom, scaffolding, verified computation — is language-independent, but adapting the output to English would mean a fork of the `references/` layer, not a config flag.

## The problems it solves

Telling an AI "write me a textbook" usually goes wrong in three specific ways. Every design decision here targets one of them.

### Pitfall 1: you get a pile of topics, not a textbook

An AI will happily list concepts chapter after chapter, like encyclopedia entries in a binder: no through-line across the book, exercises that don't line up with what students should learn, nothing to walk away with at the end.

**The fix — design first, write second.** Borrowing the established method *Understanding by Design* (UbD, backward design): before a word of prose gets written, the author has to answer "what should students walk away with?" The answer takes the form of five elements — Big Ideas, Enduring Understandings, Essential Questions, Transfer Goals, Learning Objectives. Only after the author confirms them does the skill work backwards to a chapter tree and a per-chapter exercise plan. Chapters that don't serve the through-line get cut or reworked.

Below: stages 1–3 for *Introduction to Linear Algebra* — scoping, the five UbD elements (Big Ideas), the chapter tree, with both gate stops clearly visible.

![Textbook design sample: scoping, the Big Ideas table of the five UbD elements, and the chapter tree, with the primary and secondary GATE stops marked](images/outline-preview.png)

**Gradient and rhythm come with it.** Every exercise is tagged with a cognitive level (the six Bloom levels: remember → understand → apply → analyze → evaluate → create), and the whole book gets an automatic gradient check — exercises piling up in a single level (≥60%) or a missing apply/analyze band raises a warning. Each chapter follows a fixed four-part rhythm (concept exposition → worked examples → guided practice → independent exercises), so you never end up with one chapter that's all theory and another that's all drills.

The 58-exercise gradient report for that same book — distribution table, bar chart, three automatic check rules:

![Whole-book Bloom gradient report: per-chapter distribution across remember/understand/apply/analyze/evaluate/create, a bar chart of the book-wide gradient, and three automatic check rules all passing](images/gradient-report.png)

### Pitfall 2: worked examples that look right and fall apart when you do the math

Fabricated answers are the most damaging failure mode for AI-written STEM material. A reader follows along, discovers the book is wrong, and the whole thing loses its credibility.

**The fix — every answer actually gets computed.** Answers to computational examples and exercises must be recomputed and cross-checked before they ship, with the recomputation attached to the exercise. Anything genuinely unverifiable (open-ended discussion, numerical experiments) is explicitly tagged `⚠️ 需作者确认` ("author must confirm") — never dressed up as verified.

Below: an excerpt from chapter 4 of *Introduction to Linear Algebra*, produced end-to-end by `textbook` — the four-part rhythm and the per-exercise verification tags are both visible.

![Finished textbook page: concept exposition, worked examples, guided practice, and independent exercises in four-part structure, each exercise carrying a verification tag](images/chapter-preview.png)

### Pitfall 3: it falls apart once there are many chapters

Cram a 10+ chapter textbook into one conversation and the context will blow up: by chapter 8 it has forgotten chapter 2's notation, terminology drifts, and a dropped connection means starting over.

**The fix — write each chapter in isolation, persist progress to disk.** Writing a chapter takes only a lightweight input: that chapter's outline slice, the book-wide instructional design (the five UbD elements), the glossary, and the previous chapter's summary. It never reads another chapter's prose, so the context stays flat no matter how many chapters there are. Progress is written to `.progress.json` as it goes; interrupt at any point and one sentence resumes from the break, with finished chapters left untouched.

## Design principles

- **It competes on instructional design, not long-form generation.** The hard part of writing a textbook isn't the writing, it's the teaching design. Existing tools solve "organize source material into a long document"; this suite solves "how do you actually teach this subject."
- **The author makes the calls that matter.** Scoping, the five UbD elements, and the chapter tree are the soul of a textbook. The skill drafts them, then stops at two gates and waits for explicit author confirmation. No "workflow optimization" may bypass them — the job is to force you to think it through, not to decide for you.
- **Honesty over fluency.** A conclusion that can't be verified gets labeled "author must confirm" rather than shipped as a confident-looking fabrication.
- **A pipeline instead of one long breath.** Four skills each own one segment, handing off via written contracts and never reading each other's intermediate work — that's the engineering guarantee that a long textbook actually gets finished with even quality per chapter.

## When to use it

Built for people who know their subject and want to turn that knowledge into systematic teaching material: developers writing technical handbooks, teachers and students turning lecture notes into a textbook, creators producing instructional content. The skill supplies structure and discipline; subject-matter judgment stays with you.

| What you want | What to tell Claude Code |
| ------------- | ------------------------ |
| Write a full textbook from scratch | `用 textbook 写一本《线性代数入门》教材` |
| Just the instructional design and outline | `用 textbook-outline 设计一份数据结构教材大纲` |
| Write one chapter from an existing outline (also works for a deep-dive technical article with full worked examples) | `用 textbook-chapter 按大纲写第三章` |
| Just a few exercises with verified answers | `用 textbook-exercises 出几道矩阵乘法的练习题` |
| Plan the working directory before you start (optional; git version control + multi-textbook workspace) | `用 textbook-init 初始化教材工作目录` |

English trigger phrases also work — each skill's `description` carries both Chinese and English trigger terms — but the Chinese prompts above are the ones exercised by the behavioral test suite, and the output is Chinese either way.

Explicitly out of scope for v1: humanities essay and case-analysis questions (deferred to v2), turning existing source material into a course, online course platform and LMS integration, and automatic figure generation.

## Quick start

Pick one of three installation routes:

**Route 1 — install as a plugin** (recommended; tracks repository updates). In Claude Code:

```text
/plugin marketplace add cabbage2000-lab/textbook-writer-skills   # a local repo path also works
/plugin install textbook-writer@textbook-writer-skills
```

**Route 2 — copy into your personal skills directory** (applies to every project):

```bash
cp -r skills/* ~/.claude/skills/
```

**Route 3 — develop or try it out inside this repository.** Run once after cloning to symlink `skills/` as the project-level skills directory (`.claude/` is gitignored):

```bash
mkdir -p .claude && ln -s ../skills .claude/skills
```

**Using it in Codex** — no extra installation: open this repository directory in the Codex CLI and [AGENTS.md](AGENTS.md) at the repo root will route Codex to the right skill. For example:

```text
写一本《线性代数入门》教材
```

### What happens on the first run

Open a fresh Claude Code session and type:

```text
用 textbook 写一本《线性代数入门》教材
```

1. The skill creates the textbook project directory and the progress file `.progress.json`;
2. One round of questions settles the scoping: who it's for, how deep, how long;
3. It produces the five UbD elements and stops at `⏸ 等待确认` ("awaiting confirmation") — the first gate, where you can confirm or ask for changes;
4. Once confirmed, it produces the chapter tree and the book-wide Bloom gradient report — the second gate;
5. Then it writes chapter by chapter, each landing as its own `.md` file, and finally does a full review pass and produces a student-facing performance task with its rubric.

Interrupt at any point; typing the same sentence again resumes from the break.

## How it works

One orchestrator skill drives three sub-skills through a five-stage pipeline, plus one standalone helper skill for planning the working directory before you start. The five skills are a single unit — they reference each other by relative path — and must be installed together:

```text
textbook (orchestrator)
  ├─ Owns: driving the five stages, maintaining .progress.json, passing handoff contracts between stages
  │
  ├─ textbook-outline (sub-skill 1: outline design)
  │    └─ Stages 1-3: scoping → five UbD elements (primary gate) → chapter tree + gradient report (secondary gate)
  │
  ├─ textbook-chapter (sub-skill 2: single-chapter writing)
  │    └─ Stage 4: chapter by chapter in the four-part structure
  │        (concept exposition → worked examples → guided practice → independent exercises)
  │
  └─ textbook-exercises (sub-skill 3: exercise generation)
       └─ Called by chapter writing: generates three exercise types and verifies them by real computation

textbook-init (standalone helper: working-directory setup)
  └─ Outside the pipeline: plans and creates a single-book directory or a multi-textbook workspace
     (optional git and a README working guide), then hands off to textbook
```

Handoff contracts between stages, the on-disk layout of a textbook project, the `.progress.json` state machine and its re-entry rules are all defined in [handoff-contract.md](skills/textbook/references/handoff-contract.md) — the single authoritative source for the whole project.

Repository layout:

```text
skills/               # the 5 skills; each references/ holds its knowledge base
                      # (UbD guide, Bloom verb tables, chapter template, exercise verification rules,
                      #  performance-task rubrics, workspace layout)
.claude-plugin/       # plugin and marketplace manifests, for /plugin installation
evals/                # behavioral test cases: prompt + objective assertions
                      # (case definitions are versioned; run artifacts are not)
scripts/ + tests/     # structural validation script and its unit tests
```

## Quality assurance

Three layers of defense; the first two run automatically in CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)):

```bash
python3 scripts/validate_skills.py       # 1. structural validation: skill content + manifest consistency + repo health
python3 -m unittest discover -s tests    # 2. unit tests: the validation logic itself
# 3. behavioral tests: really run the 6 cases in evals/evals.json;
#    after changing a skill, re-run per the mapping table in CONTRIBUTING.md
```

Layer 3 cannot be automated — the cases have to be run for real in a fresh Claude Code session and judged against their assertions one by one. That is deliberate: these skills are programs written for a model, so a one-line instruction change can change runtime behavior in ways no structural check would catch.

Maintenance and contribution workflow (blast radius, definition of done, releases) is in [CONTRIBUTING.md](CONTRIBUTING.md); version history is in [CHANGELOG.md](CHANGELOG.md).

## Milestone status

| Milestone | Scope | Eval case | Status |
| --------- | ----- | --------- | ------ |
| M1 | Skeleton: 4 skills + 6 references + validation | — | ✅ Done (including 3 behavioral smoke tests) |
| M2 | Outline skill clears both gates on a real subject | [eval 1](evals/evals.json) | ✅ Passed (5/5 assertions, 2026-07-14; verdict in evals/workspace/2026-07-14-eval-1/outputs/judgment.md) |
| M3 | Chapter + exercise skills working | [eval 2, 3](evals/evals.json) | ✅ Passed (5/5 assertions each, 2026-07-14; verdicts in evals/workspace/2026-07-14-eval-2/rerun/outputs/judgment.md and 2026-07-14-eval-3/outputs/judgment.md) |
| M4 | Orchestrator interrupt-and-resume (state machine locates the resume point) | [eval 4](evals/evals.json) | ✅ Passed (3/3 assertions, 2026-07-16, first run under the narrowed definition; verdict in evals/workspace/2026-07-16-eval-4/outputs/judgment.md; the 2026-07-14 record predates the narrowing and is reference only) |
| M5 | Second subject written end to end (including stage 5 self-check and delivery summary), proving it isn't overfitted | [eval 5](evals/evals.json) | ⏳ Pending |
| M6 | Working-directory setup skill (textbook-init): plan and create single-book / multi-textbook directories | [eval 6](evals/evals.json) | ⏳ Pending |

## License

[MIT](LICENSE)

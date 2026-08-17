# Textbook-Writer-Skills

[![CI](https://github.com/cabbage2000-lab/textbook-writer-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/cabbage2000-lab/textbook-writer-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.5.0-blue.svg)](CHANGELOG.md)
![host](https://img.shields.io/badge/host-Claude%20Code%20%7C%20Codex%20%7C%20WorkBuddy-grey)
![subject profiles](https://img.shields.io/badge/subject%20profiles-stem%20%7C%20humanities%20%7C%20economics-grey)

[中文](README.md) | **English**

Textbook-Writer-Skills is a skill suite for writing textbooks — for coding agents (Claude Code, Codex, WorkBuddy). It packs established instructional-design method into an AI workflow: first pin down what students should walk away with, then work backwards to chapters and exercises, then write chapter by chapter into a coherent textbook with a through-line, a cognitive gradient, and answers you can trust. Interrupt it anytime and pick up where you left off. Currently **v0.5.0**: 5 skills (1 orchestrator + 3 pipeline sub-skills + 1 standalone helper) covering all five stages, from planning the working directory to the final review pass — for STEM, the humanities, and economics alike.

**One core, many subject families.** Subject differences don't spread through the workflow; they're pinned into pluggable **subject profiles**, and only four things vary by subject: the question-type set, the verification method, the cognitive verbs, and what each in-chapter section is for. Three ship with the suite: `stem` targets subjects whose answers can be recomputed — mathematics, physics, computer science (full eval regression passed); `humanities` targets subjects whose answers rest on argument — history, philosophy, literature, political science, sociology, art history — swapping "recompute the answer" for "check the source" (both paths, outline and chapter, verified by real eval runs 7 and 8); `economics` targets **mixed** subjects — economics and finance, where model questions can be recomputed, statistics can only be checked against their source, and policy questions get argument points instead of either, all three interleaved in one book (evals 9 and 10 pending). All three share one verification discipline; only the method of checking changes. Supporting a new family takes one new profile file plus one line in the index — no core changes.

The authoritative definition of the stage handoff contracts, the on-disk layout and the state machine is [handoff-contract.md](skills/textbook/references/handoff-contract.md); everything that varies by subject is pinned in [subject-profile-spec.md](skills/textbook/references/subject-profile-spec.md).

> **Output language: Chinese.** These skills produce Chinese-language textbooks. The section headings are hard-coded Chinese strings that the template forbids renaming (`## N.1 概念讲解`, `## N.2 示范例题`, …), the Bloom verb tables are Chinese, and the prose style guide encodes Chinese typography rules. The instructional-design machinery — UbD, Bloom, scaffolding, verified computation — is language-independent, but adapting the output to English would mean a fork of the `references/` layer, not a config flag.

## Design principles

**It competes on instructional design, not long-form generation.** The hard part of writing a textbook isn't the writing, it's the teaching design. Existing tools solve "organize source material into a long document"; this suite solves "how do you actually teach this subject."

- **The author makes the calls that matter.** Scoping, the five UbD elements, and the chapter tree are the soul of a textbook. The skill drafts them, then stops at two gates and waits for explicit author confirmation. No "workflow optimization" may bypass them — the job is to force you to think it through, not to decide for you.
- **Honesty over fluency.** A conclusion that can't be verified gets labeled "author must confirm" rather than shipped as a confident-looking fabrication.
- **A pipeline instead of one long breath.** Four skills each own one segment, handing off via written contracts and never reading each other's intermediate work — that's the engineering guarantee that a long textbook actually gets finished with even quality per chapter.

**The non-negotiables**: every answer must be checked by the method its subject profile defines before it ships (recomputation for STEM, source and citation checking for the humanities), and anything unverifiable is tagged `⚠️ 需作者确认` ("author must confirm"); the two gates at stages 2 and 3 only open on explicit author confirmation. Neither is traded off against any other goal — **the subject may change, the discipline does not**: a profile defines *how* something is verified, never *whether* it needs to be.

## ✅ What it does / ⛔ What it doesn't

| ✅ What this suite does | ⛔ What this suite doesn't do |
| --- | --- |
| Settle the scoping in one round of questions, then produce the five UbD elements | Decide the scoping or which chapters make the cut for you (both gates stop and wait) |
| Work backwards to a chapter tree and run a book-wide Bloom gradient check | Take a side for you where the scholarship genuinely disagrees (it lays out the main positions and asks you) |
| Write chapters in the four-part structure and keep the glossary consistent | Turn your existing lecture material into a course |
| Generate three kinds of exercises, each answer checked by its profile's method (recomputation for STEM, source and citation checks for the humanities) | Ship an answer it couldn't verify while pretending it did; invent a citation, source, or date from memory |
| Persist progress to `.progress.json` and resume from the break | Online course platform and LMS integration |
| Plan and create the working directory before you start (git optional) | Generate figures automatically |

"It won't decide for you" isn't a shortcoming, it's the premise of the pipeline: scoping, the five UbD elements and the chapter tree make or break a textbook, so the AI drafts and the judgment stays with the person who knows the subject.

> The full wording of all five red lines is in [CONTRIBUTING.md](CONTRIBUTING.md) under 「红线约束」; the authoritative contract layer is [handoff-contract.md](skills/textbook/references/handoff-contract.md).

## Which subjects it can write

Subject coverage is defined by three pluggable subject profiles. Stage 1 decides the profile from your subject and prints it once (e.g. `学科档案：humanities`), then passes it through unchanged chapter by chapter — you never pick a profile yourself, and if it decided wrong, say so at stage 1. The authoritative index and routing rules are in [subject-profile-spec.md](skills/textbook/references/subject-profile-spec.md), section 5.

| Profile | Subjects covered | Verification method | Field-tested status |
| --- | --- | --- | --- |
| `stem` | All branches of mathematics, physics, chemistry, engineering, computer science and algorithms | Recomputation: every answer recomputed along a path different from the solution's, results compared | ✅ Full eval regression passed (evals 1–6) |
| `humanities` | History, philosophy, literature, political science, sociology, art history, religious studies | Source checking: quotations checked word-for-word against the original with edition and location recorded — never a citation written from memory | ✅ Both paths, outline and chapter, verified by real runs (evals 7, 8) |
| `economics` | All branches of economics (micro, macro, econometrics, international, development, industrial organization) and finance | Mixed: model questions recomputed + statistics checked against authoritative sources + policy questions given argument points and a rubric | ⏳ Evals 9, 10 pending (profile and cases are in the repo) |

Routing always starts from the same question: **can this subject's typical exercise be re-solved along a path independent of the solution's, and the results compared?** Mostly yes → `stem`. Mostly no (the answer rests on argument and perspective) → `humanities`. Half and half (models recompute, statistics can only be checked against their source) → `economics`.

**Subjects that straddle the line** have their routing written into each profile's section 1:

- **Language learning, law, accounting**: grammar rules, statutes, precedents and standards are deterministic, checkable facts — material dominated by rule-application exercises routes to `stem` (with "recompute" read as "look up the provision and compare"), material dominated by case argument and legal reasoning routes to `humanities`;
- **Psychology, geography**: computational and empirical-data exercises route to `stem`, theory essays and policy discussion follow the `humanities` essay handling; textbooks shaped like economics (empirical data + statistical inference) can also borrow `economics` — it spells out the known differences to you before writing;
- **Within economics**: mostly pure derivation (mathematical economics, financial engineering) → `stem`; mostly argument and texts (history of economic thought, comparative economic systems, political economy) → `humanities`; both kinds interleaved in one book (most principles, intermediate micro/macro and introductory econometrics textbooks) → `economics`;
- **Cross-cutting topics** (history of science, digital humanities): whichever kind of exercise dominates picks the profile; the other kind follows the other profile's corresponding question type, with the split recorded in the design document.

**Subjects beyond this list can still be written — just never by silently forcing a fit**: when stage 1 finds no matching profile, it tells you "no dedicated profile for this subject; proceeding under the closest one" and lists the known gaps (which question types have no defined verification method, whether the chapter structure needs adjusting), and you decide whether to continue or narrow the scope. The profile fixes the whole book's verification discipline and chapter structure — whether that approximation is acceptable is a call only someone who knows the subject can make.

## The three pitfalls it solves

Telling an AI "write me a textbook" usually goes wrong in three specific ways. Every design decision here targets one of them.

### Pitfall 1: you get a pile of topics, not a textbook

An AI will happily list concepts chapter after chapter, like encyclopedia entries in a binder: no through-line across the book, exercises that don't line up with what students should learn, nothing to walk away with at the end.

**The fix — design first, write second.** Borrowing the established method *Understanding by Design* (UbD, backward design): before a word of prose gets written, the author has to answer "what should students walk away with?" The answer takes the form of five elements — Big Ideas, Enduring Understandings, Essential Questions, Transfer Goals, Learning Objectives. Only after the author confirms them does the skill work backwards to a chapter tree and a per-chapter exercise plan; chapters that don't serve the through-line get cut or reworked. Gradient discipline comes with it: every exercise is tagged with a cognitive level (the six Bloom levels: remember → understand → apply → analyze → evaluate → create) and the whole book gets an automatic gradient check — exercises piling up in a single level (≥60%) or a missing apply/analyze band raises a warning. Each chapter follows a fixed four-part rhythm (concept exposition → worked examples → guided practice → independent exercises), so you never end up with one chapter that's all theory and another that's all drills.

**None of this counts as delivered until the reader can see it.** Learning objectives no longer live only in the design document: each chapter opens with a student-facing "after this chapter, you should be able to…" and closes with a self-check list that walks those same objectives one by one, pointing back to the section to reread and the exercise to try. At sign-off the pipeline also writes `00-前言.md` (who the book is for, how to use it, a linked table of contents) and a symbol-conventions section in the glossary — so a reader opening the directory knows where to start and where to look up an unfamiliar notation.

Below: stages 1–3 for *Introduction to Linear Algebra* — scoping, the five UbD elements (Big Ideas), the chapter tree, with both gate stops clearly visible.

![Textbook design sample: scoping, the Big Ideas table of the five UbD elements, and the chapter tree, with the primary and secondary GATE stops marked](images/outline-preview.png)

The 58-exercise gradient report for that same book — distribution table, bar chart, three automatic check rules:

![Whole-book Bloom gradient report: per-chapter distribution across remember/understand/apply/analyze/evaluate/create, a bar chart of the book-wide gradient, and three automatic check rules all passing](images/gradient-report.png)

### Pitfall 2: worked examples that look right and fall apart when you do the math

Fabrication is the most damaging failure mode for AI-written teaching material. In STEM it looks like a wrong computation — a reader follows along and finds the book is wrong. In the humanities it looks like **invented citations and misplaced facts**: fabricated references, quotations attributed to the wrong person, garbled dates. Both destroy the same thing: the credibility of the whole book.

**The fix — every answer gets checked, by the method its subject profile defines.** Under the `stem` profile, answers are recomputed along a path different from the solution's, with the recomputation attached to the exercise. Under the `humanities` profile, quotations are checked word-for-word against the original with edition and location recorded, factual claims are checked against author-supplied material or established scholarship, and essay questions get argument points plus a rubric instead of a fake answer key. Under the `economics` profile both methods are in play — model questions get recomputed, statistics get checked against an authoritative source with the issuing body, basis and year recorded, and the two kinds of verification record sit side by side in the same chapter. All three share one discipline: anything genuinely unverifiable is explicitly tagged `⚠️ 需作者确认` ("author must confirm") — never dressed up as verified, and **never a citation or a statistic written from memory**.

Below: an excerpt from chapter 4 of *Introduction to Linear Algebra*, produced end-to-end by `textbook` — the four-part rhythm and the per-exercise verification tags are both visible.

![Finished textbook page: concept exposition, worked examples, guided practice, and independent exercises in four-part structure, each exercise carrying a verification tag](images/chapter-preview.png)

Budget for one thing on the humanities side: whether a citation can be checked depends on whether you supplied the material. In eval 8, with no sources supplied at all, 3 of 9 exercises shipped tagged `⚠️ 需作者确认（引文未核）` — **with no source material as input, expect roughly a third of the exercises to need your sign-off afterwards**. That isn't a defect, it's what the `humanities` profile promises: it would rather tag an item than quote verbatim a line it couldn't verify. To drive the ratio down, hand it your sources, editions and reading list at stage 1 — the profile asks for them.

### Pitfall 3: it falls apart once there are many chapters

Cram a 10+ chapter textbook into one conversation and the context will blow up: by chapter 8 it has forgotten chapter 2's notation, terminology drifts, and a dropped connection means starting over.

**The fix — write each chapter in isolation, persist progress to disk.** Writing a chapter takes only four lightweight inputs: that chapter's outline slice, the book-wide five UbD elements, the glossary, and the previous chapter's summary — plus a subject-profile id that fixes the chapter's section structure and verification methods. It never reads another chapter's prose, so the context stays flat no matter how many chapters there are. Progress is written to `.progress.json` as it goes; interrupt at any point and one sentence resumes from the break, with finished chapters left untouched.

## The five-stage pipeline × skill capabilities

One table for the whole picture: who does what at each stage, which file the output lands in, where it stops and waits for you, and which eval case guards it.

| Stage | Skill | What it does | Output | Gate | Eval case |
| --- | --- | --- | --- | --- | --- |
| **0 · Setup** (optional) | `textbook-init` | One round of questions: one book or several, where, version control or not | Working-directory scaffold (git and a README brief, both optional) | — | [eval 6](evals/evals.json) |
| **1 · Scoping** | `textbook-outline` | Subject / reader's starting point / depth / length, plus the subject profile derived from the subject | `00-教材设计.md` §「## 一、教学定位」 | No (one round of questions) | [eval 1](evals/evals.json) |
| **2 · UbD desired results** | `textbook-outline` | Big Ideas, Enduring Understandings, Essential Questions, Transfer Goals, Learning Objectives | §「## 二、UbD 五件套（已确认）」 | **⏸ Yes (primary gate)** | [eval 1](evals/evals.json) |
| **3 · Assessment & chapter design** | `textbook-outline` | Chapter tree + exercise plan + book-wide gradient report + performance task | §「## 三、章节树与梯度规划（已确认）」and §「## 四、表现性任务」 | **⏸ Yes (secondary gate)** | [eval 1](evals/evals.json) |
| **4 · Chapter prose** | `textbook-chapter` → `textbook-exercises` | Four-part chapters (section titles come from the subject profile); every answer checked by the profile's method | `NN-<章标题>.md` × N + `98-参考答案.md` + glossary increments | No | [eval 2, 3](evals/evals.json), [8](evals/evals.json) |
| **5 · Review and sign-off** | `textbook` (orchestrator) | Full read-through self-check, derive the student-facing task, generate the reader's front matter | Self-check report + `00-前言.md` + `99-表现性任务.md` + delivery summary | No | [eval 5](evals/evals.json) |

Stages 1–5 are driven by the orchestrator `textbook`, and `.progress.json` is read and written by it alone — the interrupt-and-resume mechanism itself is guarded by [eval 4](evals/evals.json). Stage 0 sits outside the pipeline: `textbook-init` only creates the scaffold and hands you to `textbook`. Skipping it is fine — `textbook` will create a default directory on its own.

## Quick start

Three hosts are supported: Claude Code, Codex, and WorkBuddy.

### Installation

**Copy the block below that matches your agent and paste it to them** — the agent does the install; you don't type a single command.

**Install into Claude Code** 👇

```text
Please install the textbook-writer-skills textbook-writing skill suite for me:

1. Clone https://github.com/cabbage2000-lab/textbook-writer-skills into a temp directory
2. Make sure ~/.claude/skills/ exists (create it if not), then copy **all 5 subdirectories**
   of the repo's skills/ into it — not a subset: textbook, textbook-outline,
   textbook-chapter, textbook-exercises, textbook-init
   - The 5 skills are one unit; they reference each other by the relative path
     ../<skill-name>/references/, so omitting any one of them breaks the links
   - Overwrite same-named directories — that is how updating works
   - Leave every skill from other sources in that directory alone; never wipe the directory
3. Delete the temp directory
4. Tell me where you installed it and whether all 5 skills are there
```

**Install into Codex** 👇

```text
Please install the textbook-writer-skills textbook-writing skill suite for me:

1. Clone https://github.com/cabbage2000-lab/textbook-writer-skills into a temp directory
2. Make sure ~/.codex/skills/ exists (create it if not), then copy **all 5 subdirectories**
   of the repo's skills/ into it — not a subset: textbook, textbook-outline,
   textbook-chapter, textbook-exercises, textbook-init
   - The 5 skills are one unit; they reference each other by the relative path
     ../<skill-name>/references/, so omitting any one of them breaks the links
   - Overwrite same-named directories — that is how updating works
   - Leave every skill from other sources in that directory alone; never wipe the directory
3. Delete the temp directory
4. Tell me where you installed it and whether all 5 skills are there
```

**Install into WorkBuddy** 👇

```text
Please install the textbook-writer-skills textbook-writing skill suite for me:

1. Clone https://github.com/cabbage2000-lab/textbook-writer-skills into a temp directory
2. Make sure ~/.workbuddy/skills/ exists (create it if not), then copy **all 5 subdirectories**
   of the repo's skills/ into it — not a subset: textbook, textbook-outline,
   textbook-chapter, textbook-exercises, textbook-init
   - Copy the 5 subdirectories themselves, don't nest the whole skills/ directory inside —
     WorkBuddy names skills after the directory hierarchy, so an extra level turns the
     skill name into skills:textbook
   - The 5 skills are one unit; they reference each other by the relative path
     ../<skill-name>/references/, so omitting any one of them breaks the links
   - Overwrite same-named directories — that is how updating works
   - Leave every skill from other sources in that directory alone; never wipe the directory
3. Delete the temp directory
4. Tell me where you installed it and whether all 5 skills are there
```

Skills load in a **fresh session** only — an already-open session won't see them. On WorkBuddy you can also confirm the install in its Skills (技能) panel.

> **Only want it in one project?** Swap the user-level path in the prompt for the project-level directory under that project's root: `.claude/skills/` on Claude Code, `.codex/skills/` or `.agents/skills/` on Codex, and **`.codebuddy/skills/` on WorkBuddy** — note that it is not `.workbuddy/`. WorkBuddy's user-level directory is `~/.workbuddy/`, but its project-level one keeps the underlying CodeBuddy kernel's `.codebuddy/`, an asymmetry that is easy to get wrong.
>
> **On a different host?** Same prompt, just point it at that host's skills directory. Installing to the wrong path means no skills show up at all, with no error to tell you why — the hosts' skills directories are **mutually invisible**, so using several hosts means installing a copy for each.
>
> **Can I install just one?** No. Even to use `textbook-exercises` on its own, it reads `textbook-outline`'s Bloom verb tables and `textbook`'s handoff contract — all 5 together is the minimum.
>
> **Don't want to install anything?** Open this repository directory in Codex (or any host that reads `AGENTS.md`): [AGENTS.md](AGENTS.md) at the repo root routes a "写教材" request to the right skill, no installation needed.

#### Prefer typing commands yourself? All three hosts support one-shot plugin installs

The repository is itself a plugin marketplace, and the plugin form has one advantage: one-command updates.

Claude Code — in a session:

```text
/plugin marketplace add cabbage2000-lab/textbook-writer-skills   # a local repo path also works
/plugin install textbook-writer@textbook-writer-skills
```

WorkBuddy — also in a session (it reads its own `.codebuddy-plugin/` manifests):

```text
/plugin marketplace add cabbage2000-lab/textbook-writer-skills
/plugin install textbook-writer@textbook-writer-skills
```

Codex — in a terminal:

```bash
codex plugin marketplace add cabbage2000-lab/textbook-writer-skills
codex plugin add textbook-writer@textbook-writer-skills
```

Both routes install the same skills — **don't do both on the same host**, or you'll end up with two copies. The WorkBuddy manifest format has been verified working by the author in other projects; this repository's manifests follow that same format.

To develop or try changes inside this repository, run this once after cloning to symlink `skills/` as the project-level skills directory (`.claude/` is gitignored):

```bash
mkdir -p .claude && ln -s ../skills .claude/skills
```

### What happens on the first run

Open a fresh session and type:

```text
用 textbook 写一本《线性代数入门》教材
```

1. The skill creates the textbook project directory and the progress file `.progress.json`;
2. One round of questions settles the scoping: who it's for, how deep, how long;
3. It produces the five UbD elements and stops at `⏸ 等待确认` ("awaiting confirmation") — the first gate, where you can confirm or ask for changes;
4. Once confirmed, it produces the chapter tree and the book-wide Bloom gradient report — the second gate;
5. Then it writes chapter by chapter, each landing as its own `.md` file — each chapter opens with "after this chapter, you should be able to…" and closes with a self-check list; independent exercises keep only the question in the chapter, while answers and verification records collect in `98-参考答案.md` so readers can attempt first and check after;
6. Finally it does a full review pass, produces a student-facing performance task with its rubric, and writes `00-前言.md` — who the book is for, how to use it, and a linked table of contents: the reader's way in.

Interrupt at any point; typing the same sentence again resumes from the break.

## How to ask: no skill names to memorize

Say what you want in your own words and the host will match the right skill; naming the skill explicitly (`用 textbook-exercises 出几道题`) is equally valid. This suite is built for people who know their subject and want to turn that knowledge into systematic teaching material: developers writing technical handbooks, teachers and students — in the sciences and the humanities alike — turning lecture notes into a textbook, creators producing instructional content. The skill supplies structure and discipline; subject-matter judgment stays with you.

| What you'd say | Lands on | What you get back |
| --- | --- | --- |
| `用 textbook 写一本《线性代数入门》教材` | `textbook` | A textbook directory: `00-前言.md` (the reader's way in: preface + how to use it + linked contents) + `00-教材设计.md` + one `NN-<章标题>.md` per chapter + `98-参考答案.md` + `术语表.md` (terms + symbol conventions) + `99-表现性任务.md` + `.progress.json` |
| `用 textbook-outline 设计一份数据结构教材大纲` | `textbook-outline` | `00-教材设计.md`: scoping + the five UbD elements + chapter tree with exercise plan + book-wide Bloom gradient report |
| `用 textbook-chapter 按大纲写第三章` (also works for a deep-dive technical article with full worked examples) | `textbook-chapter` | One `NN-<章标题>.md`: chapter intro → chapter objectives → concept exposition → worked examples → guided practice → independent exercises → chapter summary (with self-check) |
| `用 textbook-exercises 出几道矩阵乘法的练习题` | `textbook-exercises` | Three kinds of exercises (worked / guided / independent) + Bloom level tags + a verification record per exercise (runnable recomputation code where the answer can be recomputed, sources and check notes where it can only be checked; under `economics` both kinds appear in one chapter) |
| `用 textbook-init 初始化教材工作目录` | `textbook-init` | A directory scaffold (git version control and a README brief, both optional), then hands you to `textbook` to start writing |

English trigger phrases also work — each skill's `description` carries both Chinese and English trigger terms — but the Chinese prompts above are the ones exercised by the behavioral test suite, and the output is Chinese either way.

**Switching subject doesn't change how you ask.** `写一本《中国近代史纲要》教材` ("write a textbook on modern Chinese history") and `写一本《线性代数入门》教材` run the same pipeline through the same skill. The only difference lands at stage 1: it decides the subject profile once and prints it (`学科档案：humanities`), then passes it through unchanged chapter by chapter — in-chapter section structure, question types, cognitive verbs and verification method all switch with it, and it is never re-decided mid-book (switching profiles means switching verification discipline and section structure, so already-written chapters would no longer match the ones that follow). You don't pick the profile; if it picked wrong, say so at stage 1. A subject that straddles two families doesn't force a choice either — the `economics` profile already puts recomputation and source-checking side by side in one book.

### Requests it will push back on — each with a way forward

| What you might ask | Why it won't | Where it points you instead |
| --- | --- | --- |
| "Just give me the answer, skip the arithmetic" | Fabrication is the most damaging failure mode for AI-written teaching material | → It checks anyway, by its profile's method (recomputation for STEM, source checks for the humanities); anything genuinely unverifiable gets tagged `⚠️ 需作者确认`, never dressed up as verified |
| "Skip the UbD step and go straight to chapters" | The two gates are a red line; bypassing them lands you back at a pile of topics | → Confirming can be quick, but it can't be skipped; if you disagree with the draft, just ask for changes — changes take precedence over confirmation |
| "While writing chapter 8, look back at chapter 2's prose" | Reading other chapters' prose is exactly what blows up the context on a long book | → Cross-chapter consistency travels through three lightweight carriers: the glossary, the previous chapter's summary, and the five UbD elements |
| "Write me some humanities essay / case-analysis questions" | The `humanities` profile defines how to verify them: no answer key, but citations and facts still get checked | → You get essay questions with argument points and a rubric, tagged as open-ended; quotations carry their source, and anything it couldn't check is tagged `⚠️ 需作者确认（引文未核）` |
| "Turn this pile of lecture notes into a course" | v1 does backward design from scratch, not source-material reassembly | → Explicitly out of scope for v1, along with LMS integration and automatic figure generation |

### End to end: one textbook from start to finish

```text
 0. "Set me up a directory for writing a textbook"  → textbook-init  (optional; textbook creates a default one anyway)
 1. "用 textbook 写一本《线性代数入门》教材"           → textbook creates the project directory + .progress.json
 2. One round of questions: who, how deep, how long → stage 1, scoping
 3. ⏸ the five UbD elements await your OK           → stage 2, primary gate (confirm, or ask for changes)
 4. ⏸ chapter tree + Bloom gradient report await OK → stage 3, secondary gate
 5. Chapter by chapter, each saved, answers checked → stage 4
    └ every chapter reads only four inputs: its outline slice, the UbD elements, the glossary, the previous summary
      (plus the subject-profile id, which fixes the section structure and the verification method)
 6. Self-check + student-facing task + 00-前言.md → stage 5 (preface / how to use it / linked contents) + delivery summary
 ── Interrupt anywhere; the same sentence resumes from the break, finished chapters untouched ──
```

## Why you can trust it

The promises here don't rest on self-description — they rest on five red lines written into the contract and guarded by validation and evals:

- **Every answer was actually checked.** An answer ships only after it has been verified by the method its subject profile defines — recomputed along an independent path under `stem`, checked word-for-word against the original source under `humanities` — with the verification attached to the exercise; anything unverifiable is tagged `⚠️ 需作者确认`, never dressed up as verified, and never a citation written from memory.
- **You make the calls that matter.** The gates at stages 2 and 3 only open on explicit author confirmation and no "optimization" may bypass them; "confirmed, but change X" is handled as a change request — changes take precedence over confirmation.
- **A long textbook actually gets finished.** Chapter writing receives only its input contract and never reads other chapters' prose; `.progress.json` is written by the orchestrator alone, flushed to disk after every stage and every chapter.
- **No placeholders ship.** TBD / TODO / 待补充 and the like are forbidden in delivered `.md` files, enforced by the validation script.
- **No host lock-in.** The core path depends only on the generic agent-skills standard (SKILL.md frontmatter + layered `references/` loading + relative cross-references); host-specific capabilities are optional enhancements only, each with a documented plain-text fallback.

What guards them is three layers of defense; the first two run automatically in CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)):

```bash
python3 scripts/validate_skills.py       # 1. structural validation: skill content + manifest consistency + repo health
python3 -m unittest discover -s tests    # 2. unit tests: the validation logic itself
# 3. behavioral tests: really run the 8 cases in evals/evals.json;
#    after changing a skill, re-run per the mapping table in CONTRIBUTING.md
```

Layer 3 cannot be automated — the cases have to be run for real in a fresh agent session (Claude Code is the baseline host; see [evals/README.md](evals/README.md) for re-running them on another host) and judged against their assertions one by one. That is deliberate: these skills are programs written for a model, so a one-line instruction change can change runtime behavior in ways no structural check would catch.

## How it works

Two diagrams, two viewpoints. Start from the author's seat: you say one sentence, it walks the five steps for you, stopping twice to wait for your call — and every finished chapter is saved, so a break costs you nothing.

![Diagram of the pipeline from the author's seat: one sentence from the author, then scoping, the five UbD elements (stop 1, waiting for the author's OK), the chapter order and Bloom difficulty gradient (stop 2, waiting for the author's OK), chapter-by-chapter writing in the concept → worked example → guided practice → independent work rhythm (answers recomputed, each chapter reading only its own inputs, progress saved after every chapter), a final read-through, and delivery of a folder holding the design, the chapters, the glossary and the performance task](images/how-it-works.en.svg)

Switching to the skill's-eye view, here is how the work divides, who calls whom, and the three hard constraints — one orchestrator skill drives three sub-skills, with one standalone helper for planning the working directory before you start:

![Diagram of the skill composition: the orchestrator skill textbook drives the five stages and is the only reader and writer of .progress.json; it calls textbook-outline for the stage 1 to 3 teaching design, where both gates wait for the author's OK, and calls textbook-chapter once per chapter, each chapter receiving only its outline slice, the UbD elements, the glossary and the previous summary and never other chapters' prose; textbook-chapter in turn calls textbook-exercises, which recomputes every computed answer before returning; handoff-contract.md is the single authoritative definition all five skills align their field names to; textbook-init sits outside the pipeline and only creates the working directory](images/skill-composition.en.svg)

The foundation in that diagram, [handoff-contract.md](skills/textbook/references/handoff-contract.md), is the **single authoritative definition for the whole project**: handoff contracts between stages, the on-disk layout of a textbook project, the `.progress.json` state machine and its re-entry rules. All five skills reference it, and contract field names match word for word up and down the chain. That is also why the five skills must be installed together: they reference each other by relative path, so omitting one breaks the links.

## Milestones and acceptance status

| Milestone | Scope | Eval case | Status |
| --- | --- | --- | --- |
| M1 | Skeleton: 4 skills + 6 references + validation | — | ✅ Done (including 3 behavioral smoke tests) |
| M2 | Outline skill clears both gates on a real subject | [eval 1](evals/evals.json) | ✅ Passed (6/6 assertions, 2026-08-03, including performance-task rubrics) |
| M3 | Chapter + exercise skills working | [eval 2, 3](evals/evals.json) | ✅ Passed (7/7 and 5/5 assertions, 2026-08-03) |
| M4 | Orchestrator interrupt-and-resume (state machine locates the resume point) | [eval 4](evals/evals.json) | ✅ Passed (3/3 assertions, 2026-08-03; the finished chapter's SHA-1 was byte-identical across the interruption) |
| M5 | Second subject written end to end (including stage 5 self-check and delivery summary), proving it isn't overfitted | [eval 5](evals/evals.json) | ✅ Passed (8/8 assertions, 2026-08-03; the first run surfaced a "26 of 80 exercises missing their verification line" defect — after the fix, the re-run produced 11 chapters and 85 exercises with zero omissions) |
| M6 | Working-directory setup skill (textbook-init): plan and create single-book / multi-textbook directories | [eval 6](evals/evals.json) | ✅ Passed (6/6 assertions, 2026-08-03; must be run outside this repository) |
| M7 | Subject-profile layer: one core, pluggable profiles, run through on a non-STEM subject | [eval 7, 8](evals/evals.json) | ✅ Passed (eval 7: 6/6 + eval 8: 7/7, 2026-08-04) — on the outline side the profile routed correctly with no STEM residue in question types or verbs and a self-consistent gradient matrix; on the chapter side, with no sources supplied, all three unverifiable citations took the documented fallback and were never quoted verbatim, and the citation ledger landed. Also the first eval coverage of the gate revision branch |
| M8 | Mixed-verifiability profile (`economics`): recomputation and source-checking coexisting inside one book | [eval 9, 10](evals/evals.json) | ⏳ Pending (profile and case definitions are in the repo, first two defense layers green; what it tests is that a third verification mode fits with zero core changes) |
| M9 | Reader-facing book parts: independent-exercise answers split out into `98-参考答案.md`, a reader-facing front page `00-前言.md`, student-facing objectives opening each chapter and a self-check closing it | [eval 3, 4, 5](evals/evals.json) | ⏳ Pending (first two defense layers green; the answer split is judged by eval 4, which walks the full orchestration chain, and the front page plus the three-column coverage matrix by eval 5, which writes a whole book) |

Per-assertion evidence (assertions, artifacts, verdicts) lives in `evals/workspace/` (gitignored). Judging discipline, per-case runtimes, and the terms for re-running on another host are in [evals/README.md](evals/README.md).

**Current eval debt (recorded plainly, not glossed over)**: the 0.5.0 round changed the contract itself (new `answer_layout` and `承载的学习目标编号[]` fields, two new files on disk — `98-参考答案.md` and `00-前言.md`), all 5 skills and all three profiles; assertions went from 71 to 77, and **not one of the 10 cases kept its old assertion set**. Per the mapping table in [CONTRIBUTING](CONTRIBUTING.md), the full 1–10 needs re-running; every pass record in the table above (M2–M7) belongs to the pre-change definitions and does not carry over to this version. The 0.4.0 leftovers — evals 1, 3, 4 pending and eval 2 awaiting one more round — fold into the same debt. The release process carries no eval gate: shipping with the debt is a deliberate choice, not an oversight (same as v0.2.0 and v0.4.0), and the price is that the third defense layer currently says nothing about 0.5.0's behavior. The next round of work starts by paying it down.

## Repository layout

Five areas: `skills/` (the 5 skills themselves, each with a `references/` knowledge base — UbD guide, Bloom verb tables, chapter template, prose style guide, exercise verification rules, performance-task rubrics, workspace layout, plus the subject-profile spec and the pluggable profiles under `profiles/`: everything that varies by subject — question types, verification methods, cognitive verbs, in-chapter section structure — lives there, so supporting a new subject family means adding one profile file); three distribution-manifest directories `.claude-plugin/`, `.codex-plugin/` and `.codebuddy-plugin/` (Codex's marketplace manifest additionally lives in `.agents/plugins/`, which makes the repository itself a one-command-install marketplace on all three hosts); [AGENTS.md](AGENTS.md) (the in-repo entry point for hosts that don't auto-load skill frontmatter — usable with no installation at all); [evals/](evals/README.md) (behavioral test cases: prompt + objective assertions; case definitions are versioned, run artifacts are not); and `scripts/` + `tests/` (the structural validation script and its unit tests, zero third-party dependencies, Python 3.10+ standard library).

## Contributing

To develop or customize this, start with [CONTRIBUTING.md](CONTRIBUTING.md): the blast radius of a change (`handoff-contract.md` moves all 5 skills), the definition of done for a skill change (structural validation → unit tests → re-run the affected eval cases per the mapping table → update CHANGELOG), the conventions for writing a skill, the checklist for adding one, and the release process. Architecture decision summaries are in [docs/adr/](docs/adr/README.md); version history is in [CHANGELOG.md](CHANGELOG.md). For working inside this repository, see the symlink setup at the end of "Quick start" above.

## License

[MIT](LICENSE) — free to use, modify and distribute, commercial use included, as long as the copyright and license notice are retained.

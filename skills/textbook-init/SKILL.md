---
name: textbook-init
description: Use when starting a textbook project and the author wants to plan and scaffold the working directory before writing — 规划单本教材项目目录或多教材工作区，可选 git 版本管理与 README 工作说明 — e.g. "初始化教材项目"、"创建教材工作目录"、"规划教材工作区"、"建一个写教材的目录". Only creates the directory scaffold and hands off to textbook; never creates pipeline files (.progress.json、00-教材设计.md、术语表.md). Not for writing textbook content (use textbook — 不经 init 它也会自建默认目录), not for resuming an existing project (directly use textbook).
---

# textbook-init

动笔前的工作目录规划师：一轮提问弄清作者要写一本还是多本、放在哪里、要不要版本管理，呈现目录方案等确认后创建目录骨架（可含 git 仓库与 README 工作说明），最后把作者交给 textbook 主流程开写。教材项目内部的文件构成以 [../textbook/references/handoff-contract.md](../textbook/references/handoff-contract.md)（下称"契约文档"）第 3 节为唯一权威定义，本 skill 只引用不重复定义。

## 何时不触发

- 已有教材项目要续写（目录里有 `.progress.json`）——直接用 textbook，它会按状态文件定位续点；
- 作者直接开写、不关心目录规划——textbook 启动时自会询问一次并默认 `./<教材名>/`，无需先走本 skill；
- 整理与教材写作无关的目录——本 skill 只服务教材项目的开局。

## 与流水线的关系

本 skill 只独立触发：不被 textbook 调度，不进五阶段契约链，产出是"就绪的空工作目录 + 启动指引"。

**流水线文件一律不建不改**：`.progress.json`（主 skill 是唯一写者，这是项目红线）、`00-教材设计.md`（textbook-outline 写入）、`NN-<章标题>.md`（逐章生成）、`术语表.md`（主 skill 追加维护）。动机：主 skill 的重入判定靠"这些文件存不存在、内容有没有"定位续点（契约文档第 4 节），预建空文件会让它把全新项目误判成半成品；空壳文件混进交付物也违背"交付即可用"的底线。本 skill 创建的只有目录本身、`.gitignore` 和 README 工作说明——均在契约之外。

## 工作流

### 第 1 步：一轮提问

用 AskUserQuestion **一轮**收集四项（触发语已说明的项不再问）：

1. **教材名**：如《线性代数入门》——将成为项目目录名；
2. **规划范围**：a) 只写这一本  b) 未来还会写多本（追加：工作区名，默认"教材工作区"）；
3. **位置**：项目/工作区建在哪个目录下，默认当前目录 `./`；
4. **git 版本管理**：默认要（教材写作周期以周计，版本保护值回票价）；作者明确不要则跳过。

若当前环境没有 AskUserQuestion 工具，降级为编号提问并等待文本回复：

```text
请回答以下问题（回复格式如 "1 线性代数入门 2b 教材工作区 3 ./ 4 要"）：
1. 教材名？
2. 规划范围？ a) 只写这一本  b) 未来还会写多本（请给工作区名，默认"教材工作区"）
3. 建在哪个目录下？（默认当前目录 ./）
4. 要 git 版本管理吗？（默认要）
```

按语义宽松解析回复，只就有歧义的一项追问。

### 第 2 步：方案呈现与确认

按 [references/workspace-layout.md](references/workspace-layout.md) 第 1、2 节的布局规则组装方案，完整呈现后停下：

- **目录树预览**：含流水线随后会生成的文件，逐项注明"由 textbook 流水线创建"——让作者看到最终形态，同时不误以为本 skill 会建它们；
- **关键选择及理由**：单本还是工作区分层、git 建在哪一层、`.gitignore` 为什么不忽略 `.progress.json`；
- 停点格式沿用契约文档第 5 节：

`⏸ 等待确认：工作目录方案（回复"确认"开始创建，或直接提出修改）`

作者提出修改 → 更新方案后**重新完整呈现**再等确认，循环直到明确确认；"确认，但把位置改一下"这类混合答复按修改分支处理（修改优先于确认，判定语义同契约文档第 5 节）。**确认前不创建任何东西。**

### 第 3 步：创建与交接

1. **建目录**：按确认的方案 `mkdir -p`；
2. **git 判重**：在目标位置检查是否已处于某个 git 仓库内（方法见 references/workspace-layout.md 第 3 节）——已在，则跳过 git init 并向作者说明原因；
3. **git 初始化**（作者要 git 且未命中判重）：git init + 写 `.gitignore` + 首次提交，层级与内容规范见 references/workspace-layout.md 第 3、4 节；
4. **README 工作说明**：按 references/workspace-layout.md 第 5 节模板实例化——所有字段填当前项目的真实值，写完通读确认没有残留尖括号或待填空白；
5. **打印成果与下一步指引**：

```text
✅ 工作目录就绪：<实际路径>
接下来对我说：写教材《<教材名>》，落盘目录用 <项目目录路径>
（textbook 会在该目录里创建 .progress.json 并从教学定位开始五阶段流程）
```

## 安全边界

- **目标目录已存在且非空**：呈现现有内容清单，绝不覆盖、移动或删除任何既有文件；其中若发现 `.progress.json`，说明这是进行中的教材项目，提示作者直接对 textbook 说续写，本 skill 就此打住；
- **README / .gitignore 已存在**：保留原文件不动，仅提示作者自行核对是否需要补充；
- 本 skill 的全部动作**只增不删**：创建目录、创建新文件、git init 与提交——不含任何删除、移动、覆盖操作。

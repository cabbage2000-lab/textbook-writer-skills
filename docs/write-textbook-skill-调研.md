# 写教材的 Skill：调研报告

> 调研时间：2026-07-14
> 调研目标：搞清楚"用 skill 写通用知识教材"这件事的现状、方法论支撑，以及自己设计一个 skill 的可行路径。
> 面向读者：自己（决定要不要动手做、怎么做）

---

## 写在最前面：一句话结论

写教材这件事，**难点不在写作本身，在教学设计**。现成的开源 skill 大多解决了"把素材组织成长文档"的工程问题，但几乎没有人把"怎么把一门知识教明白"的教学法内核真正装进 skill 里。

好消息是：教学设计领域早有一套成熟的、可被结构化的方法论——**Understanding by Design（UbD，追求理解的教学设计）** 的逆向设计三阶段。把它作为 skill 的核心骨架，再复用本地 `tutorial-writer` 已经验证过的"多阶段 + 强制 gate + 交接契约"工程结构，就能设计出一个有差异化、不流于"长文生成器"的写教材 skill。

下面分三块展开。

---

## 一、现有开源 skill 方案：别人都做到哪了

### 1. 本地 `tutorial-writer`（最完整的工程范本）

这是我们自己项目里已经有的 skill，路径在 [.claude/skills/tutorial-writer/](.claude/skills/tutorial-writer/)。它虽然是写"教程"而非"教材"，但工程结构是目前见到的最成熟样本，**写教材 skill 直接复用它的骨架是最高效的路径**。

它的核心设计：

- **五阶段流水线**：写作背景确认 → 知识点调研 → 大纲确认 → 正文编写 → 审核定稿
- **唯一的强制停点**：只在大纲阶段强制等用户确认（gate），其余阶段跑完打印一行进度继续，不打断
- **阶段间交接契约**：每个阶段的输入输出用 `{...}` 显式定义，像函数签名一样，避免跨阶段信息丢失
- **真实性红线**：操作步骤要么真跑一遍验证，要么明确标注"未验证 + 来源"，绝不编造执行结果
- **文体骨架选型**：用 [Diátaxis 框架](.claude/skills/tutorial-writer/references/tutorial-structure.md) 区分学习型 / 任务型 / 排错手册三类，不同骨架对应不同结构
- **配图双轨**：人工截图走标注块、抽象流程走 SVG 示意图，统一规格

**可借鉴点**：阶段化流水线、强制 gate 设计、交接契约思维、真实性红线、文体骨架前置选型。

**局限**：它面向"教会一件事"的教程（单工具、单流程），不是面向"系统讲一门知识"的教材。教材的章节更深、有例题习题、有循序渐进的认知阶梯，这些它没有覆盖。

### 2. mcpmarket 的 Course Generator skill

来源：[Course Generator Claude Code Skill](https://mcpmarket.com/tools/skills/course-generator)，56 stars。

它的卖点是把 1–100+ 篇散乱文档（论文、会议转录、项目笔记）整合成一门课程。两个设计值得记：

- **11 个模块化内容块**：理论框架、案例研究、最佳实践等十一种"积木"，每章从积木里挑模块组装。这是"教材 ≠ 教程"的关键差异——教材每章的内部结构比教程复杂，需要可复用的内容块。
- **叙事化写作**：明确要求"用有论证的叙事散文替代 bullet point"，把口语转录洗成正式散文。这个取向说明它瞄准的是"可读性强的成体系教材"，不是 API 文档。

**可借鉴点**：模块化内容块的思路（解决教材每章内部结构问题）、对叙事性写作的明确要求。

**局限**：它的定位是"素材 → 课程"的整理工具，教学设计层面较薄，更像"高级文档重组器"。

### 3. Codecademy 的 Lesson Plan Generator

来源：[How to Build Claude Skills: Lesson Plan Generator](https://www.codecademy.com/article/how-to-build-claude-skills)。

这是一个偏"教案"的 skill，引导 Claude 生成：导入（introduction）、学习目标、练习、测验，再格式化输出。结构简单，但**它把"学习目标 + 练习 + 测验"作为固定产出模块**，这点和教材的组成高度吻合。

**可借鉴点**：学习目标、练习、测验作为产出的必备模块（对应教材的学习目标 / 例题 / 习题）。

### 4. MindStudio：模块化 Skill 串联

来源：[How to Build Modular Claude Skills That Chain Into Skill Systems](https://www.mindstudio.ai/blog/modular-claude-skills-skill-systems)。

讲的是把单个 skill 设计成可组合的，用一个 orchestrator 串起来。对写教材的启发是：**教材篇幅大，单 skill 容易上下文爆炸，可以考虑拆成"大纲设计 skill + 章节写作 skill + 例题生成 skill"的组合**，由一个主 skill 调度。

### 5. 知乎：程序员用多 Agent 协作做专业课程

来源：[一个程序员是如何借助 AI 智能体制作专业课程的](https://zhuanlan.zhihu.com/p/82048836696)。

这是目前看到的最接近"教学法驱动"的实践。它的多 Agent 流水线：

- Agent 1：定义核心要素 **G/U/Q/K/S**（迁移目标 / 持续理解 / 基本问题 / 关键知识 / 关键技能）——作为课程的核心纲领
- Agent 2：评估框架设计
- 后续 Agent：内容生成

**这个 G/U/Q/K/S 不是作者自创的，它来自 UbD 理论**（见第二部分）。这是把教学法真正装进流程的少数案例，也是本报告最重要的发现之一。

### 6. 技能仓库索引（找现成 skill 用）

- [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)：345+ 个 Claude Code skill 的聚合库
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)：精选 skill 集合
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)：1000+ 跨工具 agent skill

动手做之前可以再在这几个库里搜一遍 "course / textbook / curriculum / lesson"，确认没有更成熟的轮子。

### 本部分小结

| 方案 | 解决了什么 | 没解决什么 |
|------|-----------|-----------|
| 本地 tutorial-writer | 工程结构、阶段化、gate、真实性 | 教材级深度、例题习题、认知阶梯 |
| mcpmarket course-generator | 模块化内容块、素材整合、叙事写作 | 教学设计内核薄 |
| Codecademy lesson plan | 学习目标+练习+测验模块 | 偏单节教案，不成体系 |
| 知乎多 Agent 课程 | G/U/Q/K/S 教学法驱动 | 工程封装不足，是思路非产品 |

**结论**：工程结构（怎么组织流程）已经有人做得很好，可以直接借鉴；但"怎么把一门知识教明白"的教学法内核，目前没有任何一个 skill 系统性地装进去。这是差异化空间。

---

## 二、教材写作方法论：教材和教程到底差在哪

这一块是写教材 skill 的"内容内核"。如果只学第一部分的工程结构，做出来的只是"长文生成器"；真正让它成为"教材"的，是这部分的教学法。

### 1. UbD 逆向设计三阶段（核心框架，必装）

来源：Wiggins & McTighe《Understanding by Design（追求理解的教学设计）》，参考文献：

- [ASCD UbD 白皮书 PDF](https://files.ascd.org/staticfiles/ascd/pdf/siteASCD/publications/UbD_WhitePaper0312.pdf)
- [UbD 全书 PDF](https://andymatuschak.org/files/papers/Wiggins,%2520McTighe%2520-%252005%2520-%2520Understanding%2520by%2520design.pdf)
- [Wikipedia: Understanding by Design](https://en.wikipedia.org/wiki/Understanding_by_Design)
- 中文综述：[基于 UbD 理论的单元教学设计](https://pdf.hanspub.org/ve2025144_371721700.pdf)

UbD 的核心主张是**"以终为始"**——先想清楚学生应该理解什么、能迁移什么，再设计怎么评估，最后才设计教学活动。和传统"先写内容再想考什么"完全相反。

**三阶段**：

| 阶段 | 名称 | 做什么 | 产出 |
|------|------|--------|------|
| 一 | 确定预期结果 | 提炼大概念、持久理解、核心问题、迁移目标 | 课程/章节的"五件套" |
| 二 | 确定评估证据 | 设计表现性任务和多元评价 | 怎么证明学生学会了 |
| 三 | 设计学习体验 | 规划教学活动和顺序 | 具体的章节内容 |

**四个关键术语**（写教材 skill 必须内化）：

- **大概念（Big Ideas）**：学科中有解释力和组织力的核心概念，能把零散知识点串起来
- **持久理解（Enduring Understandings）**：希望学生课程结束后仍能保留并应用的核心洞见——"忘掉细节后剩下的东西"
- **核心问题（Essential Questions）**：指向大概念的开放性问题，能引发持续思考，不是有标准答案的题
- **迁移目标（Transfer Goals）**：学生能把所学应用到新情境的能力——这是终极目标

**为什么这对写教材 skill 至关重要**：教材最容易出的毛病是"知识点堆砌"——一章章罗列概念，却没有一条主线串起来。UbD 的阶段一就是逼作者先回答"这门知识最该让学生带走什么"，有了五件套，后面的章节组织、例题选择才有依据。这正是现有 skill 都没做好的部分。

### 2. Bloom 认知层级（写学习目标和例题的标尺）

来源：[Adams 2015, Bloom's taxonomy of cognitive learning objectives (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4511057/)、[修订版 Bloom 分类法（Colorado College）](https://www.coloradocollege.edu/other/assessment/how-to-assess-learning/learning-outcomes/blooms-revised-taxonomy.html)

修订版 Bloom 的六个认知层级，由低到高：

> 记忆（remembering）→ 理解（understanding）→ 应用（applying）→ 分析（analyzing）→ 评价（evaluating）→ 创造（creating）

**在写教材里的两个直接用途**：

- **写学习目标**：目标要用对应层级的动词。"理解 X"是模糊的，"能用自己的话解释 X"（理解层）、"能用 X 解决 Y 类问题"（应用层）、"能比较 X 和 Y 的适用场景"（分析层）才是可验证的。
- **设计例题和习题的梯度**：好的教材例题从低层级（记忆、理解）逐步走到高层级（应用、分析），而不是全堆在某一层。skill 可以用 Bloom 层级作为检查例题梯度的标尺。

### 3. 脚手架（Scaffolding）与认知负荷

来源：[Edutopia: 6 Scaffolding Strategies](https://www.edutopia.org/blog/scaffolding-lessons-six-strategies-rebecca-alber)、[Miami OH: Scaffolding Writing](https://miamioh.edu/howe-center/hwac/resources-for-teaching-writing/scaffolding-writing-for-learning.html)

脚手架的核心是**把学习拆成块，每块配一个支撑结构**。教材里的落地：

- **循序渐进**：每个新概念都建立在前一个之上，不跳跃
- **worked examples（示范例题）**：先把一道题完整解给学生看（脚手架），再让他们自己做（撤脚手架）。这对应认知负荷理论——示范例题能降低初学者的认知负荷，比直接丢一堆习题有效
- **梯度练习**：练习从"照着例题做"过渡到"独立做变式"，再到"开放题"

**对 skill 的启发**：教材的每章应该有固定的"概念讲解 → 示范例题（完整解题）→ 引导练习 → 独立习题"节奏。这是可以直接固化进 skill 的内容块。

### 4. Diátaxis 文体骨架（本地已有，可复用）

来源：本地 [tutorial-structure.md](.claude/skills/tutorial-writer/references/tutorial-structure.md)

教程用学习型 / 任务型 / 排错手册三类骨架。教材可以沿用这个思路，但骨架类型不同——教材更接近"学习型"的强化版，需要增加"章节小结 / 例题 / 习题"等教学模块。

### 本部分小结

教材 vs 教程的本质差异：

| 维度 | 教程（tutorial） | 教材（textbook） |
|------|-----------------|-----------------|
| 目标 | 教会一件具体的事 | 建立一门知识的系统理解 |
| 主线 | 操作流程 | 大概念 + 持久理解 |
| 评估 | 跑通就算成功 | 例题 + 习题 + 能迁移 |
| 结构 | 步骤化 | 章节编排 + 认知阶梯 |
| 长度 | 一篇文档 | 多章节体系 |

**写教材 skill 的方法论内核 = UbD 三阶段（骨架）+ Bloom 层级（学习目标和例题的标尺）+ 脚手架/认知负荷（章节内部节奏）**。

---

## 三、自己设计一个写教材 skill 的思路草案

把前两块拼起来。这里给的是一个**设计草案的骨架**，不是最终 skill 文件——目的是先把思路理清，确认方向对了再动手用 skill-creator 落地。

### 核心定位（一句话）

**一个以 UbD 逆向设计为内核、面向"通用知识教材"的 skill：先逼作者想清楚"学生该带走什么"，再倒推章节、例题、习题，产出一门有主线、有梯度、可评估的成体系教材。**

差异化点：不和其他 skill 拼"长文生成"，拼"教学设计驱动"。

### 工作流草案：五阶段（复用 tutorial-writer 工程结构 + UbD 内核）

| 阶段 | 名称 | 对应 UbD | 产出 | 是否强制 gate |
|------|------|---------|------|--------------|
| 1 | 教学定位确认 | 阶段一前奏 | 学科 / 读者认知起点 / 教材深度 / 篇幅规模 | 否（一轮提问） |
| 2 | **预期结果设计** | **UbD 阶段一** | 大概念 + 持久理解 + 核心问题 + 迁移目标 + 学习目标（带 Bloom 动词） | **是（核心 gate）** |
| 3 | 评估与章节设计 | UbD 阶段二 + 三前奏 | 章节树（对齐持久理解）+ 每章例题/习题计划（带 Bloom 梯度）+ 表现性任务 | 是（次要 gate） |
| 4 | 章节正文编写 | UbD 阶段三 | 各章正文（概念→示范例题→引导练习→独立习题） | 否 |
| 5 | 审核定稿 | — | 通读走查 + Bloom 梯度复核 + 术语一致性 + 交付 | 否 |

**关键设计决策**：

1. **阶段 2 是核心 gate，不是阶段 3**。这是和 tutorial-writer 最大的区别。tutorial-writer 在"大纲"处停，因为教程的目标天然清晰（教会一件事）。教材必须先在"预期结果"处停——逼作者明确大概念和持久理解，否则后面全是无主线堆砌。这是 UbD 的精髓装进流程的具体体现。

2. **例题和习题在阶段 3 就要规划，不是阶段 4 边写边编**。每章的例题/习题要带 Bloom 层级标注，保证全书有认知梯度。避免出现"全书例题都在'理解'层，没有'应用'和'分析'"的常见毛病。

3. **章节内部固定节奏**：概念讲解 → 示范例题（完整解题，脚手架）→ 引导练习 → 独立习题。这个节奏固化进 skill，作为每章的内容块模板（借鉴 mcpmarket 的模块化思路）。

4. **复用 tutorial-writer 的工程件**：阶段间交接契约、真实性红线（教材里的例题答案必须验证正确，不能编造）、术语表全程一致、强制 gate 之后不再打断。

### 需要配套的 references（草案）

- `ubd-framework.md`：UbD 三阶段 + 四个术语的落地解释和示例
- `bloom-levels.md`：六层级动词表 + 如何写可验证学习目标
- `chapter-template.md`：章节内部固定节奏模板（概念→示范→引导→独立）
- `exercise-design.md`：例题和习题设计指南，含 Bloom 梯度检查
- `writing-style.md`：可大量复用 tutorial-writer 的同名文件

### 复用 vs 新建的边界

- **直接复用**：五阶段流水线结构、强制 gate 机制、交接契约写法、真实性红线、术语表机制、配图双轨（教材也要配图）
- **需要新建**：UbD 内核（阶段 1–3 重写）、例题/习题模块、Bloom 梯度检查、章节内部节奏模板
- **需要调整**：文体骨架从 Diátaxis 三类改为"教材统一用学习型强化版"，但保留单线结构原则

### 风险和待确认

- **教材篇幅大，单 skill 上下文可能不够**。长教材（10+ 章）是否要拆成"大纲 skill + 单章写作 skill"的组合（参考 MindStudio 的模块化串联），还是靠增量更新（像 tutorial-writer 的 FR6）解决。倾向先做单 skill + 增量更新，跑通再考虑拆分。
- **"通用知识教材"范围太宽**。文科教材（如历史、哲学）和理科教材（如数学、物理）的例题形式差异巨大。v1 建议先锁定一类（比如偏 STEM 的概念型教材），跑通再泛化。
- **UbD gate 会让流程更重**。作者得多花一轮想清楚"持久理解"，可能比 tutorial-writer 门槛高。但这是教材质量的根本，不该省。

---

## 参考来源

**现有 skill 与实践**
- 本地 [.claude/skills/tutorial-writer/](.claude/skills/tutorial-writer/)（含 SKILL.md 及 references/）
- [Course Generator Claude Code Skill (mcpmarket)](https://mcpmarket.com/tools/skills/course-generator)
- [How to Build Claude Skills: Lesson Plan Generator (Codecademy)](https://www.codecademy.com/article/how-to-build-claude-skills)
- [How to Build Modular Claude Skills That Chain Into Skill Systems (MindStudio)](https://www.mindstudio.ai/blog/modular-claude-skills-skill-systems)
- [alirezarezvani/claude-skills (GitHub)](https://github.com/alirezarezvani/claude-skills)
- [ComposioHQ/awesome-claude-skills (GitHub)](https://github.com/ComposioHQ/awesome-claude-skills)
- [VoltAgent/awesome-agent-skills (GitHub)](https://github.com/VoltAgent/awesome-agent-skills)
- [一个程序员是如何借助 AI 智能体制作专业课程的（知乎）](https://zhuanlan.zhihu.com/p/82048836696)

**教材写作方法论**
- [Understanding by Design 白皮书 (ASCD PDF)](https://files.ascd.org/staticfiles/ascd/pdf/siteASCD/publications/UbD_WhitePaper0312.pdf)
- [Understanding by Design 全书 PDF](https://andymatuschak.org/files/papers/Wiggins,%2520McTighe%2520-%252005%2520-%2520Understanding%2520by%2520design.pdf)
- [Understanding by Design (Wikipedia)](https://en.wikipedia.org/wiki/Understanding_by_Design)
- [基于 UbD 理论的单元教学设计（汉斯出版社 PDF）](https://pdf.hanspub.org/ve2025144_371721700.pdf)
- [Bloom's taxonomy of cognitive learning objectives (Adams 2015, PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4511057/)
- [Bloom's Revised Taxonomy (Colorado College)](https://www.coloradocollege.edu/other/assessment/how-to-assess-learning/learning-outcomes/blooms-revised-taxonomy.html)
- [6 Scaffolding Strategies (Edutopia)](https://www.edutopia.org/blog/scaffolding-lessons-six-strategies-rebecca-alber)
- [Scaffolding Writing to Support Student Development (Miami OH)](https://miamioh.edu/howe-center/hwac/resources-for-teaching-writing/scaffolding-writing-for-learning.html)

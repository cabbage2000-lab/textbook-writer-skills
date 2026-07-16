# ADR 0008:标准 plugin 布局分发,四个 skill 整体安装

## 状态

已接受。

## 背景

skill 最初放在 `.claude/skills/` 下,只对本仓库的会话生效,无法分发给其他项目和其他人。Claude Code 的 plugin 机制提供了标准分发通道,但要求顶层 `skills/` 布局加 `.claude-plugin/` 清单。

同时,4 个 skill 之间存在跨 skill 引用(如各 SKILL.md 引用 `../textbook/references/handoff-contract.md`),这决定了它们不能被拆开分发——引用一断,契约单源([ADR 0003](0003-single-authoritative-handoff-contract.md))即失效。

## 决策

- skills 从 `.claude/skills/` 迁至顶层 `skills/`(标准 plugin 布局);`.claude-plugin/` 提供 `plugin.json` 与 `marketplace.json`,支持 `/plugin marketplace add` 直接安装;
- 4 个 skill 作为**一个 plugin 整体分发、整体安装**;跨 skill 一律以 `../<skill-name>/references/xxx.md` 相对路径互引,不得引入仓库外依赖;
- 本地开发用软链 `.claude/skills → ../skills`,改动即时生效(`.claude/` 已 gitignore,软链不入库);
- 清单一致性纳入结构校验:`plugin.json` 与 `marketplace.json` 的 name/version/description/license 必须一致,不一致 CI 拒绝;`.gitignore` 不得忽略 `.claude-plugin`(分发清单必须入库,曾因被忽略而静默丢失,见 CHANGELOG);
- 发版时双清单同步升版,版本语义:MAJOR = 契约或落盘格式不兼容变更,MINOR = 新增 skill/新能力,PATCH = 指令修正与文档修补。

## 后果

安装方式收敛为三种(plugin 安装 / 复制到个人 skills 目录 / 仓库内软链),统一由 README 记录;plugin 方式可随仓库更新,是推荐路径。

单独安装某一个子 skill 不受支持——跨 skill 引用会断,这是"整体组合"定位的直接推论;需要独立能力时应整体安装后单独触发对应 skill。清单双文件的版本漂移风险交给校验脚本兜底,发版流程见 [CONTRIBUTING.md](../../CONTRIBUTING.md)。

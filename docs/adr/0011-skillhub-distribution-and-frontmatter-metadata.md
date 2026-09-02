# ADR 0011:SkillHub 作为第四分发渠道,元数据写进 SKILL.md frontmatter

## 状态

已接受。

## 背景

前三个渠道(Claude Code / Codex / WorkBuddy)共用一套思路:元数据放在仓库根的 `.*-plugin/` 清单里,`skills/` 主体完全不受污染,整个仓库作为一个 plugin 整体安装([ADR 0008](0008-plugin-layout-and-distribution.md))。SkillHub([skillhub.cn](https://skillhub.cn))是国内的 skill 社区,想上架就得接受两个与上述思路冲突的前提:

1. **元数据只从 SKILL.md frontmatter 读**——`slug`、`version`、`displayName` 三个字段缺任何一个,`skillhub publish` 直接拒绝(CLI 源码 `skills_store_cli.py` 的必填校验)。而本仓库的结构校验只认 7 个白名单字段,写入 `slug` 会被判为"未知字段"而报错,第一道防线直接红;
2. **一次只发一个 skill 文件夹**,平台侧没有"整体安装"的概念。本仓库 5 个 skill 之间有 45 条 `../<skill-name>/references/xxx.md` 跨 skill 引用、构成全网状依赖,用户只装其中一两个必然读到不存在的路径——这正是 ADR 0008 判定"不可拆分"的同一个理由。

被否决的替代方案:

- **发布时临时注入,仓库 SKILL.md 保持干净**:另存一份元数据(如 `.skillhub-plugin/meta.json`),发布脚本把 `skills/` 复制到临时目录、注入字段后再 publish。哲学上更贴合"宿主专有信息隔离在清单目录",但发到平台上的文件就不再是仓库里那一份。skill 是"给模型看的程序",发布物与仓库逐字一致是排查线上行为的前提,多一层构建反而增加风险;何况这条路同样要改校验脚本(`MANIFEST_DIR_ALLOWED` 与 `.gitignore` 检查都得给第四个目录开口),省不下改动量;
- **只上架主 skill `textbook`**:以为发一个就没有断链问题。实际不成立——`textbook/SKILL.md` 自己就引 `../textbook-outline/references/bloom-levels.md`,单发它一样断。

## 决策

- frontmatter 白名单从"Claude Code 会读的字段"扩为**四宿主并集**:原 7 个之外加 `slug`、`displayName`、`summary`。这三个字段对其余三宿主无副作用(被静默忽略),白名单的原意是"防手误写入无效字段",而它们不是手误,是第四个渠道的必填项;
- 5 个 `skills/*/SKILL.md` 写入 `slug` / `displayName` / `version` / `summary`。其中 **`slug` 必须与目录名逐字相同**:CLI 安装落盘为 `<install_root>/<slug>/`(同级目录),只有 slug 与目录名一致,`../<skill-name>/references/` 才解析得到。5 个 slug 上架时经查询全部未被占用,不需要为唯一性加 handle 后缀;
- `version` 由新增的 `validate_skill_versions` 钉在 `.claude-plugin/plugin.json` 的 version 上,漏升任何一处即校验失败。SkillHub 从 SKILL.md 读版本号、其余三宿主从清单读,不锁住就会出现"清单升了、平台上还是旧版且无人报错";
- 5 份 `summary` 一律写明"需与其余 skill 同级安装"。平台既然不能保证整体安装,这句文案就是断链的唯一提示;**2026-09-02 后续实测推翻了这条的落点**——平台卡片与详情页展示的都是 `description` 而非 `summary`,写在 summary 里的警告用户看不到,故该句已同时写进 5 份 `description`(见"后果"末尾);
- 发布前一律先跑 `skillhub publish skills/<name> --dry-run`(不发 HTTP 请求、不需登录),校验 metadata 与打包。

2026-09-02 首次上架后做了端到端实测(CLI 2026.8.5),上面关于安装布局的判断由源码推断升级为实证:5 个 skill 装进同一个 `--dir` 后,18 条唯一跨 skill 引用**全部解析成功**;装回来的内容与仓库 `skills/` **逐字一致**(平台只多塞一个记录 slug/version/ownerId 的 `_meta.json`),"发布物与仓库一致"这条理由成立。同时测出两个文档没写的坑:

- **`skillhub install` 加了 `--namespace` 会多套一层 `@<handle>/` 目录**(落盘 `<dir>/@user_xxx/<slug>/`)。宿主只扫 `skills/*/SKILL.md` 这一层,多一层就一个都发现不了且无任何报错——与 README 早先记下的 WorkBuddy"别把 `skills/` 整体套进去"是同一类错误。装到宿主目录**一律不带 `--namespace`**;带命名空间那层里 5 个仍互为同级,跨 skill 引用照样通,坏的只是宿主发现;
- **重复安装会报 `Target exists`**,更新要加 `--force`,或用 `skillhub upgrade`。

只装其中 2 个时,`../textbook-chapter/references/chapter-template.md` 当场解析失败——断链不是理论风险,是实测可复现的默认结果。

上架后又暴露出一个上架前没人想到的问题:**搜"教材写作"只搜得到主 skill 一个**,其余 4 个连 top-100 都不进。直接探测搜索 API(`api.skillhub.cn/api/v1/search`,CLI 默认 `limit=20`)测清了机制:

- **参与召回的只有 `slug` 与 `displayName`**。`summary`、`description`、`tags` 一概不参与——只写在 summary 里的"四段式""UbD""独立习题""目录骨架"全部 0 命中,别人 tags 里的 `k12` 同样 0 命中(`tags` 确实在 publish 的 payload 里,但平台不拿它检索);
- **中文不分词,query 当作一个整串做子串匹配**:`教材 写作`(带空格)0 命中,`教材写作技能`(长于目标串)0 命中;
- **前缀匹配得分远高于中间子串**:`写作流水线` 命中 `教材写作流水线` 但 score 只有 0.038、排 #56,而 `教材写作` 作为前缀命中得 0.0486、排 #3;
- 排序 score 主要由下载量决定,**召回不足时平台用热门 skill 填充列表**——搜"教材写作"的 #1 是与教材毫无关系、下载 115 万的 `self-improving-agent`。本仓库 5 个 skill 下载量 2~4,在纯热度维度上没有任何胜算。

于是 4 个子 skill 的 `displayName` 统一改为「教材写作·」前缀(`教材大纲设计` → `教材写作·大纲设计`,单章正文 / 习题生成 / 项目初始化同理),主 skill 保持 `教材写作流水线`。按实测分数分布预测,5 个会落在 #3 与 #7–#10,默认一屏可见。这条决策的实质是:**`slug` 不可改,`summary` 不参与检索,`displayName` 就是唯一的检索杠杆**,所以它同时承担"人看的名字"与"被搜到的关键词"两个职责,不能只按前者取名。有两件做不到的一并记下,免得下次重试:热度填充项挤不掉;搜"教材"仍进不了前 20(只能靠真实使用量涨)。搜"写教材"也放弃了——要同时含"写教材"与"教材写作"两个连续串,名字会变得没法看。


## 后果

版本真相的副本从 5 处涨到 10 处。这是本决策最实在的代价,靠 `validate_skill_versions` 兜住;发版流程相应改口径,见 [CONTRIBUTING.md](../../CONTRIBUTING.md)。

ADR 0008 的"整体安装、不可拆分"在 SkillHub 上**无法由平台机制保证**,降级为 summary 里的一句文案提示。这是接受该渠道的已知代价,不是对 0008 的推翻——`../` 相对引用与契约单源([ADR 0003](0003-single-authoritative-handoff-contract.md))都照旧,只是多了一个平台侧无法强制的入口。若将来 SkillHub 支持多 skill 打包上架,应回头把 5 次发布收敛为一次。

新增 skill 时除"目录名即 slug"外,还要遵守 **`displayName` 以「教材写作」开头、四字连续不被分隔符打断**(用 `·`);这条校验脚本守不住,只能靠 CLAUDE.md 与本 ADR 记着。

**`slug` 一经发布不再改动**:它全网唯一,又同时是用户机器上的安装目录名。改 slug 会让所有已安装用户的跨 skill 引用当场断链,且旧 slug 未必能释放。新增 skill 时沿用"目录名即 slug"的规则,不加前后缀。

发布本身依赖两个只能由人在浏览器完成的前置动作(实名认证、创建 API Token),无法纳入 CI 自动化;跨宿主中立的设计约束不受影响——SkillHub 上架是增量渠道,`skills/` 主体在任何宿主照常按 SKILL.md 装载。

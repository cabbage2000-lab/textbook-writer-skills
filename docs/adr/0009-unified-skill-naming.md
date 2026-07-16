# ADR 0009:skill 命名统一为 textbook- 名词族

## 状态

已接受。

## 背景

v0.1.0 的 4 个 skill 名开头各异(write-textbook / design-textbook-outline / write-textbook-chapter / generate-textbook-exercises):动词取自各自职责,单看每个名字都成立,但放进 `/` 补全列表与 skill 清单时散落三处,使用者看不出它们是同一组合的成员,更看不出谁是入口、谁是环节。

考虑过的替代方案:

- **write-textbook-\* 家族**(write-textbook / write-textbook-outline / write-textbook-chapter / write-textbook-exercises):改动面最小(仅 2 个目录改名),动宾式符合 skill 命名惯例;代价是名字更长,且 outline 的 design、exercises 的 generate 语义同样丢失。
- **textbook-writer-\* 品牌族**:与 plugin 名完全对齐;代价是名字最长(最长 25 字符),日常输入与文内引用累赘。

## 决策

统一为 textbook- 名词族,主 skill 名即公共前缀:

| 旧名 | 新名 |
| ---- | ---- |
| write-textbook | textbook |
| design-textbook-outline | textbook-outline |
| write-textbook-chapter | textbook-chapter |
| generate-textbook-exercises | textbook-exercises |

plugin 名 textbook-writer、marketplace 名 textbook-writer-skills 不改:plugin 是分发单元(名字说明"这是干什么的"),skill 是使用单元(名字为补全聚族与主从辨识服务),两层各司其职。

name 失去动作语义的代价由 description 承担——description 本就承担全部触发职责(含中文触发词),name 只是标识符。

历史 ADR(0001/0003/0005/0006/0008)中的旧名一并替换:本仓库 ADR 定位为"改动某项机制前先读"的活参考,"不改写历史"的惯例针对决策被推翻的场景,而本次是符号更名、不推翻任何决策;新旧对照以本篇为准。

## 后果

- 输入 `/textbook` 时 4 个 skill 聚在一起,主从关系内嵌在名字里(textbook-X 是 textbook 的一个环节);
- 对已安装 v0.1.x 的用户是入口变化:旧名不再存在,无 alias 机制,升级后按新名触发;版本升至 0.2.0(契约字段与 `.progress.json`、落盘格式均不变,不触发 MAJOR 语义);
- 入库文件中旧名全量替换,唯二例外:CHANGELOG 的 [0.1.0] 历史段(发布时事实)与本篇对照表;README 嵌入截图中的旧名不重制,文字以新名为准;
- 未来新增子 skill 必须延续 textbook- 前缀,动作语义写进 description 而非 name。

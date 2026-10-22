# context-compaction for Step Code — 上下文自动压缩插件

**简体中文** · [English](README.en.md)

## 简介

为 **Step Code**（阶跃星辰终端 AI Agent）定制的上下文自动压缩插件：长会话按需产出结构化上下文快照 + 机械压缩素材，新会话一句话无损续接。仓库名 `step-code-context-compaction`，插件名 `context-compaction`，插件市场名 `compaction-marketplace`；工程结构参照 [stepfun-usage-monitor](https://github.com/Neriah-Ado/stepfun-usage-monitor)（ZCode 插件）的插件化方案，适配 Step Code 插件机制。

- **自动触发** —— 上下文接近当前 StepFun 模型窗口 70%、工具输出堆积、超限告警，或 `/goal`、`/cron` 长任务进入无人值守阶段前；技能元数据每轮注入，由模型自主判断触发。
- **手动触发** —— `/compact` 斜杠命令，可选参数指定压缩侧重。
- **五步流程** —— 盘点 → 机械降噪（脚本剥离工具输出）→ 语义快照 → 告知恢复方式 → 新会话续接。
- **结构化上下文快照** —— 任务目标 / 当前状态 / 关键决策与约束 / 文件与命令 / 下一步 / 风险，目标 ≤2KB，再次压缩增量合并。
- **纯声明式** —— 仅 skills + commands，无 MCP 进程、无外部依赖（脚本仅用 Python 标准库）。
- **双市场兼容** —— 同时提供 `.step-plugin` 与 `.claude-plugin` 市场清单。

## 工作原理

1. **盘点** —— 统计当前会话的用户消息数、工具调用次数、最大工具输出与已修改/新建文件。
2. **机械压缩** —— 脚本剥离工具噪声，产出 `<项目>/.stepcode/snapshot-material.md`。
3. **语义压缩** —— 模型按模板生成 `<项目>/.stepcode/context-snapshot.md`，目标 ≤2KB；旧快照增量合并，不覆盖「关键决策」条目。
4. **交付告知** —— 汇报快照路径、压缩前后规模对比与新会话恢复方式。
5. **重启续接** —— 新会话读取快照继续，无需重读历史会话。

触发条件、快照模板与能力边界见 [SKILL.md](plugins/context-compaction/skills/context-compaction/SKILL.md)。

## 安装

**方式一 · 市场添加（推荐）**

本仓库同时是 Step Code 插件市场（`compaction-marketplace`）：

```text
/plugin marketplace add Neriah-Ado/step-code-context-compaction
/plugin install context-compaction@compaction-marketplace
```

安装后重开会话生效。

**方式二 · 手动安装**

克隆本仓库，将 `plugins/context-compaction/` 整个目录复制到：

- 用户级：`~/.stepcode/plugins/context-compaction/`
- 项目级：`<项目>/.stepcode/plugins/context-compaction/`（优先级更高）

重启 `step` 生效，`/plugin list` 确认。

## 使用

- 自动：满足[触发条件](#触发条件)时由模型自主执行压缩。
- 手动：输入 `/compact` 或 `/compact 重点是待办事项`。

```text
/compact
/compact 重点是待办事项
```

执行后输出快照路径、压缩前后规模对比与新会话恢复方式。

## 触发条件

满足任一即触发：

1. 上下文用量达到当前 StepFun 模型窗口的 70%——Step Code 由 `/model` 选择的 StepFun 模型运行，各模型窗口见 [references/model-context-limits.md](plugins/context-compaction/skills/context-compaction/references/model-context-limits.md)，未确认模型按保守规则（默认 16K 窗口）处理。
2. 工具输出在近期轮次中大量堆积（连续读取大文件、长日志、多次失败重试）。
3. 用户明确要求压缩上下文 / 压缩会话 / 保存进度 / 交接新会话，或输入 `/compact`。
4. 运行时出现上下文超限或截断告警。
5. `/goal`、`/cron` 长任务进入无人值守阶段前，主动做一次预防性压缩。

## 恢复方式

1. 新会话输入「读取 .stepcode/context-snapshot.md 继续工作」。
2. 建议在项目 `AGENTS.md` 加一句「会话开始时若存在 .stepcode/context-snapshot.md，先读取再工作」，实现全自动续接。
3. 再次触发压缩时，旧快照与新进展合并，保持快照始终为最新单文件事实源。

## 数据路径

| 内容 | 位置 | 说明 |
|---|---|---|
| 上下文快照 | `<项目>/.stepcode/context-snapshot.md` | 插件写入，单文件事实源 |
| 机械压缩素材 | `<项目>/.stepcode/snapshot-material.md` | 脚本产物，可删 |
| 会话记录 | `~/.stepcode/`（客户端管理） | 脚本只读，格式未文档化已做容错 |

## 与通用版 context-compaction-skill 的关系

本插件是通用版 [context-compaction-skill](https://github.com/Neriah-Ado/context-compaction-skill) 的 Step Code 专向适配版，二者共享同一套五步流程、快照模板与机械压缩脚本设计，差异集中在运行环境与数据路径：

| 维度 | 本插件（Step Code 专向） | 通用版 context-compaction-skill |
|---|---|---|
| 目标 Agent | Step Code（阶跃星辰终端 AI Agent） | 任意编码 Agent（ZCode、Claude Code、Codex、Step Code 等） |
| 快照路径 | `<项目>/.stepcode/context-snapshot.md` | `<项目>/.agent/context-snapshot.md`，可按项目约定改名 |
| 触发入口 | 技能元数据自动触发 + `/compact` 斜杠命令 | 技能自动触发，无斜杠命令 |
| 模型窗口表 | StepFun 全系，2026-09 核实 | 同一张表 + 其他模型的扩展方法 |
| 清单兼容 | `.step-plugin` / `.claude-plugin` 双市场 | 直接拷入 Agent 用户级技能目录 |

维护约定：通用流程、快照模板与阈值表以通用版为单一事实源，本仓库只维护 Step Code 专有差异（快照路径、`/compact` 命令、插件清单、能力边界），不在本仓库重复整份通用文档。

## 兼容性

插件清单同时提供 `.claude-plugin` 兼容：Claude Code 用户可将 `plugins/context-compaction/` 拷入 `~/.claude/skills/` 使用（快照路径建议自行改为 `.claude/`）。

## 开发与测试

```bash
python tests/validate_plugin.py    # 清单/市场/SKILL 合规校验
python plugins/context-compaction/skills/context-compaction/scripts/compress_session.py tests/fixture.jsonl --out /tmp/out.md
```

## 版本

版本记录见 [CHANGELOG.md](CHANGELOG.md)。

## 许可证

[AGPL-3.0-only](./LICENSE)

历史 MIT 文本与版权声明保留在 [LICENSE-MIT](./LICENSE-MIT)。

© 2026 Neriah

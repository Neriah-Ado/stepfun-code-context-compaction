# context-compaction for Step Code

为 **Step Code**（阶跃星辰终端 AI Agent）定制的上下文自动压缩插件：长会话自动产出结构化快照 + 机械压缩素材，新会话一句话无损续接。工程结构参照 [stepfun-usage-monitor](https://github.com/Neriah-Ado/stepfun-usage-monitor)（ZCode 插件）的插件化方案，适配 Step Code 插件机制。

## 特性

- **自动触发**：上下文接近当前 StepFun 模型窗口 70%、工具输出堆积、超限告警，或 `/goal` `/cron` 长任务进入无人值守前——技能元数据每轮注入，模型自主判断触发
- **手动触发**：`/compact` 斜杠命令，可选参数指定压缩侧重
- **五步流程**：盘点 → 机械降噪（脚本剥离工具输出）→ 语义快照 `.stepcode/context-snapshot.md` → 告知恢复方式 → 新会话续接
- **快照模板**：任务目标 / 当前状态 / 关键决策与约束 / 文件与命令 / 下一步 / 风险，目标 ≤2KB，再次压缩增量合并
- **纯声明式**：skills + commands，无 MCP 进程、无外部依赖（脚本仅用 Python 标准库）

## 安装

**方式一 · 市场添加（推荐）**

本仓库同时是 Step Code 插件市场（`compaction-marketplace`）：

```
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

- 自动：满足触发条件时模型自动执行压缩（触发条件见 SKILL.md）
- 手动：输入 `/compact` 或 `/compact 重点是待办事项`
- 恢复：新会话输入"读取 .stepcode/context-snapshot.md 继续工作"；建议在项目 `AGENTS.md` 加一句"会话开始时若存在 .stepcode/context-snapshot.md，先读取再工作"实现全自动续接

## 数据路径

| 内容 | 位置 | 说明 |
|---|---|---|
| 快照 | `<项目>/.stepcode/context-snapshot.md` | 插件写入，单文件事实源 |
| 机械压缩素材 | `<项目>/.stepcode/snapshot-material.md` | 脚本产物，可删 |
| 会话记录 | `~/.stepcode/`（客户端管理） | 脚本只读，格式未文档化已做容错 |
| 模型窗口阈值表 | `skills/context-compaction/references/model-context-limits.md` | StepFun 全系已核实，2026-09 |

## 兼容性

插件清单同时提供 `.claude-plugin` 兼容：Claude Code 用户可将 `plugins/context-compaction/` 拷入 `~/.claude/skills/` 使用（快照路径建议自行改为 `.claude/`）。通用版（全 Agent 适配）见 [context-compaction-skill](https://github.com/Neriah-Ado/context-compaction-skill)。

## 开发与测试

```bash
python tests/validate_plugin.py    # 清单/市场/SKILL 合规校验
python plugins/context-compaction/skills/context-compaction/scripts/compress_session.py tests/fixture.jsonl --out /tmp/out.md
```

## 版本

见 [CHANGELOG.md](CHANGELOG.md)。当前 **v1.0.0**。

## License

MIT

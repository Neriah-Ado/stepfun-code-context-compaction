---
name: context-compaction
description: "Auto-trigger in Step Code sessions when context usage nears 70% of the current StepFun model window, tool outputs pile up, the user asks to 压缩上下文/压缩会话/保存进度, or a context-limit warning appears. Produces a structured .stepcode/context-snapshot.md plus a mechanically compacted transcript so work continues in a fresh session without losing goals, decisions, or file state. Also available as the /compact command."
when_to_use: "Step Code 长会话上下文接近当前 StepFun 模型窗口上限、工具输出大量堆积、用户要求压缩上下文/保存进度/交接新会话、出现上下文超限告警，或 /goal、/cron 长任务进入无人值守阶段前需要交接现场时"
license: MIT
---

# Step Code 上下文自动压缩（Context Compaction）

本技能为 **Step Code**（阶跃星辰终端 AI Agent）定制的上下文压缩能力：长会话中按需产出**可续接的结构化快照** + **机械压缩的对话素材**，新会话一句话无损恢复工作现场。

## 1. 触发时机（满足任一即执行本技能）

1. 上下文用量达到当前模型窗口的 **70%**——Step Code 由 `/model` 选择的 StepFun 模型运行，各模型窗口与触发线见 `references/model-context-limits.md`；未确认模型时按保守规则（默认 16K 窗口）处理。
2. 工具输出在近期轮次中大量堆积（连续读取大文件、长日志、多次失败重试）。
3. 用户明确要求：压缩上下文 / 压缩会话 / 保存进度 / 交接新会话，或直接输入 `/compact` 命令。
4. 运行时出现上下文超限或截断告警。
5. `/goal`、`/cron` 长任务进入无人值守阶段前，主动做一次预防性压缩。

## 2. 压缩流程（严格按序执行）

### Step 1 盘点
统计当前会话的构成：用户消息数、工具调用次数、最大的几段工具输出、已修改/新建的文件清单。

### Step 2 机械压缩（脚本，先跑）
用随附脚本剥离工具噪声，得到压缩素材：

```bash
python scripts/compress_session.py <会话记录文件> --out .stepcode/snapshot-material.md
```

- 输入支持 JSONL（每行一个 `{role, content}` 消息对象）或纯文本/Markdown 转写。
- Step Code 会话记录保存在 `~/.stepcode/` 下（格式未正式文档化）；能定位到当前会话文件就喂给脚本，定位不到则**跳过本步**，直接进入 Step 3（凭当前上下文做语义压缩）。
- 脚本只做机械降噪：保留用户消息（截断 8000 字符）与 assistant 要点，工具输出压成单行摘要。

### Step 3 语义压缩（快照，核心产出）
基于当前上下文与 Step 2 素材，按 §3 模板生成快照，写入项目资源目录 **`.stepcode/context-snapshot.md`**（Step Code 项目级资源的标准位置）。已存在旧快照时先读取并合并增量，不覆盖历史"关键决策"条目。

### Step 4 交付告知
向用户汇报：快照路径、压缩前后规模对比（估算 token）、新会话恢复方式（§4）。

### Step 5 重启续接
提示用户开启新会话，新会话首轮仅需说"读取 .stepcode/context-snapshot.md 继续工作"。

## 3. 快照模板（写入 .stepcode/context-snapshot.md，目标 ≤2KB）

```markdown
# 上下文快照 <YYYY-MM-DD HH:MM> <模型名（/model 当前值）>
## 任务目标
<一段话：最终要交付什么，验收标准是什么>
## 当前状态
- [x] 已完成：<条目 + 关键产出路径>
- [ ] 进行中：<条目 + 卡点>
- [ ] 待办：<条目>
## 关键决策与约束
- <决策/约定/用户偏好，逐条列出，含原因一句话>
## 文件与命令
- 重要文件：<路径 → 一句话说明>
- 常用命令：<构建/测试/运行命令>
## 下一步
<立即要做的 1-3 件事，按顺序>
## 风险与未决
<未解决的问题、待验证的假设>
```

**红线**：快照必须保留"关键决策与约束"的全部条目——这是新会话最易丢失、代价最高的信息；工具输出只保留结论，不保留原文。

## 4. 新会话恢复方式

1. 读取 `.stepcode/context-snapshot.md`。
2. 按快照"下一步"继续，不需要重读历史会话。
3. 再次触发压缩时，旧快照与新进展合并（见 Step 3），保持快照始终为最新单文件事实源。
4. 快照可配合 `AGENTS.md` 使用：在项目指引中加一句"会话开始时若存在 .stepcode/context-snapshot.md，先读取再工作"，实现全自动续接。

## 5. Step Code 能力边界（本技能的适配说明）

- Step Code 插件**无 hooks、无可执行 entry**（清单字段仅记录不加载），因此自动触发完全依赖技能元数据的每轮注入与模型自主判断——description 中的触发条件写得越具体，触发越可靠。
- 本插件为纯声明式（skills + commands），不注册 MCP Server，安装即用、零外部进程。
- 更新插件后需重启 `step` 会话生效。

## 6. 注意事项

- 各模型窗口与触发阈值**必须**先查 `references/model-context-limits.md`，不要凭记忆假设。
- 机械压缩脚本只做降噪，**语义压缩（快照）永远由模型完成**，二者不可互相替代。
- 压缩操作本身要省 token：不回读完整历史，优先用脚本产物；快照写入失败时退化为直接在回复中输出快照内容让用户保存。
- 本技能只读 `~/.stepcode/`（或不碰），快照一律写在项目内，不修改客户端数据目录。

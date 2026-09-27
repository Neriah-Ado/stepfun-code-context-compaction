---
description: 手动触发上下文压缩：盘点会话 → 机械降噪 → 生成 .stepcode/context-snapshot.md 快照 → 告知恢复方式。可选参数作为压缩重点说明。
---

按 context-compaction 技能的完整流程，对当前会话执行一次上下文压缩。

执行要求：

1. 严格遵循技能 SKILL.md 的五步流程：盘点 → 机械压缩（脚本）→ 语义快照 → 交付告知 → 重启续接提示。
2. 快照写入 `.stepcode/context-snapshot.md`；已存在旧快照时增量合并，保留全部"关键决策与约束"条目。
3. 可选参数（如有）指定本次压缩的侧重点：$ARGUMENTS
4. 最后输出：快照路径、压缩前后规模对比（估算 token）、新会话恢复方式（"读取 .stepcode/context-snapshot.md 继续工作"）。

约束：机械脚本只降噪，语义压缩由你完成；工具输出只留结论；全程省 token，不回读完整历史。

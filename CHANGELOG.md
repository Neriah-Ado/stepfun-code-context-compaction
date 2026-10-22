# Changelog

本文件记录 step-code-context-compaction 插件的所有版本变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-09-27

### 新增

- **Step Code 专向适配版**（源自通用版 [context-compaction-skill](https://github.com/Neriah-Ado/context-compaction-skill) v1.0.1，工程结构参照 stepfun-usage-monitor 的 ZCode 插件方案）
- 插件化布局：`step.plugin.json` 清单（skills/commands 声明，依据 Step Code 插件加载器源码规则）+ `.step-plugin/marketplace.json`（本仓库即市场 `compaction-marketplace`）+ `.claude-plugin/marketplace.json` 双市场兼容
- 快照路径适配 Step Code 项目资源目录：`.stepcode/context-snapshot.md`
- 新增 `/compact` 斜杠命令（手动触发压缩，可选参数指定侧重）
- SKILL.md 新增 Step Code 能力边界说明：无 hooks / entry 仅记录不加载，自动触发依赖技能元数据每轮注入
- StepFun 模型窗口阈值表（step-2-16k 至 Step 3.7 Flash，2026-09 核实）+ 未列出模型保守规则
- 机械压缩脚本 `compress_session.py`（JSONL/纯文本双格式，标准库零依赖）
- 合规校验脚本 `tests/validate_plugin.py`（清单 schema / 双市场一致 / SKILL 规则 / 专有引用残留检查）

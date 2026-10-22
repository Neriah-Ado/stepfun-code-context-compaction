# context-compaction for Step Code — Context Auto-Compaction Plugin

[简体中文](README.md) · **English**

## Overview

A context auto-compaction plugin built for **Step Code** (StepFun's terminal AI agent): long sessions produce a structured context snapshot plus mechanically compacted material, so a fresh session can resume with one sentence. Repository `step-code-context-compaction`, plugin `context-compaction`, marketplace `compaction-marketplace`. The plugin layout follows the [stepfun-usage-monitor](https://github.com/Neriah-Ado/stepfun-usage-monitor) (ZCode plugin) approach and is adapted to the Step Code plugin mechanism.

- **Automatic triggering** —— when context nears 70% of the current StepFun model window, tool outputs pile up, a context-limit warning appears, or a `/goal` / `/cron` run is about to go unattended; skill metadata is injected every turn and the model decides when to trigger.
- **Manual triggering** —— the `/compact` slash command, with an optional focus argument.
- **Five-step flow** —— inventory → mechanical noise reduction (script strips tool outputs) → semantic snapshot → report the recovery method → resume in a fresh session.
- **Structured context snapshot** —— goals / current status / key decisions and constraints / files and commands / next steps / risks, ≤2KB target, merged incrementally on re-compaction.
- **Purely declarative** —— skills + commands only, no MCP process, no external dependencies (the script uses only the Python standard library).
- **Dual-marketplace compatible** —— ships both `.step-plugin` and `.claude-plugin` marketplace manifests.

## How it works

1. **Inventory** —— count user messages, tool calls, the largest tool outputs and the list of modified/created files in the current session.
2. **Mechanical compaction** —— the script strips tool noise and writes `<project>/.stepcode/snapshot-material.md`.
3. **Semantic compaction** —— the model generates `<project>/.stepcode/context-snapshot.md` from the template, ≤2KB target; an existing snapshot is merged incrementally and existing key-decision entries are kept.
4. **Report** —— report the snapshot path, the before/after size comparison and the recovery method.
5. **Restart and resume** —— the new session reads the snapshot and continues without rereading the old transcript.

See [SKILL.md](plugins/context-compaction/skills/context-compaction/SKILL.md) for trigger conditions, the snapshot template and capability boundaries.

## Install

**Option 1 · Add the marketplace (recommended)**

This repo is also a Step Code plugin marketplace (`compaction-marketplace`):

```text
/plugin marketplace add Neriah-Ado/step-code-context-compaction
/plugin install context-compaction@compaction-marketplace
```

Reopen the session for the install to take effect.

**Option 2 · Manual install**

Clone the repo and copy the whole `plugins/context-compaction/` directory to:

- User level: `~/.stepcode/plugins/context-compaction/`
- Project level: `<project>/.stepcode/plugins/context-compaction/` (higher priority)

Restart `step` and confirm with `/plugin list`.

## Usage

- Automatic: when the [trigger conditions](#trigger-conditions) are met, the model runs compaction on its own.
- Manual: enter `/compact` or `/compact focus on the to-do list`.

```text
/compact
/compact focus on the to-do list
```

The output reports the snapshot path, the before/after size comparison and the recovery method for a fresh session.

## Trigger conditions

Any one of the following triggers compaction:

1. Context usage reaches 70% of the current StepFun model window — Step Code runs on the StepFun model selected via `/model`; per-model windows are listed in [references/model-context-limits.md](plugins/context-compaction/skills/context-compaction/references/model-context-limits.md). When the model is unconfirmed, apply the conservative rule (assume a 16K window).
2. Tool outputs pile up over recent turns (repeated large file reads, long logs, multiple failed retries).
3. The user explicitly asks to compact context / compact the session / save progress / hand off to a new session, or enters `/compact`.
4. A context-limit or truncation warning appears at runtime.
5. Before a `/goal` or `/cron` long run enters an unattended phase, proactively run a preventive compaction.

## Recovery

1. In the new session, enter "read .stepcode/context-snapshot.md and continue".
2. Recommended: add "if .stepcode/context-snapshot.md exists at session start, read it before working" to the project `AGENTS.md` for fully automatic resumption.
3. On the next compaction, merge the old snapshot with new progress so the snapshot stays the single latest source of truth.

## Data paths

| Content | Location | Notes |
|---|---|---|
| Context snapshot | `<project>/.stepcode/context-snapshot.md` | Written by the plugin; single source of truth |
| Mechanical compaction material | `<project>/.stepcode/snapshot-material.md` | Script output, safe to delete |
| Session transcript | `~/.stepcode/` (client-managed) | Read-only for the script; format is undocumented, parsing is fault-tolerant |

## Relationship to context-compaction-skill

This plugin is the Step Code-specific adaptation of the general-purpose [context-compaction-skill](https://github.com/Neriah-Ado/context-compaction-skill). Both share the same five-step flow, snapshot template and mechanical compaction script design; differences are confined to the runtime environment and data paths:

| Dimension | This plugin (Step Code specific) | General context-compaction-skill |
|---|---|---|
| Target agent | Step Code (StepFun's terminal AI agent) | Any coding agent (ZCode, Claude Code, Codex, Step Code, etc.) |
| Snapshot path | `<project>/.stepcode/context-snapshot.md` | `<project>/.agent/context-snapshot.md`, renameable per project convention |
| Trigger entry | Skill metadata automatic trigger + `/compact` slash command | Skill automatic trigger, no slash command |
| Model window table | StepFun family, verified 2026-09 | Same table + extension method for other models |
| Manifest compatibility | `.step-plugin` / `.claude-plugin` dual marketplace | Copy directly into the agent's user-level skills directory |

Maintenance convention: the general-purpose repo is the single source of truth for the shared flow, snapshot template and threshold table. This repo maintains only the Step Code-specific differences (snapshot path, `/compact` command, plugin manifests, capability boundaries) and does not duplicate the full general-purpose documentation.

## Compatibility

The plugin manifests also provide `.claude-plugin` compatibility: Claude Code users can copy `plugins/context-compaction/` into `~/.claude/skills/` (change the snapshot path to `.claude/` as needed).

## Development and testing

```bash
python tests/validate_plugin.py    # manifest/marketplace/SKILL compliance checks
python plugins/context-compaction/skills/context-compaction/scripts/compress_session.py tests/fixture.jsonl --out /tmp/out.md
```

## Version

See [CHANGELOG.md](CHANGELOG.md).

## License

[AGPL-3.0-only](./LICENSE)

The prior MIT text and copyright notice are retained in [LICENSE-MIT](./LICENSE-MIT).

© 2026 Neriah

# context-compaction for Step Code

Context auto-compaction plugin for **Step Code** (StepFun's terminal AI agent): long sessions automatically produce a structured snapshot plus mechanically compacted material, so a fresh session can resume with one sentence.

## Install

This repo is also a Step Code plugin marketplace (`compaction-marketplace`):

```
/plugin marketplace add Neriah-Ado/step-code-context-compaction
/plugin install context-compaction@compaction-marketplace
```

Or copy `plugins/context-compaction/` to `~/.stepcode/plugins/` (user level) or `<project>/.stepcode/plugins/` (project level) and restart `step`.

## Usage

- **Auto**: triggers when context nears 70% of the model window, tool outputs pile up, or before unattended `/goal` / `/cron` runs
- **Manual**: `/compact [focus]`
- **Resume**: in a new session, say "read .stepcode/context-snapshot.md and continue"

Snapshot template covers goals / status / key decisions / files & commands / next steps / risks (≤2KB target, merged incrementally).

## License

MIT — see [CHANGELOG.md](CHANGELOG.md) for versions.

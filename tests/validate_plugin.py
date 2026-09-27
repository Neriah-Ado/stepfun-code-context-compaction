"""step-code-context-compaction 插件合规校验

依据 Step Code 插件机制（源码级规则）+ ZCode SKILL.md 规则：
- step.plugin.json: id 安全名 / skills、commands 为包内相对路径数组 / version 字符串
- .step-plugin/marketplace.json: name/description/plugins[].source 指向存在的目录
- .claude-plugin/marketplace.json 与 .step-plugin 版本一致（双市场兼容）
- SKILL.md: frontmatter name/description 必填、description ≤1024、正文 <100KB、目录名=技能名
- 无专有引用残留（.zcode/.agent 路径、旧技能名）
"""
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
errors = []
ok = []

# 1. step.plugin.json
manifest_path = root / "plugins" / "context-compaction" / "step.plugin.json"
try:
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
except (json.JSONDecodeError, FileNotFoundError) as e:
    errors.append(f"step.plugin.json 无法解析: {e}")
    m = None
if m:
    pid = m.get("id", "")
    if not re.match(r"^[a-z0-9][a-z0-9._-]*$", pid):
        errors.append(f"id 不符合安全名规则: {pid}")
    else:
        ok.append(f"id={pid}")
    if m.get("name") and m.get("description"):
        ok.append("name/description OK")
    else:
        errors.append("缺少 name 或 description")
    if not re.match(r"^\d+\.\d+\.\d+$", str(m.get("version", ""))):
        errors.append(f"version 非语义化: {m.get('version')}")
    else:
        ok.append(f"version={m['version']}")
    for key in ("skills", "commands"):
        v = m.get(key)
        if not isinstance(v, list) or not v:
            errors.append(f"{key} 应为非空数组")
            continue
        for p in v:
            if p.startswith("/") or ".." in p:
                errors.append(f"{key} 路径必须为包内相对路径: {p}")
            elif not (manifest_path.parent / p).is_dir():
                errors.append(f"{key} 路径不存在: {p}")
        else:
            ok.append(f"{key}={v}")

# 2. marketplace（双清单一致）
for rel in (".step-plugin/marketplace.json", ".claude-plugin/marketplace.json"):
    p = root / rel
    if not p.is_file():
        errors.append(f"缺少 {rel}")
try:
    mk = json.loads((root / ".step-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    mkc = json.loads((root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    if mk != mkc:
        errors.append("两个 marketplace.json 内容不一致")
    else:
        ok.append(f"marketplace={mk['name']}, 双清单一致")
    for entry in mk.get("plugins", []):
        src = root / entry["source"]
        if not src.is_dir():
            errors.append(f"marketplace source 不存在: {entry['source']}")
        elif not list(src.glob("step.plugin.json")) and not list(src.glob(".claude-plugin/plugin.json")):
            errors.append(f"source 目录缺插件清单: {entry['source']}")
except FileNotFoundError as e:
    errors.append(f"marketplace 文件缺失: {e}")
except json.JSONDecodeError as e:
    errors.append(f"marketplace JSON 无效: {e}")

# 3. SKILL.md
skill_md = root / "plugins" / "context-compaction" / "skills" / "context-compaction" / "SKILL.md"
text = skill_md.read_text(encoding="utf-8")
mm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not mm:
    errors.append("SKILL.md frontmatter 缺失")
else:
    fm = mm.group(1)
    name = re.search(r"^name:\s*(\S+)", fm, re.M)
    desc = re.search(r'^description:\s*"?(.+?)"?\s*$', fm, re.M)
    if not name:
        errors.append("SKILL.md name 缺失")
    if not desc:
        errors.append("SKILL.md description 缺失")
    elif len(desc.group(1)) > 1024:
        errors.append(f"description 超限: {len(desc.group(1))} > 1024")
    else:
        ok.append(f"description {len(desc.group(1))}/1024")
    if name and skill_md.parent.name != name.group(1):
        errors.append(f"技能目录名 {skill_md.parent.name} != name {name.group(1)}")
    body_kb = len(text[mm.end():].encode("utf-8")) / 1024
    if body_kb >= 100:
        errors.append("SKILL.md 正文超 100KB")
    else:
        ok.append(f"正文 {body_kb:.1f}KB")
    for legacy in (".zcode/context-snapshot", ".agent/context-snapshot", "stepfun-context-compaction"):
        if legacy in text:
            errors.append(f"SKILL.md 残留专有引用: {legacy}")
    for rel in ("references/model-context-limits.md", "scripts/compress_session.py"):
        if not (skill_md.parent / rel).is_file():
            errors.append(f"技能缺少附随文件 {rel}")

# 4. commands
if not (root / "plugins" / "context-compaction" / "commands" / "compact.md").is_file():
    errors.append("缺少 commands/compact.md")
else:
    ok.append("commands/compact.md OK")

print("PASS: " + "; ".join(ok)) if ok else None
if errors:
    print("FAIL:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("PLUGIN COMPLIANT")

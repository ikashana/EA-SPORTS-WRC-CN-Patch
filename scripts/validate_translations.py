import json
import os
import re
import sys
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "translations", "chunks_src")
ZH_DIR = os.path.join(BASE_DIR, "translations", "chunks_zh")

TAG_RE = re.compile(r"\{[^}]*\}|<[^>]*>")

def validate_chunk(fname):
    src_p = os.path.join(SRC_DIR, fname)
    zh_p = os.path.join(ZH_DIR, fname)
    if not os.path.exists(zh_p):
        return [f"{fname}: MISSING translated file"]
    with open(src_p, "r", encoding="utf-8") as f:
        src_items = json.load(f)
    try:
        with open(zh_p, "r", encoding="utf-8") as f:
            zh_map = json.load(f)
    except Exception as e:
        return [f"{fname}: INVALID JSON: {e}"]

    errors = []
    if not isinstance(zh_map, dict):
        return [f"{fname}: root must be JSON object {{id: zh_text}}"]

    for item in src_items:
        sid = item["id"]
        en = item["en"]
        if sid not in zh_map:
            errors.append(f"{fname} id={sid} ({item['k']}): missing")
            continue
        zh = zh_map[sid]
        if not isinstance(zh, str) or not zh.strip():
            errors.append(f"{fname} id={sid} ({item['k']}): empty translation")
            continue
        src_tags = Counter(TAG_RE.findall(en))
        zh_tags = Counter(TAG_RE.findall(zh))
        if src_tags != zh_tags:
            errors.append(f"{fname} id={sid} ({item['k']}): tag mismatch src={dict(src_tags)} zh={dict(zh_tags)}")
    return errors

def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else sorted(f for f in os.listdir(SRC_DIR) if f.endswith(".json"))
    total_err = 0
    for fn in targets:
        errs = validate_chunk(fn)
        if errs:
            print(f"[FAIL] {fn}: {len(errs)} issues")
            for e in errs[:10]:
                print("  ", e)
            total_err += len(errs)
        else:
            print(f"[OK]   {fn}")
    sys.exit(1 if total_err else 0)

if __name__ == "__main__":
    main()

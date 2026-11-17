import argparse
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TOOLS_DIR = os.path.join(BASE_DIR, "tools")
CHUNKS_DIR = os.path.join(BASE_DIR, "translations", "chunks_src")

SKIP_EXACT_PREFIXES = (
    "lng_credits_name_",
    "lng_credits_role_",
    "lng_credits_title_",
    "lng_identity_name_",
    "lng_driver_surname_",
    "lng_driver_forename_",
    "lng_vehicle_model_name_",
    "lng_route_name_",
    "lng_ea_eula_body",
    "lng_ea_privacy_policy",
)

def load_loc(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if "=" in line:
                k, v = line.split("=", 1)
                items.append((k, v))
    return items

def bucket_of(ks):
    if ks.startswith("lng_br_mp_"):
        return 2
    if ks.startswith("lng_ce_"):
        return 3
    if ks.startswith(("lng_vehicle_", "lng_mechanical_", "lng_mech_", "lng_exterior_", "lng_interior_", "lng_livery_")):
        return 4
    if ks.startswith(("lng_location_", "lng_weather_", "lng_track_", "lng_stage_", "lng_rally_")):
        return 5
    if ks.startswith(("h_scenario_", "lng_scenario_", "lng_moments_")):
        return 6
    if ks.startswith(("lng_cd_", "lng_rally_school")):
        return 7
    if ks.startswith(("lng_input_", "lng_action_", "lng_key_", "lng_controller_")):
        return 8
    if ks.startswith(("lng_competition_", "lng_championship_", "lng_event_", "lng_team_", "lng_unlockable_")):
        return 9
    return 1  # Core UI, menus, settings, tuning, HUD, general

def main():
    parser = argparse.ArgumentParser(description="Split extracted Game.locres.txt into translation chunks")
    parser.add_argument("--tools-dir", default=DEFAULT_TOOLS_DIR, help="Directory containing extracted/en and extracted/en-US")
    args = parser.parse_args()

    en_path = os.path.join(args.tools_dir, "extracted", "en", "Game.locres.txt")
    us_path = os.path.join(args.tools_dir, "extracted", "en-US", "Game.locres.txt")

    os.makedirs(CHUNKS_DIR, exist_ok=True)
    en_items = load_loc(en_path)
    us_items = load_loc(us_path)
    en_map = dict(en_items)

    combined = list(en_items)
    for k, v in us_items:
        if k not in en_map:
            combined.append((k, v))
        elif en_map[k] != v:
            combined.append((k + "__US", v))

    pool = {}  # en_text -> (bucket, key_short)
    for k, v in combined:
        ks = k.split("::", 1)[-1].replace("__US", "")
        if v == ks or v.startswith("lng_") or v.startswith("h_scenario_") or re.fullmatch(r"[a-z0-9_]+", v):
            continue
        if not re.search(r"[A-Za-z]", v) or v.startswith(("http://", "https://")):
            continue
        if ks.startswith(SKIP_EXACT_PREFIXES):
            continue
        if re.match(r"lng_driver_lng_(?:co)?driver_(?:fore|sur)name_.+", ks):
            continue
        if v not in pool:
            pool[v] = (bucket_of(ks), ks)

    # Sort by (bucket, key_short, en_text) so related strings stay together
    sorted_items = sorted(pool.items(), key=lambda kv: (kv[1][0], kv[1][1], kv[0]))

    # Split into chunks targeting ~35KB chars or max 480 items per chunk
    chunks = []
    cur = []
    cur_chars = 0
    for idx, (en_text, (b, ks)) in enumerate(sorted_items):
        cur.append({"id": str(idx), "k": ks, "en": en_text})
        cur_chars += len(en_text)
        if len(cur) >= 480 or cur_chars >= 38000:
            chunks.append(cur)
            cur = []
            cur_chars = 0
    if cur:
        chunks.append(cur)

    # Write chunks
    for old in os.listdir(CHUNKS_DIR):
        if old.endswith(".json"):
            os.remove(os.path.join(CHUNKS_DIR, old))

    for i, ch in enumerate(chunks, 1):
        out_p = os.path.join(CHUNKS_DIR, f"chunk_{i:02d}.json")
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(ch, f, ensure_ascii=False, indent=2)

    print(f"Total unique translatable strings: {len(sorted_items)}")
    print(f"Created {len(chunks)} chunks in {CHUNKS_DIR}")
    for i, ch in enumerate(chunks, 1):
        chars = sum(len(x["en"]) for x in ch)
        print(f"  chunk_{i:02d}.json: {len(ch)} items, {chars} chars (first={ch[0]['k']})")

if __name__ == "__main__":
    main()

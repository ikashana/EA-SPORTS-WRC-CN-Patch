import argparse
import json
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH_DIR = os.path.join(BASE_DIR, "translations", "chunks_zh")
SRC_DIR = os.path.join(BASE_DIR, "translations", "chunks_src")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

DEFAULT_TOOLS_DIR = os.path.join(BASE_DIR, "tools")
DEFAULT_OUTPUT_PAK = os.path.join(BASE_DIR, "dist", "pakchunk0-WindowsNoEditor_0_P.pak")

FONT_MAPPING = {
    "WRC/Content/WRC/UI/Fonts/Efigs/FNT_HelveticaCondBold.ufont": "NotoSansSC-Bold.ttf",
    "WRC/Content/WRC/UI/Fonts/Efigs/FNT_WrcCleanBold.ufont": "NotoSansSC-Bold.ttf",
    "WRC/Content/WRC/UI/Fonts/Efigs/FNT_WrcCleanRoman.ufont": "NotoSansSC-Medium.ttf",
    "Engine/Content/EngineFonts/Faces/RobotoBold.ufont": "NotoSansSC-Bold.ttf",
    "Engine/Content/EngineFonts/Faces/RobotoBoldItalic.ufont": "NotoSansSC-Bold.ttf",
    "Engine/Content/EngineFonts/Faces/RobotoRegular.ufont": "NotoSansSC-Regular.ttf",
    "Engine/Content/EngineFonts/Faces/RobotoLight.ufont": "NotoSansSC-Regular.ttf",
    "Engine/Content/EngineFonts/Faces/RobotoItalic.ufont": "NotoSansSC-Regular.ttf",
    "Engine/Content/EngineFonts/Faces/DroidSansFallback.ufont": "NotoSansSC-Regular.ttf",
}


def load_translation_map():
    en_to_zh = {}
    src_files = sorted(f for f in os.listdir(SRC_DIR) if f.endswith(".json"))
    for fn in src_files:
        zh_p = os.path.join(ZH_DIR, fn)
        if not os.path.exists(zh_p):
            continue
        with open(os.path.join(SRC_DIR, fn), "r", encoding="utf-8") as f:
            src_items = json.load(f)
        with open(zh_p, "r", encoding="utf-8") as f:
            zh_map = json.load(f)
        for item in src_items:
            sid = item["id"]
            if sid in zh_map and zh_map[sid].strip():
                en_to_zh[item["en"]] = zh_map[sid]
    return en_to_zh


def load_loc_lines(path):
    lines = []
    kv = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.rstrip("\r\n")
            if "=" in raw:
                k, v = raw.split("=", 1)
                lines.append((k, v))
                kv[k] = v
            else:
                lines.append((None, raw))
    return lines, kv


def apply_translations(src_txt, out_txt, en_to_zh, fallback_kv=None):
    lines, _ = load_loc_lines(src_txt)
    replaced = 0
    out_lines = []
    for k, v in lines:
        if k is None:
            out_lines.append(v)
            continue
        ks = k.split("::", 1)[-1]
        cand = v
        # If en-US has raw key id, fall back to en value first
        if fallback_kv and (v == ks or v.startswith("lng_") or v.startswith("h_scenario_")):
            fb = fallback_kv.get(k)
            if fb and fb != ks and not fb.startswith(("lng_", "h_scenario_")):
                cand = fb
        if cand in en_to_zh:
            out_lines.append(f"{k}={en_to_zh[cand]}")
            replaced += 1
        else:
            out_lines.append(f"{k}={cand}")
    with open(out_txt, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(out_lines) + "\n")
    return replaced


def main():
    parser = argparse.ArgumentParser(description="Build EA SPORTS WRC Chinese .pak patch")
    parser.add_argument("--tools-dir", default=DEFAULT_TOOLS_DIR, help="Directory with repak/, ue4loc/, extracted/")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PAK, help="Output .pak path")
    parser.add_argument("--install-game-paks", default=None, help="Optional WRC/Content/Paks directory to copy output pak into")
    args = parser.parse_args()

    ue4loc_exe = os.path.join(args.tools_dir, "ue4loc", "UE4localizationsTool.exe")
    repak_exe = os.path.join(args.tools_dir, "repak", "repak.exe")
    en_locres = os.path.join(args.tools_dir, "extracted", "en", "Game.locres")
    en_txt = os.path.join(args.tools_dir, "extracted", "en", "Game.locres.txt")
    us_locres = os.path.join(args.tools_dir, "extracted", "en-US", "Game.locres")
    us_txt = os.path.join(args.tools_dir, "extracted", "en-US", "Game.locres.txt")

    for p in (ue4loc_exe, repak_exe, en_locres, en_txt, us_locres, us_txt):
        if not os.path.exists(p):
            print(f"Missing required file: {p}", file=sys.stderr)
            sys.exit(1)

    en_to_zh = load_translation_map()
    print(f"Loaded {len(en_to_zh)} translated strings.")

    build_tmp = os.path.join(BASE_DIR, ".build_tmp")
    if os.path.exists(build_tmp):
        shutil.rmtree(build_tmp)
    pak_root = os.path.join(build_tmp, "pak_root")
    loc_work = os.path.join(build_tmp, "loc_work")
    os.makedirs(pak_root, exist_ok=True)

    _, en_kv = load_loc_lines(en_txt)

    for culture, orig_locres, orig_txt, fb in [
        ("en", en_locres, en_txt, None),
        ("en-US", us_locres, us_txt, en_kv),
    ]:
        c_dir = os.path.join(loc_work, culture)
        os.makedirs(c_dir, exist_ok=True)
        shutil.copy2(orig_locres, os.path.join(c_dir, "Game.locres"))
        out_txt = os.path.join(c_dir, "Game.locres.txt")
        n = apply_translations(orig_txt, out_txt, en_to_zh, fallback_kv=fb)
        print(f"[{culture}] Replaced {n} entries -> importing into Game.locres...")
        subprocess.run([ue4loc_exe, "import", out_txt], check=True)
        new_locres = os.path.join(c_dir, "Game_NEW.locres")
        dest_locres = os.path.join(pak_root, "WRC", "Content", "Localization", "Game", "Windows", culture, "Game.locres")
        os.makedirs(os.path.dirname(dest_locres), exist_ok=True)
        shutil.copy2(new_locres, dest_locres)

    for pak_rel, font_name in FONT_MAPPING.items():
        src_font = os.path.join(FONTS_DIR, font_name)
        dst_font = os.path.join(pak_root, pak_rel)
        os.makedirs(os.path.dirname(dst_font), exist_ok=True)
        shutil.copy2(src_font, dst_font)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    if os.path.exists(args.output):
        os.remove(args.output)
    subprocess.run(
        [repak_exe, "pack", "-m", "../../../", "--version", "V11", "--compression", "Zlib", pak_root, args.output],
        check=True,
    )
    print(f"Built pak: {args.output} ({os.path.getsize(args.output):,} bytes)")

    if args.install_game_paks:
        os.makedirs(args.install_game_paks, exist_ok=True)
        dst = os.path.join(args.install_game_paks, os.path.basename(args.output))
        shutil.copy2(args.output, dst)
        print(f"Installed to: {dst}")


if __name__ == "__main__":
    main()

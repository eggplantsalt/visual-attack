import json
import shutil
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

VA = Path("/storage/v-xiangxizheng/zy_workspace/visual-attack")
SRC = VA / "third_party/imgsource"
OUT = VA / "assets/visa_bench/f4_iso7010_v0_1"
RAW = OUT / "raw_svg"
PNG = OUT / "png_512"
GALLERY = OUT / "f4_iso7010_assets_gallery_v0_1.png"
MANIFEST = OUT / "f4_iso7010_assets_manifest_v0_1.json"

RAW.mkdir(parents=True, exist_ok=True)
PNG.mkdir(parents=True, exist_ok=True)

# 这 7 个是当前锁定的 ISO 7010 子集。
EXPECTED = {
    "P001": {
        "semantic_name": "general_prohibition",
        "zh": "通用禁止",
        "role": "generic_forbid",
        "libero_use": "通用禁止区域/物体/目标",
    },
    "P004": {
        "semantic_name": "no_entry_no_thoroughfare",
        "zh": "禁止进入/禁止通行",
        "role": "forbidden_area",
        "libero_use": "禁止目标区域、禁止靠近区域",
    },
    "P010": {
        "semantic_name": "do_not_touch",
        "zh": "禁止触碰",
        "role": "forbidden_interaction",
        "libero_use": "禁止抓取物体、禁止接触装置",
    },
    "W001": {
        "semantic_name": "general_warning",
        "zh": "一般警告",
        "role": "generic_hazard",
        "libero_use": "通用危险区域/风险目标",
    },
    "W017": {
        "semantic_name": "hot_surface",
        "zh": "高温表面",
        "role": "surface_hazard",
        "libero_use": "炉灶/热表面相关任务",
    },
    "W021": {
        "semantic_name": "flammable_material",
        "zh": "易燃物",
        "role": "object_hazard",
        "libero_use": "靠近炉灶的易燃/危险物体语义",
    },
    "M030": {
        "semantic_name": "place_trash_in_bin",
        "zh": "投入垃圾桶/投放容器",
        "role": "positive_container_destination",
        "libero_use": "basket/caddy/container 投放类任务",
    },
}

def find_svg_for_code(code: str) -> Path | None:
    candidates = sorted(SRC.glob(f"*{code}*.svg"))
    if candidates:
        return candidates[0]
    return None

def render_svg_to_png(svg_path: Path, png_path: Path, size: int = 512):
    # cairosvg 会保留透明背景；不要加白底。
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=size,
        output_height=size,
    )

def make_gallery(rows):
    cell_w, cell_h = 330, 390
    cols = 4
    rows_n = (len(rows) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * cell_w, rows_n * cell_h + 70), "white")
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
        small = ImageFont.truetype("DejaVuSans.ttf", 13)
        title_font = ImageFont.truetype("DejaVuSans.ttf", 24)
    except Exception:
        font = None
        small = None
        title_font = None

    draw.text((20, 18), "F4 ISO 7010 selected assets v0.1", fill="black", font=title_font)

    for i, r in enumerate(rows):
        x = (i % cols) * cell_w
        y = (i // cols) * cell_h + 70

        icon = Image.open(r["png_512"]).convert("RGBA")
        # checker-ish light background for transparency visibility
        bg = Image.new("RGB", (230, 230), (245, 245, 245))
        icon.thumbnail((220, 220), Image.LANCZOS)
        px = x + 50 + (220 - icon.width) // 2
        py = y + 10 + (220 - icon.height) // 2
        canvas.paste(bg, (x + 50, y + 10))
        canvas.paste(icon, (px, py), icon)

        text_lines = [
            f'{r["code"]}: {r["semantic_name"]}',
            r["zh"],
            f'role: {r["role"]}',
            r["libero_use"],
        ]
        ty = y + 255
        for line in text_lines:
            if len(line) > 38:
                line = line[:35] + "..."
            draw.text((x + 16, ty), line, fill="black", font=font if ty == y + 255 else small)
            ty += 26

    canvas.save(GALLERY)

def main():
    manifest = []
    missing = []

    for code, meta in EXPECTED.items():
        src_svg = find_svg_for_code(code)
        if src_svg is None:
            missing.append(code)
            print(f"[MISSING] {code}")
            continue

        norm_svg = RAW / f"ISO_7010_{code}_{meta['semantic_name']}.svg"
        norm_png = PNG / f"ISO_7010_{code}_{meta['semantic_name']}_512.png"

        shutil.copy2(src_svg, norm_svg)
        render_svg_to_png(norm_svg, norm_png, size=512)

        row = {
            "code": code,
            "source_file": str(src_svg),
            "raw_svg": str(norm_svg),
            "png_512": str(norm_png),
            **meta,
        }
        manifest.append(row)
        print(f"[OK] {code} -> {norm_png}")

    MANIFEST.write_text(json.dumps({
        "name": "f4_iso7010_selected_assets_v0_1",
        "num_assets": len(manifest),
        "missing": missing,
        "assets": manifest,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    make_gallery(manifest)

    print()
    print("WROTE_MANIFEST", MANIFEST)
    print("WROTE_GALLERY", GALLERY)
    print("OUT_DIR", OUT)
    if missing:
        print("MISSING_CODES", missing)

if __name__ == "__main__":
    main()

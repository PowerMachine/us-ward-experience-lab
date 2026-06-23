from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
SOURCE_HERO = ASSETS / "hospital-ward-hero.png"
SOURCE_COLLAGE = ASSETS / "ward-spaces-collage.png"

COLORS = {
    "ivory": "#fffaf3",
    "paper": "#ffffff",
    "ink": "#25364a",
    "muted": "#667084",
    "line": "#d9dce7",
    "sage": "#8ab7a3",
    "sage_dark": "#2f675b",
    "teal": "#2e7f95",
    "lavender": "#b9a8da",
    "lavender_soft": "#eee8fb",
    "blush": "#f2b8aa",
    "blush_soft": "#fdebe7",
    "coral": "#e77d67",
    "sky": "#b8d7ec",
    "sky_soft": "#e5f1fa",
    "gold": "#e7bd62",
    "gold_soft": "#fff1c7",
    "mint_soft": "#e5f3ed",
    "navy": "#1f3c56",
}


def font(size, bold=False):
    candidates = [
        Path("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def save_app_image(img, path, width=840):
    if img.size[0] != width:
        height = int(img.size[1] * width / img.size[0])
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(path)


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def round_rect(draw, xy, radius=18, fill=COLORS["paper"], outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def soft_card(draw, xy, radius=20, fill=COLORS["paper"]):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle((x1, y1 + 8, x2, y2 + 8), radius=radius, fill="#dfe3eb")
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_badge(draw, center, label, fill, outline=None):
    x, y = center
    draw.ellipse((x - 23, y - 23, x + 23, y + 23), fill=fill, outline=outline or "#ffffff", width=3)
    draw.text((x, y - 1), label, font=font(15, True), fill=COLORS["ink"], anchor="mm")


def create_hero():
    if not SOURCE_HERO.exists():
        return
    source = Image.open(SOURCE_HERO).convert("RGB")
    hero = ImageOps.fit(source, (1040, 390), method=Image.Resampling.LANCZOS, centering=(0.52, 0.5)).convert("RGBA")

    overlay = Image.new("RGBA", hero.size, (0, 0, 0, 0))
    px = overlay.load()
    width, height = overlay.size
    for x in range(width):
        alpha = max(0, int(120 * (1 - x / (width * 0.58))))
        for y in range(height):
            px[x, y] = (255, 250, 243, alpha)
    hero = Image.alpha_composite(hero, overlay)

    mask = Image.new("L", hero.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, hero.size[0] - 1, hero.size[1] - 1), radius=28, fill=255)
    output = Image.new("RGBA", hero.size, (0, 0, 0, 0))
    output.paste(hero, (0, 0), mask)
    save_app_image(output, ASSETS / "hero-banner.png", width=840)


def draw_simple_icon(kind, path, bg, fg):
    size = 180
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((20, 20, 160, 160), radius=38, fill=bg)
    draw.rounded_rectangle((20, 20, 160, 160), radius=38, outline="#ffffff", width=5)

    if kind == "nurse":
        draw.arc((50, 52, 130, 140), 205, 335, fill=fg, width=7)
        draw.ellipse((72, 48, 108, 84), outline=fg, width=6)
        draw.rounded_rectangle((58, 92, 122, 132), radius=16, outline=fg, width=6)
        draw.line((90, 92, 90, 132), fill=fg, width=5)
    elif kind == "med":
        draw.rounded_rectangle((48, 70, 132, 112), radius=21, outline=fg, width=7)
        draw.line((90, 70, 90, 112), fill=fg, width=6)
        draw.line((62, 91, 118, 91), fill=fg, width=4)
    elif kind == "bed":
        draw.line((42, 116, 138, 116), fill=fg, width=7)
        draw.line((42, 78, 42, 133), fill=fg, width=7)
        draw.rounded_rectangle((52, 82, 91, 108), radius=8, outline=fg, width=5)
        draw.rounded_rectangle((92, 82, 138, 108), radius=8, outline=fg, width=5)
    elif kind == "supply":
        draw.rounded_rectangle((55, 55, 125, 130), radius=12, outline=fg, width=6)
        draw.line((55, 82, 125, 82), fill=fg, width=5)
        draw.line((55, 107, 125, 107), fill=fg, width=5)
        draw.ellipse((66, 134, 82, 150), fill=fg)
        draw.ellipse((108, 134, 124, 150), fill=fg)
    elif kind == "handoff":
        draw.arc((45, 50, 98, 113), start=100, end=286, fill=fg, width=7)
        draw.arc((82, 68, 137, 132), start=-82, end=102, fill=fg, width=7)
        draw.polygon((126, 92, 148, 104, 126, 116), fill=fg)
        draw.polygon((56, 88, 34, 76, 56, 64), fill=fg)
    else:
        draw.ellipse((55, 55, 125, 125), outline=fg, width=7)
        draw.line((90, 42, 90, 138), fill=fg, width=5)
        draw.line((42, 90, 138, 90), fill=fg, width=5)
        draw.ellipse((82, 82, 98, 98), fill=fg)

    img.save(path)


def create_icons():
    specs = [
        ("nurse", "icon-nurse.png", COLORS["mint_soft"], COLORS["sage_dark"]),
        ("med", "icon-med.png", COLORS["blush_soft"], COLORS["coral"]),
        ("bed", "icon-bed.png", COLORS["sky_soft"], "#3a79a6"),
        ("supply", "icon-supply.png", COLORS["gold_soft"], "#a5791c"),
        ("handoff", "icon-handoff.png", COLORS["lavender_soft"], "#6854a2"),
        ("safety", "icon-safety.png", "#e9f7f6", COLORS["teal"]),
    ]
    for kind, name, bg, fg in specs:
        draw_simple_icon(kind, ASSETS / name, bg, fg)


def create_app_icon():
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    navy = hex_to_rgb(COLORS["navy"])
    teal = hex_to_rgb(COLORS["teal"])
    for y in range(size):
        t = y / (size - 1)
        color = tuple(int(navy[i] * (1 - t) + teal[i] * t) for i in range(3))
        draw.line((0, y, size, y), fill=color + (255,))

    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((36, 36, 988, 988), radius=220, fill=255)
    rounded = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rounded.paste(img, (0, 0), mask)
    img = rounded
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle((58, 58, 966, 966), radius=198, outline=(255, 255, 255, 185), width=22)

    # Floor-plan tiles
    tile_fill = (255, 255, 255, 42)
    tile_outline = (255, 255, 255, 96)
    tiles = [
        (162, 180, 385, 360),
        (432, 180, 660, 360),
        (690, 180, 862, 360),
        (162, 650, 380, 820),
        (432, 650, 640, 820),
        (690, 650, 862, 820),
    ]
    for tile in tiles:
        draw.rounded_rectangle(tile, radius=42, fill=tile_fill, outline=tile_outline, width=5)

    draw.rounded_rectangle((185, 435, 835, 590), radius=78, fill=(255, 255, 255, 58), outline=(255, 255, 255, 110), width=5)

    # RN route line
    route = [(275, 272), (540, 272), (760, 272), (760, 512), (535, 735), (272, 735)]
    for a, b in zip(route, route[1:]):
        draw.line((*a, *b), fill=(242, 184, 170, 235), width=34)
    for x, y in route:
        draw.ellipse((x - 38, y - 38, x + 38, y + 38), fill=(255, 250, 243, 255), outline=(242, 184, 170, 255), width=12)

    # Central medical cross inside a clipboard-map shape
    draw.rounded_rectangle((344, 326, 680, 696), radius=88, fill=(255, 250, 243, 252), outline=(255, 255, 255, 255), width=10)
    draw.rounded_rectangle((430, 278, 594, 352), radius=36, fill=(232, 125, 103, 255))
    draw.rounded_rectangle((480, 402, 544, 620), radius=24, fill=hex_to_rgb(COLORS["sage_dark"]) + (255,))
    draw.rounded_rectangle((402, 480, 622, 544), radius=24, fill=hex_to_rgb(COLORS["sage_dark"]) + (255,))

    # Small stethoscope cue
    draw.arc((210, 690, 360, 875), start=18, end=318, fill=(255, 250, 243, 230), width=24)
    draw.ellipse((326, 826, 386, 886), outline=(255, 250, 243, 235), width=18)
    draw.line((322, 712, 456, 650), fill=(255, 250, 243, 230), width=20)

    preview = ASSETS / "us-ward-icon.png"
    ico = ASSETS / "us-ward-icon.ico"
    img.save(preview)
    img.save(ico, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)])


def create_day_flow():
    img = Image.new("RGBA", (920, 500), "#f8f6fb")
    draw = ImageDraw.Draw(img)

    draw.text((44, 38), "SHIFT COMMAND BOARD", font=font(25, True), fill=COLORS["navy"])
    draw.text((44, 75), "하루 전체를 한 장의 근무 보드로 스캔합니다", font=font(18), fill=COLORS["muted"])

    # Time rail
    draw.rounded_rectangle((70, 162, 850, 188), radius=13, fill="#e5e1f0")
    draw.rounded_rectangle((70, 162, 330, 188), radius=13, fill=COLORS["lavender"])
    draw.rounded_rectangle((330, 162, 590, 188), radius=13, fill=COLORS["sage"])
    draw.rounded_rectangle((590, 162, 850, 188), radius=13, fill=COLORS["blush"])

    phases = [
        ("START", "07:00", "handoff", 100, COLORS["lavender_soft"], "#6854a2"),
        ("SCAN", "08:00", "chart + rounds", 245, COLORS["sky_soft"], "#3a79a6"),
        ("MEDS", "09:00", "MAR + safety", 390, COLORS["blush_soft"], COLORS["coral"]),
        ("TEAM", "11:00", "rounds + SBAR", 535, COLORS["mint_soft"], COLORS["sage_dark"]),
        ("ADMIT", "14:00", "room prep", 680, COLORS["gold_soft"], "#a5791c"),
        ("CLOSE", "19:00", "bedside report", 825, COLORS["lavender_soft"], "#6854a2"),
    ]

    for title, time, caption, x, fill, stroke in phases:
        draw.line((x, 138, x, 222), fill=stroke, width=3)
        draw.ellipse((x - 14, 162, x + 14, 190), fill="#ffffff", outline=stroke, width=4)
        soft_card(draw, (x - 62, 236, x + 62, 342), radius=18, fill="#ffffff")
        draw.rounded_rectangle((x - 45, 252, x + 45, 280), radius=14, fill=fill)
        draw.text((x, 266), title, font=font(14, True), fill=stroke, anchor="mm")
        draw.text((x, 304), time, font=font(21, True), fill=COLORS["ink"], anchor="mm")
        draw.text((x, 327), caption, font=font(13), fill=COLORS["muted"], anchor="mm")

    # Priority panel
    soft_card(draw, (56, 374, 864, 462), radius=22, fill="#ffffff")
    draw.text((84, 400), "Priority Lens", font=font(19, True), fill=COLORS["navy"])
    lenses = [
        ("unstable vitals", COLORS["coral"]),
        ("new orders", COLORS["teal"]),
        ("pain reassessment", COLORS["lavender"]),
        ("discharge barrier", COLORS["gold"]),
    ]
    for i, (label, color) in enumerate(lenses):
        x = 260 + i * 145
        draw.ellipse((x - 10, 416, x + 10, 436), fill=color)
        draw.text((x + 18, 426), label, font=font(13, True), fill=COLORS["muted"], anchor="lm")

    save_app_image(img, ASSETS / "day-flow-visual.png", width=840)


def create_tour_visual():
    img = Image.new("RGBA", (920, 500), "#f6fbfb")
    draw = ImageDraw.Draw(img)
    draw.text((44, 36), "UNIT NAVIGATOR", font=font(25, True), fill=COLORS["navy"])
    draw.text((44, 73), "공간을 외우는 대신 RN 동선을 따라 탐색합니다", font=font(18), fill=COLORS["muted"])

    # Map surface
    draw.rounded_rectangle((46, 120, 874, 446), radius=30, fill="#ffffff", outline="#dbe7ea", width=2)
    draw.rounded_rectangle((102, 260, 810, 306), radius=23, fill="#edf3f6")
    draw.text((456, 283), "central workflow lane", font=font(16, True), fill="#6b7d88", anchor="mm")

    zones = [
        ("Nurse Station", "assign / calls / EHR", (330, 150, 590, 235), COLORS["mint_soft"], "icon-nurse.png"),
        ("Med Room", "MAR / allergy / ADC", (96, 172, 278, 246), COLORS["blush_soft"], "icon-med.png"),
        ("Supply Core", "PPE / kits / par", (642, 172, 824, 246), COLORS["gold_soft"], "icon-supply.png"),
        ("Patient Rooms", "ID / safety / teach", (96, 324, 278, 406), COLORS["sky_soft"], "icon-bed.png"),
        ("Isolation Bay", "sign / PPE / exit", (360, 324, 560, 406), COLORS["lavender_soft"], "icon-safety.png"),
        ("Handoff Hub", "ED / SBAR / shift", (642, 324, 824, 406), COLORS["mint_soft"], "icon-handoff.png"),
    ]

    route = [(460, 235), (230, 260), (187, 324), (460, 324), (733, 324), (733, 246), (460, 235)]
    for a, b in zip(route, route[1:]):
        draw.line((*a, *b), fill="#b7c7d2", width=4)

    for title, desc, box, fill, icon_file in zones:
        soft_card(draw, box, radius=18, fill=fill)
        x1, y1, x2, y2 = box
        icon = Image.open(ASSETS / icon_file).resize((46, 46), Image.Resampling.LANCZOS)
        img.alpha_composite(icon, (x1 + 16, y1 + 16))
        draw.text((x1 + 72, y1 + 24), title, font=font(17, True), fill=COLORS["ink"])
        draw.text((x1 + 72, y1 + 50), desc, font=font(13), fill=COLORS["muted"])

    # Small locator pins
    for i, (x, y) in enumerate([(460, 260), (187, 306), (733, 306), (460, 306)], start=1):
        draw_badge(draw, (x, y), str(i), "#ffffff", COLORS["teal"])

    save_app_image(img, ASSETS / "tour-visual.png", width=840)


def create_scenario_visual():
    img = Image.new("RGBA", (920, 560), "#f8f9fc")
    draw = ImageDraw.Draw(img)
    draw.text((44, 34), "CASE LIBRARY", font=font(25, True), fill=COLORS["navy"])
    draw.text((44, 70), "단조로운 데모가 아니라 실제 병동에서 만나는 갈림길을 연습합니다", font=font(17), fill=COLORS["muted"])

    cases = [
        ("POST-OP", "pain / mobility", COLORS["sky_soft"], "icon-bed.png"),
        ("CHF", "oxygen / I&O", COLORS["mint_soft"], "icon-safety.png"),
        ("ISOLATION", "PPE / family", COLORS["lavender_soft"], "icon-supply.png"),
        ("ADMISSION", "ED handoff", COLORS["gold_soft"], "icon-nurse.png"),
        ("LOW GLUCOSE", "recheck / SBAR", COLORS["blush_soft"], "icon-med.png"),
        ("CHEST PAIN", "telemetry / call", COLORS["sky_soft"], "icon-handoff.png"),
        ("FALL EVENT", "assessment", COLORS["gold_soft"], "icon-safety.png"),
        ("DISCHARGE", "teach-back", COLORS["mint_soft"], "icon-nurse.png"),
        ("MISSING MED", "pharmacy flow", COLORS["blush_soft"], "icon-med.png"),
        ("SEPSIS ALERT", "trend / escalate", COLORS["lavender_soft"], "icon-safety.png"),
        ("FAMILY CALL", "privacy / boundary", COLORS["mint_soft"], "icon-handoff.png"),
    ]

    for i, (title, caption, fill, icon_file) in enumerate(cases):
        row = i // 4
        col = i % 4
        x = 42 + col * 218
        y = 122 + row * 132
        soft_card(draw, (x, y, x + 180, y + 104), radius=20, fill="#ffffff")
        draw.rounded_rectangle((x + 14, y + 15, x + 64, y + 65), radius=15, fill=fill)
        icon = Image.open(ASSETS / icon_file).resize((34, 34), Image.Resampling.LANCZOS)
        img.alpha_composite(icon, (x + 22, y + 23))
        draw.text((x + 80, y + 24), title, font=font(12, True), fill=COLORS["ink"])
        draw.text((x + 80, y + 48), caption, font=font(10), fill=COLORS["muted"])
        draw.rounded_rectangle((x + 80, y + 74, x + 142, y + 92), radius=9, fill=fill)
        draw.text((x + 111, y + 83), "3 steps", font=font(9, True), fill=COLORS["ink"], anchor="mm")

    save_app_image(img, ASSETS / "scenario-cards.png", width=840)


def create_photo_crops():
    if not SOURCE_COLLAGE.exists():
        return
    source = Image.open(SOURCE_COLLAGE).convert("RGB")
    width, height = source.size
    crops = {
        "nurse-station-photo.png": (0, 0, width // 2, height // 2),
        "med-room-photo.png": (width // 2, 0, width, height // 2),
        "patient-room-photo.png": (0, height // 2, width // 2, height),
        "supply-room-photo.png": (width // 2, height // 2, width, height),
    }
    for name, box in crops.items():
        crop = source.crop(box).resize((520, 360), Image.Resampling.LANCZOS)
        crop.save(ASSETS / name, quality=94)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    create_hero()
    create_icons()
    create_app_icon()
    create_day_flow()
    create_tour_visual()
    create_scenario_visual()
    create_photo_crops()
    print("VISUAL_ASSETS_OK")


if __name__ == "__main__":
    main()

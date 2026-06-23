from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "work" / "assets"
SCREENSHOTS = ROOT / "screenshots"

COLORS = {
    "bg": "#edf3f7",
    "panel": "#ffffff",
    "ink": "#16233a",
    "muted": "#506178",
    "line": "#a9b6c7",
    "primary": "#2f66d7",
    "accent": "#ec6a5c",
    "success": "#14846a",
    "soft_blue": "#cfe7ff",
    "soft_green": "#c9efdf",
    "soft_orange": "#ffd7cc",
    "soft_gold": "#ffdf86",
    "soft_lavender": "#ded1ff",
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


def load_asset(name, size):
    image = Image.open(ASSETS / name).convert("RGB")
    return image.resize(size, Image.Resampling.LANCZOS)


def card(draw, xy, fill="#ffffff", outline="#a9b6c7", radius=14):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=2)


def main_screen():
    img = Image.new("RGB", (1400, 820), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 250, 820), fill="#101b30")
    draw.text((28, 38), "U.S. Ward", fill="white", font=font(30, True))
    draw.text((28, 78), "Experience Lab", fill="#dce8ff", font=font(20, True))
    draw.rounded_rectangle((28, 130, 218, 170), radius=10, fill=COLORS["soft_gold"])
    draw.text((123, 150), "v0.1.0-beta", fill=COLORS["ink"], font=font(15, True), anchor="mm")
    nav = ["첫 7일", "입장", "직무 트랙", "병동 투어", "스테이션 실습", "환자 케이스", "SBAR"]
    y = 218
    for item in nav:
        fill = COLORS["primary"] if item == "첫 7일" else "#101b30"
        draw.rounded_rectangle((18, y - 8, 232, y + 32), radius=6, fill=fill)
        draw.text((36, y + 10), item, fill="#ffffff", font=font(16, True if item == "첫 7일" else False), anchor="lm")
        y += 48
    draw.rounded_rectangle((28, 700, 218, 748), radius=8, fill=COLORS["soft_gold"])
    draw.text((123, 724), "피드백 남기기", fill=COLORS["ink"], font=font(16, True), anchor="mm")

    panel = (285, 32, 1366, 330)
    card(draw, panel, fill="#fffaf3", outline="#c8d2df", radius=18)
    hero = load_asset("hero-banner.png", (500, 232))
    img.paste(hero, (842, 58))
    draw.text((324, 76), "미국 병동 첫 7일", fill=COLORS["ink"], font=font(38, True))
    draw.text((324, 126), "실전 적응 시뮬레이션", fill=COLORS["ink"], font=font(38, True))
    draw.text((326, 190), "NCLEX 이후 미국 이민을 준비하는 한국 RN을 위한\n병동 문화, 법/정책, 팀 커뮤니케이션 시뮬레이션", fill=COLORS["muted"], font=font(18), spacing=8)
    for i, (label, fill) in enumerate([("보고", COLORS["success"]), ("선택하고", COLORS["primary"]), ("디브리핑", COLORS["accent"])]):
        x = 326 + i * 120
        draw.rounded_rectangle((x, 248, x + 105, 286), radius=6, fill=fill)
        draw.text((x + 52, 267), label, fill="white", font=font(16, True), anchor="mm")

    tiles = [
        ("ward-spaces-collage.png", "실제 병동 공간 단서"),
        ("day-flow-visual.png", "첫 7일 흐름"),
        ("tour-visual.png", "병동 동선"),
    ]
    for i, (asset, label) in enumerate(tiles):
        x = 285 + i * 360
        card(draw, (x, 365, x + 330, 630), fill="#ffffff")
        thumb = load_asset(asset, (300, 170))
        img.paste(thumb, (x + 15, 386))
        draw.text((x + 20, 590), label, fill=COLORS["ink"], font=font(20, True))
    img.save(SCREENSHOTS / "main.png", quality=95)


def first_7_days():
    img = Image.new("RGB", (1400, 820), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw.text((40, 34), "First 7 Days Simulation", fill=COLORS["primary"], font=font(18, True))
    draw.text((40, 74), "Day 2 / 08:45  EHR, MAR, ADC, 투약실 접근", fill=COLORS["ink"], font=font(32, True))
    med = load_asset("med-room-photo.png", (420, 290))
    card(draw, (40, 140, 500, 470), fill="#ffffff")
    img.paste(med, (60, 160))
    draw.text((540, 150), "오늘 보는 장면", fill=COLORS["primary"], font=font(18, True))
    draw.text((540, 190), "preceptor가 09:00 medication pass를 보여줍니다.\nMAR, allergy, ADC 흐름을 함께 확인합니다.", fill=COLORS["ink"], font=font(22), spacing=8)
    draw.rounded_rectangle((540, 300, 1320, 358), radius=8, fill=COLORS["soft_blue"])
    draw.text((562, 329), "목표: 약을 꺼내기 전 정보 흐름을 읽고 controlled substance/waste 경계를 이해하기", fill=COLORS["ink"], font=font(20, True), anchor="lm")
    cues = [("MAR", "due time / route"), ("Allergy", "band + EHR"), ("ADC", "missing med"), ("Waste", "witness / documentation")]
    for i, (title, body) in enumerate(cues):
        x = 540 + (i % 2) * 390
        y = 388 + (i // 2) * 80
        card(draw, (x, y, x + 360, y + 62), fill=[COLORS["soft_blue"], COLORS["soft_gold"], COLORS["soft_green"], COLORS["soft_lavender"]][i], radius=10)
        draw.text((x + 16, y + 20), title, fill=COLORS["ink"], font=font(17, True))
        draw.text((x + 120, y + 20), body, fill=COLORS["ink"], font=font(17))
    choices = [
        "MAR, allergy, hold parameter, barcode 흐름을 preceptor에게 말로 확인한다.",
        "ADC만 익히면 된다고 보고 MAR review는 맡긴다.",
        "controlled substance waste를 나중에 혼자 처리한다.",
    ]
    y = 580
    for i, choice in enumerate(choices, start=1):
        card(draw, (54, y, 1320, y + 58), fill="#ffffff", outline=COLORS["primary"] if i == 1 else COLORS["line"], radius=8)
        draw.rounded_rectangle((72, y + 14, 108, y + 44), radius=6, fill=COLORS["primary"])
        draw.text((90, y + 29), str(i), fill="white", font=font(16, True), anchor="mm")
        draw.text((126, y + 29), choice, fill=COLORS["ink"], font=font(19), anchor="lm")
        y += 74
    img.save(SCREENSHOTS / "first_7_days.png", quality=95)


def ward_tour():
    img = Image.new("RGB", (1400, 820), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw.text((40, 34), "Ward Tour", fill=COLORS["primary"], font=font(18, True))
    draw.text((40, 74), "구역을 클릭하고 다음 동선을 고르는 실습 모드", fill=COLORS["ink"], font=font(32, True))
    card(draw, (40, 140, 860, 720), fill="#ffffff")
    draw.rounded_rectangle((95, 345, 805, 420), radius=24, fill="#dfe8ee")
    draw.text((450, 382), "4 WEST MAIN HALLWAY", fill=COLORS["muted"], font=font(18, True), anchor="mm")
    zones = [
        ("nurse-station-photo.png", "Nurse Station", (120, 180)),
        ("med-room-photo.png", "Medication Room", (410, 180)),
        ("supply-room-photo.png", "Supply Room", (650, 180)),
        ("patient-room-photo.png", "Patient Room", (120, 480)),
        ("supply-room-photo.png", "Utility / Isolation", (410, 480)),
        ("nurse-station-photo.png", "Handoff Zone", (650, 480)),
    ]
    for asset, label, (x, y) in zones:
        card(draw, (x, y, x + 180, y + 150), fill="#ffffff", radius=12)
        thumb = load_asset(asset, (150, 90))
        img.paste(thumb, (x + 15, y + 12))
        draw.text((x + 90, y + 122), label, fill=COLORS["ink"], font=font(15, True), anchor="mm")
    draw.line((210, 255, 500, 255, 740, 255, 740, 555, 500, 555), fill=COLORS["primary"], width=8)
    card(draw, (900, 140, 1340, 720), fill="#ffffff")
    photo = load_asset("nurse-station-photo.png", (380, 240))
    img.paste(photo, (930, 170))
    draw.text((930, 445), "간호사 스테이션", fill=COLORS["ink"], font=font(28, True))
    draw.text((930, 492), "assignment, call light, EHR task,\nprovider call을 조율하는 병동의 지휘석입니다.", fill=COLORS["muted"], font=font(19), spacing=7)
    for i, label in enumerate(["눈에 보이는 단서", "귀에 들어오는 신호", "RN 멈춤 지점"]):
        y = 570 + i * 44
        draw.rounded_rectangle((930, y, 1310, y + 32), radius=8, fill=[COLORS["soft_blue"], COLORS["soft_gold"], COLORS["soft_green"]][i])
        draw.text((948, y + 16), label, fill=COLORS["ink"], font=font(15, True), anchor="lm")
    img.save(SCREENSHOTS / "ward_tour.png", quality=95)


def main():
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    main_screen()
    first_7_days()
    ward_tour()
    print("GITHUB_SCREENSHOTS_OK")


if __name__ == "__main__":
    main()

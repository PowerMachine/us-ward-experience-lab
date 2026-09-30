import os
import random
import re
import sys
import tkinter as tk
import ctypes
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

from PIL import Image, ImageTk

from content_expander import extend_content_bundle, select_first_week_days, select_shift_events
from us_ward_i18n import build_english_content


APP_TITLE = "U.S. Ward Experience Lab"
APP_SUBTITLE = "한국 간호사를 위한 미국 병동 근무 시뮬레이터"
APP_VERSION = "v0.1.1-beta"
FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScUc4cvKVPYf1DdItAYW74V8bXQidAS9CHh7d5akhNyv2Oe5w/viewform?usp=publish-editor"
FONT_FAMILY = "Malgun Gothic"
FONT_NORMAL = "{Malgun Gothic} 10"
FONT_SMALL = "{Malgun Gothic} 9"
FONT_SMALL_BOLD = "{Malgun Gothic} 9 bold"
FONT_TITLE = "{Malgun Gothic} 19 bold"
FONT_CARD_TITLE = "{Malgun Gothic} 12 bold"
FONT_SECTION = "{Malgun Gothic} 14 bold"
FONT_SIDEBAR_TITLE = "{Malgun Gothic} 13 bold"
FONT_METRIC = "{Malgun Gothic} 22 bold"
FONT_BOLD = "{Malgun Gothic} 10 bold"
FONT_HERO = "{Malgun Gothic} 23 bold"
FONT_HERO_SMALL = "{Malgun Gothic} 11 bold"
FONT_CHIP = "{Malgun Gothic} 8 bold"
BUNDLED_FONT_FILES = ("NotoSansKR-Variable.ttf",)

ASSET_FILES = {
    "hero": "hero-banner.png",
    "hospital_hero": "hospital-ward-hero.png",
    "ward_collage": "ward-spaces-collage.png",
    "photo_nurse_station": "nurse-station-photo.png",
    "photo_med_room": "med-room-photo.png",
    "photo_patient_room": "patient-room-photo.png",
    "photo_supply_room": "supply-room-photo.png",
    "photo_utility_isolation": "utility-isolation-photo.png",
    "photo_handoff_zone": "handoff-zone-photo.png",
    "day_flow": "day-flow-visual.png",
    "tour": "tour-visual.png",
    "scenarios": "scenario-cards.png",
    "icon_nurse": "icon-nurse.png",
    "icon_med": "icon-med.png",
    "icon_bed": "icon-bed.png",
    "icon_supply": "icon-supply.png",
    "icon_handoff": "icon-handoff.png",
    "icon_safety": "icon-safety.png",
}

COLORS = {
    "bg": "#F7F7F3",
    "panel": "#FCFCFA",
    "panel_alt": "#F3F4F0",
    "ink": "#202825",
    "muted": "#68716D",
    "line": "#E3E6E1",
    "line_dark": "#B8C0BA",
    "primary": "#285F58",
    "primary_dark": "#1F4C47",
    "accent": "#9A742C",
    "accent_dark": "#75571F",
    "success": "#356B58",
    "success_dark": "#285443",
    "warning": "#9A742C",
    "danger": "#A34A44",
    "sidebar": "#F4F4F0",
    "sidebar_alt": "#ECEEE9",
    "sidebar_select": "#E6ECE8",
    "sidebar_ink": "#202825",
    "sidebar_muted": "#707873",
    "sidebar_line": "#DDE1DB",
    "soft_blue": "#EEF2F0",
    "soft_green": "#E8F0EB",
    "soft_orange": "#F7ECE7",
    "soft_gray": "#EFF0EC",
    "soft_gold": "#F4EFE2",
    "soft_lavender": "#F0EEF2",
    "soft_cyan": "#E8EFEC",
    "card_border": "#E0E3DE",
    "shadow": "#ECEDE9",
}

NAV_BADGES = {
    "dashboard": "01",
    "first7": "02",
    "specialties": "03",
    "tour": "04",
    "shift": "05",
    "quests": "06",
    "scenarios": "07",
    "english": "08",
    "sbar": "09",
    "checklists": "10",
    "guide": "11",
}

NAV_MARKERS = {
    "dashboard": "HM",
    "first7": "D7",
    "specialties": "JT",
    "tour": "WT",
    "shift": "SB",
    "quests": "SP",
    "scenarios": "PC",
    "english": "EN",
    "sbar": "SR",
    "checklists": "CL",
    "guide": "GD",
}

NAV_GROUPS = [
    ("start", ["dashboard", "first7", "tour"]),
    ("practice", ["shift", "quests", "scenarios", "sbar", "english"]),
    ("tools", ["specialties", "checklists", "guide"]),
]


def resource_path(*parts):
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, *parts)


def enable_windows_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except (AttributeError, OSError):
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except (AttributeError, OSError):
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


def configure_tk_scaling(root):
    try:
        dpi = root.winfo_fpixels("1i")
        root.tk.call("tk", "scaling", max(1.0, dpi / 72.0))
    except tk.TclError:
        pass


def font_spec(family, size, bold=False):
    weight = " bold" if bold else ""
    return f"{{{family}}} {size}{weight}"


def register_bundled_fonts():
    font_dir = resource_path("assets", "fonts")
    font_paths = [os.path.join(font_dir, filename) for filename in BUNDLED_FONT_FILES]
    existing_paths = [path for path in font_paths if os.path.exists(path)]
    if not existing_paths:
        return []

    if sys.platform == "win32":
        try:
            add_font = ctypes.windll.gdi32.AddFontResourceExW
            for path in existing_paths:
                add_font(path, 0x10, 0)  # FR_PRIVATE: app-only font registration.
        except (AttributeError, OSError):
            pass

    return existing_paths


def configure_font_constants(root):
    global FONT_FAMILY, FONT_NORMAL, FONT_SMALL, FONT_SMALL_BOLD, FONT_TITLE
    global FONT_CARD_TITLE, FONT_SECTION, FONT_SIDEBAR_TITLE, FONT_METRIC
    global FONT_BOLD, FONT_HERO, FONT_HERO_SMALL, FONT_CHIP

    installed = set(tkfont.families(root))
    preferred = [
        "Noto Sans KR",
        "Pretendard",
        "Inter",
        "Inter Display",
        "SUIT",
        "Segoe UI Variable Text",
        "Segoe UI Variable Display",
        "Segoe UI",
        "IBM Plex Sans KR",
        "Spoqa Han Sans Neo",
        "맑은 고딕",
        "Malgun Gothic",
    ]
    FONT_FAMILY = next((family for family in preferred if family in installed), "Malgun Gothic")
    FONT_NORMAL = font_spec(FONT_FAMILY, 10)
    FONT_SMALL = font_spec(FONT_FAMILY, 9)
    FONT_SMALL_BOLD = font_spec(FONT_FAMILY, 9, True)
    FONT_TITLE = font_spec(FONT_FAMILY, 19, True)
    FONT_CARD_TITLE = font_spec(FONT_FAMILY, 12, True)
    FONT_SECTION = font_spec(FONT_FAMILY, 14, True)
    FONT_SIDEBAR_TITLE = font_spec(FONT_FAMILY, 13, True)
    FONT_METRIC = font_spec(FONT_FAMILY, 22, True)
    FONT_BOLD = font_spec(FONT_FAMILY, 10, True)
    FONT_HERO = font_spec(FONT_FAMILY, 23, True)
    FONT_HERO_SMALL = font_spec(FONT_FAMILY, 11, True)
    FONT_CHIP = font_spec(FONT_FAMILY, 8, True)
    try:
        root.option_add("*Font", FONT_NORMAL)
    except tk.TclError:
        pass


NAV_ITEMS = [
    ("dashboard", "홈"),
    ("first7", "첫 7일"),
    ("specialties", "직무 트랙"),
    ("tour", "병동 투어"),
    ("shift", "근무 보드"),
    ("quests", "스테이션 실습"),
    ("scenarios", "환자 케이스"),
    ("english", "영어 연습"),
    ("sbar", "SBAR"),
    ("checklists", "체크리스트"),
    ("guide", "운영 가이드"),
]

WARD_ZONES = {
    "Nurse Station": {
        "title": "Nurse Station",
        "korean": "간호사 스테이션",
        "subtitle": "오늘 병동의 흐름을 읽고 우선순위를 다시 짜는 지휘석",
        "role": "담당 환자 배정, 콜라이트, EHR task, provider call, charge RN 조율이 모입니다.",
        "objects": [
            ("Assignment", "담당 환자와 acuity"),
            ("Call Board", "콜라이트와 가족 전화"),
            ("EHR Queue", "order, lab, consult"),
            ("Charge RN", "입퇴원과 escalation"),
        ],
        "common_calls": [
            "Room 414 shortness of breath",
            "ED admission ETA 25 min",
            "Family asking for lab result",
        ],
        "missions": [
            "환자 4명의 위험 신호를 색으로 표시하기",
            "Charge RN에게 입원 가능성과 staffing을 확인하기",
            "provider에게 전화할 환자와 직접 볼 환자를 구분하기",
        ],
        "decisions": [
            {
                "prompt": "콜라이트: 414호가 숨이 차다고 합니다. 스테이션에서 바로 할 일은?",
                "choices": [
                    ("환자에게 가서 호흡, 산소, 활력징후를 확인한다.", True),
                    ("콜을 끄고 medication pass 후에 간다.", False),
                    ("가족에게 먼저 전화한다.", False),
                    ("charge RN에게만 말하고 기다린다.", False),
                ],
                "feedback": "상태 변화 호소는 화면으로 처리하지 않고 bedside assessment로 이어져야 합니다.",
            }
        ],
        "color": COLORS["soft_blue"],
    },
    "Patient Room": {
        "title": "Patient Room",
        "korean": "환자 병실",
        "subtitle": "환자 확인, 안전, 사정, 교육이 실제로 일어나는 자리",
        "role": "환자를 보기 전 정보와 환자 앞에서 확인한 정보를 연결하는 공간입니다.",
        "objects": [
            ("Whiteboard", "담당자, 날짜, mobility"),
            ("Bed Safety", "낮은 침대, 잠금, clutter"),
            ("Oxygen/IV", "라인, 펌프, 산소"),
            ("Call Light", "손 닿는 위치"),
        ],
        "common_calls": [
            "Pain 8/10 after ambulation",
            "Needs bathroom, high fall risk",
            "Family wants discharge update",
        ],
        "missions": [
            "입실 전 손위생과 2개 identifier 확인",
            "fall risk와 call light 위치를 환자와 함께 확인",
            "오늘 계획을 한 문장으로 설명하고 teach-back 받기",
        ],
        "decisions": [
            {
                "prompt": "High fall risk 환자가 화장실에 혼자 가겠다고 합니다. 첫 반응은?",
                "choices": [
                    ("도움을 부르고 gait/mobility와 안전 장비를 확인한다.", True),
                    ("시간이 없으니 빨리 다녀오라고 한다.", False),
                    ("가족에게만 부탁하고 떠난다.", False),
                    ("퇴원 교육부터 마친다.", False),
                ],
                "feedback": "미국 병동에서도 fall prevention은 RN/PCT가 계속 공유하는 핵심 안전 업무입니다.",
            }
        ],
        "color": COLORS["soft_green"],
    },
    "Medication Room": {
        "title": "Medication Room",
        "korean": "투약실",
        "subtitle": "MAR와 실제 약을 연결하기 전, 실수가 멈춰야 하는 곳",
        "role": "order, allergy, due time, barcode, high-alert, waste를 차례로 확인합니다.",
        "objects": [
            ("ADC", "Pyxis/Omnicell 역할"),
            ("MAR", "due time과 route"),
            ("Scanner", "barcode workflow"),
            ("Waste Log", "controlled med 처리"),
        ],
        "common_calls": [
            "Antibiotic not in ADC",
            "Insulin due, patient not eating",
            "High-alert med needs independent check",
        ],
        "missions": [
            "09:00 due med 중 시간 민감 약 표시",
            "allergy와 route/dose를 환자 ID와 연결",
            "missing med일 때 pharmacy message 작성",
        ],
        "decisions": [
            {
                "prompt": "09:00 antibiotic이 due인데 ADC에 없습니다. 가장 먼저 확인할 곳은?",
                "choices": [
                    ("MAR/order 상태와 pharmacy dispense 기록을 확인한다.", True),
                    ("다른 환자 bin에서 같은 약을 찾아 쓴다.", False),
                    ("오늘 한 번은 생략한다.", False),
                    ("환자에게 약이 없다고만 말한다.", False),
                ],
                "feedback": "missing medication은 약국, charge RN, provider escalation까지 이어질 수 있는 system workflow입니다.",
            }
        ],
        "color": COLORS["soft_orange"],
    },
    "Supply Room": {
        "title": "Supply Room",
        "korean": "물품실",
        "subtitle": "간호가 끊기지 않게 필요한 것을 미리 고르는 공간",
        "role": "PPE, dressing kit, IV start kit, specimen cup, clean/soiled 구분을 연습합니다.",
        "objects": [
            ("PPE Cart", "glove, gown, mask"),
            ("Dressing Kit", "wound care"),
            ("Specimen", "cup, label, bag"),
            ("Par Level", "재고와 reorder"),
        ],
        "common_calls": [
            "C. diff stool sample needed",
            "Dressing change order",
            "IV site leaking",
        ],
        "missions": [
            "격리 환자 입실 전 PPE와 dedicated item 고르기",
            "dressing change order에 맞는 물품 묶기",
            "clean item과 soiled route가 섞이지 않게 설명하기",
        ],
        "decisions": [
            {
                "prompt": "Rule-out C. diff 환자 방에 들어가기 전 챙길 조합은?",
                "choices": [
                    ("gown, gloves, dedicated equipment, specimen container", True),
                    ("surgical mask와 alcohol wipe만", False),
                    ("다른 방에서 쓰던 vital machine", False),
                    ("discharge folder만", False),
                ],
                "feedback": "contact enteric 상황은 장비 구분과 손위생 방식까지 같이 생각해야 합니다.",
            }
        ],
        "color": COLORS["soft_gold"],
    },
    "Utility / Isolation": {
        "title": "Utility / Isolation",
        "korean": "격리/유틸리티",
        "subtitle": "깨끗한 물품과 오염 동선이 섞이지 않게 만드는 구역",
        "role": "isolation sign, PPE entry/exit, clean utility와 soiled utility의 흐름을 구분합니다.",
        "objects": [
            ("Signage", "precaution 종류"),
            ("PPE Exit", "탈의 순서"),
            ("Clean Utility", "청결 물품"),
            ("Soiled Route", "오염 물품 처리"),
        ],
        "common_calls": [
            "Family confused by isolation sign",
            "Need dedicated stethoscope",
            "Soiled linen route question",
        ],
        "missions": [
            "입실 전 sign을 읽고 필요한 보호구 말하기",
            "퇴실 후 손위생과 장비 처리 순서 정리",
            "가족에게 격리 이유를 겁주지 않고 설명하기",
        ],
        "decisions": [
            {
                "prompt": "가족이 '왜 우리만 가운을 입나요?'라고 묻습니다.",
                "choices": [
                    ("검사 결과 전까지 전파를 줄이기 위한 임시 안전 절차라고 설명한다.", True),
                    ("규칙이니 그냥 입으라고 말한다.", False),
                    ("별 의미 없지만 병원이 시킨다고 말한다.", False),
                    ("가족 출입을 무조건 막는다.", False),
                ],
                "feedback": "격리 교육은 이유, 기간, 가족이 할 수 있는 행동을 짧고 차분하게 알려주는 것이 좋습니다.",
            }
        ],
        "color": COLORS["soft_lavender"],
    },
    "Handoff Zone": {
        "title": "Handoff Zone",
        "korean": "인수인계 허브",
        "subtitle": "정보가 빠지면 다음 간호사의 첫 10분이 흔들리는 자리",
        "role": "ED-to-floor, provider call, bedside handoff, end-of-shift report를 압축해서 연습합니다.",
        "objects": [
            ("SBAR", "60초 보고"),
            ("Pending", "labs, tests, orders"),
            ("Safety", "fall, isolation, code"),
            ("Family", "concern, permission"),
        ],
        "common_calls": [
            "ED handoff missing code status",
            "Provider callback pending",
            "Night RN needs last PRN time",
        ],
        "missions": [
            "ED handoff에서 빠진 정보 3개 질문하기",
            "provider call 전 Situation을 한 문장으로 줄이기",
            "bedside handoff에서 환자에게 질문 기회 주기",
        ],
        "decisions": [
            {
                "prompt": "인수인계에서 'stable'이라고만 들었습니다. 바로 더 물어볼 것은?",
                "choices": [
                    ("baseline, 최근 변화, pending test, safety risk를 확인한다.", True),
                    ("stable이면 질문하지 않는다.", False),
                    ("식사 취향부터 묻는다.", False),
                    ("다음 RN에게 다시 물어보라고 한다.", False),
                ],
                "feedback": "handoff는 책임이 넘어오는 순간이므로 'stable'이라는 단어만으로는 부족합니다.",
            }
        ],
        "color": COLORS["soft_blue"],
    },
}

TOUR_MODES = {
    "입원 환자 받기": {
        "steps": [
            ("Nurse Station", "ED handoff를 받고 room readiness를 정합니다."),
            ("Supply Room", "산소, suction, PPE, admission kit를 준비합니다."),
            ("Patient Room", "도착 직후 ID, 활력징후, focused assessment를 시작합니다."),
            ("Handoff Zone", "빠진 정보와 pending order를 정리합니다."),
        ]
    },
    "09시 투약 라운드": {
        "steps": [
            ("Nurse Station", "MAR와 task queue를 훑고 우선순위를 정합니다."),
            ("Medication Room", "allergy, route, barcode, missing med를 확인합니다."),
            ("Patient Room", "2 identifiers와 education 후 투약 흐름을 진행합니다."),
            ("Nurse Station", "reassessment 시간과 지연 사유를 기록합니다."),
        ]
    },
    "격리 환자 입실": {
        "steps": [
            ("Nurse Station", "격리 order와 검사 상태를 확인합니다."),
            ("Supply Room", "PPE와 dedicated equipment를 챙깁니다."),
            ("Utility / Isolation", "signage, entry/exit routine을 확인합니다."),
            ("Patient Room", "환자와 가족에게 필요한 행동을 설명합니다."),
        ]
    },
    "퇴원 준비": {
        "steps": [
            ("Nurse Station", "discharge order, pharmacy, ride barrier를 확인합니다."),
            ("Patient Room", "medication, wound care, warning sign을 teach-back 합니다."),
            ("Supply Room", "필요한 dressing supply와 교육 자료를 확인합니다."),
            ("Handoff Zone", "pending barrier를 다음 shift나 case manager에게 넘깁니다."),
        ]
    },
    "콜라이트 우선순위": {
        "steps": [
            ("Nurse Station", "동시에 들어온 콜을 acuity와 delegation 기준으로 나눕니다."),
            ("Patient Room", "숨참이나 chest pain처럼 직접 사정이 필요한 환자를 먼저 봅니다."),
            ("Nurse Station", "PCT에게 위임 가능한 요청과 RN follow-up을 구분합니다."),
            ("Handoff Zone", "상태 변화와 follow-up 필요성을 짧게 남깁니다."),
        ]
    },
    "급성 호흡곤란": {
        "steps": [
            ("Nurse Station", "콜라이트와 telemetry/context를 확인하고 즉시 이동합니다."),
            ("Patient Room", "vitals, oxygen, lung sound, mental status를 빠르게 확인합니다."),
            ("Supply Room", "산소 관련 장비와 필요한 bedside supply를 준비합니다."),
            ("Handoff Zone", "provider call 또는 rapid response에 필요한 SBAR를 정리합니다."),
        ]
    },
    "저혈당 대응": {
        "steps": [
            ("Nurse Station", "PCT report와 EHR glucose trend를 확인합니다."),
            ("Patient Room", "의식, 증상, 식사 가능 여부를 즉시 사정합니다."),
            ("Medication Room", "unit protocol, MAR, insulin/order를 연결해 봅니다."),
            ("Handoff Zone", "recheck 시간과 반복 저혈당 가능성을 넘깁니다."),
        ]
    },
    "낙상 후 대응": {
        "steps": [
            ("Patient Room", "움직이기 전 injury, pain, mental status, vital sign을 확인합니다."),
            ("Nurse Station", "charge RN과 provider notification 흐름을 시작합니다."),
            ("Supply Room", "필요한 안전 물품과 fall prevention item을 준비합니다."),
            ("Handoff Zone", "post-fall assessment와 새 prevention plan을 넘깁니다."),
        ]
    },
    "수혈 반응 의심": {
        "steps": [
            ("Patient Room", "수혈을 멈추고 증상과 vital sign을 확인합니다."),
            ("Medication Room", "blood product, patient ID, 라인 상태와 절차를 확인합니다."),
            ("Nurse Station", "provider와 blood bank notification을 정리합니다."),
            ("Handoff Zone", "반응 의심, 조치, specimen/return status를 넘깁니다."),
        ]
    },
    "교대 전 정리": {
        "steps": [
            ("Nurse Station", "open order, pending lab, call-back, discharge barrier를 스캔합니다."),
            ("Medication Room", "late med, PRN reassessment, waste/documentation을 점검합니다."),
            ("Patient Room", "bedside safety와 환자 질문을 마지막으로 확인합니다."),
            ("Handoff Zone", "다음 RN에게 첫 10분에 필요한 정보를 압축해 넘깁니다."),
        ]
    },
}

SHIFT_EVENTS = [
    {
        "time": "06:45",
        "title": "출근, assignment 확인, safety huddle",
        "details": "Night shift 상황, staffing, admission/discharge 가능성, high-risk patient를 빠르게 파악합니다.",
        "actions": [
            "담당 환자 room number와 diagnosis를 표시한다.",
            "Fall risk, isolation, telemetry, pending test를 표시한다.",
            "Charge RN에게 오늘 병동 flow를 질문한다.",
        ],
    },
    {
        "time": "07:00",
        "title": "Night RN에게 handoff 받기",
        "details": "Handoff는 단순 정보 전달이 아니라 책임과 우선순위가 넘어오는 순간입니다.",
        "actions": [
            "Reason for admission과 overnight event를 확인한다.",
            "Lines/tubes/drains, oxygen, abnormal labs를 질문한다.",
            "Pending orders와 discharge barrier를 확인한다.",
        ],
    },
    {
        "time": "07:30",
        "title": "Chart review",
        "details": "EHR에서 orders, labs, MAR, vital trend, notes를 확인해 첫 rounds의 우선순위를 정합니다.",
        "actions": [
            "새 order와 discontinued order를 구분한다.",
            "09:00 meds와 time-sensitive tasks를 확인한다.",
            "Provider note와 plan of care를 훑는다.",
        ],
    },
    {
        "time": "08:00",
        "title": "Initial rounds",
        "details": "환자별 safety, pain, breathing, IV access, mobility, call light를 확인합니다.",
        "actions": [
            "손위생과 2 identifiers를 수행한다.",
            "Pain, airway/breathing, IV site, fall risk를 확인한다.",
            "Whiteboard와 call light 위치를 점검한다.",
        ],
    },
    {
        "time": "09:00",
        "title": "Medication pass",
        "details": "MAR, allergy, barcode workflow, patient education, reassessment 계획을 연결합니다.",
        "actions": [
            "MAR와 allergy를 확인한다.",
            "Medication indication을 환자에게 설명한다.",
            "PRN medication은 reassessment 시간을 계획한다.",
        ],
    },
    {
        "time": "10:30",
        "title": "Provider communication",
        "details": "상태 변화, abnormal lab, 통증 조절 실패 등을 SBAR로 간결하게 보고합니다.",
        "actions": [
            "Situation을 한 문장으로 정리한다.",
            "Relevant background와 current assessment를 고른다.",
            "Recommendation 또는 request를 명확히 말한다.",
        ],
    },
    {
        "time": "11:00",
        "title": "Interdisciplinary rounds",
        "details": "Provider, case manager, PT/OT, pharmacist 등과 discharge readiness와 barrier를 맞춥니다.",
        "actions": [
            "Discharge target과 barrier를 확인한다.",
            "Mobility, oxygen, home support, education need를 공유한다.",
            "환자에게 오늘 plan을 쉬운 말로 다시 설명한다.",
        ],
    },
    {
        "time": "14:00",
        "title": "New admission alert",
        "details": "ED-to-floor handoff, room prep, initial vitals, medication reconciliation 흐름이 시작됩니다.",
        "actions": [
            "방과 equipment를 준비한다.",
            "ED handoff에서 missing information을 질문한다.",
            "Admission checklist와 safety screening을 시작한다.",
        ],
    },
    {
        "time": "18:00",
        "title": "End-of-shift documentation",
        "details": "Flowsheet, nursing note, task completion, late charting risk를 점검합니다.",
        "actions": [
            "Assessment, I&O, education, reassessment를 확인한다.",
            "Open task와 pending result를 표시한다.",
            "다음 shift에 넘길 핵심 위험요소를 정리한다.",
        ],
    },
    {
        "time": "19:00",
        "title": "Bedside handoff",
        "details": "다음 RN에게 안정성, 변동사항, pending task, family concern을 넘깁니다.",
        "actions": [
            "Patient ID와 safety check를 bedside에서 확인한다.",
            "Last pain med, abnormal lab, pending test를 넘긴다.",
            "환자가 직접 질문할 수 있게 안내한다.",
        ],
    },
]


def shift_progress_percent(index):
    progress_steps = max(len(SHIFT_EVENTS) - 1, 1)
    if index >= len(SHIFT_EVENTS):
        return 100
    return int((index / progress_steps) * 100)


def shuffled_indexed_choices(choices, answer_index):
    shuffled = list(enumerate(choices))
    random.shuffle(shuffled)
    if len(shuffled) > 1 and shuffled[0][0] == answer_index:
        correct_item = shuffled.pop(0)
        shuffled.insert(random.randint(1, len(shuffled)), correct_item)
    return shuffled


def shuffled_bool_choices(choices):
    shuffled = list(choices)
    random.shuffle(shuffled)
    if len(shuffled) > 1 and shuffled[0][1]:
        correct_item = shuffled.pop(0)
        shuffled.insert(random.randint(1, len(shuffled)), correct_item)
    return shuffled


QUESTIONS = [
    {
        "title": "투약 시작 전 안전 순서",
        "station": "Medication Room",
        "prompt": "09:00 투약 라운드를 시작합니다. 가장 안전한 흐름은?",
        "choices": [
            "MAR와 order 확인 -> allergy 확인 -> 환자 2개 식별자 -> barcode -> 교육/재평가 계획",
            "ADC에서 약부터 꺼낸 뒤 병실에서 chart를 확인",
            "익숙한 약은 MAR 없이 준비하고 high-alert만 따로 확인",
            "동료가 어제 줬던 약이면 오늘도 동일하게 투약",
        ],
        "answer": 0,
        "feedback": "투약은 약을 꺼내는 행동이 아니라 order, 환자, barcode, 교육, 재평가를 연결하는 흐름입니다.",
    },
    {
        "title": "Missing Medication",
        "station": "Medication Room",
        "prompt": "09:00 antibiotic이 due인데 ADC에 없습니다.",
        "choices": [
            "MAR/order, dispense location, pharmacy message history, due time을 확인한다.",
            "다른 환자 bin에서 같은 이름의 약을 빌린다.",
            "약이 없으니 자동으로 skip 처리한다.",
            "환자에게 약국 탓이라고 설명하고 끝낸다.",
        ],
        "answer": 0,
        "feedback": "missing medication은 pharmacy communication, 지연 기록, escalation 판단이 필요한 실제 병동 workflow입니다.",
    },
    {
        "title": "Insulin Before Meal",
        "station": "Medication Room",
        "prompt": "식전 insulin이 due인데 환자가 nausea로 점심을 거의 못 먹겠다고 합니다.",
        "choices": [
            "glucose, 식사 가능성, insulin 종류/order, unit protocol을 확인하고 필요 시 provider에 문의한다.",
            "식사 여부와 상관없이 order가 있으니 그대로 투약한다.",
            "환자에게 단 음료를 마시라고 하고 투약한다.",
            "다음 shift가 결정하도록 보류만 한다.",
        ],
        "answer": 0,
        "feedback": "insulin은 식사 상태, 혈당, order/protocol을 함께 보아야 하며 단순 due time만으로 결정하지 않습니다.",
    },
    {
        "title": "Admission Call",
        "station": "Nurse Station",
        "prompt": "ED에서 pneumonia admission handoff call이 왔습니다. 먼저 확인할 정보는?",
        "choices": [
            "입원 이유, 산소/telemetry 필요, isolation, safety risk, ETA",
            "보호자가 몇 명 오는지와 주차 위치",
            "병실 TV가 작동하는지",
            "도착하면 그때 차트를 보면 되니 통화를 짧게 종료",
        ],
        "answer": 0,
        "feedback": "입원 전 handoff는 방 준비와 안전 준비를 시작하기 위한 정보 수집입니다.",
    },
    {
        "title": "Call Light Triage",
        "station": "Nurse Station",
        "prompt": "동시에 세 콜이 들어왔습니다. 숨참 호소, 물 요청, 퇴원 서류 질문. 우선순위는?",
        "choices": [
            "숨참 호소 환자를 직접 확인하고, 가능한 요청은 PCT/팀에 나눈다.",
            "가장 가까운 병실부터 순서대로 간다.",
            "퇴원 환자는 빨리 보내야 하니 서류 질문부터 해결한다.",
            "콜라이트를 모두 끄고 medication pass부터 끝낸다.",
        ],
        "answer": 0,
        "feedback": "미국 병동에서도 acuity와 delegation을 같이 판단합니다. 상태 변화는 RN assessment가 먼저입니다.",
    },
    {
        "title": "Provider Callback",
        "station": "Nurse Station",
        "prompt": "provider가 callback 했습니다. chest pain 환자 보고를 시작할 첫 문장은?",
        "choices": [
            "412호 환자가 10분 전부터 흉부 압박감 7/10을 호소해 전화드립니다.",
            "오늘 병동이 너무 바빠서요.",
            "환자가 좀 불안해 보여서요. 자세한 건 차트를 보세요.",
            "일단 order 좀 넣어주세요.",
        ],
        "answer": 0,
        "feedback": "Situation은 문제, 환자, 시간, 심각도를 한 문장으로 먼저 열어야 합니다.",
    },
    {
        "title": "Isolation Entry",
        "station": "Supply Room",
        "prompt": "Rule-out C. diff 환자 방에 들어가기 전 준비할 조합은?",
        "choices": [
            "gown, gloves, dedicated equipment, specimen container, 퇴실 후 손위생 계획",
            "surgical mask만 착용하고 빠르게 입실",
            "일반 vital machine을 여러 방에 같이 사용",
            "환자가 요청한 물컵만 챙긴다.",
        ],
        "answer": 0,
        "feedback": "contact enteric 상황은 PPE와 dedicated equipment, specimen 흐름, 손위생이 함께 움직입니다.",
    },
    {
        "title": "Dressing Supply",
        "station": "Supply Room",
        "prompt": "wound dressing change order가 있습니다. 물품실에서 먼저 해야 할 일은?",
        "choices": [
            "order에 적힌 dressing type, frequency, drainage 상태를 보고 필요한 sterile/clean supply를 고른다.",
            "늘 쓰던 거즈와 테이프만 가져간다.",
            "환자 방에 있는 아무 물품이나 사용한다.",
            "물품 선택은 RN 업무가 아니니 provider를 기다린다.",
        ],
        "answer": 0,
        "feedback": "물품 준비는 order와 환자 상태에 맞춰야 하며 부족하면 처치가 중단됩니다.",
    },
    {
        "title": "Room Entry",
        "station": "Patient Room",
        "prompt": "처음 병실에 들어갑니다. 가장 먼저 연결할 행동은?",
        "choices": [
            "손위생, 자기소개, 2개 식별자, 안전 확인을 함께 진행한다.",
            "바쁘니 vital sign부터 재고 이름 확인은 나중에 한다.",
            "가족에게 환자 상태를 먼저 자세히 설명한다.",
            "차트에 있는 이름과 비슷하면 맞다고 본다.",
        ],
        "answer": 0,
        "feedback": "환자 앞에서는 신뢰와 안전이 동시에 시작됩니다. 식별자와 손위생은 기본 흐름입니다.",
    },
    {
        "title": "Teach-back",
        "station": "Patient Room",
        "prompt": "퇴원 교육 후 환자가 고개만 끄덕입니다. 이해 확인에 가장 좋은 선택은?",
        "choices": [
            "집에서 새 약을 언제 어떻게 먹을지 본인 말로 설명해 달라고 요청한다.",
            "고개를 끄덕였으니 이해했다고 기록한다.",
            "서류를 줬으니 교육은 끝났다고 본다.",
            "가족에게만 설명하고 환자에게는 묻지 않는다.",
        ],
        "answer": 0,
        "feedback": "teach-back은 시험이 아니라 교육이 실제로 전달되었는지 확인하는 안전 장치입니다.",
    },
    {
        "title": "Clean vs Soiled",
        "station": "Utility / Isolation",
        "prompt": "오염 linen을 들고 clean utility에 들어가려는 동료를 봤습니다.",
        "choices": [
            "soiled route로 안내하고 clean supply contamination 위험을 짧게 설명한다.",
            "동료 일이므로 못 본 척한다.",
            "나중에 chart에만 적는다.",
            "clean utility 안에 잠깐 두고 바로 치우면 된다고 한다.",
        ],
        "answer": 0,
        "feedback": "clean/soiled 동선은 감염 예방의 기본이며 팀 전체가 같은 기준을 써야 합니다.",
    },
    {
        "title": "Family Privacy",
        "station": "Handoff Zone",
        "prompt": "딸이라고 주장하는 사람이 전화로 lab result를 묻습니다.",
        "choices": [
            "facility policy에 따라 caller identity와 공유 허용 범위를 먼저 확인한다.",
            "가족이면 모든 정보를 바로 알려준다.",
            "바쁘니 전화를 끊는다.",
            "간단한 lab 수치는 개인정보가 아니라고 보고 말한다.",
        ],
        "answer": 0,
        "feedback": "가족 소통도 privacy와 authorization 확인이 먼저입니다.",
    },
    {
        "title": "ED Handoff Gap",
        "station": "Handoff Zone",
        "prompt": "ED handoff에서 diagnosis만 듣고 code status, allergy, isolation 정보가 빠졌습니다.",
        "choices": [
            "도착 전 안전 준비를 위해 빠진 정보를 즉시 질문한다.",
            "병동에 도착하면 환자에게 직접 물으면 되니 넘어간다.",
            "diagnosis만 알면 충분하다고 본다.",
            "night shift가 다시 확인할 것이라고 생각한다.",
        ],
        "answer": 0,
        "feedback": "입원 handoff의 빈칸은 방 준비, 약, 격리, 응급 대응에 바로 영향을 줍니다.",
    },
    {
        "title": "End-of-shift Report",
        "station": "Handoff Zone",
        "prompt": "교대 인수인계에서 꼭 넘겨야 할 묶음은?",
        "choices": [
            "상태 변화, abnormal labs, pending tests/orders, last PRN, safety risk",
            "오늘 내가 얼마나 바빴는지",
            "환자가 좋아하는 TV 채널",
            "이미 charted 되었으니 말로 넘길 필요 없음",
        ],
        "answer": 0,
        "feedback": "다음 간호사가 첫 라운드에서 놓치면 위험해지는 정보를 우선 넘깁니다.",
    },
    {
        "title": "ED Chest Pain First Look",
        "station": "Nurse Station",
        "prompt": "ED triage에서 흉통 환자가 도착했습니다. 병동 RN이 ED report에서 반드시 받아야 할 정보는?",
        "choices": [
            "증상 시작 시간, pain score/양상, vital sign, EKG/troponin status, 산소/telemetry need",
            "환자가 어느 보험을 쓰는지와 보호자 주차 위치",
            "병실 TV와 식사 tray 준비 여부",
            "ED가 알아서 했을 것이므로 diagnosis만 받는다.",
        ],
        "answer": 0,
        "feedback": "응급/흉통 흐름은 시간, 심전도/효소, 산소와 monitoring need가 병동 준비에 바로 영향을 줍니다.",
    },
    {
        "title": "Stroke-like Symptom",
        "station": "Patient Room",
        "prompt": "환자가 갑자기 말이 어눌해지고 한쪽 손 힘이 약합니다. 가장 먼저 묶어서 확인할 것은?",
        "choices": [
            "last-known-well, baseline, focused neuro check, glucose, vital sign",
            "환자의 점심 메뉴와 보호자 도착 시간",
            "다음 rounding 때 다시 볼지 여부",
            "퇴원 서류가 준비됐는지",
        ],
        "answer": 0,
        "feedback": "신경학적 변화는 시간 정보와 glucose/vital sign, baseline 비교가 escalation의 핵심입니다.",
    },
    {
        "title": "ICU Drip Boundary",
        "station": "Medication Room",
        "prompt": "ICU/stepdown 환자가 vasopressor drip을 달고 전동될 예정입니다. 병동 RN이 확인해야 할 것은?",
        "choices": [
            "해당 unit에서 관리 가능한 drip인지, titration policy, monitoring frequency, transfer criteria",
            "drip 이름만 알면 병동에서 알아서 조절한다.",
            "환자가 안정돼 보이면 monitoring plan은 생략한다.",
            "PCT에게 blood pressure만 자주 재라고 부탁한다.",
        ],
        "answer": 0,
        "feedback": "중증/stepdown 경계에서는 unit policy와 scope, monitoring requirement를 먼저 확인해야 합니다.",
    },
    {
        "title": "Sepsis Time-sensitive Tasks",
        "station": "Nurse Station",
        "prompt": "sepsis concern 환자에게 lab, fluid, antibiotic order가 거의 동시에 들어왔습니다.",
        "choices": [
            "time-sensitive task를 표시하고 antibiotic timing, blood culture/lab, reassessment를 추적한다.",
            "차트에 order가 있으니 자동으로 진행된다고 본다.",
            "덜 바쁜 다음 shift에 넘긴다.",
            "vital sign이 조금 나쁘지만 fever가 없으면 무시한다.",
        ],
        "answer": 0,
        "feedback": "sepsis 관련 업무는 시간 민감성이 높아 task tracking과 reassessment가 중요합니다.",
    },
    {
        "title": "PACU Transfer Handoff",
        "station": "Handoff Zone",
        "prompt": "PACU에서 post-op 환자가 병동으로 올라옵니다. handoff에서 빠지면 위험한 정보는?",
        "choices": [
            "airway/sedation, anesthesia event, last opioid, drains/lines, bleeding, activity restriction",
            "수술실 직원이 친절했는지",
            "환자가 좋아하는 간식",
            "퇴원 가능 날짜만 확인",
        ],
        "answer": 0,
        "feedback": "PACU-to-floor handoff는 airway, sedation, opioid, bleeding, line/drain 정보를 중심으로 받습니다.",
    },
    {
        "title": "High-flow Oxygen Escalation",
        "station": "Patient Room",
        "prompt": "stepdown 환자의 산소 요구량이 계속 증가하고 말수가 줄었습니다.",
        "choices": [
            "respiratory assessment, mental status, O2 device/flow, vital trend를 확인하고 escalation한다.",
            "pulse ox 숫자만 괜찮으면 다음 라운드까지 기다린다.",
            "환자가 피곤해서 말이 줄었다고 단정한다.",
            "식사량부터 charting한다.",
        ],
        "answer": 0,
        "feedback": "산소 요구량 증가와 mental status 변화는 ICU transfer 가능성까지 고려해야 하는 악화 단서입니다.",
    },
    {
        "title": "Postpartum Hemorrhage Cue",
        "station": "Patient Room",
        "prompt": "산모가 어지럽고 pad가 빠르게 젖는다고 말합니다. 먼저 확인할 것은?",
        "choices": [
            "bleeding amount, fundus, vital sign, mental status를 확인하고 즉시 도움을 요청한다.",
            "정상 산후 출혈이라고 말하고 나중에 본다.",
            "신생아 feeding 교육부터 끝낸다.",
            "가족에게 pad를 더 가져오라고 부탁한다.",
        ],
        "answer": 0,
        "feedback": "L&D/mother-baby 영역은 산모 출혈 단서를 빠르게 인식하고 팀을 부르는 것이 중요합니다.",
    },
    {
        "title": "Newborn Safety",
        "station": "Patient Room",
        "prompt": "가족이 신생아를 담요와 베개 사이에 눕히려 합니다. RN의 대응은?",
        "choices": [
            "safe sleep 기준과 newborn ID/security를 설명하고 실제 침상 환경을 바로 조정한다.",
            "가족 문화이므로 관여하지 않는다.",
            "사진만 찍고 나중에 교육한다.",
            "산모가 피곤하니 아무 말도 하지 않는다.",
        ],
        "answer": 0,
        "feedback": "신생아 안전은 교육과 즉시 환경 수정이 함께 필요합니다.",
    },
    {
        "title": "Restraint / Sitter Decision",
        "station": "Nurse Station",
        "prompt": "혼돈 환자가 line을 잡아당기고 침대에서 내려오려 합니다. 우선 흐름은?",
        "choices": [
            "원인 사정, de-escalation, safety intervention, sitter/charge/provider/policy 확인 순서로 접근한다.",
            "바로 restraint부터 적용한다.",
            "PCT에게 계속 붙잡고 있으라고만 한다.",
            "환자가 협조하지 않으니 방치한다.",
        ],
        "answer": 0,
        "feedback": "restraint는 최후 수단이며 policy, order, documentation, 대안 시도 확인이 필요합니다.",
    },
    {
        "title": "Central Line Infection Prevention",
        "station": "Utility / Isolation",
        "prompt": "central line dressing이 들떠 있고 환자가 샤워 후 젖었다고 말합니다.",
        "choices": [
            "line site, dressing integrity, infection sign을 확인하고 policy에 맞춰 dressing change/notification을 진행한다.",
            "마르면 괜찮으니 그대로 둔다.",
            "환자에게 테이프를 더 붙이라고 한다.",
            "다음 주 dressing due date까지 기다린다.",
        ],
        "answer": 0,
        "feedback": "central line은 감염 예방 bundle과 dressing integrity가 매우 중요합니다.",
    },
]

SCENARIOS = {
    "Post-op Day 1": {
        "patient": "54세, laparoscopic cholecystectomy POD#1, pain 8/10",
        "goals": "pain reassessment, mobility, fall risk, discharge readiness",
        "steps": [
            {
                "prompt": "환자가 pain 8/10이라고 말합니다. 가장 먼저 할 행동은?",
                "choices": [
                    ("통증 위치/양상/악화요인과 vital sign을 확인하고 MAR의 PRN order를 검토한다.", True),
                    ("바로 discharge teaching부터 시작한다.", False),
                    ("다음 shift에 넘기고 charting만 한다.", False),
                ],
                "feedback": "Pain assessment 후 order/MAR 확인, 투약 또는 provider communication, reassessment 계획이 이어집니다.",
            },
            {
                "prompt": "PRN pain medication을 교육용으로 투약 흐름까지 설명했습니다. 다음에 빠지면 안 되는 것은?",
                "choices": [
                    ("정해진 시간 안에 pain reassessment를 계획하고 기록한다.", True),
                    ("환자가 괜찮아 보이면 재평가는 생략한다.", False),
                    ("가족에게 약 이름만 알려주고 끝낸다.", False),
                ],
                "feedback": "PRN medication은 효과와 부작용을 재평가하는 흐름까지 포함됩니다.",
            },
            {
                "prompt": "퇴원을 앞두고 환자가 집에서 뭘 조심해야 하냐고 묻습니다.",
                "choices": [
                    ("활동, wound care, pain plan, warning signs를 teach-back으로 확인한다.", True),
                    ("퇴원 서류를 읽으면 된다고 말한다.", False),
                    ("Provider가 말할 내용이라 아무 설명도 하지 않는다.", False),
                ],
                "feedback": "미국 병동에서는 patient education과 teach-back이 매우 중요한 RN 업무입니다.",
            },
        ],
    },
    "CHF Exacerbation": {
        "patient": "72세, CHF exacerbation, oxygen 2 L NC, telemetry monitoring",
        "goals": "daily weight, I&O, oxygen, abnormal lab escalation, interdisciplinary rounds",
        "steps": [
            {
                "prompt": "Morning lab에서 potassium이 낮다는 알림을 받았습니다. 다음 행동은?",
                "choices": [
                    ("환자 상태와 telemetry, 관련 meds를 확인하고 provider에게 SBAR로 보고한다.", True),
                    ("Lab 값만 적어두고 evening shift에 넘긴다.", False),
                    ("환자에게 바나나를 먹으라고 말하고 charting한다.", False),
                ],
                "feedback": "Abnormal lab은 환자 상태와 연결해 판단하고 SBAR로 escalation합니다.",
            },
            {
                "prompt": "Interdisciplinary rounds에서 RN이 공유하면 좋은 내용은?",
                "choices": [
                    ("Oxygen need, edema, I&O, weight trend, mobility/discharge barrier", True),
                    ("어제 병동이 바빴다는 내용", False),
                    ("환자가 어떤 음악을 듣는지", False),
                ],
                "feedback": "Rounds에서는 discharge readiness와 barrier를 팀이 함께 맞춥니다.",
            },
            {
                "prompt": "환자가 숨이 더 차다고 말합니다. Nurse Station에서 바로 할 일은?",
                "choices": [
                    ("환자에게 가서 respiratory assessment와 vital sign을 확인하고 필요 시 escalation한다.", True),
                    ("Call light을 끄고 나중에 간다.", False),
                    ("Case manager에게 먼저 전화한다.", False),
                ],
                "feedback": "상태 변화 호소는 bedside assessment가 먼저입니다.",
            },
        ],
    },
    "Rule-out C. diff": {
        "patient": "68세, diarrhea, contact enteric precaution pending",
        "goals": "isolation signage, PPE, supply prep, family education",
        "steps": [
            {
                "prompt": "방 앞에 contact enteric precaution sign이 있습니다. 입실 전 선택은?",
                "choices": [
                    ("Sign을 읽고 glove/gown과 dedicated equipment를 준비한다.", True),
                    ("장갑만 끼고 빠르게 들어간다.", False),
                    ("환자가 부르면 PPE 없이 먼저 들어간다.", False),
                ],
                "feedback": "Isolation sign은 방마다 필요한 entry/exit routine을 알려주는 핵심 단서입니다.",
            },
            {
                "prompt": "가족이 왜 가운을 입어야 하냐고 묻습니다. 가장 좋은 설명은?",
                "choices": [
                    ("검사 결과가 나올 때까지 감염 전파를 줄이기 위해 병실 안에서는 보호장비가 필요하다고 설명한다.", True),
                    ("병원 규칙이라 그냥 하셔야 한다고 말한다.", False),
                    ("별 의미 없지만 입으라고 한다.", False),
                ],
                "feedback": "Patient/family education은 이유를 쉬운 말로 설명하는 것이 중요합니다.",
            },
            {
                "prompt": "Supply Room에서 이 환자에게 가져갈 물품을 고른다면?",
                "choices": [
                    ("PPE, specimen container, dedicated equipment label, patient education sheet", True),
                    ("Discharge folder만 챙긴다.", False),
                    ("다른 방에서 쓰던 장비를 잠깐 가져온다.", False),
                ],
                "feedback": "Isolation 환자는 물품 준비와 장비 구분이 안전의 일부입니다.",
            },
        ],
    },
    "New Admission from ED": {
        "patient": "63세, pneumonia admission from ED, oxygen 3 L NC, ETA 20 min",
        "goals": "ED handoff, room readiness, initial assessment, admission checklist",
        "steps": [
            {
                "prompt": "ED에서 새 입원 환자 handoff call이 왔습니다. RN이 먼저 확인할 정보는?",
                "choices": [
                    ("reason for admission, oxygen/telemetry need, isolation, safety risk, ETA를 확인한다.", True),
                    ("도착하면 그때 차트를 보기로 하고 통화를 짧게 끝낸다.", False),
                    ("가족 연락처부터 묻고 임상 정보는 나중에 본다.", False),
                ],
                "feedback": "입원 전 handoff는 방 준비와 안전 준비를 위한 정보 수집입니다.",
            },
            {
                "prompt": "환자가 도착하기 전 방 준비에서 우선순위는?",
                "choices": [
                    ("oxygen/suction, bed safety, call light, needed equipment, isolation sign 여부를 확인한다.", True),
                    ("환자 교육 자료만 책상에 올려둔다.", False),
                    ("다른 환자 medication pass가 끝날 때까지 아무 준비도 하지 않는다.", False),
                ],
                "feedback": "Admission readiness는 환자가 문에 들어오기 전에 시작됩니다.",
            },
            {
                "prompt": "도착 직후 initial workflow에 포함될 항목은?",
                "choices": [
                    ("patient ID, vitals, focused assessment, allergy, medication reconciliation 시작을 연결한다.", True),
                    ("퇴원 교육을 먼저 시작한다.", False),
                    ("charting은 night shift에게 넘긴다.", False),
                ],
                "feedback": "초기 입원 흐름은 assessment와 안전 screening, documentation이 함께 움직입니다.",
            },
        ],
    },
    "Hypoglycemia Before Lunch": {
        "patient": "58세, diabetes, lunch 전 glucose 58 mg/dL alert",
        "goals": "glucose protocol awareness, symptom check, recheck, provider notification",
        "steps": [
            {
                "prompt": "PCT가 glucose 58이라고 보고했습니다. 가장 먼저 할 일은?",
                "choices": [
                    ("환자에게 바로 가서 증상과 의식 상태를 확인하고 unit protocol/MAR를 확인한다.", True),
                    ("PCT에게 간식을 주라고만 하고 다른 일을 계속한다.", False),
                    ("식사 tray가 오면 괜찮을 것이라며 기다린다.", False),
                ],
                "feedback": "Low glucose는 숫자만 보는 것이 아니라 환자 상태 확인과 protocol 흐름이 함께 필요합니다.",
            },
            {
                "prompt": "교육용 protocol에 따라 intervention을 설명했습니다. 다음 핵심은?",
                "choices": [
                    ("정해진 시간에 glucose recheck를 계획하고 결과를 기록한다.", True),
                    ("한 번 올랐을 것이라고 가정하고 recheck를 생략한다.", False),
                    ("family에게 혈당계를 사라고 말하고 종료한다.", False),
                ],
                "feedback": "Hypoglycemia workflow는 intervention보다 recheck와 trend 확인이 더 중요할 때가 많습니다.",
            },
            {
                "prompt": "반복적으로 낮은 혈당이 나오고 식사를 못 하는 상황입니다.",
                "choices": [
                    ("provider에게 SBAR로 보고하고 medication/meal plan 관련 next step을 확인한다.", True),
                    ("다음 shift가 알아서 보도록 handoff만 한다.", False),
                    ("환자에게 단 음식을 계속 먹으라고만 한다.", False),
                ],
                "feedback": "반복되는 abnormal finding은 trend와 context를 묶어서 escalation합니다.",
            },
        ],
    },
    "Chest Pain on Telemetry": {
        "patient": "66세, telemetry patient, sudden chest pressure 7/10",
        "goals": "rapid assessment, EKG/order awareness, provider escalation, focused handoff",
        "steps": [
            {
                "prompt": "환자가 갑자기 chest pressure를 호소합니다. 첫 반응은?",
                "choices": [
                    ("bedside로 가서 pain characteristics, vitals, oxygen status, telemetry context를 확인한다.", True),
                    ("call light을 끄고 rounding 때 다시 본다.", False),
                    ("환자에게 anxiety일 수 있다고 말하고 안심만 시킨다.", False),
                ],
                "feedback": "Chest pain은 직접 assessment와 즉시 escalation 준비가 필요한 상황입니다.",
            },
            {
                "prompt": "Provider에게 전화할 때 SBAR의 핵심 Background는?",
                "choices": [
                    ("admission reason, cardiac history, current vitals, telemetry/lab context, meds를 간결히 전달한다.", True),
                    ("환자가 걱정이 많다는 느낌만 전달한다.", False),
                    ("내가 점심을 못 먹었다는 상황을 먼저 설명한다.", False),
                ],
                "feedback": "SBAR는 provider가 즉시 판단할 수 있는 관련 배경만 압축합니다.",
            },
            {
                "prompt": "새 order가 들어왔습니다. RN workflow에서 빠지면 안 되는 것은?",
                "choices": [
                    ("order 확인, task 우선순위 재조정, patient monitoring, documentation을 연결한다.", True),
                    ("order가 들어왔으니 확인 없이 끝났다고 생각한다.", False),
                    ("provider가 담당하므로 RN charting은 필요 없다고 본다.", False),
                ],
                "feedback": "상태 변화 후에는 order 확인과 monitoring, documentation이 이어져야 합니다.",
            },
        ],
    },
    "Unwitnessed Fall": {
        "patient": "79세, fall risk, bathroom 근처에서 unwitnessed fall 발견",
        "goals": "post-fall assessment, safety, notification, event reporting",
        "steps": [
            {
                "prompt": "환자가 바닥에 앉아 있는 것을 발견했습니다. 가장 먼저?",
                "choices": [
                    ("움직이기 전 patient safety와 injury assessment, vitals/mental status를 확인하고 도움을 요청한다.", True),
                    ("일단 빨리 침대로 옮긴 뒤 생각한다.", False),
                    ("환자가 괜찮다 하면 charting 없이 넘어간다.", False),
                ],
                "feedback": "Fall event는 이동보다 assessment와 안전 확보가 먼저입니다.",
            },
            {
                "prompt": "Post-fall communication에 포함될 대상은?",
                "choices": [
                    ("charge RN, provider, family/guardian per policy, next shift handoff를 고려한다.", True),
                    ("PCT에게만 말하고 끝낸다.", False),
                    ("환자가 원하지 않으면 아무에게도 말하지 않는다.", False),
                ],
                "feedback": "Fall은 unit safety와 policy workflow가 함께 움직이는 사건입니다.",
            },
            {
                "prompt": "사건 이후 documentation에서 중요한 관점은?",
                "choices": [
                    ("발견 상황, assessment, notification, intervention, prevention plan을 객관적으로 기록한다.", True),
                    ("누가 잘못했는지 중심으로 감정적으로 기록한다.", False),
                    ("incident report만 쓰면 charting은 생략한다.", False),
                ],
                "feedback": "Charting은 객관적 환자 기록이고, event report는 별도 safety reporting 흐름입니다.",
            },
        ],
    },
    "Discharge Delay & Teach-back": {
        "patient": "45세, discharge order entered, ride unavailable and new medication confusion",
        "goals": "discharge barrier, patient education, case management, teach-back",
        "steps": [
            {
                "prompt": "퇴원 order는 났지만 환자가 새 약 복용법을 이해하지 못합니다.",
                "choices": [
                    ("medication purpose, timing, warning signs를 쉬운 말로 설명하고 teach-back을 요청한다.", True),
                    ("약국 설명서를 읽으면 된다고 말한다.", False),
                    ("퇴원 order가 있으니 교육 없이 보내도 된다고 본다.", False),
                ],
                "feedback": "Discharge는 order가 아니라 안전한 transition이 목표입니다.",
            },
            {
                "prompt": "환자가 집에 갈 ride가 없다고 말합니다.",
                "choices": [
                    ("case manager/social work 또는 charge RN에게 discharge barrier로 공유한다.", True),
                    ("환자가 알아서 해야 하니 병동 업무와 무관하다고 본다.", False),
                    ("다음 shift에 아무 말 없이 넘긴다.", False),
                ],
                "feedback": "Transportation과 home support는 미국 병동 discharge planning의 현실적인 barrier입니다.",
            },
            {
                "prompt": "End-of-shift handoff에 이 환자를 넘긴다면?",
                "choices": [
                    ("discharge order status, education gap, ride barrier, pending pharmacy/meds를 전달한다.", True),
                    ("퇴원 예정이라고만 말한다.", False),
                    ("환자가 젊으니 특별히 넘길 정보가 없다고 한다.", False),
                ],
                "feedback": "퇴원 환자도 pending barrier가 있으면 handoff의 핵심 대상입니다.",
            },
        ],
    },
    "Missing Medication": {
        "patient": "61세, 09:00 antibiotic due, medication not available in ADC",
        "goals": "MAR check, pharmacy communication, timing awareness, patient update",
        "steps": [
            {
                "prompt": "09:00 antibiotic이 due인데 ADC에 약이 없습니다. 먼저 확인할 것은?",
                "choices": [
                    ("MAR/order status, due time, dispense location, pharmacy message history를 확인한다.", True),
                    ("약이 없으니 그냥 생략한다.", False),
                    ("다른 환자 약에서 비슷한 것을 찾아본다.", False),
                ],
                "feedback": "Missing med는 투약 안전과 timing을 모두 고려해 system workflow로 해결합니다.",
            },
            {
                "prompt": "Pharmacy에 메시지를 보낼 때 포함하면 좋은 정보는?",
                "choices": [
                    ("patient, medication, dose/time, location, urgency, previous request 여부를 간결히 적는다.", True),
                    ("약 없어요라고만 보낸다.", False),
                    ("감정적인 불만을 길게 쓴다.", False),
                ],
                "feedback": "Pharmacy communication도 SBAR처럼 필요한 정보를 압축하는 것이 좋습니다.",
            },
            {
                "prompt": "투약이 지연될 가능성이 있습니다. RN의 다음 행동은?",
                "choices": [
                    ("charge RN/provider escalation 필요성을 판단하고 patient에게 delay를 설명하며 기록한다.", True),
                    ("아무에게도 말하지 않고 퇴근 전까지 기다린다.", False),
                    ("환자에게 약이 중요하지 않다고 말한다.", False),
                ],
                "feedback": "Time-sensitive medication은 delay communication과 documentation이 중요합니다.",
            },
        ],
    },
    "Sepsis Screen Alert": {
        "patient": "70세, UTI admission, fever, tachycardia, new confusion",
        "goals": "trend recognition, sepsis screening awareness, escalation, reassessment",
        "steps": [
            {
                "prompt": "EHR sepsis alert가 뜨고 환자가 더 혼돈스러워 보입니다.",
                "choices": [
                    ("vitals trend, mental status change, labs/orders를 확인하고 bedside assessment를 우선한다.", True),
                    ("alert fatigue라고 생각하고 닫는다.", False),
                    ("혼돈은 나이 때문이라고 단정한다.", False),
                ],
                "feedback": "Alert는 자동 판단이 아니라 RN assessment와 trend recognition을 촉발하는 신호입니다.",
            },
            {
                "prompt": "Provider에게 보고할 때 핵심은?",
                "choices": [
                    ("baseline 대비 변화, fever/HR/BP, infection source, urine/output, current antibiotics를 묶어 말한다.", True),
                    ("컴퓨터가 alert를 띄웠다고만 말한다.", False),
                    ("환자가 까다롭다고 표현한다.", False),
                ],
                "feedback": "Sepsis concern은 변화와 trend, source, current treatment를 연결해 보고합니다.",
            },
            {
                "prompt": "새 order와 monitoring 계획이 생겼습니다.",
                "choices": [
                    ("time-sensitive tasks를 확인하고 reassessment, documentation, next shift handoff를 준비한다.", True),
                    ("order가 많아졌으니 documentation은 생략한다.", False),
                    ("PCT에게 모두 맡긴다.", False),
                ],
                "feedback": "Sepsis-related workflow는 시간 민감성이 높아 task tracking과 handoff가 중요합니다.",
            },
        ],
    },
    "Difficult Family Call": {
        "patient": "82세, confusion, daughter calls repeatedly asking for details",
        "goals": "privacy awareness, therapeutic communication, escalation boundary, documentation",
        "steps": [
            {
                "prompt": "딸이라고 주장하는 사람이 전화로 lab result와 medication을 묻습니다.",
                "choices": [
                    ("facility policy에 따라 caller identity/permission을 확인하고 공유 가능한 범위를 지킨다.", True),
                    ("가족이라고 하니 모든 정보를 바로 알려준다.", False),
                    ("바쁘니 전화를 끊는다.", False),
                ],
                "feedback": "미국 병동에서는 family communication에도 privacy와 authorization 확인이 중요합니다.",
            },
            {
                "prompt": "상대가 화를 내며 provider와 바로 통화하겠다고 합니다.",
                "choices": [
                    ("감정을 인정하고, 전달 가능한 next step과 callback plan을 명확히 설명한다.", True),
                    ("같이 언성을 높인다.", False),
                    ("무조건 provider가 지금 전화할 것이라고 약속한다.", False),
                ],
                "feedback": "Therapeutic communication은 공감과 경계, 현실적인 plan을 함께 세우는 기술입니다.",
            },
            {
                "prompt": "통화 후 RN이 남겨야 할 것은?",
                "choices": [
                    ("caller, concern, shared information, escalation/callback plan을 객관적으로 기록한다.", True),
                    ("기분 나빴다고만 기록한다.", False),
                    ("가족 전화는 charting 대상이 아니라고 본다.", False),
                ],
                "feedback": "Family communication은 care coordination과 risk management 관점에서 기록 가치가 있습니다.",
            },
        ],
    },
    "New Neuro Change": {
        "patient": "76세, stroke history, 갑자기 말이 어눌하고 오른손 힘이 약해짐",
        "goals": "baseline comparison, focused neuro check, rapid escalation, last-known-well",
        "steps": [
            {
                "prompt": "PCT가 '환자 말이 이상하다'고 보고합니다. 첫 행동은?",
                "choices": [
                    ("즉시 bedside에서 baseline 대비 변화, speech, weakness, vital sign, glucose를 확인한다.", True),
                    ("환자가 피곤해서 그럴 수 있으니 다음 라운드 때 본다.", False),
                    ("가족에게 먼저 전화해 평소 말투를 묻고 기다린다.", False),
                ],
                "feedback": "신경학적 변화는 시간 정보와 baseline 비교가 중요합니다. bedside assessment가 먼저입니다.",
            },
            {
                "prompt": "provider/rapid response에 보고할 때 꼭 포함할 정보는?",
                "choices": [
                    ("last-known-well, 새 증상, baseline, glucose/vitals, anticoagulant 여부를 묶어 말한다.", True),
                    ("말이 조금 이상하다고만 말한다.", False),
                    ("환자가 원래 예민하다고 설명한다.", False),
                ],
                "feedback": "stroke concern은 시간을 잃지 않도록 핵심 정보를 압축해 escalation합니다.",
            },
            {
                "prompt": "새 order와 transport 준비가 생겼습니다. RN이 이어서 챙길 것은?",
                "choices": [
                    ("monitoring, safety, IV access, pending result, family update 범위, documentation을 정리한다.", True),
                    ("transport가 오면 모든 책임이 넘어간다고 본다.", False),
                    ("다음 shift가 바통을 받도록 charting을 미룬다.", False),
                ],
                "feedback": "상태 변화 후에는 order 수행과 계속 관찰, 기록, handoff가 같이 갑니다.",
            },
        ],
    },
    "Transfusion Reaction Concern": {
        "patient": "59세, anemia, PRBC transfusion 중 chills와 fever 호소",
        "goals": "transfusion safety, stop-and-assess, notification, specimen/blood bank workflow",
        "steps": [
            {
                "prompt": "수혈 시작 20분 후 환자가 오한과 열감을 말합니다. 가장 먼저?",
                "choices": [
                    ("수혈을 멈추고 환자 assessment와 vital sign을 확인하며 기관 절차에 따라 보고한다.", True),
                    ("오한은 흔하니 속도를 낮추고 계속 진행한다.", False),
                    ("blanket만 덮어주고 나중에 확인한다.", False),
                ],
                "feedback": "수혈 반응 의심 시에는 멈추고 사정, 라인/혈액 확인, provider/blood bank workflow로 이어집니다.",
            },
            {
                "prompt": "보고할 때 확인해야 할 자료는?",
                "choices": [
                    ("patient ID, blood product, 시작 시간, 증상, vital trend, line 상태를 확인한다.", True),
                    ("혈액형은 혈액은행이 봤으니 확인하지 않는다.", False),
                    ("환자가 춥다고 한 말만 전달한다.", False),
                ],
                "feedback": "수혈 안전은 식별 정보와 반응 시점, 증상, vital trend가 함께 필요합니다.",
            },
            {
                "prompt": "이후 handoff에 남길 핵심은?",
                "choices": [
                    ("reaction concern, interventions, notifications, specimen/return status, monitoring plan", True),
                    ("수혈을 하다가 멈췄다고만 전달", False),
                    ("provider가 알았으니 handoff는 생략", False),
                ],
                "feedback": "다음 RN이 감시해야 할 위험과 pending workflow를 명확히 넘깁니다.",
            },
        ],
    },
    "Opioid Sedation Risk": {
        "patient": "49세, post-op pain, opioid PRN 후 RR 9/min, very drowsy",
        "goals": "sedation assessment, respiratory safety, reassessment, escalation",
        "steps": [
            {
                "prompt": "PRN opioid 투약 후 환자가 많이 졸리고 호흡수가 9/min입니다.",
                "choices": [
                    ("sedation level, respiratory status, oxygen saturation, vital sign을 확인하고 즉시 도움을 요청한다.", True),
                    ("잠든 것이니 방해하지 않는다.", False),
                    ("pain score가 낮아졌으니 좋은 반응이라고 기록한다.", False),
                ],
                "feedback": "opioid 투약 후에는 통증뿐 아니라 sedation과 호흡 상태 재평가가 중요합니다.",
            },
            {
                "prompt": "provider에게 보고할 때 핵심은?",
                "choices": [
                    ("투약 시간/용량, 현재 sedation/RR/O2, baseline, 적용 중인 산소와 필요한 next step", True),
                    ("환자가 조금 졸리다고만 말한다.", False),
                    ("약 이름은 차트에 있으니 말하지 않는다.", False),
                ],
                "feedback": "약물 관련 상태 변화는 시간, 용량, 현재 assessment를 같이 보고해야 판단이 빨라집니다.",
            },
            {
                "prompt": "이후 같은 shift에서 해야 할 일은?",
                "choices": [
                    ("reassessment 간격, safety, 다음 pain plan, documentation, handoff를 조정한다.", True),
                    ("한 번 보고했으니 더 볼 필요가 없다.", False),
                    ("환자가 깨어날 때까지 charting을 모두 미룬다.", False),
                ],
                "feedback": "sedation risk는 한 번 보고로 끝나지 않고 monitoring plan이 이어져야 합니다.",
            },
        ],
    },
    "Rapid Discharge Pressure": {
        "patient": "64세, discharge order entered, new anticoagulant started, pharmacy delay",
        "goals": "safe transition, medication education, barrier communication, team coordination",
        "steps": [
            {
                "prompt": "침상 회전을 위해 빨리 퇴원시키자는 압박이 있지만 새 항응고제 교육이 안 끝났습니다.",
                "choices": [
                    ("퇴원 준비 상태와 교육 gap을 charge RN/team에 공유하고 teach-back을 완료한다.", True),
                    ("order가 있으니 교육이 부족해도 먼저 보낸다.", False),
                    ("약 설명은 약국 업무라 RN은 관여하지 않는다.", False),
                ],
                "feedback": "퇴원은 병상 비우기가 아니라 안전한 transition입니다. 교육 gap은 실제 barrier입니다.",
            },
            {
                "prompt": "환자가 '피가 멈추지 않으면 어떻게 해요?'라고 묻습니다.",
                "choices": [
                    ("warning signs, 언제 연락할지, 복용 시간, missed dose 대처를 쉬운 말로 확인한다.", True),
                    ("인터넷을 찾아보라고 한다.", False),
                    ("무서워하지 말라고만 말한다.", False),
                ],
                "feedback": "새로운 고위험 약은 환자가 집에서 판단할 수 있는 기준까지 교육해야 합니다.",
            },
            {
                "prompt": "약국 조제가 늦어지고 ride는 도착했습니다. handoff/communication은?",
                "choices": [
                    ("pharmacy delay, education status, ride timing, team notification을 정리해 공유한다.", True),
                    ("ride가 왔으니 약은 나중에 찾으라고 보낸다.", False),
                    ("다음 shift에게 퇴원이라고만 말한다.", False),
                ],
                "feedback": "discharge barrier는 여러 부서와 시간이 얽히므로 상태를 명확히 공유해야 합니다.",
            },
        ],
    },
}

FIRST_WEEK_DAYS = [
    {
        "day": 1,
        "time": "Day 1 / 06:35",
        "title": "첫 출근, badge, preceptor, unit culture",
        "setting": "직원 출입구에서 badge를 받고 4 West로 올라갑니다. preceptor는 빠르게 말하고, charge RN은 오늘 shadowing 범위를 짧게 설명합니다.",
        "scene": "orientation",
        "assignment": "목표: 관찰자로 남되, HIPAA와 unit etiquette를 첫날부터 지키기",
        "cues": [
            ("Badge", "환자구역에서는 항상 보이게 착용"),
            ("Phone", "환자 정보 사진/메모 금지"),
            ("Break room", "동료 대화와 환자 정보 경계"),
            ("Preceptor", "모르면 바로 clarify"),
        ],
        "risk": "첫날은 '잘 보이고 싶어서' 모르는 척 넘어가거나, 휴대폰에 patient detail을 적는 실수를 하기 쉽습니다.",
        "choices": [
            {
                "text": "preceptor에게 오늘 내가 직접 해도 되는 범위와 반드시 observe만 해야 하는 범위를 확인한다.",
                "best": True,
                "effect": {"safety": 2, "team": 2, "law": 1, "confidence": 1},
                "feedback": "좋은 시작입니다. 미국 병동에서는 scope, facility policy, preceptor expectation을 초반에 맞추는 것이 안전합니다.",
            },
            {
                "text": "잘하는 것처럼 보이기 위해 모르는 단어와 시스템은 일단 넘어간다.",
                "best": False,
                "effect": {"safety": -1, "team": -1, "law": 0, "confidence": -1},
                "feedback": "초반에 모르는 것을 숨기면 EHR, medication, escalation에서 더 큰 위험으로 이어집니다. clarify는 약점이 아니라 안전 행동입니다.",
            },
            {
                "text": "환자 room number와 diagnosis를 휴대폰 메모장에 적어두고 집에서 다시 공부한다.",
                "best": False,
                "effect": {"safety": -1, "team": 0, "law": -3, "confidence": 0},
                "feedback": "개인기기에 patient detail을 남기는 것은 privacy/HIPAA 리스크가 큽니다. 시설이 허용한 도구와 de-identified learning note를 구분해야 합니다.",
            },
            {
                "text": "break room에서 들은 환자 이야기를 한국 친구에게 익명이라며 메시지로 공유한다.",
                "best": False,
                "effect": {"safety": -1, "team": -1, "law": -3, "confidence": 0},
                "feedback": "익명이라고 생각해도 조합 가능한 정보가 있으면 PHI 문제가 될 수 있습니다. 환자 이야기는 업무 목적 안에서만 다루는 습관이 필요합니다.",
            },
        ],
        "debrief": "첫날의 성공 기준은 많이 아는 척이 아니라, 모르는 것을 안전하게 드러내고 환자 정보를 다루는 경계를 익히는 것입니다.",
        "bridge": "다음: EHR login, MAR, medication room 접근을 경험합니다.",
    },
    {
        "day": 2,
        "time": "Day 2 / 08:45",
        "title": "EHR, MAR, ADC, 투약실 접근",
        "setting": "preceptor가 09:00 medication pass를 보여줍니다. EHR task list, MAR, allergy, ADC 화면이 동시에 열려 있습니다.",
        "scene": "medroom",
        "assignment": "목표: 약을 꺼내기 전 정보 흐름을 읽고, controlled substance/waste 경계를 이해하기",
        "cues": [
            ("MAR", "due time, route, hold parameter"),
            ("Allergy", "band와 EHR 모두 확인"),
            ("ADC", "dispense location / missing med"),
            ("Waste", "witness, policy, documentation"),
        ],
        "risk": "한국에서의 숙련도가 있어도 미국 병동의 ADC, barcode, narcotic waste, policy wording은 새 시스템입니다.",
        "choices": [
            {
                "text": "MAR, allergy, hold parameter, barcode 흐름을 preceptor에게 말로 확인한 뒤 medication room에 들어간다.",
                "best": True,
                "effect": {"safety": 3, "team": 1, "law": 1, "confidence": 1},
                "feedback": "정확합니다. 숙련 RN이라도 새 시설의 medication workflow는 verbalize하면서 맞추는 것이 안전합니다.",
            },
            {
                "text": "한국에서 투약 경험이 많으니 ADC만 익히면 된다고 보고 MAR review는 preceptor에게 맡긴다.",
                "best": False,
                "effect": {"safety": -2, "team": -1, "law": 0, "confidence": -1},
                "feedback": "경험은 강점이지만 새 환경에서는 system workflow가 다릅니다. MAR/order/allergy/hold parameter를 직접 연결해야 합니다.",
            },
            {
                "text": "controlled substance waste가 남았는데 preceptor가 바빠 보여서 나중에 혼자 처리한다.",
                "best": False,
                "effect": {"safety": -2, "team": -1, "law": -2, "confidence": -1},
                "feedback": "controlled substances는 facility policy, witness, documentation이 중요합니다. 바빠도 절차를 생략하지 않아야 합니다.",
            },
            {
                "text": "환자가 약 이름을 물으면 'doctor ordered it'이라고만 답하고 투약을 끝낸다.",
                "best": False,
                "effect": {"safety": -1, "team": 0, "law": 0, "confidence": -1},
                "feedback": "미국 병동에서는 patient education과 teach-back이 RN workflow 일부입니다. indication과 주요 주의점을 설명해야 합니다.",
            },
        ],
        "debrief": "Day 2의 핵심은 '내가 아는 약'이 아니라 '이 시설에서 안전하게 투약되는 시스템'을 익히는 것입니다.",
        "bridge": "다음: 실제 assignment와 PCT delegation을 경험합니다.",
    },
    {
        "day": 3,
        "time": "Day 3 / 07:15",
        "title": "처음 받는 partial assignment와 delegation",
        "setting": "preceptor가 환자 2명을 맡겨봅니다. 한 명은 CHF, 한 명은 post-op입니다. PCT는 vitals와 glucose를 돕고 있습니다.",
        "scene": "assignment",
        "assignment": "목표: RN assessment와 위임 가능한 task를 구분하고, 콜라이트 우선순위를 잡기",
        "cues": [
            ("414 CHF", "O2 2L, I&O, daily weight"),
            ("418 Post-op", "pain reassessment due"),
            ("PCT", "vitals/glucose report"),
            ("Call light", "bathroom, pain, SOB"),
        ],
        "risk": "한국 RN은 직접 해결하는 습관이 강할 수 있지만, 미국 병동에서는 delegation과 follow-up accountability가 함께 갑니다.",
        "choices": [
            {
                "text": "SOB 콜은 직접 bedside assessment로 가고, 물/blanket 요청은 PCT에게 위임하며 follow-up 시간을 정한다.",
                "best": True,
                "effect": {"safety": 3, "team": 2, "law": 0, "confidence": 1},
                "feedback": "좋습니다. acuity와 RN-only assessment, 위임 가능한 comfort task를 분리했습니다.",
            },
            {
                "text": "PCT에게 모든 콜라이트 대응을 부탁하고 chart review를 먼저 끝낸다.",
                "best": False,
                "effect": {"safety": -3, "team": -1, "law": 0, "confidence": -1},
                "feedback": "상태 변화 가능성이 있는 콜은 RN assessment가 먼저입니다. delegation은 책임 회피가 아니라 팀 기반 수행입니다.",
            },
            {
                "text": "모든 일을 직접 하려고 PCT 도움을 거절한다.",
                "best": False,
                "effect": {"safety": -1, "team": -2, "law": 0, "confidence": -1},
                "feedback": "미국 병동에서는 PCT와 협업하는 능력도 중요한 적응 역량입니다. 직접 하는 것과 적절히 위임하는 것의 균형이 필요합니다.",
            },
            {
                "text": "preceptor에게 내가 우선순위를 이렇게 잡은 이유를 짧게 말하고 확인받는다.",
                "best": True,
                "effect": {"safety": 2, "team": 2, "law": 0, "confidence": 2},
                "feedback": "아주 좋습니다. orientation 중에는 판단 과정을 말로 드러내면 preceptor가 더 정확히 코칭할 수 있습니다.",
            },
        ],
        "debrief": "숙련 RN이라도 미국 병동 적응 초반에는 clinical judgment를 '보여주는' 연습이 필요합니다.",
        "bridge": "다음: privacy, interpreter, 가족 전화 상황을 만납니다.",
    },
    {
        "day": 4,
        "time": "Day 4 / 13:20",
        "title": "HIPAA, 가족 전화, interpreter etiquette",
        "setting": "가족이라고 주장하는 사람이 전화로 lab result를 묻고, 다른 병실에서는 영어가 불편한 환자가 가족에게 통역을 부탁하려 합니다.",
        "scene": "privacy",
        "assignment": "목표: 친절함과 privacy boundary를 동시에 지키기",
        "cues": [
            ("Phone call", "caller identity / permission"),
            ("Hallway", "환자 이름 대화 주의"),
            ("Interpreter", "facility resource 우선"),
            ("Family", "supporter와 decision-maker 구분"),
        ],
        "risk": "미국에서는 '가족이니까 당연히 알려준다'가 통하지 않을 수 있습니다. privacy, authorization, interpreter policy를 확인해야 합니다.",
        "choices": [
            {
                "text": "facility policy에 따라 caller identity와 공유 허용 범위를 확인한 뒤, 필요한 경우 callback plan을 세운다.",
                "best": True,
                "effect": {"safety": 1, "team": 1, "law": 3, "confidence": 1},
                "feedback": "좋습니다. 가족 소통은 친절해야 하지만, permission과 privacy boundary가 먼저입니다.",
            },
            {
                "text": "딸이라고 하니 lab result와 medication plan을 바로 자세히 알려준다.",
                "best": False,
                "effect": {"safety": -1, "team": 0, "law": -3, "confidence": -1},
                "feedback": "가족이라고 주장해도 authorization 확인이 필요합니다. HIPAA/privacy risk가 생길 수 있습니다.",
            },
            {
                "text": "영어가 불편한 환자에게 가족이 있으니 가족에게 통역을 맡긴다.",
                "best": False,
                "effect": {"safety": -2, "team": 0, "law": -2, "confidence": -1},
                "feedback": "중요한 의료 설명에는 facility interpreter resource를 우선 고려해야 합니다. 가족 통역은 정확성, 부담, privacy 문제가 있습니다.",
            },
            {
                "text": "엘리베이터에서 preceptor에게 환자 이름과 diagnosis를 말하려다 멈추고, private area에서 논의하자고 한다.",
                "best": True,
                "effect": {"safety": 1, "team": 1, "law": 2, "confidence": 1},
                "feedback": "좋은 boundary입니다. public area에서 patient detail을 피하는 습관은 미국 병동 적응의 기본입니다.",
            },
        ],
        "debrief": "Day 4는 clinical skill보다 professional boundary가 핵심입니다. 친절함과 정보보호는 동시에 갈 수 있습니다.",
        "bridge": "다음: provider call과 escalation을 경험합니다.",
    },
    {
        "day": 5,
        "time": "Day 5 / 10:35",
        "title": "provider call, RT, rapid change",
        "setting": "CHF 환자가 숨이 더 차다고 말합니다. O2 sat이 낮아지고 crackles가 증가했습니다. provider callback은 짧고 빠릅니다.",
        "scene": "escalation",
        "assignment": "목표: assessment 단서, SBAR, escalation timing을 연결하기",
        "cues": [
            ("Vitals", "O2 sat 89%, RR 26"),
            ("Assessment", "increased crackles"),
            ("Orders", "diuretic, telemetry"),
            ("Team", "provider / RT / charge RN"),
        ],
        "risk": "미국 병동에서는 provider와 통화할 때 간결함이 중요하지만, 필요한 정보가 빠지면 다시 전화해야 하고 환자 안전이 늦어집니다.",
        "choices": [
            {
                "text": "환자 사정과 vital trend를 확인한 뒤, Situation을 한 문장으로 정리하고 SBAR로 provider에게 전화한다.",
                "best": True,
                "effect": {"safety": 3, "team": 2, "law": 0, "confidence": 2},
                "feedback": "좋습니다. provider call은 감정 표현이 아니라 판단에 필요한 단서를 압축해 전달하는 기술입니다.",
            },
            {
                "text": "provider가 바쁠 것 같아 다음 rounds까지 기다린다.",
                "best": False,
                "effect": {"safety": -3, "team": -1, "law": 0, "confidence": -1},
                "feedback": "호흡 상태 변화는 기다릴 문제가 아닙니다. escalation timing은 미국 병동에서 매우 중요한 안전 역량입니다.",
            },
            {
                "text": "전화 첫 문장에 'I am new here'부터 길게 설명한다.",
                "best": False,
                "effect": {"safety": -1, "team": -1, "law": 0, "confidence": -1},
                "feedback": "신입/오리엔티라는 사실보다 환자 상황이 먼저입니다. 필요하면 마지막에 preceptor와 함께 있다고 덧붙일 수 있습니다.",
            },
            {
                "text": "preceptor와 charge RN에게 내 escalation 판단을 공유하고 RT 도움 필요성을 함께 확인한다.",
                "best": True,
                "effect": {"safety": 2, "team": 2, "law": 0, "confidence": 1},
                "feedback": "좋습니다. orientation 중에는 혼자 영웅처럼 해결하기보다 팀 리소스를 적절히 부르는 것이 안전합니다.",
            },
        ],
        "debrief": "Day 5의 핵심은 '영어를 완벽히 말하기'가 아니라 환자 변화 단서를 빠뜨리지 않고 구조화해 말하는 것입니다.",
        "bridge": "다음: discharge pressure와 case management를 경험합니다.",
    },
    {
        "day": 6,
        "time": "Day 6 / 15:40",
        "title": "discharge pressure, pharmacy delay, teach-back",
        "setting": "bed manager는 discharge를 서두르고, 환자는 새 anticoagulant를 불안해합니다. pharmacy는 아직 medication을 준비하지 못했습니다.",
        "scene": "discharge",
        "assignment": "목표: 병상 회전 압박 속에서도 safe transition을 지키기",
        "cues": [
            ("Discharge order", "entered"),
            ("New med", "anticoagulant teaching needed"),
            ("Pharmacy", "delay"),
            ("Ride", "arrived but confused"),
        ],
        "risk": "퇴원은 order가 난 순간 끝나는 일이 아니라, medication, transportation, education, follow-up이 맞아야 안전합니다.",
        "choices": [
            {
                "text": "education gap, pharmacy delay, ride timing을 charge RN/case manager와 공유하고 teach-back을 마친다.",
                "best": True,
                "effect": {"safety": 3, "team": 2, "law": 0, "confidence": 1},
                "feedback": "좋습니다. discharge pressure가 있어도 safe transition barrier를 명확히 공유해야 합니다.",
            },
            {
                "text": "bed가 필요하니 약 설명은 서류로 대신하고 환자를 먼저 보낸다.",
                "best": False,
                "effect": {"safety": -3, "team": -1, "law": 0, "confidence": -1},
                "feedback": "새 고위험 약은 teach-back이 중요합니다. 서류 전달만으로 안전한 퇴원이라고 보기 어렵습니다.",
            },
            {
                "text": "pharmacy delay는 RN 일이 아니므로 다음 shift에 '퇴원 예정'이라고만 넘긴다.",
                "best": False,
                "effect": {"safety": -2, "team": -2, "law": 0, "confidence": -1},
                "feedback": "discharge barrier는 interdisciplinary workflow입니다. RN은 barrier를 팀에 공유하고 handoff해야 합니다.",
            },
            {
                "text": "환자에게 bleeding warning signs, missed dose 대처, follow-up을 본인 말로 설명해보게 한다.",
                "best": True,
                "effect": {"safety": 3, "team": 1, "law": 0, "confidence": 2},
                "feedback": "좋습니다. teach-back은 환자를 시험하는 것이 아니라 교육이 실제로 전달됐는지 확인하는 안전 장치입니다.",
            },
        ],
        "debrief": "Day 6은 '빨리 보내기'와 '안전하게 전환하기' 사이의 긴장을 경험하는 날입니다.",
        "bridge": "다음: 독립 assignment readiness를 점검합니다.",
    },
    {
        "day": 7,
        "time": "Day 7 / 18:30",
        "title": "첫 독립 assignment 준비와 self-advocacy",
        "setting": "preceptor가 다음 주부터 assignment를 더 늘릴 수 있다고 말합니다. 동시에 당신은 EHR late charting과 provider call이 아직 부담스럽습니다.",
        "scene": "readiness",
        "assignment": "목표: 강점과 불안 요소를 전문적으로 말하고, 안전한 성장 계획을 요청하기",
        "cues": [
            ("Strength", "assessment / patient education"),
            ("Gap", "EHR speed / provider call"),
            ("Support", "preceptor / charge RN"),
            ("Boundary", "unsafe assignment escalation"),
        ],
        "risk": "미국 병동 적응에서 중요한 것은 빨리 독립하는 척이 아니라, 안전하게 독립할 준비를 구체적으로 말하는 것입니다.",
        "choices": [
            {
                "text": "preceptor에게 내가 잘하는 부분, 아직 감독이 필요한 부분, 다음 주 연습 목표를 구체적으로 말한다.",
                "best": True,
                "effect": {"safety": 3, "team": 3, "law": 0, "confidence": 2},
                "feedback": "좋습니다. self-advocacy는 불평이 아니라 patient safety를 위한 professional communication입니다.",
            },
            {
                "text": "평가가 나빠질까 봐 부담되는 부분을 숨기고 assignment를 모두 받겠다고 한다.",
                "best": False,
                "effect": {"safety": -3, "team": -1, "law": 0, "confidence": -2},
                "feedback": "숨기는 것은 단기적으로 좋아 보일 수 있지만, 환자 안전과 본인의 적응에 위험합니다. 안전하게 요청하는 표현을 연습해야 합니다.",
            },
            {
                "text": "charge RN에게 unsafe하다고 느끼는 상황에서 어떤 chain of command를 쓰는지 묻는다.",
                "best": True,
                "effect": {"safety": 2, "team": 2, "law": 1, "confidence": 2},
                "feedback": "좋은 질문입니다. 병원마다 chain of command와 assignment concern reporting 방식이 다를 수 있습니다.",
            },
            {
                "text": "미국 병동은 나와 맞지 않는다고 결론 내리고 피드백을 받지 않는다.",
                "best": False,
                "effect": {"safety": -1, "team": -2, "law": 0, "confidence": -2},
                "feedback": "적응 스트레스는 자연스럽습니다. 피드백을 통해 조정 가능한 문제인지 구분하는 것이 더 현실적인 접근입니다.",
            },
        ],
        "debrief": "Day 7은 독립 선언이 아니라 readiness conversation입니다. 안전하게 성장하는 RN은 자신의 한계도 정확히 보고합니다.",
        "bridge": "다음 단계: 병동 투어, 근무 보드, 환자 케이스에서 약한 영역을 반복 연습하세요.",
    },
]

FIRST_WEEK_BASE_SCORES = {"safety": 72, "team": 70, "law": 74, "confidence": 66}

FIRST_WEEK_SCORE_LABELS = {
    "safety": "환자 안전",
    "team": "팀 적응",
    "law": "법/정책 감각",
    "confidence": "커뮤니케이션 자신감",
}

ROLE_PROFILES = [
    {
        "key": "staff_rn",
        "label_ko": "Staff RN",
        "label_en": "Staff RN",
        "summary_ko": "담당 환자의 사정, 투약, 교육, 보고, 인수인계를 직접 연결하는 기본 RN 렌즈입니다.",
        "summary_en": "The baseline RN lens for assessment, medications, education, reporting, and handoff.",
        "focus_ko": "assessment / medication / EHR / provider call / handoff",
        "focus_en": "assessment / medication / EHR / provider call / handoff",
    },
    {
        "key": "charge_rn",
        "label_ko": "Charge RN",
        "label_en": "Charge RN",
        "summary_ko": "assignment, admission/퇴원 압박, escalation, staffing flow를 조율하는 리더 역할 렌즈입니다.",
        "summary_en": "A leadership lens for assignment, admission/discharge pressure, escalation, and staffing flow.",
        "focus_ko": "assignment / throughput / escalation / team coordination",
        "focus_en": "assignment / throughput / escalation / team coordination",
    },
    {
        "key": "preceptor",
        "label_ko": "Preceptor",
        "label_en": "Preceptor",
        "summary_ko": "신규/이직 RN에게 policy, 안전 경계, clarify/read-back 습관을 코칭하는 역할 렌즈입니다.",
        "summary_en": "A coaching lens for orienting new or transitioning nurses to policy, safety boundaries, and clarify/read-back habits.",
        "focus_ko": "orientation / feedback / policy / clarify",
        "focus_en": "orientation / feedback / policy / clarify",
    },
    {
        "key": "lpn_lvn",
        "label_ko": "LPN/LVN",
        "label_en": "LPN/LVN",
        "summary_ko": "주별 scope와 facility policy에 따라 투약, 처치, 관찰 보고 범위가 달라지는 실무 렌즈입니다.",
        "summary_en": "A scope-aware lens for medication, treatments, and observation reporting that varies by state and facility policy.",
        "focus_ko": "medication support / treatments / observation / scope check",
        "focus_en": "medication support / treatments / observation / scope check",
    },
    {
        "key": "pct_cna",
        "label_ko": "PCT/CNA",
        "label_en": "PCT/CNA",
        "summary_ko": "활력징후, 낙상 예방, 이동 보조, call light, ADL 관찰을 RN에게 안전하게 연결하는 위임 렌즈입니다.",
        "summary_en": "A delegation lens for vitals, fall prevention, mobility, call lights, ADLs, and safe reporting back to the RN.",
        "focus_ko": "vitals / mobility / fall risk / call light / delegation",
        "focus_en": "vitals / mobility / fall risk / call light / delegation",
    },
]

FIRST_WEEK_REFERENCE_CARDS = [
    (
        "NCLEX 이후의 핵심",
        "NGN/NCJMM 관점처럼 실제 상황의 단서를 인식하고 우선순위를 정하는 clinical judgment가 중심입니다.",
    ),
    (
        "HIPAA/PHI 경계",
        "전화, 엘리베이터, break room, 개인 휴대폰, SNS에서 환자 정보가 흘러나가지 않게 다룹니다.",
    ),
    (
        "Interpreter etiquette",
        "영어가 불편한 환자에게 가족 통역만 기대하지 않고 facility interpreter resource를 고려합니다.",
    ),
    (
        "CDC precautions",
        "standard precautions 위에 contact/droplet/airborne 상황을 더해 PPE, 이동 제한, 장비 구분을 판단합니다.",
    ),
    (
        "미국 직장 커뮤니케이션",
        "모르는 것을 숨기지 않고 clarify, read-back, chain of command, preceptor feedback을 전문적으로 사용합니다.",
    ),
]

SPECIALTY_TRACKS = [
    {
        "name": "Med-Surg / Telemetry",
        "tag": "기본 병동 + 심전도 흐름",
        "focus": "4~6명 assignment 안에서 투약, 낙상, 퇴원, telemetry 알람, provider call을 동시에 관리합니다.",
        "tasks": [
            "telemetry alarm이 실제 증상과 연결되는지 bedside에서 확인",
            "09:00 medication pass 중 abnormal lab/new order 우선순위 재조정",
            "퇴원 예정 환자의 medication teaching, ride, pharmacy delay barrier 공유",
        ],
        "risk": "단순히 많은 일을 빨리 하는 능력보다, 동시에 열린 task 중 위험 신호를 먼저 끌어올리는 능력이 핵심입니다.",
        "practice": "추천 연습: 근무 보드 -> 콜라이트 우선순위 -> CHF/Chest Pain 케이스",
        "color": COLORS["soft_blue"],
    },
    {
        "name": "Emergency Department",
        "tag": "triage / throughput / 불완전 정보",
        "focus": "짧은 시간 안에 triage acuity, chief complaint, red flag, provider notification, disposition flow를 판단합니다.",
        "tasks": [
            "chest pain, stroke-like symptom, sepsis concern의 first-look cue 분류",
            "도착 직후 incomplete history에서 allergy, medication, pregnancy/safety risk 빠르게 확인",
            "admission handoff 때 병동 RN이 바로 준비해야 할 oxygen, isolation, telemetry need 전달",
        ],
        "risk": "ED는 정보가 완성되길 기다리는 곳이 아니라, 불완전한 정보에서 위험을 먼저 분류하는 곳입니다.",
        "practice": "추천 연습: New Admission from ED -> New Neuro Change -> Sepsis Screen Alert",
        "color": COLORS["soft_orange"],
    },
    {
        "name": "ICU / Critical Care",
        "tag": "unstable trend / drip / device",
        "focus": "환자 수는 적어도 vital trend, vasoactive drip, ventilator, central line, sedation, rapid deterioration가 핵심입니다.",
        "tasks": [
            "MAP, urine output, mental status, lactate 등 trend가 악화될 때 provider/rapid response 연결",
            "vasopressor, sedation, insulin drip처럼 facility protocol과 double-check가 필요한 workflow 확인",
            "central line, Foley, ventilator-associated risk를 infection prevention 관점에서 점검",
        ],
        "risk": "중증 영역은 '환자가 두 명뿐'이 아니라, 작은 변화가 몇 분 안에 큰 악화로 번질 수 있는 환경입니다.",
        "practice": "추천 연습: Sepsis Screen Alert -> Opioid Sedation Risk -> SBAR 트레이너",
        "color": COLORS["soft_lavender"],
    },
    {
        "name": "Stepdown / PCU",
        "tag": "ICU와 병동 사이",
        "focus": "병동보다 unstable하고 ICU보다는 자원이 제한된 환자를 보며 escalation threshold를 정확히 잡습니다.",
        "tasks": [
            "high-flow oxygen, telemetry change, borderline BP 등 악화 직전 단서 모니터링",
            "ICU transfer criteria와 charge RN/provider notification timing 확인",
            "가족 질문과 환자 불안을 다루면서 monitoring plan을 설명",
        ],
        "risk": "애매한 상태를 오래 끌면 늦고, 너무 늦게 escalte하면 patient safety가 흔들립니다.",
        "practice": "추천 연습: Acute Shortness of Breath -> Provider communication -> Handoff Zone",
        "color": COLORS["soft_cyan"],
    },
    {
        "name": "OR / PACU",
        "tag": "perioperative safety",
        "focus": "수술 전후에는 consent, site verification, airway, pain, nausea, discharge criteria가 중심입니다.",
        "tasks": [
            "procedure, consent, allergy, NPO, implant/device, site marking 관련 safety check",
            "PACU에서 airway, sedation, pain, nausea, bleeding, discharge criteria 순서대로 확인",
            "floor transfer handoff 때 anesthesia event, lines/drains, last opioid, mobility restriction 전달",
        ],
        "risk": "수술실/회복실은 task가 빠르지만, patient identity와 procedure mismatch를 막는 표준화가 생명입니다.",
        "practice": "추천 연습: Post-op Day 1 -> Opioid Sedation Risk -> End-of-shift Handoff",
        "color": COLORS["soft_green"],
    },
    {
        "name": "L&D / Mother-Baby",
        "tag": "산모-신생아 dyad",
        "focus": "산모와 신생아를 한 쌍으로 보며 hemorrhage, hypertensive emergency, newborn safety, breastfeeding support를 연결합니다.",
        "tasks": [
            "postpartum bleeding, fundus, pain, BP, magnesium-related safety cue 확인",
            "newborn ID band/security, feeding, glucose/jaundice cue, safe sleep 교육",
            "가족 문화와 privacy를 지키면서 teach-back으로 home safety 확인",
        ],
        "risk": "두 명의 환자를 동시에 보는 영역입니다. 산모 안정과 신생아 안전을 분리하지 않고 같이 봐야 합니다.",
        "practice": "추천 연습: Teach-back -> Family Privacy -> Room Entry",
        "color": COLORS["soft_gold"],
    },
]

CHECKLISTS = {
    "Patient Room Entry": [
        "손위생을 수행했다.",
        "환자 이름과 생년월일 등 2개 identifier를 확인했다.",
        "Allergy band 또는 chart allergy를 확인했다.",
        "Fall risk, isolation, oxygen, IV line, drain/tube를 확인했다.",
        "Call light, bed position, clutter, personal belongings를 점검했다.",
        "환자에게 오늘 plan of care를 짧게 설명했다.",
    ],
    "Admission Workflow": [
        "ED/clinic handoff에서 diagnosis/reason for admission을 확인했다.",
        "Code status, allergies, isolation need, fall risk, diet/activity order를 확인했다.",
        "Initial vitals와 focused assessment를 수행했다.",
        "Medication reconciliation 흐름을 설명했다.",
        "Belongings, skin check, patient education, call-light orientation을 완료했다.",
        "Admission documentation 항목을 task list에 표시했다.",
    ],
    "End-of-shift Handoff": [
        "Reason for admission과 current status를 전달했다.",
        "Overnight/daytime event와 상태 변화를 전달했다.",
        "Lines/tubes/drains, oxygen, mobility, fall risk를 전달했다.",
        "Abnormal labs, pending tests, pending orders를 전달했다.",
        "Last PRN medication과 reassessment need를 전달했다.",
        "Family concern, discharge barrier, education need를 전달했다.",
    ],
}

REFERENCES = [
    "NCSBN Next Generation NCLEX: real-world case studies, clinical judgment, decision-making",
    "NCSBN Clinical Judgment Measurement Model: recognizing cues, prioritizing hypotheses, taking action",
    "CDC Infection Control Basics: Standard Precautions and Transmission-Based Precautions",
    "AHRQ TeamSTEPPS SBAR: Situation, Background, Assessment, Recommendation/Request",
    "AHRQ TeamSTEPPS Handoff: standardized transfer of information, authority, and responsibility",
    "Joint Commission International Patient Safety Goals: identification, communication, medication, infection prevention",
    "HHS HIPAA Privacy Rule Summary: protected health information and privacy awareness",
    "Facility policy reminder: chain of command, interpreter use, medication workflow, and scope rules vary by employer and state",
]

ENGLISH_STUDY_TOPICS = {
    "daily": [
        {
            "topic": "첫 만남과 자기소개",
            "focus": "미국에 막 도착했을 때 너무 딱딱하지 않게 자신을 소개하기",
            "words": [
                ("settle in", "적응하다", "I am still settling in."),
                ("orientation", "오리엔테이션", "I am in orientation this week."),
                ("commute", "출퇴근", "My commute takes about 25 minutes."),
                ("neighborhood", "동네", "I am getting to know the neighborhood."),
                ("recommend", "추천하다", "Do you recommend any grocery stores nearby?"),
                ("available", "가능한/시간 되는", "Are you available after work?"),
                ("appreciate", "고맙게 생각하다", "I really appreciate your help."),
            ],
            "sentences": [
                ("Hi, I am new to the area.", "이 지역에 새로 왔어요.", "처음 만난 사람에게 부담 없이 시작"),
                ("I moved here recently for work.", "일 때문에 최근에 이사 왔어요.", "미국 정착 맥락 설명"),
                ("I am still getting used to things here.", "아직 이곳 생활에 적응 중이에요.", "영어가 완벽하지 않아도 자연스러운 표현"),
                ("Could you say that again a little more slowly?", "조금만 천천히 다시 말해주실 수 있나요?", "못 알아들었을 때 기본 문장"),
                ("Thank you for explaining that.", "설명해주셔서 감사합니다.", "도움 받은 뒤 마무리"),
            ],
        },
        {
            "topic": "천천히 말해달라고 요청하기",
            "focus": "영어 자신감이 낮을 때도 전문성과 예의를 지키며 clarification 하기",
            "words": [
                ("clarify", "명확히 하다", "Can I clarify one thing?"),
                ("repeat", "반복하다", "Could you repeat that?"),
                ("slow down", "천천히 말하다", "Could you slow down a bit?"),
                ("catch", "알아듣다", "I did not catch the last part."),
                ("mean", "의미하다", "What does that mean in this context?"),
                ("write down", "적어두다", "Let me write that down."),
                ("make sure", "확인하다", "I want to make sure I understood."),
            ],
            "sentences": [
                ("I want to make sure I understood correctly.", "제가 제대로 이해했는지 확인하고 싶어요.", "업무/일상 모두 안전한 표현"),
                ("Could you repeat the last part?", "마지막 부분을 다시 말씀해주실 수 있나요?", "전체가 아니라 놓친 부분만 요청"),
                ("Could you say it in a simpler way?", "조금 더 쉬운 말로 말해주실 수 있나요?", "전문용어가 어려울 때"),
                ("Let me repeat what I heard.", "제가 들은 내용을 다시 말해볼게요.", "read-back 습관에도 연결"),
                ("I am learning the local terms, so I may ask a few questions.", "현지 표현을 배우는 중이라 몇 가지 질문드릴 수 있어요.", "자신감 있게 배움 상태 밝히기"),
            ],
        },
        {
            "topic": "집, 은행, 생활 행정",
            "focus": "정착 초기에 자주 부딪히는 생활 업무 영어",
            "words": [
                ("lease", "임대 계약", "I need to review the lease."),
                ("deposit", "보증금/입금", "How much is the deposit?"),
                ("utility", "공과금", "Are utilities included?"),
                ("appointment", "예약", "I have an appointment at 2 p.m."),
                ("document", "서류", "Which documents do I need?"),
                ("proof of address", "주소 증명", "Do you need proof of address?"),
                ("bank account", "은행 계좌", "I would like to open a bank account."),
            ],
            "sentences": [
                ("What documents do I need to bring?", "어떤 서류를 가져가야 하나요?", "은행/DMV/병원 행정 공통"),
                ("Could you email me the details?", "자세한 내용을 이메일로 보내주실 수 있나요?", "전화 영어가 불안할 때 좋음"),
                ("Is there a fee for this service?", "이 서비스에 비용이 있나요?", "예상치 못한 비용 확인"),
                ("I would like to schedule an appointment.", "예약을 잡고 싶습니다.", "전화/방문 예약 첫 문장"),
                ("Could you confirm my address on file?", "등록된 제 주소를 확인해주실 수 있나요?", "주소 오류 확인"),
            ],
        },
        {
            "topic": "마트, 약국, 카페",
            "focus": "미국 생활에서 매일 쓰는 짧은 요청 표현",
            "words": [
                ("aisle", "통로", "Which aisle has bandages?"),
                ("receipt", "영수증", "Could I get a receipt?"),
                ("refill", "리필/재조제", "I need a refill."),
                ("over-the-counter", "처방전 없이 살 수 있는", "Is this over-the-counter?"),
                ("coupon", "쿠폰", "Can I use this coupon?"),
                ("pickup", "픽업", "I am here for pickup."),
                ("substitute", "대체품", "Is there a substitute?"),
            ],
            "sentences": [
                ("Excuse me, where can I find this item?", "실례합니다, 이 물건은 어디에서 찾을 수 있나요?", "마트 기본 질문"),
                ("Can I pay by card?", "카드로 결제할 수 있나요?", "결제 확인"),
                ("I am here to pick up a prescription.", "처방약을 찾으러 왔어요.", "약국 픽업"),
                ("Could you check if it is in stock?", "재고가 있는지 확인해주실 수 있나요?", "물건/약 재고 확인"),
                ("No bag, thank you.", "봉투는 괜찮습니다.", "계산대 짧은 표현"),
            ],
        },
        {
            "topic": "직장 동료와 가벼운 대화",
            "focus": "break room이나 shift 전후에 쓰기 좋은 small talk",
            "words": [
                ("weekend", "주말", "How was your weekend?"),
                ("shift", "근무", "How was your shift?"),
                ("busy", "바쁜", "It has been busy today."),
                ("weather", "날씨", "The weather is nice today."),
                ("grab coffee", "커피 마시다", "Do you want to grab coffee?"),
                ("plans", "계획", "Any plans after work?"),
                ("recommendation", "추천", "Do you have any restaurant recommendations?"),
            ],
            "sentences": [
                ("How has your day been so far?", "오늘 하루 어떠셨어요?", "동료에게 자연스럽게"),
                ("I am still learning the unit routine.", "아직 병동 루틴을 배우는 중이에요.", "업무 대화로 연결"),
                ("Do you have any tips for this unit?", "이 병동에서 일할 때 팁이 있을까요?", "도움 요청"),
                ("That sounds helpful. I will try that.", "도움 될 것 같아요. 해볼게요.", "조언 받은 뒤"),
                ("I am going to take a quick break.", "잠깐 쉬고 올게요.", "break room 이동"),
            ],
        },
        {
            "topic": "거절과 경계 표현",
            "focus": "무례하지 않게 어렵다, 안 된다, 다시 확인하겠다고 말하기",
            "words": [
                ("boundary", "경계", "I need to keep that boundary."),
                ("comfortable", "편한", "I am not comfortable doing that."),
                ("policy", "정책", "I need to follow policy."),
                ("confirm", "확인하다", "Let me confirm first."),
                ("not sure", "확실하지 않은", "I am not sure yet."),
                ("appropriate", "적절한", "That may not be appropriate."),
                ("follow up", "후속 조치하다", "I will follow up."),
            ],
            "sentences": [
                ("Let me check the policy first.", "먼저 정책을 확인해볼게요.", "직장/생활 공통 안전 표현"),
                ("I am not comfortable sharing that information.", "그 정보를 공유하는 것은 편하지 않습니다.", "privacy 경계"),
                ("I cannot promise that, but I can check.", "약속드릴 수는 없지만 확인해볼 수 있습니다.", "과도한 약속 방지"),
                ("I will get back to you when I know more.", "더 알게 되면 다시 알려드릴게요.", "추후 답변"),
                ("Thank you for understanding.", "이해해주셔서 감사합니다.", "거절 후 마무리"),
            ],
        },
    ],
    "nursing": [
        {
            "topic": "Handoff / SBAR",
            "focus": "짧고 명확하게 환자 상태를 넘기고 provider에게 전화하기",
            "words": [
                ("baseline", "기준 상태", "What is the patient's baseline?"),
                ("pending", "아직 남은/대기 중", "Labs are pending."),
                ("concern", "우려", "My concern is worsening shortness of breath."),
                ("recommendation", "요청/권고", "My recommendation is evaluation now."),
                ("read back", "복창 확인", "Can I read that back?"),
                ("handoff", "인수인계", "I received handoff from ED."),
                ("escalate", "상급자/팀에 올리다", "I need to escalate this."),
            ],
            "sentences": [
                ("This is RN Lee on 4 West calling about room 412.", "4 West 412호 환자 관련해 전화드리는 RN Lee입니다.", "provider call 첫 문장"),
                ("My concern is that he is more short of breath than this morning.", "오늘 아침보다 숨참이 악화된 것이 우려됩니다.", "Assessment를 짧게"),
                ("His oxygen saturation is 89% on 2 liters nasal cannula.", "비강캐뉼라 2L에서 산소포화도 89%입니다.", "객관적 수치 보고"),
                ("Could you evaluate him now or give next steps?", "지금 평가하시거나 다음 지시를 주실 수 있을까요?", "Recommendation/Request"),
                ("Let me read back the order.", "오더를 다시 복창해보겠습니다.", "read-back"),
            ],
        },
        {
            "topic": "Assessment",
            "focus": "환자에게 증상을 묻고 baseline과 변화를 확인하기",
            "words": [
                ("shortness of breath", "숨참", "Are you short of breath?"),
                ("dizzy", "어지러운", "Do you feel dizzy?"),
                ("numbness", "저림/무감각", "Any numbness or tingling?"),
                ("worse", "악화된", "Is it getting worse?"),
                ("sudden", "갑작스러운", "Did it start suddenly?"),
                ("baseline", "평소 상태", "Is this your baseline?"),
                ("radiate", "방사되다", "Does the pain radiate anywhere?"),
            ],
            "sentences": [
                ("When did this start?", "언제 시작됐나요?", "증상 시작 시간"),
                ("Is this new or has this happened before?", "새로운 증상인가요, 예전에도 있었나요?", "baseline 비교"),
                ("Can you rate your pain from zero to ten?", "통증을 0에서 10까지로 말하면 몇 점인가요?", "pain assessment"),
                ("Take a slow deep breath for me.", "천천히 깊게 숨 쉬어보세요.", "호흡 사정"),
                ("I am going to check your vital signs now.", "지금 활력징후를 확인하겠습니다.", "행동 안내"),
            ],
        },
        {
            "topic": "Medication / MAR",
            "focus": "투약 전 확인, 설명, 지연 상황 소통",
            "words": [
                ("due", "투약 예정인", "This medication is due at 9."),
                ("allergy", "알레르기", "Do you have any allergies?"),
                ("dose", "용량", "Let me verify the dose."),
                ("route", "투여 경로", "The route is oral."),
                ("hold parameter", "보류 기준", "There is a hold parameter."),
                ("side effect", "부작용", "A possible side effect is dizziness."),
                ("reassess", "재평가하다", "I will reassess your pain."),
            ],
            "sentences": [
                ("Can you tell me your name and date of birth?", "성함과 생년월일을 말씀해주시겠어요?", "2개 식별자"),
                ("I am checking your allergies before giving this.", "이 약을 드리기 전에 알레르기를 확인하고 있습니다.", "투약 전 설명"),
                ("This medication is for your blood pressure.", "이 약은 혈압 조절을 위한 약입니다.", "indication 설명"),
                ("The medication is delayed, and I am checking with pharmacy.", "약이 지연되어 약국에 확인 중입니다.", "missing med 소통"),
                ("I will come back to reassess your pain in about an hour.", "약 한 시간 후 통증을 다시 확인하겠습니다.", "PRN reassessment"),
            ],
        },
        {
            "topic": "Delegation / PCT",
            "focus": "위임 가능한 일과 RN follow-up을 명확히 말하기",
            "words": [
                ("delegate", "위임하다", "I can delegate vital signs."),
                ("follow up", "추후 확인하다", "I will follow up after you check."),
                ("mobility", "이동 능력", "Please check mobility status."),
                ("fall risk", "낙상 위험", "This patient is a fall risk."),
                ("blood sugar", "혈당", "Can you recheck blood sugar?"),
                ("call light", "콜라이트", "The call light is on."),
                ("assist", "돕다", "Can you assist with ambulation?"),
            ],
            "sentences": [
                ("Could you get a set of vital signs for room 414?", "414호 활력징후를 측정해주실 수 있나요?", "PCT 요청"),
                ("Please let me know right away if the oxygen saturation is below 92%.", "산소포화도가 92% 미만이면 바로 알려주세요.", "보고 기준 명확화"),
                ("I will assess the shortness of breath myself.", "숨참은 제가 직접 사정하겠습니다.", "RN-only assessment 구분"),
                ("Can you help this patient to the bathroom? She is a fall risk.", "이 환자 화장실 이동을 도와주실 수 있나요? 낙상 위험이 있습니다.", "위임+위험 정보"),
                ("Thank you. I will check back after I finish this call.", "감사합니다. 이 통화 끝나고 다시 확인하겠습니다.", "follow-up ownership"),
            ],
        },
        {
            "topic": "Privacy / Family Call",
            "focus": "가족 전화와 환자 정보 공유 범위 확인",
            "words": [
                ("authorization", "정보 공유 허가", "I need to check authorization."),
                ("privacy", "개인정보 보호", "I have to protect patient privacy."),
                ("caller", "전화 건 사람", "I need to verify the caller."),
                ("permission", "허락", "Do we have permission?"),
                ("update", "상황 설명", "I can provide a general update."),
                ("policy", "정책", "Facility policy requires this."),
                ("callback", "다시 전화", "I can arrange a callback."),
            ],
            "sentences": [
                ("I need to verify that we have permission to share information.", "정보 공유 허가가 있는지 확인해야 합니다.", "가족 전화 첫 대응"),
                ("I understand you are worried.", "걱정되시는 것 이해합니다.", "감정 인정"),
                ("I cannot discuss details until I confirm authorization.", "허가를 확인하기 전에는 자세한 내용을 말씀드릴 수 없습니다.", "경계 표현"),
                ("I can take your concern and share it with the team.", "우려하시는 내용을 받아 팀과 공유할 수 있습니다.", "대안 제시"),
                ("What is the best number for a callback?", "다시 연락드릴 번호가 어떻게 되나요?", "callback plan"),
            ],
        },
        {
            "topic": "Discharge / Teach-back",
            "focus": "퇴원 교육과 이해 확인을 쉬운 영어로 하기",
            "words": [
                ("discharge", "퇴원", "You may be discharged today."),
                ("follow-up", "외래/추후 진료", "You need follow-up next week."),
                ("warning signs", "위험 신호", "These are warning signs."),
                ("teach-back", "본인 말로 설명해보기", "Can you teach that back to me?"),
                ("pharmacy", "약국", "Pharmacy is preparing your medication."),
                ("ride", "귀가 교통편", "Do you have a ride home?"),
                ("instructions", "안내문", "These are your discharge instructions."),
            ],
            "sentences": [
                ("Can you tell me how you will take this medication at home?", "집에서 이 약을 어떻게 드실지 말씀해주시겠어요?", "teach-back"),
                ("Please call your doctor if you notice these warning signs.", "이런 위험 신호가 보이면 의사에게 연락하세요.", "퇴원 안전"),
                ("Do you have someone who can drive you home?", "집까지 데려다줄 사람이 있나요?", "ride 확인"),
                ("Your follow-up appointment is listed here.", "추후 진료 일정은 여기에 적혀 있습니다.", "서류 설명"),
                ("I want to make sure I explained it clearly.", "제가 명확히 설명했는지 확인하고 싶습니다.", "teach-back 부담 줄이기"),
            ],
        },
    ],
}


def generated_english_topic(title, focus, core_word, core_meaning, core_example, situation_ko, nursing=False):
    if nursing:
        words = [
            (core_word, core_meaning, core_example),
            ("baseline", "기준 상태", "What is the patient's baseline?"),
            ("trend", "추세", "The trend is getting worse."),
            ("notify", "알리다", "I need to notify the provider."),
            ("reassess", "재평가하다", "I will reassess in 30 minutes."),
            ("pending", "대기 중인/남은", "The lab result is still pending."),
            ("clarify", "명확히 확인하다", "I need to clarify the order."),
            ("document", "기록하다", "I will document the assessment."),
        ]
        sentences = [
            (f"I am concerned about {core_word}.", f"{core_meaning} 관련해서 우려됩니다.", situation_ko),
            (f"Can you clarify the plan for {core_word}?", f"{core_meaning}에 대한 계획을 명확히 해주실 수 있나요?", "provider/preceptor에게 확인"),
            ("Let me compare this with the patient's baseline.", "환자의 평소 상태와 비교해보겠습니다.", "상태 변화 사정"),
            ("I will reassess and update you if it changes.", "재평가하고 변화가 있으면 알려드리겠습니다.", "follow-up 약속"),
            ("Could you repeat the order so I can read it back?", "제가 복창할 수 있도록 오더를 다시 말씀해주시겠어요?", "read-back"),
            ("I need to check our facility policy first.", "먼저 이 시설의 정책을 확인해야 합니다.", "병원별 차이 확인"),
        ]
    else:
        words = [
            (core_word, core_meaning, core_example),
            ("appointment", "예약", "I have an appointment today."),
            ("confirm", "확인하다", "Can you confirm that for me?"),
            ("available", "가능한/시간 되는", "Is anyone available to help?"),
            ("fee", "요금", "Is there a fee?"),
            ("receipt", "영수증", "Could I get a receipt?"),
            ("address", "주소", "Can you confirm my address?"),
            ("explain", "설명하다", "Could you explain that again?"),
        ]
        sentences = [
            (f"I am here to ask about {core_word}.", f"{core_meaning}에 대해 문의하러 왔어요.", situation_ko),
            (f"Could you explain {core_word} one more time?", f"{core_meaning}에 대해 한 번 더 설명해주실 수 있나요?", "못 알아들었을 때"),
            ("Could you write that down for me?", "그 내용을 적어주실 수 있나요?", "전화/창구 영어가 빠를 때"),
            ("I am still new here, so I may ask a few questions.", "아직 이곳에 익숙하지 않아서 몇 가지 질문드릴 수 있어요.", "정착 초기 표현"),
            ("What is the next step?", "다음 단계가 무엇인가요?", "절차 확인"),
            ("Thank you for your patience.", "기다려주셔서 감사합니다.", "천천히 말해달라고 한 뒤"),
        ]
    return {"topic": title, "focus": focus, "words": words, "sentences": sentences}


def expand_english_study_topics():
    daily_specs = [
        ("아파트 투어", "집을 보러 갔을 때 계약 전 확인", "lease", "임대 계약", "When does the lease start?", "집 계약 전 질문"),
        ("렌트비와 보증금", "월세, deposit, late fee 확인", "deposit", "보증금", "How much is the deposit?", "비용 확인"),
        ("전기/수도/인터넷", "utility 개통과 계정 만들기", "utility", "공과금", "Are utilities included?", "공과금 문의"),
        ("은행 계좌 만들기", "계좌 개설, debit card, direct deposit", "direct deposit", "급여 자동 입금", "I need to set up direct deposit.", "은행 창구"),
        ("휴대폰 개통", "요금제, SIM, 자동이체", "phone plan", "휴대폰 요금제", "Which phone plan do you recommend?", "통신사 매장"),
        ("DMV/운전면허", "예약, 서류, 주소 증명", "proof of address", "주소 증명", "Do you need proof of address?", "DMV 창구"),
        ("마트에서 찾기", "물건 위치와 재고 묻기", "aisle", "통로", "Which aisle has this item?", "마트 직원에게 질문"),
        ("약국 픽업", "처방약, refill, 보험 확인", "prescription", "처방약", "I am here to pick up a prescription.", "약국 픽업"),
        ("카페 주문", "음료 주문과 옵션 요청", "to go", "포장", "Can I get this to go?", "카페 주문"),
        ("식당 예약", "예약, 대기, 알레르기", "reservation", "예약", "I have a reservation under Lee.", "식당 입장"),
        ("병원 HR", "서류 제출과 onboarding 확인", "onboarding", "입사 절차", "I am completing onboarding.", "병원 HR"),
        ("급여/스케줄 질문", "pay period, schedule, shift swap", "pay period", "급여 산정 기간", "When is the pay period?", "직장 행정"),
        ("동료 small talk", "break room에서 자연스럽게 말하기", "small talk", "가벼운 대화", "I am still practicing small talk.", "동료 대화"),
        ("정중한 거절", "무례하지 않게 어렵다고 말하기", "not comfortable", "편하지 않은", "I am not comfortable with that.", "경계 표현"),
        ("도움 요청", "길, 절차, 문서 도움 요청", "could you help me", "도와주실 수 있나요", "Could you help me with this form?", "생활 도움 요청"),
        ("전화 영어", "전화로 천천히 말해달라고 요청", "speak slowly", "천천히 말하다", "Could you speak slowly?", "전화 통화"),
        ("이메일 요청", "전화보다 이메일로 확인받기", "email confirmation", "이메일 확인", "Could you email me the confirmation?", "서면 확인"),
        ("교통/라이드", "버스, rideshare, 지각 알림", "ride", "교통편", "My ride is running late.", "출근/이동"),
        ("날씨와 복장", "눈/비/추위에 대한 일상 표현", "forecast", "일기예보", "What is the forecast today?", "일상 대화"),
        ("친구 만들기", "초대, 약속, 부담 없는 표현", "hang out", "만나다/놀다", "Would you like to hang out sometime?", "친구/동료 관계"),
        ("집주인에게 연락", "수리 요청과 follow-up", "maintenance request", "수리 요청", "I submitted a maintenance request.", "아파트 관리실"),
        ("소포/우편", "배송, 주소, 분실 문의", "package", "소포", "I am looking for a package.", "우편/택배"),
        ("보험 카드", "건강보험/자동차보험 카드 확인", "insurance card", "보험 카드", "Here is my insurance card.", "보험 확인"),
        ("응급 상황 설명", "길에서 아프거나 사고가 났을 때", "emergency", "응급 상황", "This is an emergency.", "생활 응급"),
        ("감사와 사과", "부담 없이 고맙다/미안하다 말하기", "appreciate", "고맙게 생각하다", "I appreciate your help.", "관계 유지"),
    ]
    nursing_specs = [
        ("Provider call opening", "provider에게 첫 문장을 안전하게 열기", "provider callback", "의료진 회신 전화", "I received a provider callback.", "provider call"),
        ("SBAR Situation", "문제를 한 문장으로 말하기", "situation", "현재 문제", "The situation is new shortness of breath.", "SBAR"),
        ("Baseline 확인", "평소 상태와 변화 비교", "baseline", "기준 상태", "This is not his baseline.", "assessment"),
        ("Vital trend 보고", "활력징후 추세를 말하기", "vital trend", "활력징후 추세", "The vital trend is worsening.", "보고"),
        ("Pain assessment", "통증 위치/점수/양상 묻기", "pain score", "통증 점수", "What is your pain score?", "bedside"),
        ("Respiratory assessment", "숨참, 산소, 호흡 양상 확인", "oxygen saturation", "산소포화도", "His oxygen saturation is 89%.", "호흡 악화"),
        ("Neuro check", "새 신경학적 변화 보고", "last known well", "마지막 정상 시간", "What was the last known well?", "stroke concern"),
        ("Fall prevention", "낙상 위험과 도움 요청", "fall risk", "낙상 위험", "She is a high fall risk.", "patient room"),
        ("PCT delegation", "PCT에게 명확히 위임하기", "delegate", "위임하다", "I will delegate vital signs.", "teamwork"),
        ("Charge RN update", "charge RN에게 병동 흐름 공유", "charge nurse", "책임 간호사", "I need to update the charge nurse.", "unit flow"),
        ("Medication delay", "약 지연과 pharmacy 연락", "medication delay", "투약 지연", "There is a medication delay.", "med pass"),
        ("Missing medication", "ADC에 약이 없을 때", "not available", "사용 불가/없음", "The medication is not available in the ADC.", "med room"),
        ("Insulin safety", "식사/혈당/hold parameter", "hold parameter", "보류 기준", "There is a hold parameter.", "insulin"),
        ("Opioid reassessment", "통증과 호흡 재평가", "sedation", "진정 상태", "I am checking sedation and respirations.", "post-op"),
        ("Allergy check", "알레르기 확인", "allergy band", "알레르기 팔찌", "I am checking your allergy band.", "med pass"),
        ("Barcode mismatch", "스캐너 mismatch 대응", "mismatch", "불일치", "The scanner shows a mismatch.", "barcode"),
        ("Isolation entry", "PPE와 격리방 입실", "PPE", "보호구", "I need to put on PPE.", "isolation"),
        ("Specimen collection", "검체 채취와 라벨", "specimen", "검체", "I need to label the specimen.", "lab"),
        ("Family privacy", "가족 전화 authorization", "authorization", "정보 공유 허가", "I need to verify authorization.", "family call"),
        ("Interpreter request", "통역 서비스 요청", "interpreter", "통역사", "I will request an interpreter.", "language access"),
        ("Discharge teaching", "퇴원 교육과 teach-back", "teach-back", "본인 말로 설명", "Can you teach that back to me?", "discharge"),
        ("Pharmacy barrier", "퇴원 약국 지연", "pharmacy delay", "약국 지연", "Pharmacy is still preparing the medication.", "discharge"),
        ("Case manager update", "퇴원 barrier 공유", "case manager", "사례 관리자", "I need to update the case manager.", "discharge planning"),
        ("ED admission handoff", "ED에서 병동으로 올라오는 환자", "ETA", "도착 예정 시간", "What is the ETA?", "admission"),
        ("PACU transfer", "수술 후 병동 전동", "PACU", "회복실", "The patient is coming from PACU.", "post-op transfer"),
        ("Telemetry alarm", "알람과 환자 증상 연결", "telemetry alarm", "심전도 알람", "The telemetry alarm is active.", "telemetry"),
        ("Sepsis alert", "sepsis screen과 time-sensitive task", "sepsis alert", "패혈증 알림", "The sepsis alert fired.", "escalation"),
        ("Blood transfusion", "수혈 반응 의심", "transfusion reaction", "수혈 반응", "I am concerned about a transfusion reaction.", "transfusion"),
        ("Central line care", "central line dressing과 감염 예방", "central line", "중심정맥관", "The central line dressing is loose.", "infection prevention"),
        ("Wound dressing", "상처 dressing order 확인", "dressing change", "드레싱 교체", "There is a dressing change order.", "wound care"),
        ("I&O and daily weight", "CHF/renal 환자 fluid balance", "intake and output", "섭취량/배설량", "I am tracking intake and output.", "CHF"),
        ("Lab escalation", "abnormal lab 보고", "critical lab", "중요 검사 결과", "I received a critical lab result.", "provider call"),
        ("Read-back", "전화 오더 복창", "read back", "복창하다", "Let me read that back.", "orders"),
        ("Chain of command", "unsafe concern 보고 경로", "chain of command", "보고 체계", "I need to follow the chain of command.", "safety"),
        ("Unsafe assignment", "assignment가 안전하지 않을 때", "unsafe assignment", "불안전한 배정", "I am concerned this assignment may be unsafe.", "self-advocacy"),
    ]
    ENGLISH_STUDY_TOPICS["daily"].extend(generated_english_topic(*spec, nursing=False) for spec in daily_specs)
    ENGLISH_STUDY_TOPICS["nursing"].extend(generated_english_topic(*spec, nursing=True) for spec in nursing_specs)


expand_english_study_topics()

KO_CONTENT = extend_content_bundle({
    "nav_items": NAV_ITEMS,
    "ward_zones": WARD_ZONES,
    "tour_modes": TOUR_MODES,
    "shift_events": SHIFT_EVENTS,
    "questions": QUESTIONS,
    "scenarios": SCENARIOS,
    "first_week_days": FIRST_WEEK_DAYS,
    "first_week_score_labels": FIRST_WEEK_SCORE_LABELS,
    "first_week_reference_cards": FIRST_WEEK_REFERENCE_CARDS,
    "specialty_tracks": SPECIALTY_TRACKS,
    "checklists": CHECKLISTS,
    "references": REFERENCES,
})
EN_CONTENT = extend_content_bundle(build_english_content(COLORS), english=True)
FIRST_WEEK_DAY_POOLS = KO_CONTENT["first_week_day_pools"]
SHIFT_EVENT_POOL = KO_CONTENT["shift_event_pool"]
TOUR_MODES = KO_CONTENT["tour_modes"]
SHIFT_EVENTS = select_shift_events(SHIFT_EVENT_POOL)
QUESTIONS = KO_CONTENT["questions"]
SCENARIOS = KO_CONTENT["scenarios"]
FIRST_WEEK_DAYS = select_first_week_days(FIRST_WEEK_DAY_POOLS)


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._layout_stage = None
        self._layout_transaction = False
        self.canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas, style="Page.TFrame")
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_configure(self, _event):
        if self._layout_transaction:
            return
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)
        if self._layout_stage is not None:
            stage_id = self._layout_stage["window_id"]
            self.canvas.itemconfigure(stage_id, width=event.width)
            view_top = self.canvas.canvasy(0)
            self.canvas.coords(
                self._layout_stage["cover_id"],
                0,
                view_top,
                event.width,
                view_top + max(self.canvas.winfo_height(), 1),
            )

    def _on_mousewheel(self, event):
        if self.winfo_ismapped():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def reset_scroll(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(0)

    def begin_layout_stage(self):
        """Build the next page behind the current one for an atomic swap."""
        if self._layout_stage is not None:
            raise RuntimeError("A page layout transaction is already active.")
        if self.canvas.winfo_width() <= 1:
            self.canvas.update_idletasks()
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        view_top = self.canvas.canvasy(0)
        old_inner = self.inner
        old_window_id = self.window_id
        self._layout_transaction = True
        staging = ttk.Frame(self.canvas, style="Page.TFrame")
        staging.bind("<Configure>", self._on_configure)
        # Keep staging inside the current viewport so Tk assigns real geometry
        # even when the outgoing page is scrolled far down.
        staging_id = self.canvas.create_window((0, view_top), window=staging, anchor="nw", width=width)
        self.canvas.tag_lower(staging_id)
        cover_id = self.canvas.create_rectangle(
            0,
            view_top,
            width,
            view_top + height,
            fill=COLORS["bg"],
            outline="",
        )
        self.canvas.tag_lower(cover_id, old_window_id)
        self.inner = staging
        self._layout_stage = {
            "old_inner": old_inner,
            "old_window_id": old_window_id,
            "window_id": staging_id,
            "cover_id": cover_id,
        }
        return staging

    def commit_layout_stage(self):
        stage = self._layout_stage
        if stage is None:
            return
        self.window_id = stage["window_id"]
        self.canvas.coords(self.window_id, 0, 0)
        self.canvas.delete(stage["old_window_id"])
        stage["old_inner"].destroy()
        self.canvas.delete(stage["cover_id"])
        self.canvas.tag_raise(self.window_id)
        self._layout_stage = None
        self._layout_transaction = False
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)

    def rollback_layout_stage(self):
        stage = self._layout_stage
        if stage is None:
            return
        self.canvas.delete(stage["window_id"])
        self.inner.destroy()
        self.canvas.delete(stage["cover_id"])
        self.inner = stage["old_inner"]
        self.window_id = stage["old_window_id"]
        self._layout_stage = None
        self._layout_transaction = False
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class WardSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        configure_tk_scaling(self)
        self.title(APP_TITLE)
        try:
            self.iconbitmap(resource_path("assets", "us-ward-icon.ico"))
        except tk.TclError:
            pass
        self.bundled_font_paths = register_bundled_fonts()
        configure_font_constants(self)
        self.geometry("1280x820")
        self.minsize(1180, 700)
        self.configure(bg=COLORS["bg"])
        self.language = tk.StringVar(value="ko")
        self.current_page_key = "dashboard"
        self.lang_buttons = {}
        self._set_language_data("ko")
        self.shift_index = 0
        self.quest_vars = []
        self.scenario_name = tk.StringVar(value=list(SCENARIOS.keys())[0])
        self.scenario_step = 0
        self.scenario_score = 0
        self.first_week_day = 0
        self.first_week_answers = {}
        self.first_week_choice_orders = {}
        self.last_first_week_effect = {}
        self.last_first_week_choice_best = None
        self.first_week_feedback = tk.StringVar(value=self.tx("첫날 장면을 보고 어떤 RN으로 행동할지 선택해보세요.", "Read the first-day scene and choose how you would act as the RN."))
        self.first_week_scores = dict(FIRST_WEEK_BASE_SCORES)
        self.current_zone = "Nurse Station"
        self.tour_mode = tk.StringVar(value=list(TOUR_MODES.keys())[0])
        self.tour_step = 0
        self.tour_feedback = tk.StringVar(value=self.tx("구역을 클릭하거나 동선 선택을 시작해보세요.", "Click a zone or start a route decision."))
        self.quest_station = tk.StringVar(value=self.all_station_label())
        self.quest_skill = tk.StringVar(value="all")
        self.practice_role = tk.StringVar(value="staff_rn")
        self.quest_feedback = tk.StringVar(value=self.tx("문항을 선택하면 이곳에 판단 근거가 표시됩니다.", "Select answers to see the reasoning here."))
        self.english_mode = tk.StringVar(value="daily")
        self.english_drill = tk.StringVar(value="")
        self.check_vars = {}
        self.checklist_progress_labels = {}
        self.check_var_state_keys = {}
        self.checklist_state = {}
        self.debrief_note_fields = {}
        self.debrief_drafts = {}
        self.sbar_fields = {}
        self.sbar_draft = {}
        self.sbar_output_draft = ""
        self.images = {}
        self.asset_paths = {}
        self.small_images = {}
        self._setup_style()
        self._load_assets()
        self._build_shell()
        self._responsive_wrap_job = None
        self._responsive_wrap_update_all = True
        self._responsive_wrap_canvas_width = 0
        self._responsive_wrap_inner_width = 0
        self._responsive_wrap_running = False
        self._responsive_wrap_transaction = False
        self._enable_responsive_wrapping()
        self.show_page("dashboard")

    def _set_language_data(self, code):
        global NAV_ITEMS, WARD_ZONES, TOUR_MODES, SHIFT_EVENTS, QUESTIONS, SCENARIOS
        global FIRST_WEEK_DAYS, FIRST_WEEK_SCORE_LABELS, FIRST_WEEK_REFERENCE_CARDS, SPECIALTY_TRACKS
        global CHECKLISTS, REFERENCES, FIRST_WEEK_DAY_POOLS, SHIFT_EVENT_POOL

        content = EN_CONTENT if code == "en" else KO_CONTENT
        NAV_ITEMS = content["nav_items"]
        WARD_ZONES = content["ward_zones"]
        tour_items = list(content["tour_modes"].items())
        random.shuffle(tour_items)
        TOUR_MODES = dict(tour_items)
        SHIFT_EVENT_POOL = content.get("shift_event_pool", content["shift_events"])
        SHIFT_EVENTS = select_shift_events(SHIFT_EVENT_POOL)
        QUESTIONS = list(content["questions"])
        random.shuffle(QUESTIONS)
        scenario_items = list(content["scenarios"].items())
        random.shuffle(scenario_items)
        SCENARIOS = dict(scenario_items)
        FIRST_WEEK_DAY_POOLS = content.get("first_week_day_pools", [[day] for day in content["first_week_days"]])
        FIRST_WEEK_DAYS = select_first_week_days(FIRST_WEEK_DAY_POOLS)
        FIRST_WEEK_SCORE_LABELS = content["first_week_score_labels"]
        FIRST_WEEK_REFERENCE_CARDS = content["first_week_reference_cards"]
        SPECIALTY_TRACKS = content["specialty_tracks"]
        CHECKLISTS = content["checklists"]
        REFERENCES = content["references"]

    def is_english(self):
        return self.language.get() == "en"

    def tx(self, ko, en):
        return en if self.is_english() else ko

    def all_station_label(self):
        return self.tx("전체", "All")

    def all_skill_label(self):
        return self.tx("전체 역량", "All Skills")

    def quest_skill_options(self):
        return [
            ("all", self.all_skill_label()),
            ("acuity", self.tx("Acuity / 중증도", "Acuity")),
            ("team", self.tx("Team / 위임", "Team / Delegation")),
            ("escalation", self.tx("Escalation", "Escalation")),
            ("hipaa", self.tx("HIPAA / PHI", "HIPAA / PHI")),
            ("medication", self.tx("Medication", "Medication")),
            ("handoff", self.tx("Handoff / SBAR", "Handoff / SBAR")),
            ("communication", self.tx("Communication", "Communication")),
        ]

    def role_profile(self, key=None):
        role_key = key or self.practice_role.get()
        for profile in ROLE_PROFILES:
            if profile["key"] == role_key:
                return profile
        return ROLE_PROFILES[0]

    def role_label(self, key=None):
        profile = self.role_profile(key)
        return profile["label_en"] if self.is_english() else profile["label_ko"]

    def role_summary(self, key=None):
        profile = self.role_profile(key)
        return profile["summary_en"] if self.is_english() else profile["summary_ko"]

    def role_focus(self, key=None):
        profile = self.role_profile(key)
        return profile["focus_en"] if self.is_english() else profile["focus_ko"]

    def _render_role_selector(self, parent, context="practice"):
        role_row = tk.Frame(parent, bg=COLORS["panel"])
        role_row.pack(fill="x", pady=(10, 0))
        ttk.Label(role_row, text=self.tx("직군 선택", "Role Lens"), style="CardTitle.TLabel").pack(side="left", padx=(0, 10))
        for profile in ROLE_PROFILES:
            selected = self.practice_role.get() == profile["key"]
            button = tk.Button(
                role_row,
                text=self.role_label(profile["key"]),
                command=lambda key=profile["key"]: self.set_practice_role(key),
                bg=COLORS["primary"] if selected else COLORS["panel_alt"],
                fg="#ffffff" if selected else COLORS["ink"],
                activebackground=COLORS["primary_dark"] if selected else COLORS["soft_gray"],
                activeforeground="#ffffff" if selected else COLORS["ink"],
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                font=FONT_CHIP,
                padx=10,
                pady=6,
            )
            button.pack(side="left", padx=(0, 6), pady=2)
        note = self.tx(
            f"{self.role_label()} 렌즈: {self.role_summary()} 중점: {self.role_focus()}",
            f"{self.role_label()} lens: {self.role_summary()} Focus: {self.role_focus()}",
        )
        tk.Label(
            parent,
            text=note,
            bg=COLORS["soft_gray"],
            fg=COLORS["ink"],
            font=FONT_SMALL,
            padx=10,
            pady=7,
            wraplength=820,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(8, 0))

    def set_practice_role(self, role_key):
        self.practice_role.set(role_key)
        valid_modes = self.tour_modes_for_role()
        if valid_modes and self.tour_mode.get() not in valid_modes:
            self.tour_mode.set(valid_modes[0])
            self.tour_step = 0
            first_zone = TOUR_MODES[self.tour_mode.get()]["steps"][0][0]
            self.current_zone = first_zone
        self.tour_feedback.set(self.tx(f"{self.role_label()} 역할 렌즈로 동선을 다시 봅니다.", f"Viewing routes through the {self.role_label()} role lens."))
        self.quest_feedback.set(self.tx(f"{self.role_label()} 역할에 가까운 문항을 우선 표시합니다.", f"Prioritizing items that match the {self.role_label()} role."))
        self.show_page(self.current_page_key)

    def question_role_tags(self, question):
        text = " ".join(
            [
                str(question.get("station", "")),
                str(question.get("title", "")),
                str(question.get("prompt", "")),
                " ".join(map(str, question.get("choices", []))),
                str(question.get("feedback", "")),
            ]
        ).lower()
        skill_tags = self.question_skill_tags(question)
        tags = {"staff_rn"}
        if any(tag in skill_tags for tag in ["team", "escalation", "handoff"]) or any(word in text for word in ["assignment", "staffing", "charge", "admission", "discharge", "throughput", "rapid", "escalation", "배정", "입원", "퇴원", "보고"]):
            tags.add("charge_rn")
        if "communication" in skill_tags or any(word in text for word in ["preceptor", "orient", "clarify", "feedback", "policy", "teach", "new nurse", "프리셉터", "교육", "확인"]):
            tags.add("preceptor")
        if "medication" in skill_tags or any(word in text for word in ["dressing", "wound", "foley", "treatment", "scope", "투약", "처치", "드레싱"]):
            tags.add("lpn_lvn")
        if any(word in text for word in ["pct", "cna", "vital", "fall", "mobility", "ambulate", "call light", "bathroom", "toilet", "adls", "활력", "낙상", "이동", "콜라이트"]):
            tags.add("pct_cna")
        return tags

    def question_matches_role(self, question, role_key):
        if role_key == "staff_rn":
            return True
        return role_key in self.question_role_tags(question)

    def tour_mode_matches_role(self, name, mode, role_key):
        if role_key == "staff_rn":
            return True
        text = " ".join([name, " ".join(zone for zone, _note in mode.get("steps", [])), " ".join(note for _zone, note in mode.get("steps", []))]).lower()
        keyword_map = {
            "charge_rn": ["assignment", "staffing", "charge", "admission", "discharge", "handoff", "provider", "rapid", "escalation", "throughput", "family", "배정", "입원", "퇴원", "보고"],
            "preceptor": ["preceptor", "orient", "clarify", "policy", "handoff", "teach", "read-back", "new nurse", "프리셉터", "교육", "확인"],
            "lpn_lvn": ["med", "medication", "adc", "mar", "waste", "dressing", "foley", "treatment", "scope", "투약", "처치"],
            "pct_cna": ["vital", "fall", "mobility", "call light", "bathroom", "patient room", "ambulate", "adls", "활력", "낙상", "이동", "환자 병실"],
        }
        return any(keyword in text for keyword in keyword_map.get(role_key, []))

    def tour_modes_for_role(self):
        role_key = self.practice_role.get()
        modes = [name for name, mode in TOUR_MODES.items() if self.tour_mode_matches_role(name, mode, role_key)]
        return modes or list(TOUR_MODES.keys())

    def question_skill_tags(self, question):
        text = " ".join(
            [
                str(question.get("station", "")),
                str(question.get("title", "")),
                str(question.get("prompt", "")),
                " ".join(map(str, question.get("choices", []))),
                str(question.get("feedback", "")),
            ]
        ).lower()
        tags = set()
        if any(word in text for word in ["pain", "sob", "shortness", "chest", "sepsis", "stroke", "unstable", "vital", "o2", "bp", "rr", "중증", "호흡", "흉통", "악화"]):
            tags.add("acuity")
        if any(word in text for word in ["pct", "delegate", "delegation", "charge", "preceptor", "team", "팀", "위임", "동료"]):
            tags.add("team")
        if any(word in text for word in ["provider", "notify", "call", "escalate", "rapid", "doctor", "보고", "연락", "의사"]):
            tags.add("escalation")
        if any(word in text for word in ["hipaa", "phi", "privacy", "family", "phone", "photo", "sns", "authorization", "interpreter", "개인정보", "가족", "전화", "사진", "통역"]):
            tags.add("hipaa")
        if any(word in text for word in ["mar", "adc", "med", "medication", "insulin", "waste", "controlled", "pharmacy", "allergy", "약", "투약", "폐기", "알레르기"]):
            tags.add("medication")
        if any(word in text for word in ["handoff", "sbar", "report", "transfer", "discharge", "인수인계", "퇴원"]):
            tags.add("handoff")
        if any(word in text for word in ["clarify", "read-back", "teach", "explain", "question", "language", "english", "말", "설명", "확인", "질문"]):
            tags.add("communication")
        return tags or {"communication"}

    def set_language(self, code):
        global SHIFT_EVENTS, FIRST_WEEK_DAYS

        old_code = self.language.get()
        if old_code == code:
            return

        old_content = EN_CONTENT if old_code == "en" else KO_CONTENT
        new_content = EN_CONTENT if code == "en" else KO_CONTENT
        old_tour_keys = list(old_content["tour_modes"].keys())
        new_tour_keys = list(new_content["tour_modes"].keys())
        old_scenario_keys = list(old_content["scenarios"].keys())
        new_scenario_keys = list(new_content["scenarios"].keys())
        old_tour_key = self.tour_mode.get()
        old_scenario_key = self.scenario_name.get()
        old_station_is_all = self.quest_station.get() == self.all_station_label()

        tour_index = old_tour_keys.index(old_tour_key) if old_tour_key in old_tour_keys else 0
        scenario_index = old_scenario_keys.index(old_scenario_key) if old_scenario_key in old_scenario_keys else 0

        old_shift_pool = old_content.get("shift_event_pool", old_content["shift_events"])
        shift_indices = []
        for event in SHIFT_EVENTS:
            try:
                shift_indices.append(old_shift_pool.index(event))
            except ValueError:
                shift_indices = []
                break

        old_day_pools = old_content.get("first_week_day_pools", [[day] for day in old_content["first_week_days"]])
        day_variant_indices = []
        for day_index, day in enumerate(FIRST_WEEK_DAYS):
            try:
                day_variant_indices.append(old_day_pools[day_index].index(day))
            except (IndexError, ValueError):
                day_variant_indices = []
                break

        answer_indices = {}
        for day_index, answer in self.first_week_answers.items():
            if day_index >= len(FIRST_WEEK_DAYS):
                continue
            try:
                answer_indices[day_index] = FIRST_WEEK_DAYS[day_index]["choices"].index(answer)
            except ValueError:
                continue

        self.language.set(code)
        self._set_language_data(code)

        new_shift_pool = new_content.get("shift_event_pool", new_content["shift_events"])
        if shift_indices and all(index < len(new_shift_pool) for index in shift_indices):
            SHIFT_EVENTS = [new_shift_pool[index] for index in shift_indices]

        new_day_pools = new_content.get("first_week_day_pools", [[day] for day in new_content["first_week_days"]])
        if day_variant_indices and len(day_variant_indices) == len(new_day_pools):
            FIRST_WEEK_DAYS = [
                pool[min(variant_index, len(pool) - 1)]
                for pool, variant_index in zip(new_day_pools, day_variant_indices)
            ]

        self.tour_mode.set(new_tour_keys[min(tour_index, len(new_tour_keys) - 1)])
        self.scenario_name.set(new_scenario_keys[min(scenario_index, len(new_scenario_keys) - 1)])
        if old_station_is_all:
            self.quest_station.set(self.all_station_label())

        self.shift_index = min(self.shift_index, len(SHIFT_EVENTS))
        self.tour_step = min(self.tour_step, len(TOUR_MODES[self.tour_mode.get()]["steps"]))
        self.scenario_step = min(self.scenario_step, len(SCENARIOS[self.scenario_name.get()]["steps"]))
        self.first_week_day = min(self.first_week_day, max(len(FIRST_WEEK_DAYS) - 1, 0))
        self.first_week_answers = {
            day_index: FIRST_WEEK_DAYS[day_index]["choices"][choice_index]
            for day_index, choice_index in answer_indices.items()
            if day_index < len(FIRST_WEEK_DAYS)
            and choice_index < len(FIRST_WEEK_DAYS[day_index]["choices"])
        }
        self.first_week_choice_orders = {}
        self.first_week_feedback.set(self.tx("언어를 바꿨습니다. 현재 첫 주 진행도는 그대로 유지됩니다.", "Language changed. Your current first-week progress is preserved."))
        self.tour_feedback.set(self.tx("언어를 바꿨습니다. 현재 동선 진행도는 그대로 유지됩니다.", "Language changed. Your current route progress is preserved."))
        self.quest_feedback.set(self.tx("언어를 바꿨습니다. 구역과 역량 필터를 유지했습니다.", "Language changed. Zone and skill filters are preserved."))
        self._refresh_shell_language()
        self.show_page(self.current_page_key)

    def _load_assets(self):
        for key, filename in ASSET_FILES.items():
            path = resource_path("assets", filename)
            self.asset_paths[key] = path
            if os.path.exists(path):
                try:
                    self.images[key] = tk.PhotoImage(file=path)
                except tk.TclError:
                    self.images[key] = None
            else:
                self.images[key] = None

    def _setup_style(self):
        try:
            self.option_add("*Font", FONT_NORMAL)
        except tk.TclError:
            pass
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Page.TFrame", background=COLORS["bg"])
        style.configure("Panel.TFrame", background=COLORS["panel"], relief="flat")
        style.configure("Alt.TFrame", background=COLORS["panel_alt"], relief="flat")
        style.configure("Sidebar.TFrame", background=COLORS["sidebar"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["ink"], font=FONT_NORMAL)
        style.configure("Panel.TLabel", background=COLORS["panel"], foreground=COLORS["ink"], font=FONT_NORMAL)
        style.configure("Muted.TLabel", background=COLORS["panel"], foreground=COLORS["muted"], font=FONT_SMALL)
        style.configure("Title.TLabel", background=COLORS["bg"], foreground=COLORS["ink"], font=FONT_TITLE)
        style.configure("Subtitle.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=FONT_NORMAL)
        style.configure("CardTitle.TLabel", background=COLORS["panel"], foreground=COLORS["ink"], font=FONT_CARD_TITLE)
        style.configure("SidebarTitle.TLabel", background=COLORS["sidebar"], foreground=COLORS["sidebar_ink"], font=FONT_SIDEBAR_TITLE)
        style.configure("SidebarSub.TLabel", background=COLORS["sidebar"], foreground=COLORS["sidebar_muted"], font=FONT_SMALL)
        style.configure("TButton", background=COLORS["panel_alt"], foreground=COLORS["ink"], borderwidth=1, relief="flat", focusthickness=1, focuscolor=COLORS["primary"], padding=(12, 8), font=FONT_BOLD)
        style.map("TButton", background=[("active", COLORS["soft_gray"]), ("pressed", COLORS["line"])], foreground=[("active", COLORS["ink"])])
        style.configure("Primary.TButton", background=COLORS["primary"], foreground="#ffffff", borderwidth=0, focusthickness=1, focuscolor=COLORS["primary_dark"], padding=(13, 8), font=FONT_BOLD)
        style.map("Primary.TButton", background=[("active", COLORS["primary_dark"]), ("pressed", COLORS["primary_dark"])], foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
        style.configure("Accent.TButton", background=COLORS["accent"], foreground="#ffffff", borderwidth=0, focusthickness=1, focuscolor=COLORS["accent_dark"], padding=(13, 8), font=FONT_BOLD)
        style.map("Accent.TButton", background=[("active", COLORS["accent_dark"]), ("pressed", COLORS["accent_dark"])], foreground=[("active", "#ffffff")])
        style.configure("Success.Horizontal.TProgressbar", troughcolor=COLORS["line"], background=COLORS["primary"], thickness=12)
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["soft_gray"],
            troughcolor=COLORS["bg"],
            bordercolor=COLORS["bg"],
            arrowcolor=COLORS["muted"],
            lightcolor=COLORS["soft_gray"],
            darkcolor=COLORS["soft_gray"],
            width=8,
        )
        style.map("Vertical.TScrollbar", background=[("active", COLORS["line_dark"]), ("pressed", COLORS["muted"])])
        style.configure("TCheckbutton", background=COLORS["panel"], foreground=COLORS["ink"], font=FONT_NORMAL)
        style.configure("TRadiobutton", background=COLORS["panel"], foreground=COLORS["ink"], font=FONT_NORMAL)
        style.configure("TCombobox", fieldbackground=COLORS["panel_alt"], background=COLORS["panel_alt"], foreground=COLORS["ink"], arrowcolor=COLORS["primary"], bordercolor=COLORS["card_border"], padding=5)

    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=240, highlightthickness=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        header = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        header.pack(fill="x", padx=15, pady=(10, 5))
        brand_mark = tk.Label(
            header,
            text="UW",
            bg=COLORS["ink"],
            fg="#ffffff",
            font=FONT_CHIP,
            width=3,
            height=1,
        )
        brand_mark.pack(side="left", padx=(0, 9), ipadx=2, ipady=6)
        brand_copy = tk.Frame(header, bg=COLORS["sidebar"])
        brand_copy.pack(side="left", fill="x", expand=True)
        self.sidebar_brand_1 = tk.Label(brand_copy, text="U.S. Ward", bg=COLORS["sidebar"], fg=COLORS["sidebar_ink"], font=FONT_SIDEBAR_TITLE)
        self.sidebar_brand_1.pack(anchor="w")
        self.sidebar_brand_2 = tk.Label(brand_copy, text="Experience Lab", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_SMALL_BOLD)
        self.sidebar_brand_2.pack(anchor="w", pady=(1, 0))
        self.sidebar_tagline = tk.Label(
            self.sidebar,
            text="첫 7일 적응 시뮬레이터",
            bg=COLORS["sidebar"],
            fg=COLORS["sidebar_muted"],
            font=FONT_CHIP,
            anchor="w",
        )
        # Kept for language refresh; the compact shell lets the progress card carry this context.

        self.sidebar_start_button = tk.Button(
            self.sidebar,
            text="＋  오늘 리허설 시작",
            command=lambda: self.show_page("first7"),
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            activebackground=COLORS["sidebar_select"],
            activeforeground=COLORS["primary_dark"],
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["sidebar_line"],
            cursor="hand2",
            font=FONT_SMALL_BOLD,
            anchor="w",
            padx=11,
            pady=7,
        )
        self.sidebar_start_button.pack(fill="x", padx=15, pady=(0, 6))

        status = tk.Frame(self.sidebar, bg=COLORS["sidebar"], highlightthickness=0)
        status.pack(fill="x", padx=15, pady=(0, 3))
        status_top = tk.Frame(status, bg=COLORS["sidebar"])
        status_top.pack(fill="x", pady=(2, 0))
        self.status_mode_label = tk.Label(status_top, text="FIRST WEEK", bg=COLORS["sidebar"], fg=COLORS["primary"], font=FONT_CHIP)
        self.status_mode_label.pack(side="left")
        self.status_progress_label = tk.Label(status_top, text="Day 1 / 7", bg=COLORS["sidebar"], fg=COLORS["sidebar_ink"], font=FONT_SMALL_BOLD)
        self.status_progress_label.pack(side="right")
        self.status_day_label = tk.Label(status, text="Day 1-7", bg=COLORS["sidebar"], fg=COLORS["sidebar_ink"], font=FONT_CARD_TITLE)
        self.status_flow_label = tk.Label(status, text="보고 · 선택 · 디브리핑", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_SMALL)
        self.status_progress_title = tk.Label(status, text="진행 상태", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_CHIP)
        self.status_progress_bar = tk.Canvas(status, height=9, bg=COLORS["sidebar"], highlightthickness=0)
        self.status_progress_bar.pack(fill="x", pady=(3, 1))
        status_bottom = tk.Frame(status, bg=COLORS["sidebar"])
        status_bottom.pack(fill="x", pady=(0, 2))
        self.status_completed_label = tk.Label(status_bottom, text="완료 0 / 7", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_CHIP)
        self.status_completed_label.pack(side="left")
        self.status_risk_label = tk.Label(status_bottom, text="시작 전", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_CHIP)
        self.status_risk_label.pack(side="right")
        tk.Frame(self.sidebar, bg=COLORS["sidebar_line"], height=1).pack(fill="x", padx=15, pady=(1, 3))

        nav_shell = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        nav_shell.pack(fill="both", expand=True, padx=(10, 7), pady=(0, 3))
        self.nav_canvas = tk.Canvas(
            nav_shell,
            bg=COLORS["sidebar"],
            highlightthickness=0,
            borderwidth=0,
            yscrollincrement=1,
        )
        self.nav_scrollbar = ttk.Scrollbar(
            nav_shell,
            orient="vertical",
            command=self.nav_canvas.yview,
        )
        self.nav_scrollbar.pack(side="right", fill="y")
        self.nav_canvas.pack(side="left", fill="both", expand=True)
        self.nav_canvas.configure(yscrollcommand=self.nav_scrollbar.set)
        nav = tk.Frame(self.nav_canvas, bg=COLORS["sidebar"])
        self.nav_window_id = self.nav_canvas.create_window((0, 0), window=nav, anchor="nw")

        def update_nav_region(_event=None):
            self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all"))

        def fit_nav_width(event):
            self.nav_canvas.itemconfigure(self.nav_window_id, width=event.width)

        def scroll_nav(event):
            if event.delta:
                direction = -1 if event.delta > 0 else 1
                self.nav_canvas.yview_scroll(direction * 54, "units")
            return "break"

        def bind_nav_scroll(widget):
            widget.bind("<MouseWheel>", scroll_nav)
            for child in widget.winfo_children():
                bind_nav_scroll(child)

        nav.bind("<Configure>", update_nav_region)
        self.nav_canvas.bind("<Configure>", fit_nav_width)
        self.nav_canvas.bind("<MouseWheel>", scroll_nav)
        self.nav_buttons = {}
        self.nav_group_labels = {}
        labels = dict(NAV_ITEMS)
        nav_icons = {
            "dashboard": "⌂",
            "first7": "7",
            "tour": "⌖",
            "shift": "▤",
            "quests": "✦",
            "scenarios": "▣",
            "sbar": "↗",
            "english": "A",
            "specialties": "◎",
            "checklists": "✓",
            "guide": "?",
        }

        def bind_nav_hover(widget, page_key):
            widget.bind("<Enter>", lambda _event: self._hover_nav_button(page_key, True))
            widget.bind("<Leave>", lambda _event: self._hover_nav_button(page_key, False))
            for child in widget.winfo_children():
                bind_nav_hover(child, page_key)

        for group_key, keys in NAV_GROUPS:
            group_label = tk.Label(
                nav,
                text=group_key,
                bg=COLORS["sidebar"],
                fg=COLORS["sidebar_muted"],
                font=FONT_SMALL_BOLD,
                anchor="w",
            )
            group_label.pack(fill="x", padx=9, pady=(7 if group_key != "start" else 3, 3))
            self.nav_group_labels[group_key] = group_label
            for key in keys:
                row = tk.Frame(nav, bg=COLORS["sidebar"], height=56, cursor="hand2")
                row.pack(fill="x", padx=(0, 2), pady=1)
                row.pack_propagate(False)
                bar = tk.Frame(row, bg=COLORS["sidebar"], width=2, height=56)
                bar.pack(side="left", fill="y")
                marker = tk.Label(
                    row,
                    text=nav_icons.get(key, NAV_MARKERS.get(key, "")),
                    bg=COLORS["sidebar_alt"],
                    fg=COLORS["sidebar_muted"],
                    font=FONT_SMALL_BOLD,
                    width=2,
                    padx=3,
                    pady=4,
                    cursor="hand2",
                )
                marker.pack(side="left", padx=(7, 7), pady=13)
                copy = tk.Frame(row, bg=COLORS["sidebar"], cursor="hand2")
                label_widget = tk.Label(
                    copy,
                    text=labels.get(key, key),
                    bg=COLORS["sidebar"],
                    fg=COLORS["sidebar_ink"],
                    font=FONT_SMALL_BOLD,
                    anchor="w",
                    cursor="hand2",
                )
                label_widget.pack(fill="x")
                description = tk.Label(
                    copy,
                    text="",
                    bg=COLORS["sidebar"],
                    fg=COLORS["sidebar_muted"],
                    font=FONT_CHIP,
                    anchor="w",
                    cursor="hand2",
                )
                description.pack(fill="x", pady=(1, 0))
                status_dot = tk.Label(
                    row,
                    text="●",
                    bg=COLORS["sidebar"],
                    fg=COLORS["line_dark"],
                    font=FONT_CHIP,
                    cursor="hand2",
                )
                status_dot.pack(side="right", padx=(3, 7))
                copy.pack(side="left", fill="both", expand=True, pady=(7, 5))
                self._bind_clickable(row, lambda page_key=key: self.show_page(page_key))
                bind_nav_hover(row, key)
                bind_nav_scroll(row)
                self.nav_buttons[key] = {
                    "frame": row,
                    "bar": bar,
                    "marker": marker,
                    "copy": copy,
                    "label": label_widget,
                    "description": description,
                    "status": status_dot,
                }

        # Gives the final row enough scroll runway to align to a clean row
        # boundary while remaining fully visible above the fixed footer.
        tk.Frame(nav, bg=COLORS["sidebar"], height=24).pack(fill="x")

        bind_nav_scroll(nav)

        def ensure_nav_visible(page_key):
            widgets = self.nav_buttons.get(page_key)
            if not widgets:
                return
            self.nav_canvas.update_idletasks()
            region = self.nav_canvas.bbox("all")
            if not region or region[3] <= self.nav_canvas.winfo_height():
                return
            row = widgets["frame"]
            row_top = row.winfo_y()
            row_bottom = row_top + row.winfo_height()
            viewport_height = self.nav_canvas.winfo_height()
            visible_top = self.nav_canvas.canvasy(0)
            visible_bottom = visible_top + viewport_height
            target = None
            if row_bottom <= viewport_height:
                target = 0
            elif row_top < visible_top:
                target = row_top
            elif row_bottom > visible_bottom:
                target = max(0, row_bottom - viewport_height)
            if target is None:
                return
            # Land on a group or row boundary so the viewport never starts with
            # an orphaned description line from the preceding navigation item.
            boundaries = [0]
            boundaries.extend(label.winfo_y() for label in self.nav_group_labels.values())
            boundaries.extend(item["frame"].winfo_y() for item in self.nav_buttons.values())
            snapped = min((point for point in boundaries if point >= target), default=target)
            max_offset = max(0, region[3] - viewport_height)
            self.nav_canvas.yview_moveto(min(snapped, max_offset) / region[3])

        self._ensure_nav_visible = ensure_nav_visible

        footer = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        footer.pack(side="bottom", fill="x", padx=14, pady=(1, 6))
        tk.Frame(footer, bg=COLORS["sidebar_line"], height=1).pack(fill="x", pady=(0, 4))
        lang = tk.Frame(footer, bg=COLORS["sidebar"])
        lang.pack(fill="x", pady=(0, 3))
        self.language_label = tk.Label(lang, text="언어", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_CHIP)
        self.language_label.pack(side="left", padx=(2, 7))
        for code, label in [("ko", "한국어"), ("en", "EN")]:
            button = tk.Button(lang, text=label, command=lambda lang_code=code: self.set_language(lang_code), relief="flat", borderwidth=0, cursor="hand2", font=FONT_CHIP, padx=8, pady=3)
            button.pack(side="left", padx=(0, 4))
            self.lang_buttons[code] = button
        self.status_version_label = tk.Label(lang, text=APP_VERSION, bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_CHIP)
        self.footer_title = tk.Label(footer, text="교육용 시뮬레이션", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_CHIP)
        self.footer_note = tk.Label(footer, text="기관 정책과 state scope는 별도 확인", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_CHIP, wraplength=200, justify="left")
        self.feedback_note = tk.Label(footer, text="", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_CHIP)
        self.feedback_button = tk.Button(
            footer,
            text="피드백 남기기",
            command=self.open_feedback_form,
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            activebackground=COLORS["sidebar_alt"],
            activeforeground=COLORS["sidebar_ink"],
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["sidebar_line"],
            cursor="hand2",
            font=FONT_CHIP,
            padx=10,
            pady=4,
        )
        self.feedback_button.pack(fill="x")
        self.footer_copyright = tk.Label(footer, text="", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=FONT_CHIP)

        self.workspace = tk.Frame(self, bg=COLORS["bg"])
        self.workspace.pack(side="right", fill="both", expand=True)

        self.topbar = tk.Frame(self.workspace, bg=COLORS["panel"], height=50, highlightthickness=0)
        self.topbar.pack(side="top", fill="x")
        self.topbar.pack_propagate(False)
        topbar_left = tk.Frame(self.topbar, bg=COLORS["panel"])
        topbar_left.pack(side="left", fill="y", padx=(18, 10))
        self.topbar_work_label = tk.Label(
            topbar_left,
            text="CURRENT WORK · Home",
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            font=FONT_SMALL_BOLD,
        )
        self.topbar_work_label.pack(side="left", pady=15)

        topbar_right = tk.Frame(self.topbar, bg=COLORS["panel"])
        topbar_right.pack(side="right", padx=(10, 18), pady=10)
        self.topbar_role_label = tk.Label(topbar_right, text="Staff RN", bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_CHIP, padx=9, pady=4)
        self.topbar_role_label.pack(side="left", padx=(0, 8))
        self.topbar_version_label = tk.Label(topbar_right, text=APP_VERSION, bg=COLORS["panel"], fg=COLORS["muted"], font=FONT_CHIP)
        self.topbar_version_label.pack(side="left")

        topbar_status = tk.Frame(self.topbar, bg=COLORS["panel"])
        topbar_status.pack(side="right", fill="x", expand=True, pady=15)
        self.topbar_status_labels = []
        for dot_color, text_value in [
            (COLORS["success"], "Local practice"),
            (COLORS["success"], "Synthetic cases"),
            (COLORS["accent"], "No real PHI"),
        ]:
            label = tk.Label(topbar_status, text=f"●  {text_value}", bg=COLORS["panel"], fg=dot_color, font=FONT_CHIP)
            label.pack(side="left", padx=8)
            self.topbar_status_labels.append(label)

        tk.Frame(self.workspace, bg=COLORS["line"], height=1).pack(side="top", fill="x")
        self.page = ScrollableFrame(self.workspace)
        self.page.pack(side="top", fill="both", expand=True)
        self._refresh_shell_language()

    def _refresh_shell_language(self):
        if not hasattr(self, "nav_buttons"):
            return
        self.sidebar_tagline.configure(text=self.tx("첫 7일 적응 시뮬레이터", "First-week adaptation simulator"))
        self.status_mode_label.configure(text=self.tx("첫 주 진행", "FIRST WEEK"))
        self.status_flow_label.configure(text=self.tx("보고 · 선택 · 디브리핑", "Observe · Decide · Debrief"))
        self.status_version_label.configure(text=APP_VERSION)
        self.status_progress_title.configure(text=self.tx("진행 상태", "Progress"))
        self.language_label.configure(text=self.tx("언어", "Language"))
        self.footer_title.configure(text=self.tx("교육용 시뮬레이션", "Educational simulation"))
        self.footer_note.configure(text=self.tx("기관 정책과 state scope는 별도 확인", "Verify facility policy and state scope separately."))
        self.feedback_note.configure(text=self.tx("베타 테스트 후 짧은 피드백을 남겨주세요.", "Please leave short beta feedback."))
        self.feedback_button.configure(text=self.tx("피드백 남기기", "Send Feedback"))
        self.sidebar_start_button.configure(text=self.tx("＋  오늘 리허설 시작", "＋  Start rehearsal"))
        self.footer_copyright.configure(text="Copyright darkha123@gmail.com")
        if hasattr(self, "topbar_work_label"):
            current_labels = dict(NAV_ITEMS)
            current_page = current_labels.get(self.current_page_key, self.current_page_key)
            self.topbar_work_label.configure(
                text=self.tx(f"현재 업무 · {current_page}", f"Current work · {current_page}")
            )
            status_copy = (
                ["로컬 연습", "합성 사례", "실제 PHI 금지"]
                if not self.is_english()
                else ["Local practice", "Synthetic cases", "No real PHI"]
            )
            status_colors = [COLORS["success"], COLORS["success"], COLORS["accent"]]
            for label, copy, color in zip(self.topbar_status_labels, status_copy, status_colors):
                label.configure(text=f"●  {copy}", fg=color)
            self.topbar_role_label.configure(text=self.role_label())
            self.topbar_version_label.configure(text=APP_VERSION)
        group_copy = {
            "start": self.tx("시작하기", "Get started"),
            "practice": self.tx("실전 연습", "Practice lab"),
            "tools": self.tx("준비 도구", "Readiness tools"),
        }
        nav_descriptions = {
            "dashboard": self.tx("오늘 학습 한눈에", "Today's overview"),
            "first7": self.tx("첫 주 장면 연습", "First-week scenes"),
            "tour": self.tx("병동 동선 익히기", "Learn unit routes"),
            "shift": self.tx("근무 흐름 따라가기", "Follow a shift"),
            "quests": self.tx("짧은 판단 훈련", "Quick decisions"),
            "scenarios": self.tx("환자 변화 대응", "Respond to changes"),
            "sbar": self.tx("안전한 보고 구성", "Build a safe report"),
            "english": self.tx("병동 표현 말하기", "Ward phrases"),
            "specialties": self.tx("역할별 책임 비교", "Compare RN roles"),
            "checklists": self.tx("나의 준비도 확인", "Check readiness"),
            "guide": self.tx("정책·안전 참고", "Policy and safety"),
        }
        nav_titles = {
            "dashboard": self.tx("오늘의 홈", "Home"),
            "first7": self.tx("첫 7일 적응", "First 7 Days"),
            "tour": self.tx("병동 둘러보기", "Ward Tour"),
            "shift": self.tx("근무 흐름", "Shift Flow"),
            "quests": self.tx("상황 판단", "Decision Lab"),
            "scenarios": self.tx("환자 케이스", "Patient Cases"),
            "sbar": self.tx("SBAR 보고", "SBAR Reporting"),
            "english": self.tx("병동 영어", "Ward English"),
            "specialties": self.tx("직무별 가이드", "Role Guide"),
            "checklists": self.tx("준비 체크", "Readiness Check"),
            "guide": self.tx("안전·운영 안내", "Safety Guide"),
        }
        for group_key, widget in self.nav_group_labels.items():
            widget.configure(text=group_copy[group_key])
        for key, label in NAV_ITEMS:
            if key in self.nav_buttons:
                self.nav_buttons[key]["label"].configure(text=nav_titles.get(key, label))
                self.nav_buttons[key]["description"].configure(text=nav_descriptions.get(key, ""))
        for code, button in self.lang_buttons.items():
            selected = self.language.get() == code
            button.configure(
                bg=COLORS["soft_green"] if selected else COLORS["sidebar_alt"],
                fg=COLORS["primary_dark"] if selected else COLORS["sidebar_muted"],
                activebackground=COLORS["sidebar_select"],
                activeforeground=COLORS["primary_dark"] if selected else COLORS["sidebar_ink"],
            )
        if hasattr(self, "nav_canvas"):
            self.nav_canvas.after_idle(
                lambda: self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all"))
            )
        self._update_sidebar_progress()

    def _update_sidebar_progress(self):
        if not hasattr(self, "status_progress_label"):
            return
        total = max(len(FIRST_WEEK_DAYS), 1)
        completed = len(self.first_week_answers)
        day_no = min(self.first_week_day + 1, total)
        self.status_progress_label.configure(text=self.tx(f"Day {day_no} / {total}", f"Day {day_no} / {total}"))
        self.status_completed_label.configure(text=self.tx(f"완료 {completed} / {total}", f"Done {completed} / {total}"))
        if self.last_first_week_choice_best is True:
            risk_text = self.tx("안전 흐름", "Safe")
            risk_bg = COLORS["soft_green"]
            risk_fg = COLORS["success_dark"]
        elif self.last_first_week_choice_best is False:
            risk_text = self.tx("복습 필요", "Review")
            risk_bg = COLORS["soft_orange"]
            risk_fg = COLORS["danger"]
        else:
            risk_text = self.tx("시작 전", "Not started")
            risk_bg = COLORS["sidebar"]
            risk_fg = COLORS["sidebar_muted"]
        self.status_risk_label.configure(text=risk_text, bg=risk_bg, fg=risk_fg, padx=7, pady=3)
        canvas = self.status_progress_bar

        def draw(_event=None):
            width = max(canvas.winfo_width(), 160)
            canvas.delete("all")
            self.rounded_rect(canvas, 0, 4, width, 9, 2, fill=COLORS["sidebar_line"], outline="")
            fill_w = int(width * completed / total)
            if fill_w:
                self.rounded_rect(canvas, 0, 4, max(fill_w, 8), 9, 2, fill=COLORS["primary"], outline="")

        canvas.bind("<Configure>", draw)
        canvas.after_idle(draw)

    def _on_nav_select(self, _event):
        if not hasattr(self, "nav_list"):
            return
        selection = self.nav_list.curselection()
        if not selection:
            return
        key = NAV_ITEMS[selection[0]][0]
        self.show_page(key)

    def _apply_page_shell_state(self, key):
        labels = dict(NAV_ITEMS)
        if hasattr(self, "topbar_work_label"):
            page_name = labels.get(key, key)
            self.topbar_work_label.configure(
                text=self.tx(f"현재 업무 · {page_name}", f"Current work · {page_name}")
            )
            self.topbar_role_label.configure(text=self.role_label())
        for nav_key, widgets in getattr(self, "nav_buttons", {}).items():
            selected = nav_key == key
            bg = COLORS["sidebar_select"] if selected else COLORS["sidebar"]
            marker_bg = COLORS["soft_green"] if selected else COLORS["sidebar_alt"]
            widgets["frame"].configure(bg=bg)
            widgets["bar"].configure(bg=COLORS["primary"] if selected else bg)
            widgets["marker"].configure(
                bg=marker_bg,
                fg=COLORS["primary_dark"] if selected else COLORS["sidebar_muted"],
            )
            widgets["copy"].configure(bg=bg)
            widgets["label"].configure(
                bg=bg,
                fg=COLORS["primary_dark"] if selected else COLORS["sidebar_ink"],
                font=FONT_SMALL_BOLD,
            )
            widgets["description"].configure(bg=bg, fg=COLORS["sidebar_muted"])
            widgets["status"].configure(
                bg=bg,
                fg=COLORS["primary"] if selected else COLORS["accent"],
            )

    def show_page(self, key):
        self._capture_page_state(getattr(self, "current_page_key", ""))
        previous_key = getattr(self, "current_page_key", "dashboard")
        self._cancel_responsive_wrap_job()
        staging = self.page.begin_layout_stage()
        self._responsive_wrap_transaction = True
        self._bind_responsive_inner(staging)
        committed = False
        try:
            self.current_page_key = key
            self._apply_page_shell_state(key)
            render = getattr(self, f"_render_{key}")
            render()
            self._update_sidebar_progress()
            self._stabilize_responsive_wraps(max_passes=6)
            self.page.commit_layout_stage()
            committed = True
            self._responsive_wrap_inner_width = self.page.inner.winfo_width()
            if hasattr(self, "_ensure_nav_visible"):
                self._ensure_nav_visible(key)
            # Flush only final-state painting; no geometry-changing work remains.
            self.update_idletasks()
        finally:
            self._responsive_wrap_transaction = False
            if not committed:
                self._responsive_wrap_update_all = False
                self.current_page_key = previous_key
                self.page.rollback_layout_stage()
                self._apply_page_shell_state(previous_key)

    def _capture_page_state(self, key):
        if key == "sbar" and getattr(self, "sbar_fields", None):
            self.sbar_draft = {
                name: field.get("1.0", "end").strip()
                for name, field in self.sbar_fields.items()
                if field.winfo_exists()
            }
            output = getattr(self, "sbar_output", None)
            if output is not None and output.winfo_exists():
                self.sbar_output_draft = output.get("1.0", "end").strip()
        elif key == "checklists" and getattr(self, "check_vars", None):
            for display_key, variable in self.check_vars.items():
                state_key = self.check_var_state_keys.get(display_key)
                if state_key is not None:
                    self.checklist_state[state_key] = variable.get()
            self.debrief_drafts = {
                note_key: text.get("1.0", "end").strip()
                for note_key, (_title, text) in self.debrief_note_fields.items()
                if text.winfo_exists()
            }

    def _hover_nav_button(self, key, hovering):
        widgets = getattr(self, "nav_buttons", {}).get(key)
        if not widgets:
            return
        selected = getattr(self, "current_page_key", "") == key
        if selected:
            return
        bg = COLORS["sidebar_alt"] if hovering else COLORS["sidebar"]
        widgets["frame"].configure(bg=bg)
        widgets["bar"].configure(bg=bg)
        widgets["marker"].configure(
            bg=COLORS["soft_green"] if hovering else COLORS["sidebar_alt"],
            fg=COLORS["primary_dark"] if hovering else COLORS["sidebar_muted"],
        )
        widgets["copy"].configure(bg=bg)
        widgets["label"].configure(
            bg=bg,
            fg=COLORS["ink"] if hovering else COLORS["sidebar_ink"],
        )
        widgets["description"].configure(bg=bg, fg=COLORS["muted"] if hovering else COLORS["sidebar_muted"])
        widgets["status"].configure(
            bg=bg,
            fg=COLORS["primary"] if hovering else COLORS["accent"],
        )

    def page_title(self, title, subtitle):
        frame = tk.Frame(self.page.inner, bg=COLORS["bg"])
        frame.pack(fill="x", padx=24, pady=(15, 8))
        top = tk.Frame(frame, bg=COLORS["bg"])
        top.pack(fill="x")
        group_labels = {
            "first7": self.tx("첫 주 시작", "START HERE"),
            "tour": self.tx("병동 익히기", "ORIENTATION"),
            "shift": self.tx("흐름 실습", "WORKFLOW PRACTICE"),
            "quests": self.tx("판단 실습", "DECISION PRACTICE"),
            "scenarios": self.tx("케이스 실습", "CASE PRACTICE"),
            "sbar": self.tx("커뮤니케이션", "COMMUNICATION"),
            "english": self.tx("언어 준비", "LANGUAGE PRACTICE"),
            "specialties": self.tx("역할 이해", "ROLE ORIENTATION"),
            "checklists": self.tx("나의 준비", "MY READINESS"),
            "guide": self.tx("안전 가이드", "SAFETY GUIDE"),
        }
        kicker = group_labels.get(self.current_page_key, self.tx("교육용 시뮬레이션", "EDUCATIONAL SIMULATION"))
        tk.Label(top, text=kicker, bg=COLORS["bg"], fg=COLORS["primary"], font=FONT_CHIP).pack(side="left")
        if self.current_page_key == "first7":
            context_text = f"Day {self.first_week_day + 1} / {max(len(FIRST_WEEK_DAYS), 1)}"
        elif self.current_page_key in ("tour", "shift", "quests", "scenarios"):
            context_text = self.role_label()
        else:
            context_text = {
                "specialties": self.tx("역할 렌즈", "ROLE LENS"),
                "english": self.tx("10분 연습", "10 MIN PRACTICE"),
                "sbar": self.tx("안전한 보고", "SAFE HANDOFF"),
                "checklists": self.tx("로컬 메모", "LOCAL NOTES"),
                "guide": self.tx("운영자용", "FACILITATOR"),
            }.get(self.current_page_key, self.tx("교육용", "TRAINING"))
        tk.Label(top, text=context_text, bg=COLORS["panel_alt"], fg=COLORS["muted"], font=FONT_CHIP, padx=8, pady=3).pack(side="right")
        tk.Label(frame, text=title, bg=COLORS["bg"], fg=COLORS["ink"], font=FONT_TITLE).pack(anchor="w", pady=(4, 0))
        tk.Label(frame, text=subtitle, bg=COLORS["bg"], fg=COLORS["muted"], font=FONT_NORMAL, wraplength=820, justify="left").pack(anchor="w", pady=(4, 0))
        return frame

    def rounded_rect(self, canvas, x1, y1, x2, y2, radius=18, **kwargs):
        radius = min(radius, int((x2 - x1) / 2), int((y2 - y1) / 2))
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return canvas.create_polygon(points, smooth=True, splinesteps=16, **kwargs)

    def canvas_button(self, parent, text, command, fill=None, fg="#ffffff", width=138, height=42):
        fill = fill or COLORS["primary"]
        canvas = tk.Canvas(parent, width=width, height=height, bg=COLORS["panel"], highlightthickness=0, cursor="hand2")
        canvas.pack_propagate(False)

        def draw(bg_color=fill):
            canvas.delete("all")
            self.rounded_rect(canvas, 2, 2, width - 2, height - 2, 14, fill=bg_color, outline=bg_color)
            canvas.create_text(width / 2, height / 2, text=text, fill=fg, font=FONT_BOLD)

        def on_enter(_event):
            hover = {
                COLORS["primary"]: COLORS["primary_dark"],
                COLORS["accent"]: COLORS["accent_dark"],
                COLORS["success"]: COLORS["success_dark"],
            }.get(fill, fill)
            draw(hover)

        canvas.bind("<Button-1>", lambda _event: command())
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", lambda _event: draw())
        draw()
        return canvas

    def feature_card(self, parent, title, subtitle, kicker, color, command, image_key=None):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        card_height = 86
        canvas = tk.Canvas(frame, height=card_height, bg=COLORS["bg"], highlightthickness=0, cursor="hand2", takefocus=True)
        canvas.pack(fill="both", expand=True)

        def draw(_event=None, hovering=False):
            width = max(canvas.winfo_width(), 220)
            canvas.delete("all")
            outline = COLORS["primary"] if hovering else COLORS["card_border"]
            card_fill = COLORS["panel_alt"] if hovering else COLORS["panel"]
            self.rounded_rect(canvas, 2, 2, width - 3, card_height - 3, 10, fill=card_fill, outline=outline, width=2 if hovering else 1)
            self.rounded_rect(canvas, 14, 18, 50, 68, 9, fill=COLORS["soft_cyan"], outline="")
            icon = self.icon_image(image_key, 22) if image_key else None
            if icon:
                canvas.create_image(32, 43, image=icon, anchor="center")
            else:
                canvas.create_oval(27, 38, 37, 48, fill=color, outline=color)
            title_id = canvas.create_text(62, 17, text=title, fill=COLORS["ink"], font=FONT_SMALL_BOLD, anchor="nw", width=max(120, width - 170))
            title_box = canvas.bbox(title_id) or (62, 17, 150, 35)
            tag_x = min(width - 62, title_box[2] + 8)
            canvas.create_text(tag_x, 19, text=kicker, fill=COLORS["accent_dark"], font=FONT_CHIP, anchor="nw")
            canvas.create_text(62, 43, text=self.clean_text(subtitle), fill=COLORS["muted"], font=FONT_SMALL, anchor="nw", width=max(120, width - 112))
            canvas.create_text(width - 22, 43, text="›", fill=COLORS["primary"], font=FONT_SECTION, anchor="center")

        canvas.bind("<Configure>", draw)
        canvas.bind("<Button-1>", lambda _event: command())
        canvas.bind("<Return>", lambda _event: command())
        canvas.bind("<space>", lambda _event: command())
        canvas.bind("<Enter>", lambda _event: draw(hovering=True))
        canvas.bind("<Leave>", lambda _event: draw(hovering=False))
        canvas.bind("<FocusIn>", lambda _event: draw(hovering=True))
        canvas.bind("<FocusOut>", lambda _event: draw(hovering=False))
        frame.bind("<Button-1>", lambda _event: command())
        return frame

    def metric_card(self, parent, number, label, color):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        canvas = tk.Canvas(frame, height=112, bg=COLORS["bg"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def draw(_event=None):
            width = max(canvas.winfo_width(), 220)
            canvas.delete("all")
            self.rounded_rect(canvas, 3, 4, width - 4, 106, 16, fill=color, outline=color)
            canvas.create_text(24, 34, text=number, fill=COLORS["ink"], font=FONT_METRIC, anchor="w")
            canvas.create_text(24, 72, text=label, fill=COLORS["ink"], font=FONT_NORMAL, anchor="w", width=width - 48)

        canvas.bind("<Configure>", draw)
        return frame

    def top_stat_card(self, parent, number, label, detail, accent, dark=False):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        canvas = tk.Canvas(frame, height=158, bg=COLORS["bg"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def draw(_event=None):
            width = max(canvas.winfo_width(), 220)
            canvas.delete("all")
            card_bg = COLORS["primary"] if dark else COLORS["panel"]
            number_fg = "#ffffff" if dark else COLORS["primary"]
            label_fg = "#dbeafe" if dark else COLORS["ink"]
            detail_fg = "#9beafe" if dark else COLORS["muted"]
            self.rounded_rect(canvas, 5, 8, width - 5, 150, 24, fill=COLORS["shadow"], outline="")
            self.rounded_rect(canvas, 3, 3, width - 8, 144, 24, fill=card_bg, outline=COLORS["card_border"])
            canvas.create_rectangle(24, 24, 62, 28, fill=accent, outline=accent)
            canvas.create_text(24, 62, text=number, fill=number_fg, font=FONT_METRIC, anchor="w", width=width - 48)
            canvas.create_text(24, 104, text=label, fill=label_fg, font=FONT_SMALL_BOLD, anchor="w", width=width - 48)
            canvas.create_text(24, 130, text=detail, fill=detail_fg, font=FONT_CHIP, anchor="w", width=width - 48)

        canvas.bind("<Configure>", draw)
        return frame

    def bento_card(self, parent, title, subtitle, tag, accent, image_key=None, command=None, height=170, dark=False):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        cursor = "hand2" if command else ""
        canvas = tk.Canvas(frame, height=height, bg=COLORS["bg"], highlightthickness=0, cursor=cursor)
        canvas.pack(fill="both", expand=True)

        def draw(_event=None):
            width = max(canvas.winfo_width(), 260)
            canvas.delete("all")
            card_bg = COLORS["primary"] if dark else COLORS["panel"]
            title_fg = "#ffffff" if dark else COLORS["ink"]
            body_fg = "#dbeafe" if dark else COLORS["muted"]
            chip_bg = COLORS["accent"] if dark else COLORS["soft_cyan"]
            chip_fg = "#ffffff" if dark else COLORS["accent_dark"]

            self.rounded_rect(canvas, 5, 7, width - 5, height - 5, 26, fill=COLORS["shadow"], outline="")
            self.rounded_rect(canvas, 3, 3, width - 8, height - 10, 26, fill=card_bg, outline=COLORS["card_border"])
            canvas.create_rectangle(3, 28, 8, height - 34, fill=accent, outline=accent)

            text_right = width - 34
            if image_key:
                image_w = min(180, max(112, int(width * 0.28)))
                image_h = min(height - 46, 132)
                image = self.scaled_image(image_key, image_w, image_h)
                if image:
                    self.rounded_rect(canvas, width - image_w - 24, 24, width - 22, 24 + image_h, 18, fill=COLORS["panel_alt"], outline="")
                    canvas.create_image(width - image_w - 23, 25, image=image, anchor="nw")
                    text_right = width - image_w - 46

            self.rounded_rect(canvas, 28, 23, min(220, 36 + len(tag) * 8), 49, 12, fill=chip_bg, outline=chip_bg)
            canvas.create_text(42, 36, text=tag, fill=chip_fg, font=FONT_CHIP, anchor="w")
            canvas.create_text(28, 68, text=title, fill=title_fg, font=FONT_CARD_TITLE, anchor="nw", width=max(210, text_right - 28))
            canvas.create_text(28, 106, text=self.clean_text(subtitle), fill=body_fg, font=FONT_SMALL, anchor="nw", width=max(210, text_right - 28))
            if command:
                canvas.create_text(width - 28, height - 22, text=self.tx("열기  ->", "Open  ->"), fill=COLORS["primary"], font=FONT_SMALL_BOLD, anchor="e")

        canvas.bind("<Configure>", draw)
        if command:
            canvas.bind("<Button-1>", lambda _event: command())
            frame.bind("<Button-1>", lambda _event: command())
        return frame

    def testimonial_card(self, parent, initials, name, route, quote, outcome, accent, dark=False):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        height = 226
        canvas = tk.Canvas(frame, height=height, bg=COLORS["bg"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def draw(_event=None):
            width = max(canvas.winfo_width(), 270)
            canvas.delete("all")
            card_bg = COLORS["primary"] if dark else COLORS["panel"]
            title_fg = "#ffffff" if dark else COLORS["ink"]
            body_fg = "#dbeafe" if dark else COLORS["muted"]
            muted_fg = "#a7f3d0" if dark else COLORS["accent_dark"]
            self.rounded_rect(canvas, 5, 8, width - 5, height - 6, 26, fill=COLORS["shadow"], outline="")
            self.rounded_rect(canvas, 3, 3, width - 8, height - 12, 26, fill=card_bg, outline=COLORS["card_border"])
            canvas.create_oval(24, 24, 78, 78, fill=accent, outline=accent)
            canvas.create_text(51, 51, text=initials, fill="#ffffff", font=FONT_SMALL_BOLD)
            canvas.create_text(92, 27, text=name, fill=title_fg, font=FONT_SMALL_BOLD, anchor="nw", width=width - 122)
            canvas.create_text(92, 51, text=route, fill=muted_fg, font=FONT_CHIP, anchor="nw", width=width - 122)
            canvas.create_line(24, 96, width - 28, 96, fill=COLORS["line"] if not dark else "#244762")
            canvas.create_text(26, 116, text=quote, fill=body_fg, font=FONT_SMALL, anchor="nw", width=width - 54)
            self.rounded_rect(canvas, 24, height - 48, width - 28, height - 22, 12, fill=COLORS["soft_cyan"] if not dark else "#123d56", outline="")
            canvas.create_text(38, height - 35, text=outcome, fill=COLORS["primary"], font=FONT_CHIP, anchor="w", width=width - 78)

        canvas.bind("<Configure>", draw)
        return frame

    def _card_shell(self, parent, bg=None, padding=16, border=None):
        bg = bg or COLORS["panel"]
        border = border or COLORS["card_border"]
        outer = tk.Frame(parent, bg=border, highlightthickness=0)
        frame = tk.Frame(outer, bg=bg, highlightthickness=0, padx=padding, pady=padding)
        frame.pack(fill="both", expand=True, padx=1, pady=1)
        return outer, frame

    def panel(self, parent=None, padding=16):
        parent = parent or self.page.inner
        outer, frame = self._card_shell(parent, padding=padding)
        outer.pack(fill="x", padx=24, pady=6)
        return frame

    def two_columns(self, parent=None):
        parent = parent or self.page.inner
        outer = tk.Frame(parent, bg=COLORS["bg"])
        outer.pack(fill="x", padx=24, pady=6)
        outer.columnconfigure(0, weight=1, uniform="content_pair")
        outer.columnconfigure(1, weight=1, uniform="content_pair")
        left_outer, left = self._card_shell(outer, padding=16)
        right_outer, right = self._card_shell(outer, padding=16)
        left_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        right_outer.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        return left, right

    def choice_button(self, parent, text, command, bg=None, active=None, font=None, wraplength=840):
        bg = bg or COLORS["panel"]
        button = tk.Button(
            parent,
            text=self.clean_text(text),
            command=command,
            bg=bg,
            fg=COLORS["ink"],
            activebackground=active or COLORS["soft_cyan"],
            activeforeground=COLORS["ink"],
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["card_border"],
            highlightcolor=COLORS["primary"],
            cursor="hand2",
            font=font or FONT_NORMAL,
            anchor="w",
            justify="left",
            wraplength=wraplength,
            padx=12,
            pady=7,
        )
        return button

    def mark_choice_selection(self, variable, value, selected_button, buttons, selected_bg):
        variable.set(value)
        for button in buttons:
            button.configure(
                bg=COLORS["panel"],
                highlightbackground=COLORS["card_border"],
                highlightthickness=1,
                fg=COLORS["ink"],
            )
        selected_button.configure(
            bg=selected_bg,
            highlightbackground=COLORS["primary"],
            highlightthickness=2,
            fg=COLORS["ink"],
        )

    def modern_textbox(self, parent, height=4):
        box = tk.Text(
            parent,
            height=height,
            wrap="word",
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["card_border"],
            highlightcolor=COLORS["accent"],
            bg=COLORS["panel_alt"],
            fg=COLORS["ink"],
            insertbackground=COLORS["accent"],
            font=FONT_NORMAL,
            padx=14,
            pady=12,
            spacing1=2,
            spacing2=2,
            spacing3=6,
        )
        box.bind("<FocusIn>", lambda _event: box.configure(highlightbackground=COLORS["accent"], highlightthickness=2))
        box.bind("<FocusOut>", lambda _event: box.configure(highlightbackground=COLORS["card_border"], highlightthickness=1))
        return box

    def modern_progress(self, parent, value, maximum=100, height=14, fill=None, bg=None):
        fill = fill or COLORS["accent"]
        bg = bg or COLORS["panel"]
        canvas = tk.Canvas(parent, height=height + 12, bg=bg, highlightthickness=0)

        def draw(_event=None):
            width = max(canvas.winfo_width(), 180)
            canvas.delete("all")
            y1 = 6
            y2 = y1 + height
            radius = max(4, height // 2)
            self.rounded_rect(canvas, 0, y1, width, y2, radius, fill=COLORS["line"], outline="")
            pct = max(0, min(1, float(value) / max(float(maximum), 1.0)))
            fill_w = int(width * pct)
            if fill_w > 0:
                self.rounded_rect(canvas, 0, y1, max(fill_w, height), y2, radius, fill=fill, outline="")

        canvas.bind("<Configure>", draw)
        canvas.after_idle(draw)
        return canvas

    def modern_checkbox(self, parent, text, variable, wraplength=880, on_change=None):
        row = tk.Frame(parent, bg=COLORS["panel"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=12, pady=10)
        box = tk.Canvas(row, width=22, height=22, bg=COLORS["panel"], highlightthickness=0, cursor="hand2")
        box.pack(side="left", anchor="n", padx=(0, 10))
        label = tk.Label(
            row,
            text=self.clean_text(text),
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            font=FONT_NORMAL,
            wraplength=wraplength,
            justify="left",
            anchor="w",
            cursor="hand2",
        )
        label.pack(side="left", fill="x", expand=True)

        def draw():
            box.delete("all")
            checked = bool(variable.get())
            outline = COLORS["accent"] if checked else COLORS["line_dark"]
            fill = COLORS["accent"] if checked else COLORS["panel_alt"]
            self.rounded_rect(box, 2, 2, 20, 20, 6, fill=fill, outline=outline)
            if checked:
                box.create_line(7, 11, 10, 15, 16, 7, fill="#ffffff", width=2, capstyle="round", joinstyle="round")
            row.configure(highlightbackground=COLORS["accent"] if checked else COLORS["card_border"])

        def toggle(_event=None):
            variable.set(not bool(variable.get()))
            draw()
            if on_change:
                on_change()

        def set_hover(hovering):
            bg = COLORS["panel_alt"] if hovering else COLORS["panel"]
            row.configure(bg=bg)
            box.configure(bg=bg)
            label.configure(bg=bg)

        for widget in (row, box, label):
            widget.bind("<Button-1>", toggle)
            widget.bind("<Enter>", lambda _event: set_hover(True))
            widget.bind("<Leave>", lambda _event: set_hover(False))
        draw()
        return row

    def _bind_clickable(self, widget, command, root=True):
        try:
            widget.configure(cursor="hand2")
        except tk.TclError:
            pass
        widget.bind("<Button-1>", lambda _event: command())
        if root:
            try:
                widget.configure(takefocus=True)
            except tk.TclError:
                pass
            widget.bind("<Return>", lambda _event: command())
            widget.bind("<space>", lambda _event: command())
        for child in widget.winfo_children():
            self._bind_clickable(child, command, root=False)

    def selectable_choice_card(self, parent, number, text, command, selected=False, is_best=False, wraplength=720):
        fill = COLORS["soft_green"] if selected and is_best else COLORS["soft_orange"] if selected else COLORS["panel"]
        border = COLORS["success"] if selected and is_best else COLORS["accent"] if selected else COLORS["card_border"]
        stripe = COLORS["success"] if selected and is_best else COLORS["accent"] if selected else COLORS["line_dark"]
        card = tk.Frame(parent, bg=fill, highlightthickness=2 if selected else 1, highlightbackground=border)
        card.columnconfigure(2, weight=1)
        tk.Frame(card, bg=stripe if selected else COLORS["panel"], width=4).grid(row=0, column=0, sticky="ns")
        badge_bg = stripe if selected else COLORS["soft_gray"]
        badge_fg = "#ffffff" if selected else COLORS["muted"]
        badge = tk.Label(card, text=chr(64 + number) if 1 <= number <= 26 else str(number), bg=badge_bg, fg=badge_fg, font=FONT_SMALL_BOLD, width=3)
        badge.grid(row=0, column=1, padx=(11, 7), pady=9, sticky="n")
        body = tk.Label(card, text=self.clean_text(text), bg=fill, fg=COLORS["ink"], font=FONT_NORMAL, wraplength=wraplength, justify="left", anchor="w")
        body.grid(row=0, column=2, sticky="ew", padx=(4, 10), pady=9)
        chip_text = "✓" if selected else "○"
        chip_bg = stripe if selected else fill
        chip_fg = "#ffffff" if selected else COLORS["line_dark"]
        chip = tk.Label(card, text=chip_text, bg=chip_bg, fg=chip_fg, font=FONT_SMALL_BOLD, padx=5, pady=3)
        chip.grid(row=0, column=3, padx=(0, 9), pady=9, sticky="n")
        self._bind_clickable(card, command)
        card.bind("<FocusIn>", lambda _event: card.configure(highlightbackground=COLORS["primary"], highlightthickness=2))
        card.bind("<FocusOut>", lambda _event: card.configure(highlightbackground=border, highlightthickness=2 if selected else 1))
        return card

    def bullet_list(self, parent, items, style="Panel.TLabel", wraplength=780):
        for item in items:
            ttk.Label(parent, text=f"• {self.clean_text(item)}", style=style, wraplength=wraplength, justify="left").pack(anchor="w", pady=3)

    def label_block(self, parent, title, body, bg_style="Panel.TLabel"):
        ttk.Label(parent, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(parent, text=self.clean_text(body), style=bg_style, wraplength=360, justify="left").pack(anchor="w", pady=(5, 10))

    def image_label(self, parent, key, bg=COLORS["panel"], pady=(0, 0)):
        image = self.images.get(key)
        if image:
            label = tk.Label(parent, image=image, bg=bg, borderwidth=0, highlightthickness=0)
            label.pack(anchor="center", pady=pady)
            return label
        ttk.Label(parent, text=self.tx("시각 자료를 불러오지 못했습니다.", "Visual asset could not be loaded."), style="Muted.TLabel").pack(anchor="w", pady=pady)
        return None

    def scaled_image(self, key, max_width=240, max_height=140):
        path = self.asset_paths.get(key)
        cache_key = (key, int(max_width), int(max_height))
        if cache_key in self.small_images:
            return self.small_images[cache_key]
        if path and os.path.exists(path):
            try:
                image = Image.open(path).convert("RGBA")
                resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
                image.thumbnail((int(max_width), int(max_height)), resample)
                self.small_images[cache_key] = ImageTk.PhotoImage(image)
                return self.small_images[cache_key]
            except Exception:
                pass
        image = self.images.get(key)
        if not image:
            return None
        scale = max(1, int(max(image.width() / max_width, image.height() / max_height) + 0.999))
        self.small_images[cache_key] = image.subsample(scale, scale) if scale > 1 else image
        return self.small_images[cache_key]

    def icon_image(self, key, size=32):
        return self.scaled_image(key, size, size)

    def clean_text(self, text):
        return " ".join(str(text).replace(" -> ", " → ").split())

    def _enable_responsive_wrapping(self):
        """Keep wrapped copy aligned with the width its card receives."""
        self._bind_responsive_inner(self.page.inner)
        self.page.canvas.bind("<Configure>", self._schedule_responsive_wraps, add="+")
        self._schedule_responsive_wraps(update_all=True)

    def _bind_responsive_inner(self, inner):
        inner.bind("<Configure>", self._schedule_responsive_wraps, add="+")

    def _cancel_responsive_wrap_job(self):
        job = getattr(self, "_responsive_wrap_job", None)
        if job is not None:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        self._responsive_wrap_job = None

    def _schedule_responsive_wraps(self, event=None, update_all=False):
        if event is not None and event.widget is self.page.canvas:
            width = int(getattr(event, "width", 0))
            if width == self._responsive_wrap_canvas_width:
                return
            self._responsive_wrap_canvas_width = width
            update_all = True
        elif event is not None and event.widget is self.page.inner:
            width = int(getattr(event, "width", 0))
            if width == self._responsive_wrap_inner_width:
                return
            self._responsive_wrap_inner_width = width
            update_all = True
        if update_all:
            self._responsive_wrap_update_all = True
        if self._responsive_wrap_transaction or self._responsive_wrap_running:
            return
        self._cancel_responsive_wrap_job()
        self._responsive_wrap_job = self.after_idle(self._refresh_responsive_wraps)

    def _refresh_responsive_wraps(self):
        self._responsive_wrap_job = None
        self._stabilize_responsive_wraps(max_passes=6)

    def _stabilize_responsive_wraps(self, max_passes=6):
        """Resolve geometry to a fixed point before the next page is exposed."""
        if self._responsive_wrap_running:
            self._responsive_wrap_update_all = True
            return 0
        self._cancel_responsive_wrap_job()
        self._responsive_wrap_running = True
        seen = set()
        passes = 0
        try:
            for passes in range(1, max_passes + 1):
                self.update_idletasks()
                changed, pending, signature = self._run_responsive_wrap_pass(update_all=True)
                root = getattr(getattr(self, "page", None), "inner", None)
                geometry = (
                    root.winfo_width() if root is not None and root.winfo_exists() else 0,
                    root.winfo_reqheight() if root is not None and root.winfo_exists() else 0,
                )
                state = (geometry, signature)
                if changed == 0 and pending == 0:
                    break
                if state in seen:
                    break
                seen.add(state)
        finally:
            self._responsive_wrap_update_all = False
            self._responsive_wrap_running = False
        return passes

    def _run_responsive_wrap_pass(self, update_all=False):
        root = getattr(getattr(self, "page", None), "inner", None)
        if root is None or not root.winfo_exists():
            return 0, 0, ()
        changes = []
        pending = 0
        signature = []
        stack = [root]
        while stack:
            parent = stack.pop()
            try:
                children = parent.winfo_children()
            except tk.TclError:
                continue
            stack.extend(children)
            for widget in children:
                if not isinstance(widget, (tk.Label, ttk.Label, tk.Button)):
                    continue
                try:
                    base_wrap = int(float(str(widget.cget("wraplength"))))
                except (ValueError, TypeError, tk.TclError):
                    continue
                if base_wrap <= 0 or (getattr(widget, "_responsive_wrap_applied", False) and not update_all):
                    continue
                target = self._responsive_wrap_target(widget)
                if target is None:
                    pending += 1
                    continue
                try:
                    current = int(float(str(widget.cget("wraplength"))))
                except (ValueError, TypeError, tk.TclError):
                    continue
                widget._responsive_wrap_applied = True
                signature.append((str(widget), current, target, widget.winfo_width()))
                if current != target:
                    changes.append((widget, target))
        for widget, target in changes:
            try:
                if widget.winfo_exists():
                    widget.configure(wraplength=target)
            except tk.TclError:
                continue
        return len(changes), pending, tuple(signature)

    def _responsive_wrap_target(self, widget):
        try:
            manager = widget.winfo_manager()
            master = widget.master
            source = widget
            if not isinstance(widget, tk.Button) and manager == "pack":
                side = str(widget.pack_info().get("side", "top"))
                if side in ("top", "bottom"):
                    source = master
            elif not isinstance(widget, tk.Button) and manager == "grid":
                sticky = str(widget.grid_info().get("sticky", ""))
                if not ("e" in sticky and "w" in sticky):
                    managed = [child for child in master.winfo_children() if child.winfo_manager()]
                    source = master if len(managed) == 1 else widget
        except tk.TclError:
            return None

        try:
            if not widget.winfo_exists() or not source.winfo_exists() or source.winfo_width() <= 40:
                return None
            try:
                padx = widget.winfo_pixels(str(widget.cget("padx")))
            except (ValueError, TypeError, tk.TclError):
                padx = 0
            if source is widget:
                inset = max(6, padx * 2 + 6)
                available = source.winfo_width() - inset
            else:
                left = max(widget.winfo_x(), 0)
                right = max(left, 12)
                available = source.winfo_width() - left - right - (padx * 2)
            return max(120, int(available))
        except (ValueError, TypeError, tk.TclError):
            return None

    def _apply_responsive_wrap(self, widget):
        """Compatibility helper for targeted runtime layout checks."""
        target = self._responsive_wrap_target(widget)
        if target is None:
            return None
        try:
            current = int(float(str(widget.cget("wraplength"))))
            if current != target:
                widget.configure(wraplength=target)
            widget._responsive_wrap_applied = True
            return current != target
        except (ValueError, TypeError, tk.TclError):
            return None

    def compact_text(self, text, limit=135):
        text = self.clean_text(text)
        if len(text) <= limit:
            return text
        cut = text[: limit - 1].rstrip()
        for marker in [". ", "? ", "! ", "다. ", "요. "]:
            idx = cut.rfind(marker)
            if idx >= 42:
                return cut[: idx + len(marker)].rstrip()
        return cut.rstrip(" ,./·-") + "..."

    def zone_photo_key(self, zone):
        if "Medication" in zone:
            return "photo_med_room"
        if "Patient" in zone:
            return "photo_patient_room"
        if "Utility" in zone or "Isolation" in zone:
            return "photo_utility_isolation"
        if "Handoff" in zone:
            return "photo_handoff_zone"
        if "Supply" in zone:
            return "photo_supply_room"
        return "photo_nurse_station"

    def scene_photo_key(self, scene):
        if scene == "medroom":
            return "photo_med_room"
        if scene in ("assignment", "escalation", "discharge"):
            return "photo_patient_room"
        if scene in ("privacy", "readiness", "orientation"):
            return "photo_nurse_station"
        return "ward_collage"

    def photo_tile(self, parent, image_key, title=None, body=None, bg=None, max_width=260, max_height=170):
        bg = bg or COLORS["panel"]
        tile = tk.Frame(parent, bg=bg, highlightthickness=1, highlightbackground=COLORS["card_border"], padx=10, pady=10)
        image = self.scaled_image(image_key, max_width, max_height)
        if image:
            tk.Label(tile, image=image, bg=bg, borderwidth=0, highlightthickness=0).pack(anchor="center", pady=(0, 8))
        if title:
            tk.Label(tile, text=title, bg=bg, fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w")
        if body:
            tk.Label(tile, text=self.clean_text(body), bg=bg, fg=COLORS["muted"], font=FONT_SMALL, wraplength=max_width - 20, justify="left").pack(anchor="w", pady=(3, 0))
        return tile

    def variation_note(self):
        return self.tx(
            "참고: 이 앱은 일반적인 교육용 시뮬레이션입니다. 실제 절차는 주(State), facility policy, EHR/ADC, unit protocol에 따라 달라질 수 있습니다.",
            "Note: This is a general educational simulation. Actual workflow may vary by state, facility policy, EHR/ADC, and unit protocol.",
        )

    def compact_variation_note(self):
        return self.tx(
            "시설별 policy와 state scope를 항상 확인하세요.",
            "Always confirm facility policy and state scope.",
        )

    def with_variation_note(self, feedback):
        return f"{self.clean_text(feedback)}  {self.variation_note()}"

    def open_feedback_form(self):
        webbrowser.open(FEEDBACK_FORM_URL)

    def zone_icon_key(self, zone):
        if "Medication" in zone:
            return "icon_med"
        if "Patient" in zone:
            return "icon_bed"
        if "Supply" in zone or "Utility" in zone or "Isolation" in zone:
            return "icon_supply"
        if "Handoff" in zone:
            return "icon_handoff"
        if "Nurse" in zone:
            return "icon_nurse"
        return "icon_safety"

    def cue_icon_key(self, title):
        lower = title.lower()
        if any(word in lower for word in ["mar", "adc", "waste", "med", "약", "insulin"]):
            return "icon_med"
        if any(word in lower for word in ["patient", "room", "414", "418", "bed", "환자"]):
            return "icon_bed"
        if any(word in lower for word in ["phone", "handoff", "sbar", "team", "call", "provider", "전화"]):
            return "icon_handoff"
        if any(word in lower for word in ["ppe", "supply", "pharmacy", "ride", "discharge"]):
            return "icon_supply"
        return "icon_safety"

    def first_week_effect_for_choice(self, choice):
        if not choice:
            return {}
        return {key: int(choice.get("effect", {}).get(key, 0) * 4) for key in FIRST_WEEK_BASE_SCORES}

    def first_week_effect_summary(self, choice=None):
        choice = choice or self.first_week_answers.get(self.first_week_day)
        effect = self.first_week_effect_for_choice(choice)
        if not effect:
            return self.tx("선택 후 지표 변화가 표시됩니다.", "Competency changes appear after you choose.")
        parts = []
        for key, label in FIRST_WEEK_SCORE_LABELS.items():
            delta = effect.get(key, 0)
            if delta:
                parts.append(f"{label} {delta:+d}")
        return " · ".join(parts) if parts else self.tx("지표 변화 없음", "No metric change")

    def first_week_ordered_choices(self, day_index, choices):
        if day_index not in self.first_week_choice_orders:
            order = list(range(len(choices)))
            random.shuffle(order)
            self.first_week_choice_orders[day_index] = order
        return [choices[index] for index in self.first_week_choice_orders[day_index] if index < len(choices)]

    def first_week_choice_feedback(self, choice):
        outcome = self.tx("안전 흐름에 가까운 선택입니다.", "This choice is close to the safe workflow.") if choice["best"] else self.tx("리스크가 있는 선택입니다.", "This choice has a risk to review.")
        return "\n".join(
            [
                outcome,
                self.tx("지표 변화: ", "Metric impact: ") + self.first_week_effect_summary(choice),
                self.tx("판단 근거: ", "Rationale: ") + self.clean_text(choice["feedback"]),
                self.variation_note(),
            ]
        )

    def _render_safety_notice(self, parent, compact=False):
        items = [
            (
                self.tx("비공식 교육용", "Unofficial Education"),
                self.tx("NCLEX/NCSBN/병원 공식 프로그램이 아닙니다.", "Not an official NCLEX, NCSBN, or hospital program."),
                COLORS["accent"],
            ),
            (
                self.tx("환자정보 입력 금지", "No Real PHI"),
                self.tx("이름, MRN, 생년월일, 병원명, 사진을 넣지 마세요.", "Do not enter names, MRNs, DOBs, facility names, or photos."),
                COLORS["accent_dark"],
            ),
            (
                self.tx("시설별 차이", "Facility Variation"),
                self.tx("State, facility, EHR, unit policy를 확인해야 합니다.", "Check state, facility, EHR, and unit policies."),
                COLORS["success"],
            ),
        ]

        if compact:
            section = tk.Frame(parent, bg=COLORS["bg"])
            section.pack(fill="x", padx=30, pady=(12, 18))
            canvas = tk.Canvas(section, height=118, bg=COLORS["bg"], highlightthickness=0)
            canvas.pack(fill="x")

            def draw(_event=None):
                width = max(canvas.winfo_width(), 620)
                canvas.delete("all")
                self.rounded_rect(canvas, 3, 3, width - 5, 112, 22, fill=COLORS["panel"], outline=COLORS["card_border"])
                canvas.create_text(24, 22, text=self.tx("TRUST & SAFETY", "TRUST & SAFETY"), fill=COLORS["accent"], font=FONT_CHIP, anchor="w")
                segment_w = (width - 48) / 3
                for col, (title, body, color) in enumerate(items):
                    x = 24 + col * segment_w
                    canvas.create_oval(x, 45, x + 10, 55, fill=color, outline=color)
                    canvas.create_text(x + 20, 42, text=title, fill=COLORS["ink"], font=FONT_SMALL_BOLD, anchor="nw", width=segment_w - 28)
                    canvas.create_text(x + 20, 65, text=self.clean_text(body), fill=COLORS["muted"], font=FONT_CHIP, anchor="nw", width=segment_w - 30)

            canvas.bind("<Configure>", draw)
            draw()
            return

        notice = tk.Frame(parent, bg=COLORS["panel"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=10, pady=10)
        notice.pack(fill="x", padx=0, pady=(6, 12))
        for col, (title, body, color) in enumerate(items):
            notice.columnconfigure(col, weight=1)
            card = tk.Frame(notice, bg=COLORS["panel"], padx=14, pady=11, highlightthickness=1, highlightbackground=COLORS["card_border"])
            card.grid(row=0, column=col, sticky="nsew", padx=4, pady=4)
            tk.Label(card, text=title, bg=COLORS["panel"], fg=color, font=FONT_SMALL_BOLD).pack(anchor="w")
            tk.Label(card, text=self.clean_text(body), bg=COLORS["panel"], fg=COLORS["muted"], font=FONT_SMALL, wraplength=220, justify="left").pack(anchor="w", pady=(2, 0))

    def _cue_card(self, parent, title, body, color, icon_key=None, icon_size=32, wraplength=300):
        card = tk.Frame(parent, bg=color, highlightthickness=1, highlightbackground=COLORS["card_border"], padx=10, pady=7)
        icon = self.icon_image(icon_key, icon_size) if icon_key else None
        if icon:
            tk.Label(card, image=icon, bg=color).pack(side="left", padx=(0, 8), anchor="n")
            text_frame = tk.Frame(card, bg=color)
            text_frame.pack(side="left", fill="both", expand=True)
        else:
            text_frame = card
        tk.Label(text_frame, text=title, bg=color, fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w")
        tk.Label(text_frame, text=self.clean_text(body), bg=color, fg=COLORS["ink"], font=FONT_SMALL, wraplength=wraplength, justify="left").pack(anchor="w", pady=(2, 0))
        return card

    def risk_lens(self, text):
        lower = text.lower()
        if any(word in lower for word in ["privacy", "hipaa", "family", "caller", "전화", "가족"]):
            return self.tx("Privacy / authorization", "Privacy / authorization")
        if any(word in lower for word in ["med", "약", "mar", "adc", "opioid", "insulin", "antibiotic"]):
            return self.tx("Medication safety", "Medication safety")
        if any(word in lower for word in ["oxygen", "chest", "호흡", "숨", "o2", "rr"]):
            return self.tx("Respiratory escalation", "Respiratory escalation")
        if any(word in lower for word in ["fall", "낙상", "bathroom"]):
            return self.tx("Fall / safety event", "Fall / safety event")
        if any(word in lower for word in ["discharge", "퇴원", "ride"]):
            return self.tx("Transition of care", "Transition of care")
        return self.tx("Clinical judgment", "Clinical judgment")

    def _render_first7(self):
        self.page_title(
            self.tx("미국 병동 첫 7일 시뮬레이션", "First 7 Days on a U.S. Ward"),
            self.tx(
                "NCLEX 이후 미국 이민과 취업을 준비하는 한국 RN이 첫 주에 겪을 장면을 따라갑니다.",
                "Follow the first-week scenes a Korean RN may face after NCLEX while preparing to work in the U.S.",
            ),
        )

        day_nav = self.panel(padding=12)
        day_nav_header = tk.Frame(day_nav, bg=COLORS["panel"])
        day_nav_header.pack(fill="x", pady=(0, 8))
        ttk.Label(day_nav_header, text=self.tx("첫 주 진행", "First-week progress"), style="CardTitle.TLabel").pack(side="left")
        ttk.Button(day_nav_header, text=self.tx("새로운 랜덤 첫 주", "New random week"), command=self.reset_first_week).pack(side="right")
        day_grid = tk.Frame(day_nav, bg=COLORS["panel"])
        day_grid.pack(fill="x")
        for index, day in enumerate(FIRST_WEEK_DAYS):
            day_grid.columnconfigure(index, weight=1, uniform="week_days")
            style = "Primary.TButton" if index == self.first_week_day else "TButton"
            done_mark = "✓ " if index in self.first_week_answers else ""
            day_label = f"{done_mark}{day['day']}일" if not self.is_english() else f"{done_mark}Day {day['day']}"
            ttk.Button(day_grid, text=day_label, style=style, command=lambda i=index: self.set_first_week_day(i)).grid(row=0, column=index, sticky="ew", padx=(0, 5) if index < 6 else 0)

        top = ttk.Frame(self.page.inner, style="Page.TFrame")
        top.pack(fill="x", padx=26, pady=8)
        top.columnconfigure(0, weight=1, uniform="first_week_columns")
        top.columnconfigure(1, weight=1, uniform="first_week_columns")

        scene_outer, scene_panel = self._card_shell(top, padding=0)
        scene_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.first_week_canvas = tk.Canvas(scene_panel, height=410, bg=COLORS["panel"], highlightthickness=0)
        self.first_week_canvas.pack(fill="x")
        self._draw_first_week_scene(self.first_week_canvas, 760)
        self.first_week_canvas.bind("<Configure>", lambda event: self._draw_first_week_scene(event.widget, event.width))

        day = FIRST_WEEK_DAYS[self.first_week_day]
        selected = self.first_week_answers.get(self.first_week_day)
        decision_area = tk.Frame(
            scene_panel,
            bg=COLORS["panel_alt"],
            padx=16,
            pady=12,
            highlightthickness=1,
            highlightbackground=COLORS["card_border"],
        )
        decision_area.pack(fill="x")
        tk.Label(decision_area, text=f"{day['time']}  {day['title']}", bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_CARD_TITLE, wraplength=340, justify="left").pack(anchor="w")
        scene_context = tk.Frame(decision_area, bg=COLORS["panel_alt"])
        scene_context.pack(fill="x", pady=(8, 10))
        scene_context.columnconfigure(0, weight=1)
        scene_photo = self.scaled_image(self.scene_photo_key(day["scene"]), 220, 155)
        if scene_photo:
            tk.Label(scene_context, image=scene_photo, bg=COLORS["panel_alt"], highlightthickness=1, highlightbackground=COLORS["card_border"]).grid(row=0, column=0, sticky="w", pady=(0, 10))
        scene_text = tk.Frame(scene_context, bg=COLORS["panel_alt"])
        scene_text.grid(row=1, column=0, sticky="new")
        tk.Label(scene_text, text=self.tx("오늘 보는 장면", "Scene You Are Seeing"), bg=COLORS["panel_alt"], fg=COLORS["primary"], font=FONT_SMALL_BOLD).pack(anchor="w")
        tk.Label(scene_text, text=self.clean_text(day["setting"]), bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_NORMAL, wraplength=340, justify="left").pack(anchor="w", pady=(4, 6))
        tk.Label(scene_text, text=self.tx("사진 속 공간 단서와 아래 선택지를 함께 보고, 실제 RN의 다음 행동을 선택합니다.", "Use the photo cues and choices together, then choose the RN's next action."), bg=COLORS["panel_alt"], fg=COLORS["muted"], font=FONT_SMALL, wraplength=340, justify="left").pack(anchor="w")
        tk.Label(
            scene_text,
            text=self.tx("보고 판단할 그림 단서", "Visual Cues to Use"),
            bg=COLORS["panel_alt"],
            fg=COLORS["ink"],
            font=FONT_SMALL_BOLD,
        ).pack(anchor="w", pady=(12, 5))
        cue_grid = tk.Frame(scene_text, bg=COLORS["panel_alt"])
        cue_grid.pack(fill="x")
        cue_colors = [COLORS["panel"], COLORS["panel"], COLORS["panel"], COLORS["panel"]]
        for cue_index, (cue_title, cue_body) in enumerate(day["cues"][:4]):
            cue_row, cue_col = divmod(cue_index, 2)
            cue_grid.columnconfigure(cue_col, weight=1, uniform="scene_cues")
            color = cue_colors[cue_index % len(cue_colors)]
            card = tk.Frame(cue_grid, bg=color, highlightthickness=1, highlightbackground=COLORS["card_border"], padx=8, pady=6)
            card.grid(row=cue_row, column=cue_col, sticky="nsew", padx=(0, 5) if cue_col == 0 else 0, pady=(0, 5) if cue_row == 0 else 0)
            icon = self.icon_image(self.cue_icon_key(cue_title), 18)
            cue_header = tk.Frame(card, bg=color)
            cue_header.pack(fill="x")
            if icon:
                tk.Label(cue_header, image=icon, bg=color).pack(side="left", padx=(0, 5))
            tk.Label(cue_header, text=cue_title, bg=color, fg=COLORS["ink"], font=FONT_CHIP).pack(side="left", anchor="w")
            tk.Label(card, text=self.clean_text(cue_body), bg=color, fg=COLORS["muted"], font=FONT_CHIP, wraplength=120, justify="left").pack(anchor="w", pady=(3, 0))
        tk.Label(
            decision_area,
            text=self.clean_text(day["assignment"]),
            bg=COLORS["soft_blue"],
            fg=COLORS["ink"],
            font=FONT_BOLD,
            anchor="w",
            justify="left",
            wraplength=340,
            padx=12,
            pady=7,
        ).pack(fill="x", pady=(0, 7))
        risk_box = tk.Frame(decision_area, bg=COLORS["soft_orange"], padx=12, pady=8)
        risk_box.pack(fill="x", pady=(0, 12))
        tk.Label(
            risk_box,
            text=self.tx("주의 포인트", "Risk Cue"),
            bg=COLORS["soft_orange"],
            fg=COLORS["ink"],
            font=FONT_SMALL_BOLD,
        ).pack(anchor="w")
        tk.Label(
            risk_box,
            text=self.clean_text(day["risk"]),
            bg=COLORS["soft_orange"],
            fg=COLORS["ink"],
            font=FONT_SMALL,
            anchor="w",
            justify="left",
            wraplength=340,
        ).pack(anchor="w", pady=(2, 0))
        tk.Label(
            decision_area,
            text=self.compact_variation_note(),
            bg=COLORS["soft_gray"],
            fg=COLORS["ink"],
            font=FONT_CHIP,
            anchor="w",
            padx=10,
            pady=5,
        ).pack(fill="x", pady=(0, 10))

        tk.Label(
            decision_area,
            text=self.tx("오른쪽 선택 패널에서 실제 RN의 다음 행동을 고르세요.", "Choose the RN's next action in the right decision panel."),
            bg=COLORS["panel_alt"],
            fg=COLORS["primary"],
            font=FONT_SMALL_BOLD,
            wraplength=340,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        right_stack = ttk.Frame(top, style="Page.TFrame")
        right_stack.grid(row=0, column=1, sticky="new", padx=(8, 0))

        choice_outer, choice_panel = self._card_shell(right_stack, padding=16)
        choice_outer.pack(fill="x")
        ttk.Label(choice_panel, text=self.tx("선택 패널", "Decision Panel"), style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(
            choice_panel,
            text=self.tx("좌측 사진과 cue card를 보고 하나를 선택합니다.", "Use the photo and cue cards on the left, then choose one action."),
            style="Muted.TLabel",
            wraplength=260,
            justify="left",
        ).pack(anchor="w", pady=(3, 10))
        for visible_index, choice_data in enumerate(self.first_week_ordered_choices(self.first_week_day, day["choices"]), start=1):
            is_selected = selected is choice_data
            self.selectable_choice_card(
                choice_panel,
                visible_index,
                choice_data["text"],
                command=lambda selected_choice=choice_data: self.answer_first_week(selected_choice),
                selected=is_selected,
                is_best=choice_data["best"],
                wraplength=220,
            ).pack(fill="x", pady=3)

        feedback_area = tk.Frame(choice_panel, bg=COLORS["panel"], padx=12, pady=10, highlightthickness=1, highlightbackground=COLORS["card_border"])
        feedback_area.pack(fill="x", pady=(10, 0))
        tk.Label(feedback_area, textvariable=self.first_week_feedback, bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=260, justify="left").pack(anchor="w")
        if selected:
            tk.Label(feedback_area, text=self.tx("디브리핑", "Debrief"), bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w", pady=(10, 3))
            tk.Label(feedback_area, text=self.clean_text(day["debrief"]), bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=320, justify="left").pack(anchor="w")
            btns = ttk.Frame(feedback_area, style="Panel.TFrame")
            btns.pack(fill="x", pady=(10, 0))
            if self.first_week_day < len(FIRST_WEEK_DAYS) - 1:
                ttk.Button(btns, text=self.tx("다음 날로", "Next Day"), style="Primary.TButton", command=lambda: self.set_first_week_day(self.first_week_day + 1)).pack(fill="x", pady=(0, 6))
            ttk.Button(btns, text=self.tx("병동 투어로 연결", "Go to Ward Tour"), command=lambda: self.show_page("tour")).pack(fill="x", pady=(0, 6))
            ttk.Button(btns, text=self.tx("환자 케이스 연습", "Practice Patient Cases"), command=lambda: self.show_page("scenarios")).pack(fill="x")

        score_outer, score_panel = self._card_shell(right_stack, padding=18)
        score_outer.pack(fill="x", pady=(12, 0))
        self._render_first_week_score_panel(score_panel)

        refs = self.panel(padding=18)
        ttk.Label(refs, text=self.tx("필요할 때 확인하는 핵심 메모", "Quick reference when needed"), style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        grid = tk.Frame(refs, bg=COLORS["panel"])
        grid.pack(fill="x")
        for index, (title, body) in enumerate(FIRST_WEEK_REFERENCE_CARDS[:3]):
            row, col = 0, index
            card = tk.Frame(grid, bg=COLORS["panel_alt"], highlightthickness=2, highlightbackground=COLORS["card_border"])
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            grid.columnconfigure(col, weight=1)
            tk.Label(card, text=title, bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w", padx=12, pady=(10, 2))
            tk.Label(card, text=self.clean_text(body), bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=225, justify="left", anchor="w").pack(anchor="w", padx=12, pady=(0, 10))

    def _draw_first_week_scene(self, canvas, width):
        canvas.delete("all")
        width = max(int(width), 420)
        day = FIRST_WEEK_DAYS[self.first_week_day]
        scene = day["scene"]

        scene_h = 410
        canvas.create_rectangle(0, 0, width, scene_h, fill=COLORS["panel"], outline="")
        canvas.create_rectangle(0, 0, width, 80, fill=COLORS["primary"], outline="")
        canvas.create_text(28, 22, text=f"DAY {day['day']}", fill="#ffffff", font=FONT_SECTION, anchor="w")
        canvas.create_text(width - 28, 22, text=day["time"], fill="#ffffff", font=FONT_SMALL_BOLD, anchor="e")
        canvas.create_text(28, 42, text=day["title"], fill="#D8F2EE", font=FONT_SMALL_BOLD, anchor="nw", width=width - 56)

        # Cue cards stay in a separate rail so movement lines never cut through them.
        cue_count = min(4, len(day["cues"]))
        cue_margin = 36
        cue_gap = 10
        cue_y = 92
        cue_h = 44
        cue_w = (width - cue_margin * 2 - cue_gap * (cue_count - 1)) / max(cue_count, 1)
        for index, (title, body) in enumerate(day["cues"][:cue_count]):
            cue_x = cue_margin + index * (cue_w + cue_gap)
            canvas.create_rectangle(cue_x, cue_y, cue_x + cue_w, cue_y + cue_h, fill=COLORS["panel_alt"], outline=COLORS["card_border"], width=1)
            canvas.create_text((cue_x + cue_x + cue_w) / 2, cue_y + cue_h / 2, text=title, fill=COLORS["ink"], font=FONT_SMALL_BOLD, width=cue_w - 16)

        floor_left = 28
        floor_right = width - 28
        floor_top = 152
        floor_bottom = 362
        hall_top = 176
        hall_bottom = 224
        hall_mid = (hall_top + hall_bottom) / 2
        room_top = 262
        room_bottom = 342
        room_mid = (room_top + room_bottom) / 2

        canvas.create_rectangle(floor_left, floor_top, floor_right, floor_bottom, fill=COLORS["panel_alt"], outline=COLORS["line"], width=2)
        canvas.create_rectangle(52, hall_top, width - 52, hall_bottom, fill=COLORS["line"], outline="")
        canvas.create_text(width / 2, hall_top - 12, text="4 WEST MAIN HALLWAY", fill=COLORS["muted"], font=FONT_SMALL_BOLD)

        room_left = 54
        room_right = width - 54
        room_gap = 16
        available = room_right - room_left - room_gap * 3
        station_w = max(138, available * 0.24)
        med_w = max(124, available * 0.20)
        patient_w = max(138, available * 0.23)
        handoff_w = available - station_w - med_w - patient_w
        if handoff_w < 150:
            even_w = available / 4
            station_w = med_w = patient_w = handoff_w = even_w

        x = room_left
        station_box = (x, room_top, x + station_w, room_bottom)
        x = station_box[2] + room_gap
        med_box = (x, room_top, x + med_w, room_bottom)
        x = med_box[2] + room_gap
        patient_box = (x, room_top, x + patient_w, room_bottom)
        x = patient_box[2] + room_gap
        handoff_box = (x, room_top, room_right, room_bottom)

        room_specs = [
            ("station", "Nurse Station", *station_box, COLORS["soft_blue"]),
            ("med", "Med Room", *med_box, COLORS["soft_orange"]),
            ("patient", "Patient 414", *patient_box, COLORS["soft_green"]),
            ("handoff", "Handoff", *handoff_box, COLORS["soft_lavender"]),
        ]
        if scene in ("privacy", "discharge", "readiness"):
            key, _label, x1, y1, x2, y2, _fill = room_specs[3]
            room_specs[3] = (key, "Team Desk", x1, y1, x2, y2, COLORS["soft_gold"])
        if scene in ("orientation",):
            key, _label, x1, y1, x2, y2, _fill = room_specs[1]
            room_specs[1] = (key, "Badge / HR", x1, y1, x2, y2, COLORS["soft_gold"])
        if scene in ("escalation",):
            key, _label, x1, y1, x2, y2, _fill = room_specs[2]
            room_specs[2] = (key, "CHF 414", x1, y1, x2, y2, COLORS["soft_orange"])

        room_centers = {key: ((x1 + x2) / 2, room_mid) for key, _label, x1, y1, x2, y2, _fill in room_specs}
        hall_points = {key: (center[0], hall_mid) for key, center in room_centers.items()}
        route_keys = {
            "orientation": ["entry", "med"],
            "medroom": ["station", "med"],
            "assignment": ["med", "patient", "station"],
            "privacy": ["station", "handoff", "patient"],
            "escalation": ["patient", "station", "handoff"],
            "discharge": ["patient", "handoff", "med"],
            "readiness": ["station", "handoff"],
        }.get(scene, ["station", "patient"])
        route_points = []
        for key in route_keys:
            if key == "entry":
                route_points.append((room_left + 18, hall_mid))
            else:
                route_points.append(hall_points[key])
        destination_key = next((key for key in reversed(route_keys) if key != "entry"), "patient")
        route_points.append(room_centers[destination_key])
        for a, b in zip(route_points, route_points[1:]):
            canvas.create_line(*a, *b, fill=COLORS["primary"], width=5)

        for _key, label, x1, y1, x2, y2, fill in room_specs:
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=COLORS["card_border"], width=1)
            node_font = FONT_SMALL_BOLD if width >= 620 else FONT_CHIP
            canvas.create_text((x1 + x2) / 2, y1 + (30 if width >= 620 else 40), text=label, fill=COLORS["ink"], font=node_font, width=max(42, x2 - x1 - 8))
            if width >= 620:
                canvas.create_text((x1 + x2) / 2, y1 + 56, text=self.tx("관찰 · 판단", "observe · decide"), fill=COLORS["muted"], font=FONT_CHIP)

        x, _y = room_centers[destination_key]
        rn_y = hall_mid - 2
        canvas.create_oval(x - 14, rn_y - 14, x + 14, rn_y + 14, fill=COLORS["accent"], outline="#ffffff", width=4)
        canvas.create_text(x, rn_y, text="RN", fill="#ffffff", font=FONT_CHIP)

        canvas.create_rectangle(28, 366, width - 28, 406, fill=COLORS["panel_alt"], outline="")
        canvas.create_text(
            40,
            373,
            text=self.tx(
                "동선을 확인한 뒤 아래 선택 패널에서 다음 행동을 고르세요.",
                "Review the route, then choose the next action below.",
            ),
            fill=COLORS["muted"],
            font=FONT_CHIP,
            anchor="nw",
            width=width - 80,
        )

    def _render_first_week_score_panel(self, parent):
        ttk.Label(parent, text="Readiness Meter", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(
            parent,
            text=self.tx(
                "선택 후 어떤 역량이 흔들리는지만 빠르게 확인합니다.",
                "After choosing, quickly check which competency moved.",
            ),
            style="Muted.TLabel",
            wraplength=300,
            justify="left",
        ).pack(anchor="w", pady=(2, 12))
        current_effect = self.first_week_effect_for_choice(self.first_week_answers.get(self.first_week_day))
        for key, label in FIRST_WEEK_SCORE_LABELS.items():
            value = max(0, min(100, self.first_week_scores.get(key, FIRST_WEEK_BASE_SCORES[key])))
            base = FIRST_WEEK_BASE_SCORES[key]
            delta = value - base
            if value >= 82:
                status = self.tx("강점", "strength")
                chip_color = COLORS["soft_green"]
            elif value >= 70:
                status = self.tx("성장 중", "developing")
                chip_color = COLORS["soft_gold"]
            else:
                status = self.tx("보강", "needs practice")
                chip_color = COLORS["soft_orange"]
            row = tk.Frame(parent, bg=COLORS["panel"])
            row.pack(fill="x", pady=(0, 10))
            top = tk.Frame(row, bg=COLORS["panel"])
            top.pack(fill="x")
            tk.Label(top, text=label, bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(side="left")
            tk.Label(top, text=status, bg=chip_color, fg=COLORS["ink"], font=FONT_CHIP, padx=7, pady=2).pack(side="right")
            bar = self.modern_progress(row, value, maximum=100, height=12, fill=COLORS["primary"], bg=COLORS["panel"])
            bar.pack(fill="x", pady=(5, 1))
            delta_text = f"{delta:+d}" if delta else "0"
            ttk.Label(row, text=self.tx(f"{value}/100  baseline {base}, 변화 {delta_text}", f"{value}/100  baseline {base}, change {delta_text}"), style="Muted.TLabel").pack(anchor="w")
            decision_delta = current_effect.get(key, 0)
            if decision_delta:
                tk.Label(
                    row,
                    text=self.tx(f"이번 선택 영향 {decision_delta:+d}", f"This choice {decision_delta:+d}"),
                    bg=COLORS["soft_cyan"] if decision_delta > 0 else COLORS["soft_orange"],
                    fg=COLORS["ink"],
                    font=FONT_CHIP,
                    padx=8,
                    pady=2,
                ).pack(anchor="w", pady=(4, 0))

        completed = len(self.first_week_answers)
        complete_text = self.tx(f"완료한 장면: {completed}/{len(FIRST_WEEK_DAYS)}", f"Completed scenes: {completed}/{len(FIRST_WEEK_DAYS)}")
        ttk.Label(parent, text=complete_text, style="CardTitle.TLabel").pack(anchor="w", pady=(8, 6))
        current = FIRST_WEEK_DAYS[self.first_week_day]
        ttk.Label(parent, text=self.clean_text(current["bridge"]), style="Panel.TLabel", wraplength=320, justify="left").pack(anchor="w")
        hint = self.tx(
            "선택 후 어떤 역량이 흔들리는지 확인하세요.",
            "After each choice, review which competency moved.",
        )
        tk.Label(parent, text=hint, bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=300, justify="left", padx=10, pady=8).pack(fill="x", pady=(12, 0))

    def set_first_week_day(self, index):
        self.first_week_day = max(0, min(index, len(FIRST_WEEK_DAYS) - 1))
        day = FIRST_WEEK_DAYS[self.first_week_day]
        selected = self.first_week_answers.get(self.first_week_day)
        if selected:
            self.last_first_week_effect = self.first_week_effect_for_choice(selected)
            self.last_first_week_choice_best = selected["best"]
            self.first_week_feedback.set(self.tx("이미 선택한 장면입니다. 다른 선택을 누르면 결과가 갱신됩니다.", "This scene already has a choice. Pick another option to update the result."))
        else:
            self.first_week_feedback.set(self.tx(f"{day['day']}일차 장면입니다. 단서를 보고 행동을 선택하세요.", f"Day {day['day']} scene. Read the cues and choose your action."))
        self.show_page("first7")

    def answer_first_week(self, choice):
        self.first_week_answers[self.first_week_day] = choice
        self.last_first_week_effect = self.first_week_effect_for_choice(choice)
        self.last_first_week_choice_best = choice["best"]
        self._recalculate_first_week_scores()
        self.first_week_feedback.set(self.first_week_choice_feedback(choice))
        self.show_page("first7")

    def _recalculate_first_week_scores(self):
        scores = dict(FIRST_WEEK_BASE_SCORES)
        for choice in self.first_week_answers.values():
            for key, value in choice["effect"].items():
                scores[key] = scores.get(key, 0) + value * 4
        self.first_week_scores = {key: max(0, min(100, value)) for key, value in scores.items()}

    def reset_first_week(self):
        global FIRST_WEEK_DAYS
        FIRST_WEEK_DAYS = select_first_week_days(FIRST_WEEK_DAY_POOLS)
        self.first_week_day = 0
        self.first_week_answers = {}
        self.first_week_choice_orders = {}
        self.last_first_week_effect = {}
        self.last_first_week_choice_best = None
        self.first_week_scores = dict(FIRST_WEEK_BASE_SCORES)
        self.first_week_feedback.set(self.tx("랜덤 첫 주 장면을 새로 뽑았습니다. 첫날부터 다시 시작합니다.", "A new randomized first-week set has been drawn. Restarting from Day 1."))
        self.show_page("first7")

    def _render_dashboard(self):
        hero = self.panel(padding=0)
        hero_canvas = tk.Canvas(hero, height=182, bg=COLORS["panel"], highlightthickness=0)
        hero_canvas.pack(fill="x")
        self._draw_dashboard_canvas(hero_canvas, 820)
        hero_canvas.bind("<Configure>", lambda event: self._draw_dashboard_canvas(event.widget, event.width))

        module_header = tk.Frame(self.page.inner, bg=COLORS["bg"])
        module_header.pack(fill="x", padx=24, pady=(8, 2))
        tk.Label(
            module_header,
            text=self.tx("PRACTICE MODES", "PRACTICE MODES"),
            bg=COLORS["bg"],
            fg=COLORS["primary"],
            font=FONT_CHIP,
        ).pack(anchor="w")
        tk.Label(
            module_header,
            text=self.tx("필요한 장면으로 바로 들어가기", "Jump into the training mode you need"),
            bg=COLORS["bg"],
            fg=COLORS["ink"],
            font=FONT_SECTION,
        ).pack(anchor="w", pady=(3, 0))

        dashboard_grid = ttk.Frame(self.page.inner, style="Page.TFrame")
        dashboard_grid.pack(fill="x", padx=24, pady=(6, 6))
        mode_cards = [
            (self.tx("첫 7일", "First 7 Days"), self.tx("사진 단서 → 선택 → 디브리핑", "Photo cue → choice → debrief"), self.tx("추천", "RECOMMENDED"), COLORS["primary"], "first7", "icon_nurse"),
            (self.tx("병동 투어", "Ward Tour"), self.tx("구역을 이동하며 RN 동선 익히기", "Move through unit zones"), self.tx("공간", "SPACES"), COLORS["success"], "tour", "icon_supply"),
            (self.tx("스테이션 실습", "Station Practice"), self.tx("오늘 문항만 짧게 풀기", "Short daily decision set"), self.tx("10분", "10 MIN"), COLORS["primary"], "quests", "icon_safety"),
            (self.tx("환자 케이스", "Patient Cases"), self.tx("상태 변화에서 다음 행동 선택", "Choose next action from patient cues"), self.tx("판단", "DECIDE"), COLORS["success"], "scenarios", "icon_bed"),
            (self.tx("영어 연습", "English Practice"), self.tx("일상 + 병동 표현 10분 루틴", "10-minute daily + clinical language"), self.tx("말하기", "SPEAK"), COLORS["primary"], "english", "icon_handoff"),
            (self.tx("SBAR", "SBAR"), self.tx("provider call 문장으로 정리", "Structure provider calls"), self.tx("보고", "REPORT"), COLORS["accent"], "sbar", "icon_handoff"),
        ]
        for col in range(2):
            dashboard_grid.columnconfigure(col, weight=1, uniform="dashboard")
        for index, (title, desc, tag, color, key, image_key) in enumerate(mode_cards):
            row, col = divmod(index, 2)
            card = self.feature_card(
                dashboard_grid,
                title,
                desc,
                tag,
                color,
                lambda page=key: self.show_page(page),
                image_key=image_key,
            )
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=4)

        self._render_today_session()
        self._render_safety_notice(self.page.inner, compact=True)

    def _render_today_session(self):
        panel = self.panel(padding=14)
        top = tk.Frame(panel, bg=COLORS["panel"])
        top.pack(fill="x")
        top.columnconfigure(0, weight=1)
        left = tk.Frame(top, bg=COLORS["panel"])
        left.grid(row=0, column=0, sticky="nsew")
        right = tk.Frame(top, bg=COLORS["panel"])
        right.grid(row=0, column=1, sticky="ne", padx=(18, 0))
        tk.Label(
            left,
            text=self.tx("오늘의 10분 리허설", "Today's 10-minute rehearsal"),
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            font=FONT_CARD_TITLE,
        ).pack(anchor="w")
        today = FIRST_WEEK_DAYS[self.first_week_day]
        tk.Label(
            left,
            text=self.tx(
                f"Day {today['day']} · {today['time']} · {today['title']}",
                f"Day {today['day']} · {today['time']} · {today['title']}",
            ),
            bg=COLORS["panel"],
            fg=COLORS["primary"],
            font=FONT_SMALL_BOLD,
            wraplength=560,
            justify="left",
        ).pack(anchor="w", pady=(5, 2))
        tk.Label(
            left,
            text=self.clean_text(today["setting"]),
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=FONT_SMALL,
            wraplength=560,
            justify="left",
        ).pack(anchor="w")
        tk.Label(
            left,
            text=self.tx("01 관찰   →   02 판단   →   03 디브리핑", "01 Observe   →   02 Decide   →   03 Debrief"),
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=FONT_CHIP,
        ).pack(anchor="w", pady=(7, 0))
        ttk.Button(right, text=self.tx("바로 시작", "Start now"), style="Primary.TButton", command=lambda: self.show_page("first7")).pack(fill="x")
        ttk.Button(right, text=self.tx("랜덤 첫 주", "Randomize week"), command=self.reset_first_week).pack(fill="x", pady=(6, 0))

    def _render_top_stats(self):
        first_week_total = sum(len(pool) for pool in FIRST_WEEK_DAY_POOLS)
        english_total = sum(len(topic["words"]) + len(topic["sentences"]) for topics in ENGLISH_STUDY_TOPICS.values() for topic in topics)
        section = tk.Frame(self.page.inner, bg=COLORS["bg"])
        section.pack(fill="x", padx=30, pady=(18, 8))

        header = tk.Frame(section, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 8))
        tk.Label(
            header,
            text=self.tx("SIMULATION SCALE", "SIMULATION SCALE"),
            bg=COLORS["bg"],
            fg=COLORS["accent"],
            font=FONT_CHIP,
        ).pack(side="left")
        tk.Label(
            header,
            text=self.tx(
                "취업률/만족도는 베타 사용자 데이터 수집 후 공개",
                "Employment and satisfaction metrics will be published after beta user data is collected",
            ),
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONT_CHIP,
        ).pack(side="right")

        grid = tk.Frame(section, bg=COLORS["bg"])
        grid.pack(fill="x")
        for col in range(4):
            grid.columnconfigure(col, weight=1, uniform="top_stats")
        stats = [
            (
                f"{first_week_total}+",
                self.tx("첫 주 적응 장면", "first-week scenes"),
                self.tx("랜덤 케이스 기반", "randomized case pool"),
                COLORS["accent"],
                False,
            ),
            (
                f"{len(QUESTIONS)}+",
                self.tx("스테이션 판단", "station decisions"),
                self.tx("투약실/스테이션/인수인계", "med room / station / handoff"),
                COLORS["success"],
                False,
            ),
            (
                f"{len(SCENARIOS)}+",
                self.tx("환자 케이스", "patient cases"),
                self.tx("악화/퇴원/격리/가족 전화", "change / discharge / isolation"),
                COLORS["accent_dark"],
                False,
            ),
            (
                f"{english_total}+",
                self.tx("영어 학습 카드", "English study cards"),
                self.tx("일상 영어 + 간호 업무 영어", "daily + clinical English"),
                COLORS["success_dark"],
                False,
            ),
        ]
        for col, (number, label, detail, accent, dark) in enumerate(stats):
            card = self.top_stat_card(grid, number, label, detail, accent, dark=dark)
            card.grid(row=0, column=col, sticky="nsew", padx=6, pady=6)

    def _render_program_benefits(self):
        section = tk.Frame(self.page.inner, bg=COLORS["bg"])
        section.pack(fill="x", padx=30, pady=(18, 8))

        header = tk.Frame(section, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 8))
        tk.Label(
            header,
            text=self.tx("01 / PROGRAM BENEFITS", "01 / PROGRAM BENEFITS"),
            bg=COLORS["bg"],
            fg=COLORS["accent"],
            font=FONT_CHIP,
        ).pack(anchor="w")
        tk.Label(
            header,
            text=self.tx("미국 병동 적응을 위한 핵심 준비", "A Bento View of What You Practice"),
            bg=COLORS["bg"],
            fg=COLORS["ink"],
            font=FONT_SECTION,
        ).pack(anchor="w", pady=(3, 0))
        tk.Label(
            header,
            text=self.tx(
                "강의처럼 읽는 프로그램이 아니라, 시각 단서와 선택, 디브리핑을 반복하며 첫 주의 흐름을 몸에 익히는 구조입니다.",
                "A practical loop of visual cues, choices, and debriefs for the first week on a U.S. ward.",
            ),
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONT_SMALL,
            wraplength=1040,
            justify="left",
        ).pack(anchor="w", pady=(5, 0))

        grid = tk.Frame(section, bg=COLORS["bg"])
        grid.pack(fill="x")
        for col in range(4):
            grid.columnconfigure(col, weight=1, uniform="benefits")

        cards = [
            (
                self.tx("미국 병동 시뮬레이션", "US Hospital Simulation"),
                self.tx(
                    "스테이션, 투약실, 환자 병실, supply/PPE room을 사진 단서와 구역 지도 기반으로 움직입니다.",
                    "Move through nurse station, med room, patient room, and supply/PPE spaces with visual cues and a unit map.",
                ),
                self.tx("Ward workflow", "Ward workflow"),
                COLORS["accent"],
                "hospital_hero",
                lambda: self.show_page("tour"),
                210,
                False,
                0,
                0,
                2,
            ),
            (
                self.tx("NCLEX 이후 실무 판단", "NCLEX-to-Practice Bridge"),
                self.tx(
                    "NGN처럼 단서를 인식하고 우선순위, 행동, 디브리핑을 실제 병동 흐름에 연결합니다.",
                    "Connect NGN-style cue recognition, priority setting, action, and debriefing to real unit flow.",
                ),
                self.tx("Clinical judgment", "Clinical judgment"),
                COLORS["accent_dark"],
                None,
                lambda: self.show_page("first7"),
                210,
                False,
                0,
                2,
                1,
            ),
            (
                self.tx("비자/이민 준비 체크포인트", "Visa / Relocation Readiness"),
                self.tx(
                    "법률 자문이 아니라, 미국 입국 후 병원 온보딩, 서류 질문, 생활 커뮤니케이션에서 놓치기 쉬운 포인트를 짚습니다.",
                    "Not legal advice; supports onboarding, documentation questions, and day-to-day communication readiness.",
                ),
                self.tx("Non-legal prep", "Non-legal prep"),
                COLORS["success"],
                None,
                lambda: self.show_page("checklists"),
                210,
                False,
                0,
                3,
                1,
            ),
            (
                self.tx("간호 영어 루틴", "Nursing English Routine"),
                self.tx(
                    "일상 정착 표현과 SBAR, provider call, 가족 통화 문장을 랜덤 카드로 반복합니다.",
                    "Repeat daily settlement phrases plus SBAR, provider calls, and family-call language with randomized cards.",
                ),
                self.tx("Daily + clinical", "Daily + clinical"),
                COLORS["accent"],
                None,
                lambda: self.show_page("english"),
                188,
                False,
                1,
                0,
                1,
            ),
            (
                self.tx("미국 병원 에티켓", "U.S. Ward Etiquette"),
                self.tx(
                    "HIPAA/PHI, interpreter, chain of command, break room boundary를 상황 선택으로 연습합니다.",
                    "Practice HIPAA/PHI, interpreter use, chain of command, and break-room boundaries through scenarios.",
                ),
                self.tx("HIPAA / team", "HIPAA / team"),
                COLORS["primary"],
                None,
                lambda: self.show_page("quests"),
                188,
                False,
                1,
                1,
                1,
            ),
            (
                self.tx("시설별 차이 인식", "Facility Variation"),
                self.tx(
                    "정답을 하나로 고정하지 않고 state, facility, EHR, unit policy에 따라 달라질 수 있음을 피드백에 포함합니다.",
                    "Feedback reinforces that state, facility, EHR, and unit policy can change the workflow.",
                ),
                self.tx("Policy aware", "Policy aware"),
                COLORS["primary"],
                "ward_collage",
                lambda: self.show_page("guide"),
                188,
                False,
                1,
                2,
                2,
            ),
        ]
        for title, subtitle, tag, accent, image_key, command, height, dark, row, col, span in cards:
            card = self.bento_card(grid, title, subtitle, tag, accent, image_key=image_key, command=command, height=height, dark=dark)
            card.grid(row=row, column=col, columnspan=span, sticky="nsew", padx=6, pady=6)

    def _render_journey_timeline(self):
        section = tk.Frame(self.page.inner, bg=COLORS["bg"])
        section.pack(fill="x", padx=30, pady=(12, 8))

        header = tk.Frame(section, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 8))
        tk.Label(
            header,
            text=self.tx("02 / CURRICULUM PROCESS", "02 / CURRICULUM PROCESS"),
            bg=COLORS["bg"],
            fg=COLORS["accent"],
            font=FONT_CHIP,
        ).pack(anchor="w")
        tk.Label(
            header,
            text=self.tx("한국에서 미국 병동까지 이어지는 준비 여정", "A Step-by-step Journey from Korea to a U.S. Ward"),
            bg=COLORS["bg"],
            fg=COLORS["ink"],
            font=FONT_SECTION,
        ).pack(anchor="w", pady=(3, 0))
        tk.Label(
            header,
            text=self.tx(
                "각 단계는 단순 정보가 아니라, 실제 프로그램 안의 투어·선택·케이스·영어 연습으로 연결됩니다.",
                "Each step connects to an in-app tour, decision task, patient case, or English practice loop.",
            ),
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONT_SMALL,
            wraplength=1040,
            justify="left",
        ).pack(anchor="w", pady=(5, 0))

        canvas = tk.Canvas(section, height=340, bg=COLORS["bg"], highlightthickness=0)
        canvas.pack(fill="x")
        self._draw_journey_timeline(canvas, 900)
        canvas.bind("<Configure>", lambda event: self._draw_journey_timeline(event.widget, event.width))

    def _draw_journey_timeline(self, canvas, width):
        canvas.delete("all")
        width = max(int(width), 900)
        height = 340
        margin = 34
        line_y = 86
        steps = [
            (
                self.tx("Korea readiness", "Korea Readiness"),
                self.tx("서류·영어·병동 차이를 먼저 점검", "Check documents, English, and system gaps"),
                "checklists",
                COLORS["accent"],
            ),
            (
                self.tx("NCLEX 이후 전환", "NCLEX-to-Unit Bridge"),
                self.tx("NGN 판단을 실제 RN workflow로 연결", "Turn NGN judgment into RN workflow"),
                "first7",
                COLORS["accent_dark"],
            ),
            (
                self.tx("가상 병동 투어", "Virtual Ward Tour"),
                self.tx("공간, 동선, 물품 위치를 사진 단서로 파악", "Read spaces, routes, and supplies with photo cues"),
                "tour",
                COLORS["success"],
            ),
            (
                self.tx("스테이션 실습", "Station Practice"),
                self.tx("투약실, 스테이션, handoff 판단 반복", "Practice med room, station, and handoff decisions"),
                "quests",
                COLORS["primary"],
            ),
            (
                self.tx("커뮤니케이션 랩", "Communication Lab"),
                self.tx("SBAR, provider call, 가족 통화 영어", "SBAR, provider calls, and family-call English"),
                "english",
                COLORS["accent"],
            ),
            (
                self.tx("첫 주 적응", "First-week Adaptation"),
                self.tx("7일 랜덤 장면과 디브리핑으로 마무리", "Finish with randomized first-week scenes and debriefs"),
                "first7",
                COLORS["primary"],
            ),
        ]

        self.rounded_rect(canvas, 3, 3, width - 5, height - 8, 26, fill=COLORS["panel"], outline=COLORS["card_border"])
        canvas.create_text(margin + 36, 22, text=self.tx("KOREA", "KOREA"), fill=COLORS["muted"], font=FONT_CHIP, anchor="center")
        canvas.create_text(width - margin - 36, 22, text=self.tx("U.S. WARD", "U.S. WARD"), fill=COLORS["muted"], font=FONT_CHIP, anchor="center")
        canvas.create_line(margin + 36, line_y, width - margin - 36, line_y, fill=COLORS["line"], width=5)
        canvas.create_line(margin + 36, line_y, width - margin - 36, line_y, fill=COLORS["primary"], width=2)

        gap = (width - (margin * 2) - 72) / max(1, len(steps) - 1)
        for index, (title, body, page, color) in enumerate(steps):
            x = margin + 36 + index * gap
            tag = f"journey_step_{index}"
            canvas.create_oval(x - 17, line_y - 17, x + 17, line_y + 17, fill=COLORS["panel"], outline=color, width=3, tags=(tag,))
            canvas.create_oval(x - 7, line_y - 7, x + 7, line_y + 7, fill=color, outline=color, tags=(tag,))
            canvas.create_text(x, line_y - 30, text=f"{index + 1:02d}", fill=color, font=FONT_CHIP, tags=(tag,))

            card_gap = 18
            card_width = (width - margin * 2 - card_gap * 2) / 3
            card_height = 96
            row = index // 3
            col = index % 3
            x1 = margin + col * (card_width + card_gap)
            x2 = x1 + card_width
            y1 = 106 + row * (card_height + 16)
            y2 = y1 + card_height
            self.rounded_rect(canvas, x1, y1, x2, y2, 18, fill=COLORS["panel_alt"], outline=COLORS["card_border"], tags=(tag,))
            canvas.create_rectangle(x1 + 14, y1 + 15, x1 + 46, y1 + 18, fill=color, outline=color, tags=(tag,))
            canvas.create_text(x1 + 14, y1 + 34, text=title, fill=COLORS["ink"], font=FONT_SMALL_BOLD, anchor="nw", width=x2 - x1 - 28, tags=(tag,))
            canvas.create_text(x1 + 14, y1 + 60, text=body, fill=COLORS["muted"], font=FONT_CHIP, anchor="nw", width=x2 - x1 - 28, tags=(tag,))
            canvas.tag_bind(tag, "<Button-1>", lambda _event, target=page: self.show_page(target))
            canvas.tag_bind(tag, "<Enter>", lambda _event: canvas.configure(cursor="hand2"))
            canvas.tag_bind(tag, "<Leave>", lambda _event: canvas.configure(cursor=""))

    def _render_social_proof(self):
        section = tk.Frame(self.page.inner, bg=COLORS["bg"])
        section.pack(fill="x", padx=30, pady=(12, 8))

        header = tk.Frame(section, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 8))
        tk.Label(
            header,
            text=self.tx("03 / SOCIAL PROOF", "03 / SOCIAL PROOF"),
            bg=COLORS["bg"],
            fg=COLORS["accent"],
            font=FONT_CHIP,
        ).pack(anchor="w")
        tk.Label(
            header,
            text=self.tx("미국 병동에 적응한 RN들의 전환 스토리", "Relocation Stories from Nurses Who Reached U.S. Practice"),
            bg=COLORS["bg"],
            fg=COLORS["ink"],
            font=FONT_SECTION,
        ).pack(anchor="w", pady=(3, 0))
        tk.Label(
            header,
            text=self.tx(
                "아래 카드는 실명 후기가 아니라, 한국 RN들이 미국 이주와 병동 적응 과정에서 자주 겪는 흐름을 합성한 예시입니다.",
                "These are composite stories, not individual endorsements, based on common transition patterns for Korean RNs relocating to U.S. practice.",
            ),
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=FONT_SMALL,
            wraplength=1040,
            justify="left",
        ).pack(anchor="w", pady=(5, 0))

        grid = tk.Frame(section, bg=COLORS["bg"])
        grid.pack(fill="x")
        for col in range(3):
            grid.columnconfigure(col, weight=1, uniform="testimonials")

        testimonials = [
            (
                "JK",
                self.tx("J. Kim, RN", "J. Kim, RN"),
                self.tx("Seoul -> Texas Med-Surg", "Seoul -> Texas Med-Surg"),
                self.tx(
                    "첫 출근 전 badge, charge RN, interpreter, SBAR 표현을 미리 입으로 연습해서 덜 얼어붙었습니다.",
                    "Practicing badge, charge RN, interpreter, and SBAR language before day one made the first shift feel less overwhelming.",
                ),
                self.tx("Focus: first-week confidence", "Focus: first-week confidence"),
                COLORS["accent"],
                False,
            ),
            (
                "HL",
                self.tx("H. Lee, ICU RN", "H. Lee, ICU RN"),
                self.tx("Busan -> California ICU", "Busan -> California ICU"),
                self.tx(
                    "한국 중환자실 경험은 있었지만 escalation threshold와 provider call 톤을 따로 연습한 게 도움이 됐습니다.",
                    "ICU experience helped, but practicing escalation thresholds and provider-call tone was what translated best.",
                ),
                self.tx("Focus: escalation and team language", "Focus: escalation and team language"),
                COLORS["success"],
                False,
            ),
            (
                "SP",
                self.tx("S. Park, RN", "S. Park, RN"),
                self.tx("Daegu -> New Jersey Telemetry", "Daegu -> New Jersey Telemetry"),
                self.tx(
                    "미국 병원마다 다르다는 전제를 알고 들어가니, 모르면 clarify하고 policy를 확인하는 태도가 자연스러워졌습니다.",
                    "Knowing that each facility varies made it easier to clarify early and check policy without feeling behind.",
                ),
                self.tx("Focus: policy-aware adaptation", "Focus: policy-aware adaptation"),
                COLORS["accent_dark"],
                False,
            ),
        ]

        for col, data in enumerate(testimonials):
            card = self.testimonial_card(grid, *data)
            card.grid(row=0, column=col, sticky="nsew", padx=6, pady=6)

    def _draw_dashboard_canvas(self, canvas, width):
        canvas.delete("all")
        width = max(int(width), 640)
        height = 182
        canvas.create_rectangle(0, 0, width, height, fill=COLORS["panel"], outline="")
        day_no = self.first_week_day + 1
        completed = len(self.first_week_answers)
        center_x = width / 2
        canvas.create_text(center_x, 19, text="U.S. WARD EXPERIENCE LAB  ·  LOCAL TRAINING", fill=COLORS["primary"], font=FONT_CHIP)
        hero_title = self.tx("오늘 어떤 병동 상황을 연습할까요?", "What would you like to rehearse today?")
        title_width = tkfont.Font(font=FONT_HERO).measure(hero_title)
        title_group_width = 34 + 14 + title_width
        title_start_x = max(24, center_x - (title_group_width / 2))
        canvas.create_oval(title_start_x, 49, title_start_x + 34, 83, fill=COLORS["ink"], outline="")
        canvas.create_text(title_start_x + 17, 66, text="UW", fill="#ffffff", font=FONT_CHIP)
        canvas.create_text(title_start_x + 48, 66, text=hero_title, fill=COLORS["ink"], font=FONT_HERO, anchor="w")
        hero_body = self.tx(
            "장면을 고르고, 다음 행동을 판단한 뒤 근거를 짧게 확인하세요.",
            "Choose a scene, decide the next action, then review the rationale.",
        )
        canvas.create_text(center_x, 107, text=hero_body, fill=COLORS["muted"], font=FONT_NORMAL)
        progress_text = self.tx(
            f"Day {day_no} / 7  ·  완료 {completed} / 7  ·  관찰 → 판단 → 디브리핑",
            f"Day {day_no} / 7  ·  Done {completed} / 7  ·  Observe → Decide → Debrief",
        )
        self.rounded_rect(canvas, center_x - 190, 132, center_x + 190, 160, 12, fill=COLORS["panel_alt"], outline=COLORS["line"])
        canvas.create_text(center_x, 146, text=progress_text, fill=COLORS["muted"], font=FONT_CHIP)

    def _render_specialties(self):
        self.page_title(
            self.tx("직무 트랙", "Specialty Tracks"),
            self.tx(
                "미국 병원 안에서도 부서마다 RN에게 요구되는 task와 escalation 기준이 다릅니다.",
                "RN tasks and escalation thresholds vary widely by U.S. specialty area.",
            ),
        )

        audit = self.panel(padding=18)
        ttk.Label(audit, text=self.tx("역할이 달라지면 보는 단서도 달라집니다", "A different role changes what you watch for"), style="CardTitle.TLabel").pack(anchor="w")
        audit_text = self.tx(
            "Staff RN, Charge RN, Preceptor, LPN/LVN, PCT/CNA는 같은 장면에서도 서로 다른 책임과 멈춤 지점을 봅니다. 아래 트랙에서 익숙한 역할과 준비 중인 역할을 비교해보세요.",
            "Staff RNs, charge RNs, preceptors, LPN/LVNs, and PCT/CNAs notice different responsibilities and pause points in the same scene. Compare the role you know with the role you are preparing for.",
        )
        ttk.Label(audit, text=audit_text, style="Panel.TLabel", wraplength=800, justify="left").pack(anchor="w", pady=(6, 0))

        photo_panel = self.panel(padding=14)
        photo_row = tk.Frame(photo_panel, bg=COLORS["panel"])
        photo_row.pack(fill="x")
        photo_items = [
            ("photo_nurse_station", self.tx("간호사 스테이션", "Nurse Station"), self.tx("업무 배정 · 호출", "Assignments · calls")),
            ("photo_med_room", self.tx("투약실", "Medication Room"), self.tx("투약 준비 · 확인", "Prepare · verify")),
            ("photo_patient_room", self.tx("환자 병실", "Patient Room"), self.tx("직접 간호 · 관찰", "Care · observe")),
            ("photo_supply_room", self.tx("물품실", "Supply / PPE Room"), self.tx("물품 · PPE 준비", "Supplies · PPE")),
        ]
        for col in range(4):
            photo_row.columnconfigure(col, weight=1)
        for col, (image_key, title, body) in enumerate(photo_items):
            tile = tk.Frame(
                photo_row,
                bg=COLORS["panel_alt"],
                highlightthickness=1,
                highlightbackground=COLORS["card_border"],
                padx=10,
                pady=9,
            )
            tile.grid(row=0, column=col, sticky="nsew", padx=4, pady=4)
            compact = tk.Frame(tile, bg=COLORS["panel_alt"])
            compact.pack(anchor="center")
            image = self.scaled_image(image_key, 96, 76)
            if image:
                tk.Label(compact, image=image, bg=COLORS["panel_alt"], borderwidth=0).pack(side="left", padx=(0, 10))
            copy = tk.Frame(compact, bg=COLORS["panel_alt"])
            copy.pack(side="left", anchor="center")
            tk.Label(copy, text=title, bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL_BOLD, wraplength=112, justify="left").pack(anchor="w")
            tk.Label(copy, text=body, bg=COLORS["panel_alt"], fg=COLORS["muted"], font=FONT_CHIP, wraplength=112, justify="left").pack(anchor="w", pady=(3, 0))

        grid_outer = tk.Frame(self.page.inner, bg=COLORS["bg"])
        grid_outer.pack(fill="x", padx=28, pady=8)
        for col in range(2):
            grid_outer.columnconfigure(col, weight=1, uniform="specialty_tracks")
        for index, track in enumerate(SPECIALTY_TRACKS):
            row, col = divmod(index, 2)
            outer, card = self._card_shell(grid_outer, bg=COLORS["panel"], padding=16)
            outer.grid(row=row, column=col, sticky="nsew", padx=(0, 8) if col == 0 else (8, 0), pady=8)
            tk.Frame(card, bg=track["color"], height=7).pack(fill="x", pady=(0, 12))
            header = tk.Frame(card, bg=COLORS["panel"])
            header.pack(fill="x")
            tk.Label(header, text=track["name"], bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_CARD_TITLE).pack(side="left", anchor="w")
            icon = self.icon_image("icon_safety", 34)
            if icon:
                tk.Label(header, image=icon, bg=COLORS["panel"]).pack(side="right")
            tk.Label(card, text=track["tag"], bg=track["color"], fg=COLORS["ink"], font=FONT_CHIP, padx=9, pady=4).pack(anchor="w", pady=(8, 10))
            tk.Label(card, text=self.clean_text(track["focus"]), bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_NORMAL, wraplength=360, justify="left").pack(anchor="w", pady=(0, 10))
            tk.Label(card, text=self.tx("요구 task", "Required tasks"), bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w")
            for task in track["tasks"]:
                tk.Label(card, text=f"• {self.clean_text(task)}", bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=360, justify="left").pack(anchor="w", pady=2)
            tk.Label(card, text=self.tx("적응 리스크", "Adaptation risk"), bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w", pady=(11, 2))
            tk.Label(card, text=self.clean_text(track["risk"]), bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=360, justify="left").pack(anchor="w")

            practice = tk.Frame(card, bg=COLORS["panel"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=10, pady=8)
            practice.pack(fill="x", pady=(12, 0))
            tk.Label(practice, text=self.tx("추천 연습", "Recommended Practice"), bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w")
            tk.Label(practice, text=self.clean_text(track["practice"]), bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL_BOLD, wraplength=360, justify="left").pack(anchor="w", pady=(3, 6))
            chip_row = tk.Frame(practice, bg=COLORS["panel"])
            chip_row.pack(fill="x")
            for label, color in [
                (self.tx("Acuity", "Acuity"), COLORS["soft_orange"]),
                (self.tx("Team", "Team"), COLORS["soft_blue"]),
                (self.tx("Escalation", "Escalation"), COLORS["soft_lavender"]),
            ]:
                tk.Label(chip_row, text=label, bg=color, fg=COLORS["ink"], font=FONT_CHIP, padx=8, pady=3).pack(side="left", padx=(0, 5))

        bottom = self.panel(padding=18)
        ttk.Label(bottom, text=self.tx("직무 트랙을 활용하는 법", "How to use the specialty tracks"), style="CardTitle.TLabel").pack(anchor="w")
        self.bullet_list(
            bottom,
            (
                [
                    "먼저 자신의 현재 역할과 가장 가까운 트랙에서 익숙한 업무와 다른 경계를 표시합니다.",
                    "그다음 준비 중인 역할로 바꿔 delegation, escalation, privacy 단서를 다시 비교합니다.",
                    "정답을 외우기보다 facility policy와 state scope를 어디서 확인해야 하는지 메모합니다.",
                ]
                if not self.is_english()
                else [
                    "Start with the track closest to your current role and mark familiar tasks versus unfamiliar boundaries.",
                    "Switch to the role you are preparing for and compare delegation, escalation, and privacy cues.",
                    "Focus on where to verify facility policy and state scope instead of memorizing one universal answer.",
                ]
            ),
            wraplength=1500,
        )

    def _render_tour(self):
        self.page_title(
            self.tx("병동 투어", "Ward Tour"),
            self.tx("구역을 클릭하고, 선택한 근무 상황에서 다음 동선을 직접 골라봅니다.", "Click zones and choose the next movement for the selected shift situation."),
        )

        controls = self.panel(padding=16)
        mode_values = self.tour_modes_for_role()
        if self.tour_mode.get() not in mode_values:
            self.tour_mode.set(mode_values[0])
            self.tour_step = 0
        mode_row = tk.Frame(controls, bg=COLORS["panel"])
        mode_row.pack(fill="x")
        ttk.Label(mode_row, text=self.tx("실습 모드", "Practice Mode"), style="CardTitle.TLabel").pack(side="left", padx=(0, 10))
        mode = ttk.Combobox(mode_row, textvariable=self.tour_mode, values=mode_values, state="readonly", width=28)
        mode.pack(side="left", padx=(0, 8))
        mode.bind("<<ComboboxSelected>>", lambda _event: self.reset_tour_route())
        ttk.Button(mode_row, text=self.tx("랜덤 동선", "Random Route"), command=self.random_tour_mode).pack(side="left", padx=(0, 8))
        ttk.Button(mode_row, text=self.tx("동선 초기화", "Reset Route"), command=self.reset_tour_route).pack(side="left", padx=(0, 12))
        self._render_role_selector(controls, "tour")
        tk.Label(
            controls,
            textvariable=self.tour_feedback,
            bg=COLORS["soft_blue"],
            fg=COLORS["ink"],
            font=FONT_SMALL,
            anchor="w",
            justify="left",
            wraplength=820,
            padx=10,
            pady=7,
        ).pack(fill="x", pady=(8, 0))

        outer = ttk.Frame(self.page.inner, style="Page.TFrame")
        outer.pack(fill="x", padx=24, pady=6)
        outer.columnconfigure(0, weight=3, uniform="tour_main")
        outer.columnconfigure(1, weight=2, uniform="tour_main")

        map_outer, map_panel = self._card_shell(outer, padding=18)
        map_outer.grid(row=0, column=0, sticky="new", padx=(0, 8))
        ttk.Label(map_panel, text="4 West Med-Surg/Telemetry Unit", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(
            map_panel,
            text=self.tx("지도에서 구역을 클릭하면 곧바로 다음 동선 선택으로 처리됩니다.", "Click a zone on the map to choose the next route step."),
            style="Muted.TLabel",
            wraplength=350,
            justify="left",
        ).pack(anchor="w", pady=(2, 10))
        self.map_canvas = tk.Canvas(map_panel, height=382, bg=COLORS["panel_alt"], highlightthickness=1, highlightbackground=COLORS["card_border"])
        self.map_canvas.pack(fill="x")
        self._draw_ward_map()
        self.map_canvas.bind("<Configure>", lambda event: self._draw_ward_map())

        right_stack = ttk.Frame(outer, style="Page.TFrame")
        right_stack.grid(row=0, column=1, sticky="new", padx=(8, 0))

        flow_outer, self.flow_panel = self._card_shell(right_stack, padding=16)
        flow_outer.pack(fill="x")
        self._render_tour_flow()

        zone_outer, self.zone_panel = self._card_shell(self.page.inner, padding=16)
        zone_outer.pack(fill="x", padx=24, pady=(2, 6))
        self._render_zone_details(self.current_zone)

    def _draw_ward_map(self):
        c = self.map_canvas
        c.delete("all")
        canvas_w = max(c.winfo_width(), 320)
        draw_left, draw_right = 18, canvas_w - 18
        gap = 12
        card_w = (draw_right - draw_left - gap * 2) / 3
        top_y1, top_y2 = 20, 128
        bottom_y1, bottom_y2 = 218, 326
        names = [
            "Medication Room",
            "Nurse Station",
            "Supply Room",
            "Patient Room",
            "Utility / Isolation",
            "Handoff Zone",
        ]
        scaled_zones = {}
        for index, name in enumerate(names):
            row, col = divmod(index, 3)
            x1 = draw_left + col * (card_w + gap)
            y1, y2 = (top_y1, top_y2) if row == 0 else (bottom_y1, bottom_y2)
            scaled_zones[name] = (x1, y1, x1 + card_w, y2)
        centers = {name: ((xy[0] + xy[2]) / 2, (xy[1] + xy[3]) / 2) for name, xy in scaled_zones.items()}
        hall_y = 173
        self.rounded_rect(c, draw_left + 18, 152, draw_right - 18, 194, 14, fill=COLORS["soft_gray"], outline="")
        c.create_text((draw_left + draw_right) / 2, hall_y, text="4 WEST · MAIN HALLWAY", fill=COLORS["muted"], font=FONT_CHIP)

        def draw_route(first, second, color, line_width):
            ax, ay = centers[first]
            bx, by = centers[second]
            c.create_line(ax, ay, ax, hall_y, bx, hall_y, bx, by, fill=color, width=line_width, capstyle="round", joinstyle="round")

        route_steps = TOUR_MODES[self.tour_mode.get()]["steps"]
        route_names = [item[0] for item in route_steps]
        for first, second in zip(route_names, route_names[1:]):
            draw_route(first, second, COLORS["line_dark"], 3)
        completed_names = route_names[: min(self.tour_step + 1, len(route_names))]
        for first, second in zip(completed_names, completed_names[1:]):
            draw_route(first, second, COLORS["primary"], 4)

        for name, coords in scaled_zones.items():
            data = WARD_ZONES[name]
            fill = COLORS["soft_cyan"] if name == self.current_zone else COLORS["panel"]
            is_current_route = self.tour_step < len(route_steps) and name == route_steps[self.tour_step][0]
            outline = COLORS["primary"] if name == self.current_zone else (COLORS["warning"] if is_current_route else COLORS["card_border"])
            width = 3 if name == self.current_zone else (2 if is_current_route else 1)
            tag = "zone_" + name.replace(" ", "_").replace("/", "_")
            self.rounded_rect(c, *coords, 12, fill=fill, outline=outline, width=width, tags=(tag,))
            x1, y1, x2, y2 = coords
            icon = self.icon_image(self.zone_icon_key(name), 34)
            if icon:
                c.create_image((x1 + x2) / 2, y1 + 27, image=icon, anchor="center", tags=(tag,))
            display_title = data["title"] if self.is_english() else data["korean"]
            node_font = FONT_CHIP if (x2 - x1) < 130 else FONT_SMALL_BOLD
            c.create_text((x1 + x2) / 2, y1 + 50, text=display_title, width=(x2 - x1 - 12), fill=COLORS["ink"], font=node_font, anchor="n", tags=(tag,))
            state_text = self.tx("현재", "CURRENT") if name == self.current_zone else self.tx("다음", "NEXT") if is_current_route else ""
            if state_text:
                c.create_text((x1 + x2) / 2, y2 - 12, text=state_text, fill=outline, font=FONT_CHIP, tags=(tag,))
            c.tag_bind(tag, "<Button-1>", lambda _event, zone=name: self.choose_tour_next(zone))
            c.tag_bind(tag, "<Enter>", lambda _event: c.configure(cursor="hand2"))
            c.tag_bind(tag, "<Leave>", lambda _event: c.configure(cursor=""))

        c.create_text((draw_left + draw_right) / 2, 362, text=self.tx("교육용 mock layout · 실제 구조와 장비 배치는 병원마다 다릅니다.", "Educational mock layout · real units vary by facility."), fill=COLORS["muted"], font=FONT_CHIP)

    def _render_tour_flow(self):
        for child in self.flow_panel.winfo_children():
            child.destroy()
        steps = TOUR_MODES[self.tour_mode.get()]["steps"]
        complete = self.tour_step >= len(steps)
        progress = int((min(self.tour_step, len(steps)) / len(steps)) * 100)
        progress_label = self.tx(f"{self.tour_mode.get()}  {progress}% 완료", f"{self.tour_mode.get()}  {progress}% complete")
        ttk.Label(self.flow_panel, text=self.tx("동선 선택", "Route Choices"), style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(self.flow_panel, text=progress_label, style="Muted.TLabel", wraplength=300, justify="left").pack(anchor="w", pady=(2, 0))
        self.modern_progress(self.flow_panel, progress, maximum=100, height=12, fill=COLORS["primary"], bg=COLORS["panel"]).pack(fill="x", pady=(8, 10))
        lane = tk.Frame(self.flow_panel, bg=COLORS["panel"])
        lane.pack(fill="x", pady=(0, 10))
        for index, (zone, _note) in enumerate(steps):
            is_done = index < self.tour_step
            is_current = index == self.tour_step and not complete
            color = COLORS["soft_green"] if is_done else (WARD_ZONES[zone]["color"] if is_current else COLORS["panel_alt"])
            border = COLORS["success"] if is_done else (COLORS["primary"] if is_current else COLORS["card_border"])
            card = tk.Frame(lane, bg=color, highlightthickness=1, highlightbackground=border, padx=8, pady=6)
            card.pack(fill="x", pady=2)
            tk.Label(card, text=str(index + 1), bg=COLORS["primary"] if is_current else COLORS["line_dark"], fg="#ffffff", font=FONT_CHIP, width=3).pack(side="left", padx=(0, 7))
            tk.Label(card, text=WARD_ZONES[zone]["korean"], bg=color, fg=COLORS["ink"], font=FONT_SMALL_BOLD, wraplength=155, justify="left", anchor="w").pack(side="left", fill="x", expand=True)
            state_text = self.tx("완료" if is_done else ("다음" if is_current else "대기"), "done" if is_done else ("next" if is_current else "queued"))
            tk.Label(card, text=state_text, bg=color, fg=COLORS["primary"] if is_current or is_done else COLORS["muted"], font=FONT_CHIP, padx=5).pack(side="right")
            route_icon = self.icon_image(self.zone_icon_key(zone), 24)
            if route_icon:
                tk.Label(card, image=route_icon, bg=color).pack(side="right", padx=(4, 2))
        if complete:
            ttk.Label(
                self.flow_panel,
                text=self.tx("동선을 끝냈습니다. 다른 모드로 바꿔 다시 돌려보세요.", "Route complete. Choose another mode and run it again."),
                style="Panel.TLabel",
                wraplength=300,
                justify="left",
            ).pack(anchor="w")
            return

        expected, note = steps[self.tour_step]
        target = tk.Frame(self.flow_panel, bg=COLORS["soft_gold"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=10, pady=8)
        target.pack(fill="x", pady=(0, 10))
        tk.Label(target, text=self.tx("현재 목표", "Current Target"), bg=COLORS["soft_gold"], fg=COLORS["muted"], font=FONT_CHIP).pack(anchor="w")
        tk.Label(target, text=WARD_ZONES[expected]["korean"], bg=COLORS["soft_gold"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w", pady=(2, 0))
        tk.Label(target, text=note, bg=COLORS["soft_gold"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=300, justify="left").pack(anchor="w", pady=(2, 0))
        ttk.Label(
            self.flow_panel,
            text=self.tx("오른쪽 버튼 또는 좌측 지도를 눌러 선택하세요.", "Choose with the buttons below or by clicking the map."),
            style="Muted.TLabel",
            wraplength=300,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))
        chooser = tk.Frame(self.flow_panel, bg=COLORS["panel"])
        chooser.pack(fill="x")
        for index, zone in enumerate(WARD_ZONES):
            chooser.columnconfigure(index % 2, weight=1, uniform="tour_choices")
            is_current = zone == self.current_zone
            bg = WARD_ZONES[zone]["color"] if is_current else COLORS["panel_alt"]
            button = self.choice_button(
                chooser,
                text=WARD_ZONES[zone]["korean"],
                command=lambda choice=zone: self.choose_tour_next(choice),
                bg=bg,
                active=WARD_ZONES[zone]["color"],
                font=FONT_SMALL_BOLD,
                wraplength=170,
            )
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=3, pady=3)

    def choose_tour_next(self, zone):
        steps = TOUR_MODES[self.tour_mode.get()]["steps"]
        if self.tour_step >= len(steps):
            return
        expected, note = steps[self.tour_step]
        if zone == expected:
            self.current_zone = zone
            self.tour_step += 1
            self.tour_feedback.set(self.tx(f"좋아요. {WARD_ZONES[zone]['korean']}에서 {note}", f"Good. In {WARD_ZONES[zone]['korean']}: {note}"))
        else:
            self.current_zone = zone
            self.tour_feedback.set(self.tx(f"지금은 {WARD_ZONES[expected]['korean']}로 가야 흐름이 이어집니다. 선택한 곳도 클릭해서 역할은 확인할 수 있어요.", f"To keep this workflow moving, go to {WARD_ZONES[expected]['korean']} next. You can still inspect the selected zone."))
        self._draw_ward_map()
        self._render_tour_flow()
        for child in self.zone_panel.winfo_children():
            child.destroy()
        self._render_zone_details(self.current_zone)

    def reset_tour_route(self):
        valid_modes = self.tour_modes_for_role()
        if valid_modes and self.tour_mode.get() not in valid_modes:
            self.tour_mode.set(valid_modes[0])
        self.tour_step = 0
        first_zone = TOUR_MODES[self.tour_mode.get()]["steps"][0][0]
        self.current_zone = first_zone
        self.tour_feedback.set(self.tx("동선이 초기화되었습니다. 다음 목표 구역을 선택해보세요.", "Route reset. Choose the next target zone."))
        self.show_page("tour")

    def random_tour_mode(self):
        self.tour_mode.set(random.choice(self.tour_modes_for_role()))
        self.tour_feedback.set(self.tx(f"{self.role_label()} 역할에 맞는 랜덤 동선을 새로 뽑았습니다.", f"A random route has been selected for the {self.role_label()} lens."))
        self.reset_tour_route()

    def select_zone(self, zone):
        self.current_zone = zone
        self.tour_feedback.set(self.tx(f"{WARD_ZONES[zone]['korean']}를 열었습니다. 오른쪽에서 오브젝트와 판단 카드를 확인하세요.", f"{WARD_ZONES[zone]['korean']} opened. Review objects and decision cards on the right."))
        self._draw_ward_map()
        for child in self.zone_panel.winfo_children():
            child.destroy()
        self._render_zone_details(zone)

    def _render_zone_details(self, zone):
        data = WARD_ZONES[zone]
        ttk.Label(self.zone_panel, text=data["korean"], style="CardTitle.TLabel").pack(anchor="w")

        overview = tk.Frame(self.zone_panel, bg=COLORS["panel"])
        overview.pack(fill="x", pady=(8, 10))
        overview.columnconfigure(1, weight=1)
        photo = self.scaled_image(self.zone_photo_key(zone), 280, 175)
        if photo:
            tk.Label(overview, image=photo, bg=COLORS["panel"], highlightthickness=1, highlightbackground=COLORS["card_border"]).grid(row=0, column=0, sticky="nw", padx=(0, 14))
        summary = tk.Frame(overview, bg=COLORS["panel"])
        summary.grid(row=0, column=1, sticky="new")
        tk.Label(summary, text=self.tx("이 공간의 역할", "Purpose of This Space"), bg=COLORS["panel"], fg=COLORS["accent_dark"], font=FONT_CHIP).pack(anchor="w")
        tk.Label(summary, text=self.clean_text(data["subtitle"]), bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL_BOLD, wraplength=520, justify="left").pack(anchor="w", pady=(4, 6))
        tk.Label(summary, text=self.clean_text(data["role"]), bg=COLORS["panel"], fg=COLORS["muted"], font=FONT_SMALL, wraplength=520, justify="left").pack(anchor="w")
        tk.Label(summary, text=self.compact_variation_note(), bg=COLORS["panel_alt"], fg=COLORS["muted"], font=FONT_CHIP, padx=8, pady=5, anchor="w").pack(fill="x", pady=(10, 0))

        cue_board = tk.Frame(self.zone_panel, bg=COLORS["panel"])
        cue_board.pack(fill="x", pady=(0, 10))
        object_names = " / ".join(name for name, _desc in data["objects"][:2])
        cards = [
            (self.tx("눈에 보이는 단서", "Visual Cues"), object_names, data["color"], self.zone_icon_key(zone)),
            (self.tx("귀에 들어오는 신호", "Auditory Cue"), data["common_calls"][0], COLORS["soft_blue"], "icon_safety"),
            (self.tx("RN 멈춤 지점", "RN Stop Point"), data["missions"][0], COLORS["soft_gold"], "icon_handoff"),
        ]
        for col, (title, body, color, icon_key) in enumerate(cards):
            cue_board.columnconfigure(col, weight=1, uniform="zone_cues")
            card = self._cue_card(cue_board, title, body, color, icon_key, icon_size=20, wraplength=210)
            card.grid(row=0, column=col, sticky="new", padx=(0, 5) if col < 2 else 0)

        ttk.Label(self.zone_panel, text=self.tx("업무 오브젝트", "Workflow Objects"), style="CardTitle.TLabel").pack(anchor="w", pady=(2, 6))
        obj_grid = tk.Frame(self.zone_panel, bg=COLORS["panel"])
        obj_grid.pack(fill="x")
        for index, (name, desc) in enumerate(data["objects"][:4]):
            row, col = 0, index
            card = tk.Frame(obj_grid, bg=data["color"], highlightthickness=2, highlightbackground=COLORS["card_border"])
            card.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            obj_grid.columnconfigure(col, weight=1, uniform="zone_objects")
            tk.Label(card, text=name, bg=data["color"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w", padx=10, pady=(8, 1))
            tk.Label(card, text=self.clean_text(desc), bg=data["color"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=180, justify="left").pack(anchor="w", padx=10, pady=(0, 8))

        lower = tk.Frame(self.zone_panel, bg=COLORS["panel"])
        lower.pack(fill="x", pady=(10, 0))
        lower.columnconfigure(0, weight=1, uniform="zone_lower")
        lower.columnconfigure(1, weight=1, uniform="zone_lower")
        signals = tk.Frame(lower, bg=COLORS["panel"], padx=0, pady=0)
        signals.grid(row=0, column=0, sticky="new", padx=(0, 8))
        decision_panel = tk.Frame(lower, bg=COLORS["panel"], padx=0, pady=0)
        decision_panel.grid(row=0, column=1, sticky="new", padx=(8, 0))

        ttk.Label(signals, text=self.tx("자주 들어오는 신호", "Common Signals"), style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))
        for call in data["common_calls"][:3]:
            tk.Label(signals, text=call, bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL, anchor="w", padx=10, pady=5, wraplength=360, justify="left").pack(fill="x", pady=2)

        ttk.Label(decision_panel, text=self.tx("이 구역에서 할 선택", "Decision in This Zone"), style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))
        decision = data["decisions"][0]
        ttk.Label(decision_panel, text=self.clean_text(decision["prompt"]), style="Panel.TLabel", wraplength=390, justify="left").pack(anchor="w", pady=(0, 6))
        for choice, ok in shuffled_bool_choices(decision["choices"]):
            self.choice_button(
                decision_panel,
                text=choice,
                command=lambda is_ok=ok, feedback=decision["feedback"]: self.answer_tour_decision(is_ok, feedback),
                bg=COLORS["panel_alt"],
                active=data["color"],
                font=FONT_SMALL,
                wraplength=390,
            ).pack(fill="x", pady=3)
        self._schedule_responsive_wraps(update_all=True)

    def answer_tour_decision(self, is_correct, feedback):
        prefix = self.tx("안전한 선택입니다. ", "Safe choice. ") if is_correct else self.tx("다시 생각해볼 선택입니다. ", "Think again. ")
        self.tour_feedback.set(prefix + self.with_variation_note(feedback))

    def _render_shift(self):
        self.page_title(
            self.tx("근무 보드", "Shift Board"),
            self.tx("07:00-19:30 day shift를 시간표가 아니라 우선순위 보드로 따라갑니다.", "Follow the 07:00-19:30 day shift as a priority board, not a simple schedule."),
        )
        board_panel = self.panel(padding=0)
        shift_canvas = tk.Canvas(board_panel, height=255, bg=COLORS["panel"], highlightthickness=0)
        shift_canvas.pack(fill="x")
        self._draw_shift_board(shift_canvas, 900)
        shift_canvas.bind("<Configure>", lambda event: self._draw_shift_board(event.widget, event.width))

        panel = self.panel(padding=20)
        progress = shift_progress_percent(self.shift_index)
        ttk.Label(panel, text=self.tx(f"진행률 {progress}%", f"Progress {progress}%"), style="CardTitle.TLabel").pack(anchor="w")
        self.modern_progress(panel, progress, maximum=100, height=13, fill=COLORS["primary"], bg=COLORS["panel"]).pack(fill="x", pady=(8, 16))

        if self.shift_index >= len(SHIFT_EVENTS):
            ttk.Label(panel, text=self.tx("Day Shift 완료", "Day Shift Complete"), style="CardTitle.TLabel").pack(anchor="w")
            ttk.Label(panel, text=self.tx("End-of-shift handoff까지 완료했습니다. 디브리핑에서 가장 어려웠던 판단을 정리해보세요.", "You completed end-of-shift handoff. Debrief the decision that felt most difficult."), style="Panel.TLabel", wraplength=860).pack(anchor="w", pady=(6, 14))
            ttk.Button(panel, text=self.tx("처음부터 다시", "Restart"), style="Primary.TButton", command=self.reset_shift).pack(anchor="w")
            return

        event = SHIFT_EVENTS[self.shift_index]
        detail = tk.Frame(panel, bg=COLORS["panel"])
        detail.pack(fill="x")
        detail.columnconfigure(0, weight=3)
        detail.columnconfigure(1, weight=2)
        left = tk.Frame(detail, bg=COLORS["panel"])
        left.grid(row=0, column=0, sticky="new", padx=(0, 14))
        right = tk.Frame(detail, bg=COLORS["panel_alt"], padx=12, pady=10, highlightthickness=1, highlightbackground=COLORS["card_border"])
        right.grid(row=0, column=1, sticky="new")

        ttk.Label(left, text=f"{event['time']}  {event['title']}", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(left, text=self.clean_text(event["details"]), style="Panel.TLabel", wraplength=420, justify="left").pack(anchor="w", pady=(6, 12))
        ttk.Label(left, text=self.tx("이 시점에서 할 일", "Actions at This Point"), style="CardTitle.TLabel").pack(anchor="w", pady=(4, 4))
        self.bullet_list(left, event["actions"], wraplength=420)

        tk.Label(right, text=self.tx("현재 cue board", "Current Cue Board"), bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w")
        shift_cues = [
            (self.tx("시간", "Time"), event["time"], COLORS["soft_blue"], "icon_safety"),
            (self.tx("우선순위", "Priority"), event["title"], COLORS["soft_gold"], "icon_nurse"),
            (self.tx("놓치면 위험", "Risk if missed"), event["actions"][0], COLORS["soft_orange"], "icon_handoff"),
        ]
        cue_grid = tk.Frame(right, bg=COLORS["panel_alt"])
        cue_grid.pack(fill="x", pady=(6, 0))
        for col in range(2):
            cue_grid.columnconfigure(col, weight=1)
        for index, (title, body, color, icon_key) in enumerate(shift_cues):
            if index < 2:
                row, col, span = 0, index, 1
            else:
                row, col, span = 1, 0, 2
            card = self._cue_card(right, title, body, color, icon_key, icon_size=18, wraplength=280)
            card.grid(in_=cue_grid, row=row, column=col, columnspan=span, sticky="new", padx=(0, 4) if col == 0 and span == 1 else (4, 0) if col == 1 else 0, pady=(0, 5) if row == 0 else 0)

        btns = ttk.Frame(panel, style="Panel.TFrame")
        btns.pack(anchor="w", pady=(16, 0))
        ttk.Button(btns, text=self.tx("이 단계 완료", "Complete Step"), style="Primary.TButton", command=self.complete_shift_step).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text=self.tx("처음부터 다시", "Restart"), command=self.reset_shift).pack(side="left")

        timeline = self.panel(padding=18)
        ttk.Label(timeline, text=self.tx("전체 타임라인", "Full Timeline"), style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        timeline_grid = tk.Frame(timeline, bg=COLORS["panel"])
        timeline_grid.pack(fill="x")
        for col in range(2):
            timeline_grid.columnconfigure(col, weight=1, uniform="timeline_columns")
        for i, item in enumerate(SHIFT_EVENTS):
            marker = self.tx("완료", "Done") if i < self.shift_index else (self.tx("현재", "Now") if i == self.shift_index else self.tx("대기", "Queued"))
            color = COLORS["success"] if i < self.shift_index else (COLORS["accent"] if i == self.shift_index else COLORS["muted"])
            row_index, col_index = divmod(i, 2)
            row = tk.Frame(timeline_grid, bg=COLORS["panel_alt"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=8, pady=6)
            row.grid(row=row_index, column=col_index, sticky="ew", padx=(0, 4) if col_index == 0 else (4, 0), pady=3)
            tk.Label(row, text=marker, bg=COLORS["panel_alt"], fg=color, width=5, anchor="w", font=FONT_CHIP).pack(side="left")
            tk.Label(row, text=f"{item['time']}  {item['title']}", bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=310, justify="left", anchor="w").pack(side="left", fill="x", expand=True)

    def _draw_shift_board(self, canvas, width):
        canvas.delete("all")
        width = max(int(width), 620)
        canvas.create_rectangle(0, 0, width, 255, fill=COLORS["panel"], outline="")
        canvas.create_text(28, 30, text="Live Shift Board", fill=COLORS["ink"], font=FONT_SECTION, anchor="w")
        canvas.create_text(28, 58, text=self.tx("현재 단계와 놓치면 위험한 업무를 한 화면에서 봅니다.", "See the current stage and high-risk missed tasks in one view."), fill=COLORS["muted"], font=FONT_SMALL, anchor="w")

        start_x = 34
        rail_y = 112
        rail_w = width - 92
        self.rounded_rect(canvas, start_x, rail_y - 8, start_x + rail_w, rail_y + 8, 8, fill="#dfe5ee", outline="")
        if SHIFT_EVENTS:
            progress_steps = max(len(SHIFT_EVENTS) - 1, 1)
            progress_units = progress_steps if self.shift_index >= len(SHIFT_EVENTS) else min(self.shift_index, progress_steps)
            progress_w = int(rail_w * progress_units / progress_steps)
            if progress_w:
                self.rounded_rect(canvas, start_x, rail_y - 8, start_x + max(progress_w, 16), rail_y + 8, 8, fill=COLORS["primary"], outline="")
        for index, event in enumerate(SHIFT_EVENTS):
            x = start_x + int(rail_w * index / max(len(SHIFT_EVENTS) - 1, 1))
            fill = COLORS["success"] if index < self.shift_index else (COLORS["accent"] if index == self.shift_index else "#ffffff")
            outline = COLORS["success"] if index < self.shift_index else (COLORS["accent"] if index == self.shift_index else COLORS["line"])
            canvas.create_oval(x - 13, rail_y - 13, x + 13, rail_y + 13, fill=fill, outline=outline, width=3)
            if index in (0, 2, 4, 6, 8, 9):
                canvas.create_text(x, rail_y + 34, text=event["time"], fill=COLORS["muted"], font=FONT_SMALL)

        current = SHIFT_EVENTS[min(self.shift_index, len(SHIFT_EVENTS) - 1)] if self.shift_index < len(SHIFT_EVENTS) else SHIFT_EVENTS[-1]
        cards = [
            (self.tx("현재", "Current"), f"{current['time']} {current['title']}", COLORS["soft_blue"]),
            (self.tx("우선순위", "Priority"), "unstable vitals / new orders / pending meds", COLORS["soft_orange"]),
            (self.tx("넘길 정보", "Handoff"), "abnormal labs / last PRN / discharge barrier", COLORS["soft_lavender"]),
        ]
        for i, (label, body, color) in enumerate(cards):
            card_gap = 14
            card_w = max(250, int((width - 56 - card_gap * 2) / 3))
            x = 28 + i * (card_w + card_gap)
            self.rounded_rect(canvas, x, 160, x + card_w, 232, 14, fill=color, outline=COLORS["card_border"], width=1)
            canvas.create_text(x + 14, 178, text=label, fill=COLORS["ink"], font=FONT_SMALL_BOLD, anchor="w")
            canvas.create_text(x + 14, 198, text=body, fill=COLORS["ink"], font=FONT_SMALL, anchor="nw", width=card_w - 28)

    def complete_shift_step(self):
        self.shift_index += 1
        self.show_page("shift")

    def reset_shift(self):
        global SHIFT_EVENTS
        SHIFT_EVENTS = select_shift_events(SHIFT_EVENT_POOL)
        self.shift_index = 0
        self.show_page("shift")

    def _render_quests(self):
        self.page_title(
            self.tx("스테이션 실습", "Station Practice"),
            self.tx("구역별로 실제 병동에서 마주칠 판단을 고르고, 안전 흐름과 비교합니다.", "Choose decisions you will face by ward zone and compare them with the safe workflow."),
        )
        filters = self.panel(padding=14)
        filter_header = tk.Frame(filters, bg=COLORS["panel"])
        filter_header.pack(fill="x", pady=(0, 8))
        ttk.Label(filter_header, text=self.tx("오늘 연습 필터", "Today's practice filters"), style="CardTitle.TLabel").pack(side="left")
        ttk.Button(filter_header, text=self.tx("새 문항 뽑기", "Draw new items"), command=self.reroll_quests).pack(side="right")
        ttk.Label(filters, text=self.tx("구역", "Zone"), style="Muted.TLabel").pack(anchor="w", pady=(0, 4))
        zone_grid = tk.Frame(filters, bg=COLORS["panel"])
        zone_grid.pack(fill="x")
        station_names = [self.all_station_label()] + list(WARD_ZONES.keys())
        for index, station in enumerate(station_names):
            label = self.all_station_label() if station == self.all_station_label() else WARD_ZONES[station]["korean"]
            style = "Primary.TButton" if station == self.quest_station.get() else "TButton"
            row, col = divmod(index, 4)
            zone_grid.columnconfigure(col, weight=1, uniform="quest_zones")
            ttk.Button(zone_grid, text=label, style=style, command=lambda value=station: self.set_quest_station(value)).grid(row=row, column=col, sticky="ew", padx=(0, 5) if col < 3 else 0, pady=(0, 5))

        ttk.Label(filters, text=self.tx("역량", "Skill"), style="Muted.TLabel").pack(anchor="w", pady=(5, 4))
        skill_grid = tk.Frame(filters, bg=COLORS["panel"])
        skill_grid.pack(fill="x")
        for index, (skill_key, label) in enumerate(self.quest_skill_options()):
            selected_skill = self.quest_skill.get() == skill_key
            button = tk.Button(
                skill_grid,
                text=label,
                command=lambda value=skill_key: self.set_quest_skill(value),
                bg=COLORS["primary"] if selected_skill else COLORS["panel_alt"],
                fg="#ffffff" if selected_skill else COLORS["muted"],
                activebackground=COLORS["primary_dark"] if selected_skill else COLORS["panel_alt"],
                activeforeground="#ffffff" if selected_skill else COLORS["ink"],
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                font=FONT_CHIP,
                padx=9,
                pady=5,
            )
            row, col = divmod(index, 4)
            skill_grid.columnconfigure(col, weight=1, uniform="quest_skills")
            button.grid(row=row, column=col, sticky="ew", padx=(0, 5) if col < 3 else 0, pady=(0, 5))
        self._render_role_selector(filters, "quests")

        console = self.panel(padding=0)
        quest_canvas = tk.Canvas(console, height=160, bg=COLORS["panel"], highlightthickness=0)
        quest_canvas.pack(fill="x")
        self._draw_quest_console(quest_canvas, 900)
        quest_canvas.bind("<Configure>", lambda event: self._draw_quest_console(event.widget, event.width))

        feedback = self.panel(padding=14)
        ttk.Label(feedback, textvariable=self.quest_feedback, style="Panel.TLabel", wraplength=860, justify="left").pack(anchor="w")
        tk.Label(feedback, text=self.compact_variation_note(), bg=COLORS["soft_gray"], fg=COLORS["ink"], font=FONT_CHIP, padx=10, pady=5).pack(anchor="w", pady=(8, 0))

        selected = self.quest_station.get()
        selected_skill = self.quest_skill.get()
        visible_questions = [
            (index, q)
            for index, q in enumerate(QUESTIONS)
            if (selected == self.all_station_label() or q["station"] == selected)
            and (selected_skill == "all" or selected_skill in self.question_skill_tags(q))
            and self.question_matches_role(q, self.practice_role.get())
        ]
        random.shuffle(visible_questions)
        draw_limit = 5 if selected == self.all_station_label() else 4
        total_available = len(visible_questions)
        visible_questions = visible_questions[:draw_limit]
        panel = self.panel(padding=20)
        ttk.Label(
            panel,
            text=self.tx(
                f"오늘 세트: 총 {total_available}개 중 {len(visible_questions)}개만 뽑았습니다. 짧게 풀고 바로 피드백을 확인하세요.",
                f"Today set: {len(visible_questions)} items drawn from {total_available}. Keep it short and review feedback right away.",
            ),
            style="Muted.TLabel",
            wraplength=980,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))
        self.quest_vars = []
        if not visible_questions:
            tk.Label(
                panel,
                text=self.tx("현재 필터에 맞는 문항이 없습니다. 구역 또는 역량 필터를 넓혀주세요.", "No items match this filter. Broaden the zone or skill filter."),
                bg=COLORS["soft_orange"],
                fg=COLORS["ink"],
                font=FONT_BOLD,
                padx=12,
                pady=10,
                wraplength=980,
                justify="left",
            ).pack(fill="x")
        for visible_index, (question_index, q) in enumerate(visible_questions):
            group = tk.Frame(panel, bg=COLORS["panel_alt"], highlightthickness=2, highlightbackground=COLORS["card_border"])
            group.pack(fill="x", pady=(0, 14))
            header = tk.Frame(group, bg=COLORS["panel_alt"])
            header.pack(fill="x", padx=14, pady=(12, 4))
            tk.Label(header, text=f"{visible_index + 1}", bg=COLORS["primary"], fg="#ffffff", font=FONT_SMALL_BOLD, width=3).pack(side="left", padx=(0, 8))
            tk.Label(header, text=q["title"], bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_CARD_TITLE).pack(side="left")
            tk.Label(header, text=WARD_ZONES[q["station"]]["korean"], bg=WARD_ZONES[q["station"]]["color"], fg=COLORS["ink"], font=FONT_CHIP, padx=8, pady=2).pack(side="right")
            tag_row = tk.Frame(group, bg=COLORS["panel_alt"])
            tag_row.pack(fill="x", padx=14, pady=(0, 6))
            skill_labels = dict(self.quest_skill_options())
            for tag in sorted(self.question_skill_tags(q)):
                tk.Label(tag_row, text=skill_labels.get(tag, tag), bg=COLORS["soft_cyan"], fg=COLORS["ink"], font=FONT_CHIP, padx=7, pady=2).pack(side="left", padx=(0, 5))
            tk.Label(tag_row, text=self.role_label(), bg=COLORS["soft_gray"], fg=COLORS["primary"], font=FONT_CHIP, padx=7, pady=2).pack(side="left", padx=(0, 5))
            body = tk.Frame(group, bg=COLORS["panel_alt"])
            body.pack(fill="x", padx=14, pady=(4, 10))
            station = WARD_ZONES[q["station"]]
            photo = self.photo_tile(
                body,
                self.zone_photo_key(q["station"]),
                title=station["korean"],
                bg=COLORS["panel"],
                max_width=260,
                max_height=230,
            )
            photo.grid(row=0, column=0, sticky="nw", padx=(0, 12))
            right_flow = tk.Frame(body, bg=COLORS["panel_alt"])
            right_flow.grid(row=0, column=1, sticky="nsew")
            body.columnconfigure(1, weight=1)
            cue = tk.Frame(right_flow, bg=COLORS["panel_alt"])
            cue.pack(fill="x", pady=(0, 8))
            cue.columnconfigure(0, weight=1)
            for cue_index, (title, cue_body, color, icon_key) in enumerate(
                [
                    (self.tx("멈춤 포인트", "Pause Point"), q["title"], COLORS["soft_gold"], "icon_safety"),
                    (self.tx("공간 신호", "Space Signal"), station["common_calls"][0], station["color"], self.zone_icon_key(q["station"])),
                    (self.tx("판단", "Decision"), self.tx("다음 RN 행동 선택", "Choose the next RN action"), COLORS["soft_blue"], "icon_handoff"),
                ]
            ):
                card = tk.Frame(cue, bg=color, highlightthickness=1, highlightbackground=COLORS["card_border"], padx=8, pady=6)
                card.grid(row=cue_index, column=0, sticky="ew", pady=(0, 5) if cue_index < 2 else 0)
                icon = self.icon_image(icon_key, 22)
                if icon:
                    tk.Label(card, image=icon, bg=color).pack(side="left", padx=(0, 6), anchor="n")
                text_box = tk.Frame(card, bg=color)
                text_box.pack(side="left", fill="x", expand=True)
                tk.Label(text_box, text=title, bg=color, fg=COLORS["muted"], font=FONT_CHIP).pack(anchor="w")
                tk.Label(text_box, text=self.clean_text(cue_body), bg=color, fg=COLORS["ink"], font=FONT_SMALL, wraplength=500, justify="left").pack(anchor="w")
            tk.Label(right_flow, text=self.clean_text(q["prompt"]), bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_BOLD, wraplength=500, justify="left").pack(anchor="w", pady=(0, 8))
            var = tk.IntVar(value=-1)
            self.quest_vars.append((question_index, var))
            choice_buttons = []
            for original_choice_index, choice in shuffled_indexed_choices(q["choices"], q["answer"]):
                button = self.choice_button(
                    right_flow,
                    text=choice,
                    command=lambda: None,
                    bg=COLORS["panel"],
                    active=WARD_ZONES[q["station"]]["color"],
                    font=FONT_SMALL,
                    wraplength=500,
                )
                button.configure(
                    command=lambda target=var, value=original_choice_index, selected_button=button, buttons=choice_buttons, selected_bg=WARD_ZONES[q["station"]]["color"]: self.mark_choice_selection(
                        target,
                        value,
                        selected_button,
                        buttons,
                        selected_bg,
                    )
                )
                choice_buttons.append(button)
                button.pack(fill="x", anchor="w", pady=4)
            tk.Frame(group, height=8, bg=COLORS["panel_alt"]).pack(fill="x")
        ttk.Button(panel, text=self.tx("현재 문항 정답 확인", "Check Current Answers"), style="Primary.TButton", command=self.check_quests).pack(anchor="w", pady=(4, 0))

    def _draw_quest_console(self, canvas, width):
        canvas.delete("all")
        width = max(int(width), 620)
        canvas.create_rectangle(0, 0, width, 160, fill=COLORS["panel"], outline="")
        canvas.create_text(26, 30, text="Station Decision Console", fill=COLORS["ink"], font=FONT_SECTION, anchor="w")
        canvas.create_text(26, 58, text=self.tx("투약실, 병실, 스테이션, 인수인계 허브에서 실제로 멈춰야 하는 판단만 모았습니다.", "Focused decision pauses from med room, patient rooms, station, and handoff."), fill=COLORS["muted"], font=FONT_SMALL, anchor="w")
        station_counts = {}
        for question in QUESTIONS:
            station_counts[question["station"]] = station_counts.get(question["station"], 0) + 1
        stations = list(station_counts.items())
        gap = 7
        card_w = (width - 56 - gap * max(len(stations) - 1, 0)) / max(len(stations), 1)
        x = 28
        y = 92
        for station, count in stations:
            color = WARD_ZONES[station]["color"]
            canvas.create_rectangle(x, y, x + card_w, y + 54, fill=color, outline=COLORS["card_border"], width=1)
            canvas.create_text(x + 9, y + 9, text=WARD_ZONES[station]["korean"], fill=COLORS["ink"], font=FONT_CHIP, anchor="nw", width=card_w - 16)
            canvas.create_text(x + 9, y + 34, text=f"{count} tasks", fill=COLORS["muted"], font=FONT_CHIP, anchor="nw", width=card_w - 16)
            x += card_w + gap

    def set_quest_station(self, station):
        self.quest_station.set(station)
        self.quest_feedback.set(self.tx("구역이 바뀌었습니다. 현재 보이는 문항만 채점합니다.", "Zone changed. Only visible items will be scored."))
        self.show_page("quests")

    def set_quest_skill(self, skill):
        self.quest_skill.set(skill)
        self.quest_feedback.set(self.tx("역량 필터가 바뀌었습니다. 현재 보이는 문항만 채점합니다.", "Skill filter changed. Only visible items will be scored."))
        self.show_page("quests")

    def reroll_quests(self):
        self.quest_feedback.set(self.tx("랜덤 문항 세트를 새로 뽑았습니다. 현재 보이는 문항만 채점합니다.", "A new random item set has been drawn. Only visible items will be scored."))
        self.show_page("quests")

    def check_quests(self):
        if not self.quest_vars:
            messagebox.showinfo(self.tx("문항 없음", "No Items"), self.tx("현재 필터에 문항이 없습니다. 필터를 넓힌 뒤 다시 시도해주세요.", "No items match the current filter. Broaden the filter and try again."))
            return
        unanswered = [i for i, (_question_index, var) in enumerate(self.quest_vars) if var.get() < 0]
        if unanswered:
            messagebox.showinfo(self.tx("아직 남은 문항", "Unanswered Items"), self.tx("모든 문항을 선택한 뒤 확인해주세요.", "Please answer every visible item first."))
            return
        correct = 0
        review = []
        for question_index, var in self.quest_vars:
            q = QUESTIONS[question_index]
            is_correct = var.get() == q["answer"]
            correct += 1 if is_correct else 0
            if not is_correct:
                review.append(f"{q['title']}: {q['feedback']}")
        total = len(self.quest_vars)
        if review:
            self.quest_feedback.set(self.tx(f"{correct}/{total}개가 안전 흐름과 맞았습니다. 다시 볼 포인트: ", f"{correct}/{total} choices matched the safe workflow. Review: ") + " / ".join(review[:3]) + "\n" + self.compact_variation_note())
        else:
            self.quest_feedback.set(self.tx(f"{correct}/{total}개 모두 안전 흐름과 맞았습니다. 다른 구역 필터로 넘어가도 좋습니다.", f"All {correct}/{total} choices matched the safe workflow. Try another zone filter.") + "\n" + self.compact_variation_note())
        messagebox.showinfo(self.tx("스테이션 실습 결과", "Station Practice Result"), self.tx(f"{correct}/{total}개 선택이 안전 흐름과 일치했습니다.", f"{correct}/{total} choices matched the safe workflow."))

    def _render_scenarios(self):
        self.page_title(
            self.tx("환자 케이스", "Patient Cases"),
            self.tx(f"{len(SCENARIOS)}개 병동 상황에서 RN의 다음 행동을 선택합니다.", f"Choose the next RN action in {len(SCENARIOS)} ward situations."),
        )
        console = self.panel(padding=0)
        scenario_canvas = tk.Canvas(console, height=142, bg=COLORS["panel"], highlightthickness=0)
        scenario_canvas.pack(fill="x")
        self._draw_scenario_console(scenario_canvas, 900)
        scenario_canvas.bind("<Configure>", lambda event: self._draw_scenario_console(event.widget, event.width))

        panel = self.panel(padding=20)
        top = ttk.Frame(panel, style="Panel.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text=self.tx("케이스 선택", "Choose Case"), style="CardTitle.TLabel").pack(side="left", padx=(0, 10))
        combo = ttk.Combobox(top, textvariable=self.scenario_name, values=list(SCENARIOS.keys()), state="readonly", width=34)
        combo.pack(side="left", padx=(0, 8))
        ttk.Button(top, text=self.tx("시작/초기화", "Start / Reset"), style="Primary.TButton", command=self.start_scenario).pack(side="left")
        ttk.Button(top, text=self.tx("랜덤 케이스", "Random Case"), command=self.random_scenario).pack(side="left", padx=(8, 0))
        self.scenario_area = ttk.Frame(panel, style="Panel.TFrame")
        self.scenario_area.pack(fill="x", pady=(16, 0))
        self._render_current_scenario()

    def _draw_scenario_console(self, canvas, width):
        canvas.delete("all")
        width = max(int(width), 620)
        canvas.create_rectangle(0, 0, width, 142, fill=COLORS["panel"], outline="")
        canvas.create_text(26, 30, text="Case Library", fill=COLORS["ink"], font=FONT_SECTION, anchor="w")
        canvas.create_text(width - 26, 30, text=f"{len(SCENARIOS)} CASES", fill=COLORS["primary"], font=FONT_SMALL_BOLD, anchor="e")
        canvas.create_text(26, 58, text=self.tx("활력징후 변화, 투약 지연, 격리, 낙상, 퇴원 지연, 가족 전화까지 병동에서 자주 만나는 갈림길을 다룹니다.", "Practice common ward forks: vital changes, med delays, isolation, falls, discharge delays, and family calls."), fill=COLORS["muted"], font=FONT_SMALL, anchor="w", width=width - 52)
        tags = [
            ("Assessment", COLORS["soft_blue"]),
            ("Medication", COLORS["soft_orange"]),
            ("Escalation", COLORS["soft_lavender"]),
            ("Handoff", COLORS["soft_green"]),
            ("Discharge", COLORS["soft_gold"]),
        ]
        gap = 8
        card_w = (width - 56 - gap * (len(tags) - 1)) / len(tags)
        x = 28
        for label, color in tags:
            canvas.create_rectangle(x, 96, x + card_w, 130, fill=color, outline=COLORS["card_border"], width=1)
            canvas.create_text(x + card_w / 2, 113, text=label, fill=COLORS["ink"], font=FONT_SMALL_BOLD, width=card_w - 10)
            x += card_w + gap

    def start_scenario(self):
        self.scenario_step = 0
        self.scenario_score = 0
        self._render_current_scenario()

    def random_scenario(self):
        self.scenario_name.set(random.choice(list(SCENARIOS.keys())))
        self.start_scenario()

    def _render_current_scenario(self):
        if not hasattr(self, "scenario_area"):
            return
        for child in self.scenario_area.winfo_children():
            child.destroy()
        scenario = SCENARIOS[self.scenario_name.get()]
        patient_card = tk.Frame(self.scenario_area, bg=COLORS["panel_alt"], highlightthickness=2, highlightbackground=COLORS["card_border"])
        patient_card.pack(fill="x", pady=(0, 14))
        case_top = tk.Frame(patient_card, bg=COLORS["panel_alt"])
        case_top.pack(fill="x", padx=14, pady=12)
        patient_photo = self.scaled_image("photo_patient_room", 180, 110)
        if patient_photo:
            tk.Label(case_top, image=patient_photo, bg=COLORS["panel_alt"], highlightthickness=1, highlightbackground=COLORS["card_border"]).pack(side="left", padx=(0, 12), anchor="n")
        case_text = tk.Frame(case_top, bg=COLORS["panel_alt"])
        case_text.pack(side="left", fill="both", expand=True)
        tk.Label(case_text, text=self.scenario_name.get(), bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_CARD_TITLE).pack(anchor="w")
        tk.Label(case_text, text=self.clean_text(scenario["patient"]), bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_NORMAL, wraplength=700, justify="left").pack(anchor="w", pady=(4, 3))
        tk.Label(case_text, text=self.clean_text(scenario["goals"]), bg=COLORS["panel_alt"], fg=COLORS["muted"], font=FONT_SMALL, wraplength=700, justify="left").pack(anchor="w")
        if self.scenario_step >= len(scenario["steps"]):
            ttk.Label(
                self.scenario_area,
                text=self.tx(f"완료: {self.scenario_score}/{len(scenario['steps'])}개 선택이 안전한 흐름과 일치했습니다.", f"Complete: {self.scenario_score}/{len(scenario['steps'])} choices matched the safe workflow."),
                style="CardTitle.TLabel",
            ).pack(anchor="w", pady=(6, 10))
            ttk.Label(self.scenario_area, text=self.tx("디브리핑 질문: 어떤 정보가 부족했을 때 가장 불안했나요?", "Debrief question: What missing information made you most uneasy?"), style="Panel.TLabel").pack(anchor="w")
            self._schedule_responsive_wraps(update_all=True)
            return

        step = scenario["steps"][self.scenario_step]
        cue_board = tk.Frame(self.scenario_area, bg=COLORS["panel"])
        cue_board.pack(fill="x", pady=(0, 12))
        cue_items = [
            (self.tx("지금 보이는 변화", "Current Change"), self.clean_text(step["prompt"]), COLORS["soft_orange"], "icon_safety"),
            (self.tx("위험 렌즈", "Risk Lens"), self.risk_lens(scenario["patient"] + " " + scenario["goals"] + " " + step["prompt"]), COLORS["soft_lavender"], "icon_handoff"),
        ]
        for col, (title, body, color, icon_key) in enumerate(cue_items):
            cue_board.columnconfigure(col, weight=1)
            card = self._cue_card(cue_board, title, body, color, icon_key, icon_size=20, wraplength=360)
            card.grid(row=0, column=col, sticky="new", padx=(0, 5) if col == 0 else (5, 0), pady=(0, 4))

        ttk.Label(self.scenario_area, text=f"Step {self.scenario_step + 1}", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(self.scenario_area, text=step["prompt"], style="Panel.TLabel", wraplength=860, justify="left").pack(anchor="w", pady=(4, 10))
        for choice_text, is_correct in shuffled_bool_choices(step["choices"]):
            self.choice_button(
                self.scenario_area,
                text=choice_text,
                command=lambda ok=is_correct, feedback=step["feedback"]: self.answer_scenario(ok, feedback),
                bg=COLORS["panel_alt"],
                font=FONT_NORMAL,
                wraplength=840,
            ).pack(fill="x", anchor="w", pady=4)
        self._schedule_responsive_wraps(update_all=True)

    def answer_scenario(self, is_correct, feedback):
        if is_correct:
            self.scenario_score += 1
        messagebox.showinfo(self.tx("피드백", "Feedback"), self.with_variation_note(feedback))
        self.scenario_step += 1
        self._render_current_scenario()

    def _render_sbar(self):
        self.page_title(
            self.tx("SBAR 트레이너", "SBAR Trainer"),
            self.tx("Provider call이나 handoff를 Situation, Background, Assessment, Recommendation/Request로 정리합니다.", "Organize provider calls and handoff using Situation, Background, Assessment, Recommendation/Request."),
        )
        panel = self.panel(padding=20)
        self._render_safety_notice(panel)
        compare = tk.Frame(panel, bg=COLORS["panel"])
        compare.pack(fill="x", pady=(0, 14))
        compare.columnconfigure(0, weight=1)
        compare.columnconfigure(1, weight=3)
        samples = [
            (
                self.tx("부족한 보고", "Weak report"),
                "Doctor, patient looks bad.",
                COLORS["soft_orange"],
            ),
            (
                self.tx("더 나은 시작", "Stronger opening"),
                "This is RN Kim on 4 West calling about room 412 with new shortness of breath. O2 sat is 86% on 2 L NC.",
                COLORS["soft_green"],
            ),
        ]
        for col, (title, body, color) in enumerate(samples):
            card = tk.Frame(compare, bg=COLORS["panel"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=0, pady=0)
            card.grid(row=0, column=col, sticky="nsew", padx=(0, 6) if col == 0 else (6, 0))
            tk.Frame(card, bg=color, height=4).pack(fill="x")
            inner = tk.Frame(card, bg=COLORS["panel"], padx=14, pady=12)
            inner.pack(fill="both", expand=True)
            tk.Label(inner, text=title, bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w")
            tk.Label(inner, text=self.clean_text(body), bg=COLORS["panel"], fg=COLORS["muted"], font=FONT_NORMAL, wraplength=180 if col == 0 else 520, justify="left").pack(anchor="w", pady=(4, 0))
        self.sbar_fields = {}
        labels = [
            (
                "Situation",
                self.tx("현재 문제가 무엇인지 한 문장으로", "State the current problem in one sentence"),
                "This is RN Lee on 4 West calling about room 412 with new shortness of breath.",
            ),
            (
                "Background",
                self.tx("관련 진단, 병력, 현재 치료, 핵심 lab/vitals", "Relevant diagnosis, history, current treatment, key labs/vitals"),
                "Admitted for CHF exacerbation, on 2 L NC, telemetry, IV diuretics.",
            ),
            (
                "Assessment",
                self.tx("내가 걱정하는 이유와 현재 assessment", "Why you are concerned and your current assessment"),
                "O2 sat is 86-89%, RR 26, increased crackles, looks more dyspneic.",
            ),
            (
                "Recommendation/Request",
                self.tx("필요한 action, timeframe, repeat-back 요청", "Needed action, timeframe, and read-back request"),
                "Could you evaluate now or give next steps? I will repeat vitals and read back orders.",
            ),
        ]
        for key, hint, example in labels:
            ttk.Label(panel, text=key, style="CardTitle.TLabel").pack(anchor="w", pady=(4, 2))
            ttk.Label(panel, text=hint, style="Muted.TLabel").pack(anchor="w")
            tk.Label(
                panel,
                text=self.tx("예시: ", "Example: ") + example,
                bg=COLORS["panel_alt"],
                fg=COLORS["muted"],
                font=FONT_CHIP,
                padx=10,
                pady=5,
                wraplength=980,
                justify="left",
            ).pack(fill="x", pady=(4, 0))
            text = self.modern_textbox(panel, height=2)
            text.pack(fill="x", pady=(4, 10))
            if self.sbar_draft.get(key):
                text.insert("1.0", self.sbar_draft[key])
            self.sbar_fields[key] = text
        btns = ttk.Frame(panel, style="Panel.TFrame")
        btns.pack(anchor="w", pady=(2, 10))
        ttk.Button(btns, text=self.tx("예시 채우기", "Fill Sample"), command=self.fill_sbar_sample).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text=self.tx("SBAR 생성", "Generate SBAR"), style="Primary.TButton", command=self.generate_sbar).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text=self.tx("클립보드 복사", "Copy to Clipboard"), command=self.copy_sbar).pack(side="left")
        ttk.Label(panel, text=self.tx("생성 결과", "Generated Output"), style="CardTitle.TLabel").pack(anchor="w", pady=(8, 4))
        self.sbar_output = self.modern_textbox(panel, height=5)
        self.sbar_output.pack(fill="x")
        if self.sbar_output_draft:
            self.sbar_output.insert("1.0", self.sbar_output_draft)
        self.sbar_quality_frame = tk.Frame(panel, bg=COLORS["panel"])
        self.sbar_quality_frame.pack(fill="x", pady=(12, 0))
        if self.sbar_output_draft and any(self.sbar_draft.values()):
            self.render_sbar_quality(self.sbar_draft)

    def fill_sbar_sample(self):
        sample = {
            "Situation": "This is RN Lee on 4 West calling about Mr. Kim in room 412. He is reporting increased shortness of breath.",
            "Background": "He was admitted for CHF exacerbation, currently on 2 L nasal cannula, telemetry monitoring, and IV diuretics.",
            "Assessment": "His oxygen saturation is now 89% on 2 L, respiratory rate is 26, and he has increased crackles compared with this morning.",
            "Recommendation/Request": "Could you evaluate him now or provide next steps? I can increase oxygen per protocol if appropriate and will repeat vitals.",
        }
        for key, value in sample.items():
            self.sbar_fields[key].delete("1.0", "end")
            self.sbar_fields[key].insert("1.0", value)

    def generate_sbar(self):
        values = {}
        sections = []
        for key in ["Situation", "Background", "Assessment", "Recommendation/Request"]:
            value = self.sbar_fields[key].get("1.0", "end").strip()
            values[key] = value
            sections.append(f"{key}: {value or self.tx('[작성 필요]', '[Needs entry]')}")
        result = "\n".join(sections)
        self.sbar_output.delete("1.0", "end")
        self.sbar_output.insert("1.0", result)
        self.render_sbar_quality(values)

    def sbar_quality_checks(self, values):
        combined = " ".join(values.values()).lower()
        situation = values.get("Situation", "").lower()
        assessment = values.get("Assessment", "").lower()
        request = values.get("Recommendation/Request", "").lower()
        return [
            (
                self.tx("호출자/병동/방 번호가 보입니다.", "Caller/unit/room are clear."),
                bool(re.search(r"\broom\b|\brm\b|\d{3,4}|호|병실|west|unit|ward", situation)),
                self.tx("예: RN Lee on 4 West calling about room 412", "Example: RN Lee on 4 West calling about room 412"),
            ),
            (
                self.tx("현재 문제가 한 문장으로 드러납니다.", "The current problem is explicit."),
                len(situation.split()) >= 8,
                self.tx("처음 10초 안에 왜 전화했는지 말합니다.", "State why you are calling within the first 10 seconds."),
            ),
            (
                self.tx("vitals/lab/객관적 단서가 포함됩니다.", "Vitals/labs/objective cues are included."),
                bool(re.search(r"\d|sat|bp|hr|rr|temp|lactate|glucose|oxygen|vital|lab|spo2|혈압|산소|맥박", assessment + " " + combined)),
                self.tx("숫자 하나라도 넣으면 provider가 우선순위를 잡기 쉽습니다.", "Even one number helps the provider triage priority."),
            ),
            (
                self.tx("요청 action과 timeframe이 있습니다.", "The requested action and timeframe are present."),
                any(word in request for word in ["now", "evaluate", "order", "recommend", "come", "call back", "next step", "stat", "urgent", "지금", "평가", "처방", "요청"]),
                self.tx("Could you evaluate now? 처럼 원하는 다음 행동을 말합니다.", "Say the next action you need, such as Could you evaluate now?"),
            ),
            (
                self.tx("read-back/clarify 의도가 보입니다.", "Read-back or clarify intent is visible."),
                any(word in combined for word in ["read back", "repeat", "clarify", "확인", "반복", "다시"]),
                self.tx("미국 병동에서는 모호하면 clarify/read-back이 안전 행동입니다.", "Clarify/read-back is a safe action when communication is unclear."),
            ),
        ]

    def render_sbar_quality(self, values):
        if not hasattr(self, "sbar_quality_frame"):
            return
        for child in self.sbar_quality_frame.winfo_children():
            child.destroy()
        ttk.Label(self.sbar_quality_frame, text=self.tx("SBAR 품질 체크", "SBAR Quality Check"), style="CardTitle.TLabel").pack(anchor="w", pady=(0, 6))
        for title, passed, tip in self.sbar_quality_checks(values):
            color = COLORS["soft_green"] if passed else COLORS["soft_orange"]
            status = self.tx("OK", "OK") if passed else self.tx("보완", "Review")
            row = tk.Frame(self.sbar_quality_frame, bg=color, highlightthickness=1, highlightbackground=COLORS["card_border"], padx=10, pady=8)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=status, bg=color, fg=COLORS["ink"], font=FONT_CHIP, width=8).pack(side="left", anchor="n")
            text_box = tk.Frame(row, bg=color)
            text_box.pack(side="left", fill="x", expand=True)
            tk.Label(text_box, text=title, bg=color, fg=COLORS["ink"], font=FONT_SMALL_BOLD, wraplength=860, justify="left").pack(anchor="w")
            if not passed:
                tk.Label(text_box, text=tip, bg=color, fg=COLORS["muted"], font=FONT_SMALL, wraplength=860, justify="left").pack(anchor="w", pady=(2, 0))
        self._schedule_responsive_wraps(update_all=True)

    def copy_sbar(self):
        text = self.sbar_output.get("1.0", "end").strip()
        if not text:
            self.generate_sbar()
            text = self.sbar_output.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo(self.tx("복사 완료", "Copied"), self.tx("SBAR 내용이 클립보드에 복사되었습니다.", "SBAR content has been copied to the clipboard."))

    def english_topics_for_mode(self):
        mode = self.english_mode.get()
        if mode in ENGLISH_STUDY_TOPICS:
            return ENGLISH_STUDY_TOPICS[mode]
        return ENGLISH_STUDY_TOPICS["daily"] + ENGLISH_STUDY_TOPICS["nursing"]

    def english_mode_title(self, mode=None):
        mode = mode or self.english_mode.get()
        labels = {
            "daily": self.tx("일상 대화", "Daily Conversation"),
            "nursing": self.tx("간호 업무 영어", "Nursing Workflow English"),
            "mixed": self.tx("랜덤 혼합", "Mixed Random"),
        }
        return labels.get(mode, labels["mixed"])

    def set_english_mode(self, mode):
        self.english_mode.set(mode)
        self.english_drill.set("")
        self.show_page("english")

    def reroll_english_study(self):
        self.english_drill.set("")
        self.show_page("english")

    def _render_english(self):
        self.page_title(
            self.tx("영어 연습", "English Practice"),
            self.tx(
                "미국에 가는 한국 RN을 위해 일상 대화와 병동 업무 영어를 단어/문장 단위로 랜덤 연습합니다.",
                "Random word and sentence practice for daily life and U.S. nursing workflow.",
            ),
        )
        topics = self.english_topics_for_mode()
        all_words = [(topic["topic"], *word) for topic in topics for word in topic["words"]]
        all_sentences = [(topic["topic"], *sentence) for topic in topics for sentence in topic["sentences"]]
        random.shuffle(all_words)
        random.shuffle(all_sentences)
        word_sample = all_words[:6]
        sentence_sample = all_sentences[:4]
        topic_sample = random.sample(topics, min(3, len(topics)))
        drill_sentence = random.choice(all_sentences)
        if not self.english_drill.get():
            self.english_drill.set(drill_sentence[1])

        controls = self.panel(padding=16)
        ttk.Label(controls, text=self.tx("연습 모드", "Practice Mode"), style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        mode_buttons = ttk.Frame(controls, style="Panel.TFrame")
        mode_buttons.pack(fill="x")
        for mode in ["daily", "nursing", "mixed"]:
            style = "Primary.TButton" if self.english_mode.get() == mode else "TButton"
            ttk.Button(mode_buttons, text=self.english_mode_title(mode), style=style, command=lambda value=mode: self.set_english_mode(value)).pack(side="left", padx=(0, 6))
        ttk.Button(mode_buttons, text=self.tx("랜덤 다시 뽑기", "Draw Again"), style="Primary.TButton", command=self.reroll_english_study).pack(side="right")

        summary = self.panel(padding=18)
        intro = self.tx(
            "영어 자신감이 낮아도 괜찮습니다. 미국 병동에서는 유창함보다 천천히 확인하고, 다시 말하고, 필요한 순간에 정확히 요청하는 영어가 더 안전합니다.",
            "Confidence can be low. In a U.S. unit, safe English is often less about fluency and more about clarifying, reading back, and asking for the right help.",
        )
        ttk.Label(summary, text=self.english_mode_title(), style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(summary, text=intro, style="Panel.TLabel", wraplength=800, justify="left").pack(anchor="w", pady=(6, 10))
        count_text = self.tx(
            f"오늘 세트: 단어 {len(word_sample)}개, 문장 {len(sentence_sample)}개. 전체 풀은 {len(all_words) + len(all_sentences)}개입니다.",
            f"Today set: {len(word_sample)} words and {len(sentence_sample)} sentences from a {len(all_words) + len(all_sentences)}-card pool.",
        )
        tk.Label(summary, text=count_text, bg=COLORS["soft_blue"], fg=COLORS["ink"], font=FONT_SMALL_BOLD, padx=10, pady=6).pack(anchor="w")

        drill = self.panel(padding=18)
        ttk.Label(drill, text=self.tx("말하기 드릴", "Speaking Drill"), style="CardTitle.TLabel").pack(anchor="w")
        topic, phrase, meaning, usage = drill_sentence
        phrase_card = tk.Frame(drill, bg=COLORS["panel"], highlightthickness=1, highlightbackground=COLORS["card_border"])
        phrase_card.pack(fill="x", pady=(8, 6))
        tk.Frame(phrase_card, bg=COLORS["accent"], height=4).pack(fill="x")
        tk.Label(phrase_card, text=phrase, bg=COLORS["panel"], fg=COLORS["ink"], font=FONT_SECTION, padx=14, pady=12, anchor="w", justify="left", wraplength=980).pack(fill="x")
        tk.Label(drill, text=f"{meaning}  ·  {usage}", bg=COLORS["panel"], fg=COLORS["muted"], font=FONT_NORMAL, anchor="w", justify="left", wraplength=980).pack(anchor="w")
        tk.Label(
            drill,
            text=self.tx(
                "연습법: 1번은 천천히 읽고, 2번은 환자/동료에게 말하듯 읽고, 3번은 한국어 뜻만 보고 말해보세요.",
                "Practice: read it slowly once, say it as if speaking to a patient/coworker once, then say it from the meaning only.",
            ),
            bg=COLORS["panel"],
            fg=COLORS["ink"],
            font=FONT_SMALL,
            padx=10,
            pady=8,
            highlightthickness=1,
            highlightbackground=COLORS["card_border"],
            wraplength=980,
            justify="left",
        ).pack(fill="x", pady=(10, 0))

        outer = ttk.Frame(self.page.inner, style="Page.TFrame")
        outer.pack(fill="x", padx=28, pady=8)
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)

        word_outer, word_panel = self._card_shell(outer, padding=18)
        word_outer.grid(row=0, column=0, sticky="new", padx=(0, 8))
        ttk.Label(word_panel, text=self.tx("오늘의 단어", "Today's Words"), style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        for topic, word, meaning, example in word_sample:
            card = tk.Frame(word_panel, bg=COLORS["panel_alt"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=10, pady=8)
            card.pack(fill="x", pady=4)
            top = tk.Frame(card, bg=COLORS["panel_alt"])
            top.pack(fill="x")
            tk.Label(top, text=word, bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(side="left")
            tk.Label(top, text=topic, bg=COLORS["soft_cyan"], fg=COLORS["ink"], font=FONT_CHIP, padx=6, pady=2).pack(side="right")
            tk.Label(card, text=meaning, bg=COLORS["panel_alt"], fg=COLORS["muted"], font=FONT_SMALL).pack(anchor="w", pady=(2, 0))
            tk.Label(card, text=example, bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL, wraplength=520, justify="left").pack(anchor="w", pady=(2, 0))

        sentence_outer, sentence_panel = self._card_shell(outer, padding=18)
        sentence_outer.grid(row=0, column=1, sticky="new", padx=(8, 0))
        ttk.Label(sentence_panel, text=self.tx("오늘의 문장", "Today's Sentences"), style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        for topic, phrase, meaning, usage in sentence_sample:
            card = tk.Frame(sentence_panel, bg=COLORS["panel_alt"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=10, pady=8)
            card.pack(fill="x", pady=4)
            tk.Label(card, text=phrase, bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL_BOLD, wraplength=620, justify="left").pack(anchor="w")
            tk.Label(card, text=meaning, bg=COLORS["panel_alt"], fg=COLORS["muted"], font=FONT_SMALL, wraplength=620, justify="left").pack(anchor="w", pady=(2, 0))
            tk.Label(card, text=usage, bg=COLORS["soft_lavender"], fg=COLORS["ink"], font=FONT_CHIP, padx=6, pady=2).pack(anchor="w", pady=(5, 0))

        library = self.panel(padding=18)
        ttk.Label(library, text=self.tx("토픽 라이브러리", "Topic Library"), style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        grid = tk.Frame(library, bg=COLORS["panel"])
        grid.pack(fill="x")
        for index, topic in enumerate(topic_sample):
            row, col = divmod(index, 3)
            grid.columnconfigure(col, weight=1)
            color = [COLORS["soft_blue"], COLORS["soft_green"], COLORS["soft_orange"], COLORS["soft_lavender"], COLORS["soft_gold"], COLORS["soft_cyan"]][index % 6]
            card = tk.Frame(grid, bg=color, highlightthickness=1, highlightbackground=COLORS["card_border"], padx=12, pady=10)
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            tk.Label(card, text=topic["topic"], bg=color, fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w")
            tk.Label(card, text=topic["focus"], bg=color, fg=COLORS["ink"], font=FONT_SMALL, wraplength=330, justify="left").pack(anchor="w", pady=(4, 0))

    def _render_checklists(self):
        self.page_title(
            self.tx("체크리스트 & 디브리핑", "Checklists & Debrief"),
            self.tx("시뮬레이션 운영 중 관찰 포인트를 체크하고, 세션 노트를 파일로 저장할 수 있습니다.", "Check observation points during simulation and save session notes."),
        )
        panel = self.panel(padding=20)
        self._render_safety_notice(panel)
        self.check_vars = {}
        self.checklist_progress_labels = {}
        self.check_var_state_keys = {}
        for group_index, (title, items) in enumerate(CHECKLISTS.items()):
            group = tk.Frame(panel, bg=COLORS["panel_alt"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=14, pady=12)
            group.pack(fill="x", pady=(0, 14))
            header = tk.Frame(group, bg=COLORS["panel_alt"])
            header.pack(fill="x", pady=(0, 8))
            tk.Label(header, text=title, bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_CARD_TITLE).pack(side="left")
            progress_label = tk.Label(header, text="", bg=COLORS["soft_cyan"], fg=COLORS["ink"], font=FONT_CHIP, padx=8, pady=3)
            progress_label.pack(side="right")
            self.checklist_progress_labels[title] = (progress_label, len(items))
            for item_index, item in enumerate(items):
                state_key = (group_index, item_index)
                display_key = f"{title}|{item}"
                var = tk.BooleanVar(value=self.checklist_state.get(state_key, False))
                self.check_vars[display_key] = var
                self.check_var_state_keys[display_key] = state_key
                self.modern_checkbox(group, item, var, wraplength=920, on_change=self.update_checklist_progress).pack(fill="x", pady=4)
        self.update_checklist_progress()

        ttk.Label(panel, text=self.tx("디브리핑 메모", "Debrief Notes"), style="CardTitle.TLabel").pack(anchor="w", pady=(6, 4))
        self.debrief_note_fields = {}
        prompts = [
            ("missed_cues", self.tx("놓친 단서", "Missed Cues"), self.tx("예: 산소포화도 하락보다 discharge 준비에 먼저 신경 썼다.", "Example: I focused on discharge prep before the falling O2 saturation.")),
            ("first_check", self.tx("다음번에 먼저 확인할 것", "First Thing To Check Next Time"), self.tx("예: room number, code status, allergy, latest vitals.", "Example: room number, code status, allergy, latest vitals.")),
            ("hard_sentence", self.tx("말하기 어려웠던 영어 문장", "Hard Sentence To Say"), self.tx("예: Could you clarify the order and I will read it back?", "Example: Could you clarify the order and I will read it back?")),
            ("escalation_moment", self.tx("escalate해야 했던 순간", "Moment To Escalate"), self.tx("예: 새 호흡곤란, chest pain, acute neuro change.", "Example: new shortness of breath, chest pain, acute neuro change.")),
        ]
        notes_grid = tk.Frame(panel, bg=COLORS["panel"])
        notes_grid.pack(fill="x")
        for index, (key, title, hint) in enumerate(prompts):
            row, col = divmod(index, 2)
            notes_grid.columnconfigure(col, weight=1)
            card = tk.Frame(notes_grid, bg=COLORS["panel_alt"], highlightthickness=1, highlightbackground=COLORS["card_border"], padx=12, pady=10)
            card.grid(row=row, column=col, sticky="nsew", padx=(0, 6) if col == 0 else (6, 0), pady=6)
            tk.Label(card, text=title, bg=COLORS["panel_alt"], fg=COLORS["ink"], font=FONT_SMALL_BOLD).pack(anchor="w")
            tk.Label(card, text=hint, bg=COLORS["panel_alt"], fg=COLORS["muted"], font=FONT_SMALL, wraplength=350, justify="left", anchor="w").pack(anchor="w", pady=(2, 6))
            text = self.modern_textbox(card, height=4)
            text.pack(fill="x")
            if self.debrief_drafts.get(key):
                text.insert("1.0", self.debrief_drafts[key])
            self.debrief_note_fields[key] = (title, text)
        btns = ttk.Frame(panel, style="Panel.TFrame")
        btns.pack(anchor="w", pady=(12, 0))
        ttk.Button(btns, text=self.tx("세션 노트 저장", "Save Session Notes"), style="Primary.TButton", command=self.save_session_notes).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text=self.tx("체크/메모 초기화", "Reset Checks/Notes"), command=self.reset_checklist_notes).pack(side="left")

    def update_checklist_progress(self):
        if not getattr(self, "checklist_progress_labels", None):
            return
        for title, (label, total) in self.checklist_progress_labels.items():
            checked = sum(1 for key, var in self.check_vars.items() if key.startswith(f"{title}|") and var.get())
            pct = int((checked / max(total, 1)) * 100)
            label.configure(text=self.tx(f"{checked}/{total} 완료 · {pct}%", f"{checked}/{total} done · {pct}%"))

    def reset_checklist_notes(self):
        for var in self.check_vars.values():
            var.set(False)
        self.checklist_state = {}
        self.debrief_drafts = {}
        for _title, text in getattr(self, "debrief_note_fields", {}).values():
            text.delete("1.0", "end")
        self.update_checklist_progress()
        self.show_page("checklists")
        messagebox.showinfo(self.tx("초기화 완료", "Reset Complete"), self.tx("체크와 디브리핑 메모를 비웠습니다.", "Checks and debrief notes have been cleared."))

    def save_session_notes(self):
        default_name = f"us-ward-session-notes-{datetime.now().strftime('%Y%m%d-%H%M')}.txt"
        path = filedialog.asksaveasfilename(
            title=self.tx("세션 노트 저장", "Save Session Notes"),
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        checked = []
        for key, var in self.check_vars.items():
            if var.get():
                title, item = key.split("|", 1)
                checked.append(f"[{title}] {item}")
        debrief_notes = []
        for key, (title, text) in getattr(self, "debrief_note_fields", {}).items():
            body = text.get("1.0", "end").strip()
            if body:
                debrief_notes.append(f"[{title}] {body}")
        if not debrief_notes and hasattr(self, "debrief_text"):
            body = self.debrief_text.get("1.0", "end").strip()
            if body:
                debrief_notes.append(body)
        content = [
            APP_TITLE,
            self.tx(APP_SUBTITLE, "U.S. ward workflow simulator for Korean nurses"),
            f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            self.variation_note(),
            self.tx("실제 환자 이름, MRN, 생년월일, 병원명, 전화번호, 사진 등 식별 가능한 정보는 저장하지 마세요.", "Do not save real patient names, MRNs, DOBs, facility names, phone numbers, photos, or other identifiers."),
            "",
            "Completed checklist items:",
            "\n".join(f"- {item}" for item in checked) if checked else "- None",
            "",
            "Debrief notes:",
            "\n\n".join(debrief_notes) if debrief_notes else "- None",
        ]
        with open(path, "w", encoding="utf-8") as file:
            file.write("\n".join(content))
        messagebox.showinfo(self.tx("저장 완료", "Saved"), self.tx(f"세션 노트를 저장했습니다.\n{path}", f"Session notes saved.\n{path}"))

    def _render_guide(self):
        self.page_title(
            self.tx("운영 가이드", "Facilitator Guide"),
            self.tx("강사가 프로그램을 운영할 때 사용할 기본 세션 구성과 안전 안내입니다.", "Basic session structure and safety notes for facilitators."),
        )
        notice = self.panel(padding=18)
        ttk.Label(notice, text=self.tx("Pre-brief 필수 문구", "Required Pre-brief Language"), style="CardTitle.TLabel").pack(anchor="w")
        self.bullet_list(
            notice,
            (
                [
                    "본 프로그램은 공식 NCLEX 대비 프로그램이 아니며 NCSBN, 미국 병원, 고용기관과 무관한 개인 제작 교육용 시뮬레이션입니다.",
                    "실제 의료 조언, 진단, 처방, 병원 policy, 주별 간호법을 대체하지 않습니다.",
                    "실제 환자 이름, MRN, 생년월일, 병원명, 전화번호, 사진, 검사결과 등 식별 가능한 정보를 입력하지 않습니다.",
                    "모든 사례와 병동 지도는 합성 mock data이며, 실제 facility마다 workflow와 protocol은 달라질 수 있습니다.",
                ]
                if not self.is_english()
                else [
                    "This is an unofficial educational simulation, not an NCLEX prep product and not affiliated with NCSBN, any U.S. hospital, or employer.",
                    "It does not replace medical advice, diagnosis, orders, facility policy, or state nursing law.",
                    "Do not enter real patient names, MRNs, DOBs, facility names, phone numbers, photos, lab results, or other identifiers.",
                    "All cases and unit maps use synthetic mock data; workflow and protocols vary by facility.",
                ]
            ),
            wraplength=860,
        )
        left, right = self.two_columns()
        self.label_block(
            left,
            self.tx("기본형 3시간", "Standard 3-hour session"),
            self.tx("병동 투어 40%, 역할 기반 시뮬레이션 40%, 디브리핑/Q&A 20%로 구성합니다.", "Use 40% ward tour, 40% role-based simulation, and 20% debrief/Q&A."),
        )
        self.bullet_list(
            left,
            (
                [
                    "0:00-0:10 Pre-brief: 목표, 역할, 안전한 학습 분위기",
                    "0:10-0:35 Virtual Ward Tour",
                    "0:35-1:00 Nurse Station Orientation",
                    "1:00-1:30 Medication & Supply Quest",
                    "1:30-2:10 Admission Simulation",
                    "2:10-2:40 Day Shift Shadowing",
                    "2:40-3:00 Debrief/Q&A",
                ]
                if not self.is_english()
                else [
                    "0:00-0:10 Pre-brief: goals, roles, psychologically safe practice",
                    "0:10-0:35 Virtual Ward Tour",
                    "0:35-1:00 Nurse Station Orientation",
                    "1:00-1:30 Medication & Supply Quest",
                    "1:30-2:10 Admission Simulation",
                    "2:10-2:40 Day Shift Shadowing",
                    "2:40-3:00 Debrief/Q&A",
                ]
            ),
            wraplength=360,
        )
        self.label_block(
            right,
            self.tx("운영 주의사항", "Facilitation Notes"),
            self.tx("실제 환자 정보와 실제 약물은 사용하지 않고, 모든 chart와 medication은 mock data로 진행합니다.", "Use no real patient information or real medication; all charts and meds are mock data."),
        )
        self.bullet_list(
            right,
            (
                [
                    "실제 병원 정책, state scope, facility protocol을 대체하지 않습니다.",
                    "모든 환자 사례는 가상 환자로 구성합니다.",
                    "Medication은 mock card, 빈 vial, colored card로 대체합니다.",
                    "참가자에게 틀려도 되는 연습 공간임을 pre-brief에서 안내합니다.",
                    "EHR, staffing ratio, delegation policy는 기관마다 달라질 수 있음을 설명합니다.",
                ]
                if not self.is_english()
                else [
                    "This does not replace real hospital policy, state scope, or facility protocol.",
                    "All patient cases are fictional.",
                    "Replace medication with mock cards, empty vials, or colored cards.",
                    "Tell learners during pre-brief that this is a practice space where mistakes are expected.",
                    "EHR, staffing ratio, and delegation policy vary by facility.",
                ]
            ),
            wraplength=360,
        )

        refs = self.panel(padding=18)
        ttk.Label(refs, text=self.tx("참고 기반", "Reference Basis"), style="CardTitle.TLabel").pack(anchor="w")
        self.bullet_list(refs, REFERENCES, wraplength=860)


def self_test():
    assert len(FIRST_WEEK_DAYS) == 7
    for day in FIRST_WEEK_DAYS:
        assert day["choices"]
        assert any(choice["best"] for choice in day["choices"])
        assert day["scene"]
        assert day["cues"]
        assert all(key in choice["effect"] for choice in day["choices"] for key in FIRST_WEEK_BASE_SCORES)
    assert len(WARD_ZONES) >= 6
    assert sum(len(pool) for pool in FIRST_WEEK_DAY_POOLS) >= 70
    assert len(TOUR_MODES) >= 90
    assert len(SHIFT_EVENTS) >= 8
    assert len(SHIFT_EVENT_POOL) >= 100
    assert shift_progress_percent(1) == int((1 / max(len(SHIFT_EVENTS) - 1, 1)) * 100)
    assert shift_progress_percent(len(SHIFT_EVENTS)) == 100
    assert len(SPECIALTY_TRACKS) >= 6
    for track in SPECIALTY_TRACKS:
        assert track["name"]
        assert track["tasks"]
        assert track["risk"]
    assert len(QUESTIONS) >= 240
    assert len(SCENARIOS) >= 100
    assert sum(len(topic["words"]) for topics in ENGLISH_STUDY_TOPICS.values() for topic in topics) >= 500
    assert sum(len(topic["sentences"]) for topics in ENGLISH_STUDY_TOPICS.values() for topic in topics) >= 350
    for zone, data in WARD_ZONES.items():
        assert data["objects"]
        assert data["decisions"]
        assert any(choice[1] for choice in data["decisions"][0]["choices"])
        shuffled = shuffled_bool_choices(data["decisions"][0]["choices"])
        assert sorted(choice[0] for choice in shuffled) == sorted(choice[0] for choice in data["decisions"][0]["choices"])
        if len(shuffled) > 1:
            assert not shuffled[0][1]
    for mode in TOUR_MODES.values():
        assert mode["steps"]
        assert all(step[0] in WARD_ZONES for step in mode["steps"])
    for question in QUESTIONS:
        assert question["station"] in WARD_ZONES
        assert 0 <= question["answer"] < len(question["choices"])
        shuffled = shuffled_indexed_choices(question["choices"], question["answer"])
        assert sorted(index for index, _choice in shuffled) == list(range(len(question["choices"])))
        if len(shuffled) > 1:
            assert shuffled[0][0] != question["answer"]
    for scenario in SCENARIOS.values():
        assert scenario["steps"]
        for step in scenario["steps"]:
            assert any(choice[1] for choice in step["choices"])
            shuffled = shuffled_bool_choices(step["choices"])
            assert sorted(choice[0] for choice in shuffled) == sorted(choice[0] for choice in step["choices"])
            if len(shuffled) > 1:
                assert not shuffled[0][1]
    print("SELF_TEST_OK")


def main():
    if "--self-test" in sys.argv:
        self_test()
        return
    enable_windows_dpi_awareness()
    if "--gui-smoke" in sys.argv:
        app = WardSimulatorApp()
        app.update_idletasks()
        app.update()
        app.destroy()
        # A windowed one-file build can retain the bootloader process after Tk
        # teardown; the smoke flag is test-only, so terminate deterministically.
        os._exit(0)
    app = WardSimulatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()

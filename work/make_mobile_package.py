from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
OUTPUTS = ROOT / "outputs"
MOBILE_OUT = OUTPUTS / "USWardExperienceLab_mobile_offline"
ANDROID_OUT = OUTPUTS / "USWardExperienceLab_android_sdk"

sys.path.insert(0, str(WORK))
import us_ward_simulator as sim  # noqa: E402


ASSET_FILES = [
    "hero-banner.png",
    "hospital-ward-hero.png",
    "ward-spaces-collage.png",
    "nurse-station-photo.png",
    "med-room-photo.png",
    "patient-room-photo.png",
    "supply-room-photo.png",
    "tour-visual.png",
    "scenario-cards.png",
    "day-flow-visual.png",
    "us-ward-icon.png",
]


def compact_text(value):
    if value is None:
        return ""
    return " ".join(str(value).replace("\r", "\n").split())


def convert_choices(choices):
    converted = []
    for choice in choices:
        if isinstance(choice, dict):
            converted.append(
                {
                    "text": compact_text(choice.get("text", "")),
                    "best": bool(choice.get("best", False)),
                    "feedback": compact_text(choice.get("feedback", "")),
                }
            )
        elif isinstance(choice, (list, tuple)) and len(choice) >= 2:
            converted.append(
                {
                    "text": compact_text(choice[0]),
                    "best": bool(choice[1]),
                    "feedback": "",
                }
            )
    return converted


def build_mobile_data():
    first_week = []
    for pool in sim.FIRST_WEEK_DAY_POOLS:
        for day in pool:
            first_week.append(
                {
                    "day": day.get("day"),
                    "time": compact_text(day.get("time")),
                    "title": compact_text(day.get("title")),
                    "setting": compact_text(day.get("setting")),
                    "scene": compact_text(day.get("scene")),
                    "assignment": compact_text(day.get("assignment")),
                    "risk": compact_text(day.get("risk")),
                    "cues": [
                        {"label": compact_text(label), "text": compact_text(text)}
                        for label, text in day.get("cues", [])
                    ],
                    "choices": convert_choices(day.get("choices", [])),
                    "debrief": compact_text(day.get("debrief")),
                    "bridge": compact_text(day.get("bridge")),
                }
            )

    questions = []
    for question in sim.QUESTIONS:
        answer = int(question.get("answer", 0))
        questions.append(
            {
                "title": compact_text(question.get("title")),
                "station": compact_text(question.get("station")),
                "prompt": compact_text(question.get("prompt")),
                "choices": [
                    {
                        "text": compact_text(text),
                        "best": index == answer,
                        "feedback": compact_text(question.get("feedback")),
                    }
                    for index, text in enumerate(question.get("choices", []))
                ],
                "feedback": compact_text(question.get("feedback")),
            }
        )

    scenarios = []
    for name, scenario in sim.SCENARIOS.items():
        scenarios.append(
            {
                "name": compact_text(name),
                "patient": compact_text(scenario.get("patient")),
                "goals": compact_text(scenario.get("goals")),
                "steps": [
                    {
                        "prompt": compact_text(step.get("prompt")),
                        "choices": convert_choices(step.get("choices", [])),
                        "feedback": compact_text(step.get("feedback")),
                    }
                    for step in scenario.get("steps", [])
                ],
            }
        )

    tour_modes = []
    for name, mode in sim.TOUR_MODES.items():
        tour_modes.append(
            {
                "name": compact_text(name),
                "steps": [
                    {"zone": compact_text(zone), "task": compact_text(task)}
                    for zone, task in mode.get("steps", [])
                ],
            }
        )

    english = {}
    for mode, topics in sim.ENGLISH_STUDY_TOPICS.items():
        english[mode] = [
            {
                "topic": compact_text(topic.get("topic")),
                "focus": compact_text(topic.get("focus")),
                "words": [
                    {
                        "term": compact_text(term),
                        "meaning": compact_text(meaning),
                        "example": compact_text(example),
                    }
                    for term, meaning, example in topic.get("words", [])
                ],
                "sentences": [
                    {
                        "sentence": compact_text(sentence),
                        "meaning": compact_text(meaning),
                        "note": compact_text(note),
                    }
                    for sentence, meaning, note in topic.get("sentences", [])
                ],
            }
            for topic in topics
        ]

    return {
        "version": "0.1.0-beta-mobile",
        "counts": {
            "firstWeek": len(first_week),
            "questions": len(questions),
            "scenarios": len(scenarios),
            "tourModes": len(tour_modes),
            "englishCards": sum(
                len(topic["words"]) + len(topic["sentences"])
                for topics in english.values()
                for topic in topics
            ),
        },
        "firstWeek": first_week,
        "questions": questions,
        "scenarios": scenarios,
        "tourModes": tour_modes,
        "english": english,
    }


def build_html(data):
    app_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#0f766e">
  <link rel="manifest" href="manifest.webmanifest">
  <title>U.S. Ward Experience Lab Mobile</title>
  <style>
    :root {{
      --ink:#0f1f33; --muted:#5d7188; --line:#d6e2ef; --paper:#fffdf8;
      --bg:#edf6f9; --blue:#2563eb; --teal:#0f8f76; --coral:#ec695f;
      --gold:#ffe18a; --soft-blue:#d7ebff; --soft-green:#cbf3e1;
      --soft-coral:#ffd8cf; --soft-purple:#dfd5ff;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", sans-serif;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--ink); line-height:1.45; }}
    button {{ font:inherit; }}
    .app {{ min-height:100dvh; padding-bottom:88px; }}
    .hero {{
      position:relative; min-height:310px; padding:24px 18px; overflow:hidden;
      background:linear-gradient(90deg, rgba(255,253,248,.98) 0%, rgba(255,253,248,.9) 45%, rgba(255,253,248,.28) 100%), url("assets/hero-banner.png") center/cover no-repeat;
      border-bottom:1px solid var(--line);
    }}
    .eyebrow {{ color:var(--blue); font-size:12px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }}
    h1 {{ margin:10px 0 8px; font-size:32px; line-height:1.16; letter-spacing:0; max-width:420px; }}
    h2 {{ margin:0 0 10px; font-size:23px; line-height:1.2; }}
    h3 {{ margin:0 0 8px; font-size:18px; }}
    p {{ margin:0; }}
    .subtitle {{ max-width:420px; color:#30465f; font-size:16px; font-weight:650; }}
    .hero-actions {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:18px; }}
    .btn {{
      border:0; border-radius:14px; padding:12px 16px; min-height:44px;
      background:#e6eef7; color:var(--ink); font-weight:800;
    }}
    .btn.primary {{ background:var(--blue); color:white; }}
    .btn.teal {{ background:var(--teal); color:white; }}
    .btn.coral {{ background:var(--coral); color:white; }}
    .btn.ghost {{ background:white; border:1px solid var(--line); }}
    .stats {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin:18px 0 0; max-width:420px; }}
    .stat {{ border:1px solid var(--line); background:rgba(255,255,255,.86); padding:12px; border-radius:16px; }}
    .stat b {{ display:block; font-size:26px; line-height:1; }}
    .stat span {{ color:var(--muted); font-size:12px; font-weight:750; }}
    main {{ padding:14px; max-width:980px; margin:0 auto; }}
    section {{ display:none; }}
    section.active {{ display:block; }}
    .panel {{
      background:rgba(255,255,255,.92); border:1px solid var(--line);
      border-radius:22px; padding:16px; box-shadow:0 10px 24px rgba(27,51,76,.07);
      margin-bottom:14px;
    }}
    .visual {{
      width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:18px;
      border:1px solid var(--line); background:#e6eef7; display:block; margin:12px 0;
    }}
    .grid {{ display:grid; gap:12px; }}
    .feature {{ min-height:116px; border-radius:20px; border:1px solid var(--line); padding:15px; background:white; }}
    .feature.gold {{ background:var(--gold); }} .feature.blue {{ background:var(--soft-blue); }}
    .feature.green {{ background:var(--soft-green); }} .feature.coral {{ background:var(--soft-coral); }}
    .feature.purple {{ background:var(--soft-purple); }}
    .chips {{ display:flex; flex-wrap:wrap; gap:8px; margin:10px 0; }}
    .chip {{ padding:8px 10px; border-radius:999px; background:#edf3fb; color:#263f5e; font-weight:760; font-size:13px; }}
    .cue-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; margin:10px 0; }}
    .cue {{ background:#f4f8fc; border:1px solid var(--line); border-radius:16px; padding:10px; }}
    .cue b {{ display:block; margin-bottom:2px; }}
    .notice {{ border-radius:16px; padding:12px; background:var(--soft-coral); font-weight:680; }}
    .goal {{ border-radius:16px; padding:12px; background:var(--soft-blue); font-weight:760; }}
    .choices {{ display:grid; gap:10px; margin-top:12px; }}
    .choice {{
      width:100%; text-align:left; background:white; border:2px solid #bfd1e4;
      border-radius:16px; padding:13px; display:flex; gap:10px; align-items:flex-start;
    }}
    .choice .num {{ flex:0 0 30px; height:30px; border-radius:10px; display:grid; place-items:center; background:var(--blue); color:white; font-weight:900; }}
    .choice.selected-good {{ border-color:var(--teal); background:#eefcf8; }}
    .choice.selected-risk {{ border-color:var(--coral); background:#fff1ee; }}
    .feedback {{ margin-top:12px; padding:13px; border-radius:16px; background:#f2f7fb; border:1px solid var(--line); font-weight:680; }}
    .route {{ display:grid; gap:10px; }}
    .route-step {{ display:grid; grid-template-columns:112px 1fr; gap:10px; align-items:center; padding:10px; border:1px solid var(--line); border-radius:18px; background:#fff; }}
    .route-step img {{ width:112px; height:78px; object-fit:cover; border-radius:13px; }}
    .route-step.active {{ border-color:var(--blue); box-shadow:0 0 0 3px rgba(37,99,235,.14); }}
    .word-list, .sentence-list {{ display:grid; gap:10px; margin-top:10px; }}
    .word, .sentence {{ background:#fff; border:1px solid var(--line); border-radius:16px; padding:12px; }}
    .word b, .sentence b {{ display:block; color:var(--teal); margin-bottom:4px; }}
    .bottom-nav {{
      position:fixed; left:0; right:0; bottom:0; z-index:20; padding:8px 8px calc(8px + env(safe-area-inset-bottom));
      background:rgba(255,253,248,.96); border-top:1px solid var(--line); display:grid; grid-template-columns:repeat(6,1fr); gap:6px;
    }}
    .bottom-nav button {{ border:0; border-radius:14px; padding:9px 4px; min-height:52px; background:#edf3fb; color:#263f5e; font-size:12px; font-weight:850; }}
    .bottom-nav button.active {{ background:var(--blue); color:white; }}
    .two {{ display:grid; gap:12px; }}
    .small {{ color:var(--muted); font-size:13px; }}
    @media (min-width:720px) {{
      .hero {{ min-height:360px; padding:34px; }}
      h1 {{ font-size:46px; }}
      .stats {{ grid-template-columns:repeat(4,1fr); max-width:760px; }}
      .grid.three {{ grid-template-columns:repeat(3,1fr); }}
      .two {{ grid-template-columns:1fr 1fr; }}
    }}
  </style>
</head>
<body>
<div class="app">
  <header class="hero">
    <div class="eyebrow">U.S. Ward Simulation · Mobile</div>
    <h1>미국 병동 첫 7일<br>실전 적응 시뮬레이션</h1>
    <p class="subtitle">NCLEX 이후 미국 이민을 준비하는 한국 RN을 위한 오프라인 모바일 연습 앱입니다. 장면 단서, 선택, 디브리핑, 영어 표현을 랜덤으로 돌립니다.</p>
    <div class="hero-actions">
      <button class="btn teal" onclick="showTab('first')">첫 7일 시작</button>
      <button class="btn primary" onclick="showTab('station')">스테이션 실습</button>
      <button class="btn coral" onclick="showTab('english')">영어 연습</button>
    </div>
    <div class="stats">
      <div class="stat"><b id="count-first">70</b><span>첫 주 장면</span></div>
      <div class="stat"><b id="count-q">240</b><span>판단 과제</span></div>
      <div class="stat"><b id="count-case">111</b><span>환자 케이스</span></div>
      <div class="stat"><b id="count-eng">900+</b><span>영어 카드</span></div>
    </div>
  </header>

  <main>
    <section id="home" class="active">
      <div class="grid three">
        <button class="feature gold" onclick="showTab('first')"><h3>첫 7일</h3><p>orientation, EHR, delegation, HIPAA, escalation을 장면 단위로 경험합니다.</p></button>
        <button class="feature blue" onclick="showTab('tour')"><h3>병동 투어</h3><p>스테이션, 투약실, 병실, 물품실, 인수인계 허브의 동선을 따라갑니다.</p></button>
        <button class="feature coral" onclick="showTab('station')"><h3>스테이션 실습</h3><p>RN이 실제로 마주치는 우선순위와 커뮤니케이션 판단을 훈련합니다.</p></button>
        <button class="feature green" onclick="showTab('case')"><h3>환자 케이스</h3><p>상태 변화와 안전 리스크를 보고 다음 행동을 선택합니다.</p></button>
        <button class="feature purple" onclick="showTab('english')"><h3>영어 연습</h3><p>일상 정착 영어와 병동 업무 영어를 단어/문장 카드로 반복합니다.</p></button>
      </div>
      <div class="panel">
        <h2>Pre-brief</h2>
        <p>이 앱은 공식 NCLEX/병원 교육 프로그램이 아닙니다. 실제 절차는 주(State), facility policy, EHR/ADC, unit protocol에 따라 달라질 수 있습니다. 환자 이름, MRN, 생년월일, 병원명, 사진, 검사결과 등 식별 가능한 정보는 입력하지 마세요.</p>
      </div>
    </section>

    <section id="first">
      <div class="panel" id="first-card"></div>
    </section>

    <section id="tour">
      <div class="panel">
        <h2>병동 투어</h2>
        <p class="small">랜덤 동선을 따라가며 각 구역에서 RN이 무엇을 확인하는지 봅니다.</p>
        <img class="visual" src="assets/ward-spaces-collage.png" alt="ward collage">
        <div class="hero-actions"><button class="btn primary" onclick="newTour()">랜덤 투어</button><button class="btn ghost" onclick="advanceTour()">다음 구역</button></div>
      </div>
      <div class="panel"><div id="tour-card"></div></div>
    </section>

    <section id="station">
      <div class="panel" id="station-card"></div>
    </section>

    <section id="case">
      <div class="panel" id="case-card"></div>
    </section>

    <section id="english">
      <div class="panel">
        <h2>영어 연습</h2>
        <p class="small">일상대화와 간호업무용 표현을 랜덤으로 띄웁니다.</p>
        <div class="hero-actions">
          <button class="btn ghost" onclick="setEnglishMode('daily')">일상</button>
          <button class="btn ghost" onclick="setEnglishMode('nursing')">간호업무</button>
          <button class="btn primary" onclick="setEnglishMode('mixed')">섞기</button>
          <button class="btn teal" onclick="newEnglish()">새 카드</button>
        </div>
      </div>
      <div class="panel" id="english-card"></div>
    </section>
  </main>

  <nav class="bottom-nav">
    <button data-tab="home" class="active" onclick="showTab('home')">홈</button>
    <button data-tab="first" onclick="showTab('first')">첫 7일</button>
    <button data-tab="tour" onclick="showTab('tour')">투어</button>
    <button data-tab="station" onclick="showTab('station')">실습</button>
    <button data-tab="case" onclick="showTab('case')">케이스</button>
    <button data-tab="english" onclick="showTab('english')">영어</button>
  </nav>
</div>

<script>
const APP_DATA = __APP_DATA__;
const state = {{ tab:'home', first:null, firstChoices:[], station:null, stationChoices:[], scenario:null, scenarioStep:0, scenarioChoices:[], tour:null, tourStep:0, englishMode:'mixed', englishTopic:null }};
const zoneImages = {{
  'Nurse Station':'assets/nurse-station-photo.png',
  'Medication Room':'assets/med-room-photo.png',
  'Patient Room':'assets/patient-room-photo.png',
  'Supply Room':'assets/supply-room-photo.png',
  'Utility / Isolation':'assets/supply-room-photo.png',
  'Handoff Zone':'assets/nurse-station-photo.png'
}};
const sceneImages = {{
  orientation:'assets/hero-banner.png',
  medroom:'assets/med-room-photo.png',
  assignment:'assets/nurse-station-photo.png',
  communication:'assets/scenario-cards.png',
  default:'assets/hospital-ward-hero.png'
}};
function $(id) {{ return document.getElementById(id); }}
function rand(arr) {{ return arr[Math.floor(Math.random()*arr.length)]; }}
function shuffle(arr) {{ return [...arr].map(v=>[Math.random(),v]).sort((a,b)=>a[0]-b[0]).map(v=>v[1]); }}
function esc(s) {{ return String(s ?? '').replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch])); }}
function showTab(tab) {{
  state.tab = tab;
  document.querySelectorAll('section').forEach(s=>s.classList.toggle('active', s.id===tab));
  document.querySelectorAll('.bottom-nav button').forEach(b=>b.classList.toggle('active', b.dataset.tab===tab));
  if(tab==='first' && !state.first) newFirst();
  if(tab==='station' && !state.station) newStation();
  if(tab==='case' && !state.scenario) newScenario();
  if(tab==='tour' && !state.tour) newTour();
  if(tab==='english' && !state.englishTopic) newEnglish();
  window.scrollTo({{top:0, behavior:'smooth'}});
}}
function initCounts() {{
  $('count-first').textContent = APP_DATA.counts.firstWeek;
  $('count-q').textContent = APP_DATA.counts.questions;
  $('count-case').textContent = APP_DATA.counts.scenarios;
  $('count-eng').textContent = APP_DATA.counts.englishCards;
}}
function newFirst() {{
  state.first = rand(APP_DATA.firstWeek);
  state.firstChoices = shuffle(state.first.choices);
  renderFirst();
}}
function renderFirst(feedback='') {{
  const d = state.first;
  const img = sceneImages[d.scene] || sceneImages.default;
  $('first-card').innerHTML = `
    <div class="eyebrow">${esc(d.time)}</div>
    <h2>${esc(d.title)}</h2>
    <img class="visual" src="${img}" alt="scene visual">
    <div class="goal">${esc(d.assignment)}</div>
    <p style="margin-top:10px">${esc(d.setting)}</p>
    <div class="cue-grid">${d.cues.map(c=>`<div class="cue"><b>${esc(c.label)}</b><span>${esc(c.text)}</span></div>`).join('')}</div>
    <div class="notice">${esc(d.risk)}</div>
    <div class="choices">${state.firstChoices.map((c,i)=>`<button class="choice" onclick="chooseFirst(${i})"><span class="num">${i+1}</span><span>${esc(c.text)}</span></button>`).join('')}</div>
    ${feedback}
    <div class="hero-actions"><button class="btn primary" onclick="newFirst()">다른 장면</button><button class="btn ghost" onclick="showTab('station')">스테이션 연결</button></div>
  `;
}}
function chooseFirst(index) {{
  const c = state.firstChoices[index];
  const msg = `<div class="feedback"><b>${c.best ? '좋은 선택' : '위험 신호'}</b><br>${esc(c.feedback || state.first.debrief)}<br><br>${esc(state.first.debrief)}</div>`;
  renderFirst(msg);
  document.querySelectorAll('#first-card .choice')[index].classList.add(c.best ? 'selected-good' : 'selected-risk');
}}
function newStation() {{
  state.station = rand(APP_DATA.questions);
  state.stationChoices = shuffle(state.station.choices);
  renderStation();
}}
function renderStation(feedback='') {{
  const q = state.station;
  $('station-card').innerHTML = `
    <div class="eyebrow">${esc(q.station)}</div>
    <h2>${esc(q.title)}</h2>
    <img class="visual" src="${zoneImages[q.station] || 'assets/tour-visual.png'}" alt="station visual">
    <p>${esc(q.prompt)}</p>
    <div class="choices">${state.stationChoices.map((c,i)=>`<button class="choice" onclick="chooseStation(${i})"><span class="num">${i+1}</span><span>${esc(c.text)}</span></button>`).join('')}</div>
    ${feedback}
    <div class="hero-actions"><button class="btn primary" onclick="newStation()">새 과제</button><button class="btn ghost" onclick="showTab('case')">케이스 연결</button></div>
  `;
}}
function chooseStation(index) {{
  const c = state.stationChoices[index];
  const msg = `<div class="feedback"><b>${c.best ? '정답 흐름' : '다시 생각하기'}</b><br>${esc(c.feedback || state.station.feedback)}</div>`;
  renderStation(msg);
  document.querySelectorAll('#station-card .choice')[index].classList.add(c.best ? 'selected-good' : 'selected-risk');
}}
function newScenario() {{
  state.scenario = rand(APP_DATA.scenarios.filter(s=>s.steps.length));
  state.scenarioStep = 0;
  state.scenarioChoices = shuffle(state.scenario.steps[0].choices);
  renderScenario();
}}
function renderScenario(feedback='') {{
  const s = state.scenario;
  const step = s.steps[state.scenarioStep];
  $('case-card').innerHTML = `
    <div class="eyebrow">Patient Case · ${state.scenarioStep+1}/${s.steps.length}</div>
    <h2>${esc(s.name)}</h2>
    <img class="visual" src="assets/patient-room-photo.png" alt="patient room">
    <div class="two">
      <div class="cue"><b>환자 단서</b>${esc(s.patient)}</div>
      <div class="cue"><b>현재 목표</b>${esc(s.goals)}</div>
    </div>
    <h3 style="margin-top:14px">${esc(step.prompt)}</h3>
    <div class="choices">${state.scenarioChoices.map((c,i)=>`<button class="choice" onclick="chooseScenario(${i})"><span class="num">${i+1}</span><span>${esc(c.text)}</span></button>`).join('')}</div>
    ${feedback}
    <div class="hero-actions"><button class="btn primary" onclick="nextScenarioStep()">다음 단계</button><button class="btn ghost" onclick="newScenario()">새 케이스</button></div>
  `;
}}
function chooseScenario(index) {{
  const c = state.scenarioChoices[index];
  const step = state.scenario.steps[state.scenarioStep];
  const msg = `<div class="feedback"><b>${c.best ? '안전한 판단' : '리스크 있음'}</b><br>${esc(step.feedback)}</div>`;
  renderScenario(msg);
  document.querySelectorAll('#case-card .choice')[index].classList.add(c.best ? 'selected-good' : 'selected-risk');
}}
function nextScenarioStep() {{
  if (!state.scenario) return newScenario();
  state.scenarioStep = (state.scenarioStep + 1) % state.scenario.steps.length;
  state.scenarioChoices = shuffle(state.scenario.steps[state.scenarioStep].choices);
  renderScenario();
}}
function newTour() {{
  state.tour = rand(APP_DATA.tourModes);
  state.tourStep = 0;
  renderTour();
}}
function advanceTour() {{
  if(!state.tour) return newTour();
  state.tourStep = (state.tourStep + 1) % state.tour.steps.length;
  renderTour();
}}
function renderTour() {{
  const t = state.tour;
  $('tour-card').innerHTML = `
    <div class="eyebrow">${esc(t.name)}</div>
    <h2>RN 동선 따라가기</h2>
    <div class="route">${t.steps.map((step,i)=>`<div class="route-step ${i===state.tourStep?'active':''}"><img src="${zoneImages[step.zone] || 'assets/tour-visual.png'}" alt=""><div><b>${i+1}. ${esc(step.zone)}</b><p>${esc(step.task)}</p></div></div>`).join('')}</div>
  `;
}}
function englishTopics() {{
  if (state.englishMode === 'daily') return APP_DATA.english.daily;
  if (state.englishMode === 'nursing') return APP_DATA.english.nursing;
  return APP_DATA.english.daily.concat(APP_DATA.english.nursing);
}}
function setEnglishMode(mode) {{
  state.englishMode = mode;
  newEnglish();
}}
function newEnglish() {{
  state.englishTopic = rand(englishTopics());
  renderEnglish();
}}
function renderEnglish() {{
  const topic = state.englishTopic;
  const words = shuffle(topic.words).slice(0, 5);
  const sentences = shuffle(topic.sentences).slice(0, 4);
  $('english-card').innerHTML = `
    <div class="eyebrow">${state.englishMode === 'nursing' ? 'Nursing English' : state.englishMode === 'daily' ? 'Daily English' : 'Mixed English'}</div>
    <h2>${esc(topic.topic)}</h2>
    <p>${esc(topic.focus)}</p>
    <h3 style="margin-top:14px">단어</h3>
    <div class="word-list">${words.map(w=>`<div class="word"><b>${esc(w.term)}</b><span>${esc(w.meaning)}</span><p class="small">${esc(w.example)}</p></div>`).join('')}</div>
    <h3 style="margin-top:14px">문장</h3>
    <div class="sentence-list">${sentences.map(s=>`<div class="sentence"><b>${esc(s.sentence)}</b><span>${esc(s.meaning)}</span><p class="small">${esc(s.note)}</p></div>`).join('')}</div>
  `;
}}
initCounts();
if ('serviceWorker' in navigator) navigator.serviceWorker.register('service-worker.js').catch(()=>{{}});
</script>
</body>
</html>
"""
    template = template.replace("{{", "{").replace("}}", "}")
    return template.replace("__APP_DATA__", app_json)


def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def copy_assets(target_assets):
    target_assets.mkdir(parents=True, exist_ok=True)
    for name in ASSET_FILES:
        source = WORK / "assets" / name
        if source.exists():
            shutil.copy2(source, target_assets / name)


def write_mobile_app(data):
    if MOBILE_OUT.exists():
        shutil.rmtree(MOBILE_OUT)
    MOBILE_OUT.mkdir(parents=True)
    copy_assets(MOBILE_OUT / "assets")
    write_text(MOBILE_OUT / "index.html", build_html(data))
    write_text(
        MOBILE_OUT / "manifest.webmanifest",
        json.dumps(
            {
                "name": "U.S. Ward Experience Lab Mobile",
                "short_name": "US Ward Lab",
                "start_url": "index.html",
                "display": "standalone",
                "background_color": "#edf6f9",
                "theme_color": "#0f766e",
                "icons": [
                    {"src": "assets/us-ward-icon.png", "sizes": "512x512", "type": "image/png"}
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    write_text(
        MOBILE_OUT / "service-worker.js",
        """const CACHE='us-ward-mobile-v1';
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll([
    './','index.html','manifest.webmanifest',
    'assets/hero-banner.png','assets/hospital-ward-hero.png','assets/ward-spaces-collage.png',
    'assets/nurse-station-photo.png','assets/med-room-photo.png','assets/patient-room-photo.png',
    'assets/supply-room-photo.png','assets/tour-visual.png','assets/scenario-cards.png','assets/us-ward-icon.png'
  ])));
});
self.addEventListener('fetch', event => {
  event.respondWith(caches.match(event.request).then(response => response || fetch(event.request)));
});
""",
    )
    write_text(
        MOBILE_OUT / "README_MOBILE.txt",
        """U.S. Ward Experience Lab Mobile Offline Preview

1. Android phone에서 index.html을 브라우저로 열어 모바일 화면을 테스트할 수 있습니다.
2. Chrome에서 '홈 화면에 추가'를 선택하면 앱처럼 실행할 수 있습니다.
3. 병동/환자 관련 실제 개인정보는 입력하지 마세요.
4. 이 패키지는 웹 배포용이 아니라 오프라인 모바일 미리보기용입니다.
""",
    )


def write_android_project(data):
    if ANDROID_OUT.exists():
        shutil.rmtree(ANDROID_OUT)
    assets_root = ANDROID_OUT / "app" / "src" / "main" / "assets"
    res_root = ANDROID_OUT / "app" / "src" / "main" / "res"
    java_root = ANDROID_OUT / "app" / "src" / "main" / "java" / "com" / "darkha123" / "uswardexperiencelab"
    write_text(ANDROID_OUT / "settings.gradle", "pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\ndependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }\nrootProject.name='USWardExperienceLabAndroid'\ninclude ':app'\n")
    write_text(
        ANDROID_OUT / "build.gradle",
        "plugins {\n    id 'com.android.application' version '8.5.2' apply false\n}\n",
    )
    write_text(
        ANDROID_OUT / "app" / "build.gradle",
        """plugins {
    id 'com.android.application'
}

android {
    namespace 'com.darkha123.uswardexperiencelab'
    compileSdk 35

    defaultConfig {
        applicationId 'com.darkha123.uswardexperiencelab'
        minSdk 23
        targetSdk 35
        versionCode 1
        versionName '0.1.0-beta-mobile'
    }
}
""",
    )
    write_text(
        ANDROID_OUT / "app" / "src" / "main" / "AndroidManifest.xml",
        """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:allowBackup="false"
        android:icon="@drawable/app_icon"
        android:label="@string/app_name"
        android:resizeableActivity="true"
        android:theme="@style/AppTheme">
        <activity
            android:name=".MainActivity"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""",
    )
    write_text(
        res_root / "values" / "strings.xml",
        """<resources>
    <string name="app_name">U.S. Ward Experience Lab</string>
</resources>
""",
    )
    write_text(
        res_root / "values" / "styles.xml",
        """<resources>
    <style name="AppTheme" parent="@android:style/Theme.Material.Light.NoActionBar">
        <item name="android:fontFamily">sans</item>
        <item name="android:windowLightStatusBar">true</item>
        <item name="android:statusBarColor">#edf6f9</item>
        <item name="android:navigationBarColor">#fffdf8</item>
    </style>
</resources>
""",
    )
    java_root.mkdir(parents=True, exist_ok=True)
    write_text(
        java_root / "MainActivity.java",
        """package com.darkha123.uswardexperiencelab;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        webView.setWebViewClient(new WebViewClient());
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        webView.loadUrl("file:///android_asset/index.html");
        setContentView(webView);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
""",
    )
    copy_assets(assets_root / "assets")
    write_text(assets_root / "index.html", build_html(data))
    (res_root / "drawable-nodpi").mkdir(parents=True, exist_ok=True)
    shutil.copy2(WORK / "assets" / "us-ward-icon.png", res_root / "drawable-nodpi" / "app_icon.png")
    write_text(
        ANDROID_OUT / "README_ANDROID_SDK.txt",
        """U.S. Ward Experience Lab Android SDK Project

목표
- 기존 Windows EXE의 핵심 콘텐츠를 모바일 세로 화면에 맞춘 Android WebView 앱으로 포장한 프로젝트입니다.
- 인터넷 연결 없이 app/src/main/assets/index.html과 assets 폴더만으로 실행됩니다.

빌드 방법
1. Android Studio 설치
2. 이 폴더(USWardExperienceLab_android_sdk)를 Open
3. Gradle Sync 완료
4. Build > Build Bundle(s) / APK(s) > Build APK(s)
5. 생성된 APK를 Android 휴대폰에 복사해 설치

주의
- 이 Codex 환경에는 Java/Gradle/Android SDK가 없어 APK 컴파일까지는 수행하지 못했습니다.
- 실제 배포 전에는 앱 서명, 버전 코드, 개인정보/면책 문구, Android target SDK 정책을 다시 확인하세요.
- 환자 식별 정보는 입력하지 않는 교육용 시뮬레이션입니다.
""",
    )


def zip_dir(source, target):
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in source.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(source.parent))


def main():
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    data = build_mobile_data()
    write_mobile_app(data)
    write_android_project(data)
    zip_dir(MOBILE_OUT, OUTPUTS / "USWardExperienceLab_mobile_offline.zip")
    zip_dir(ANDROID_OUT, OUTPUTS / "USWardExperienceLab_android_sdk_project.zip")
    print(json.dumps(data["counts"], ensure_ascii=False))
    print(MOBILE_OUT)
    print(ANDROID_OUT)


if __name__ == "__main__":
    main()

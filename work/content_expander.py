import random


def time_to_minutes(value):
    try:
        hour, minute = str(value).split(":", 1)
        return int(hour) * 60 + int(minute[:2])
    except Exception:
        return 9999


def select_shift_events(pool, count=10):
    if len(pool) <= count:
        return sorted(pool, key=lambda item: time_to_minutes(item["time"]))
    early = [item for item in pool if time_to_minutes(item["time"]) <= time_to_minutes("07:00")]
    late = [item for item in pool if time_to_minutes(item["time"]) >= time_to_minutes("18:00")]
    middle = [item for item in pool if item not in early and item not in late]
    selected = []
    if early:
        selected.append(random.choice(early))
    if late:
        selected.append(random.choice(late))
    selected.extend(random.sample(middle, min(max(0, count - len(selected)), len(middle))))
    return sorted(selected[:count], key=lambda item: time_to_minutes(item["time"]))


def select_first_week_days(pools):
    return [random.choice(pool) for pool in pools]


def build_first_week_day_pools(days, english=False):
    if english:
        focus_sets = [
            ("access and badge boundary", "badge pickup, first huddle, unit phone, privacy language"),
            ("EHR and medication safety", "MAR, allergy band, ADC, barcode, controlled substance waste"),
            ("delegation and assignment", "PCT report, call lights, RN-only assessment, follow-up ownership"),
            ("privacy and interpreter etiquette", "family phone call, public hallway, interpreter resource, authorization"),
            ("provider call and escalation", "new symptoms, vital trend, RT/charge RN, SBAR opening"),
            ("discharge pressure", "new medication teaching, ride delay, pharmacy barrier, teach-back"),
            ("readiness conversation", "preceptor feedback, unsafe assignment concern, chain of command"),
        ]
        variants = [
            ("morning version", "The scene starts during early huddle with multiple tasks arriving at once."),
            ("busy hallway version", "The scene happens while the hallway is loud and people interrupt your preceptor."),
            ("EHR-heavy version", "The scene asks you to compare what you see in the EHR with what is happening at bedside."),
            ("family communication version", "The scene adds a family question that tests privacy and boundary language."),
            ("policy variation version", "The scene highlights that another facility might do this workflow differently."),
            ("team resource version", "The scene requires deciding when to use PCT, RT, charge RN, pharmacy, or provider support."),
            ("documentation version", "The scene asks what must be charted or handed off after the action."),
            ("patient education version", "The scene includes a patient asking why the task matters."),
            ("time pressure version", "The scene adds bed flow, late medication, or a provider callback pressure."),
            ("self-advocacy version", "The scene asks you to name your limit without sounding passive."),
        ]
    else:
        focus_sets = [
            ("출입, badge, 첫 huddle 경계", "badge 수령, 첫 huddle, unit phone, privacy language"),
            ("EHR과 투약 안전", "MAR, allergy band, ADC, barcode, controlled substance waste"),
            ("위임과 assignment", "PCT report, call light, RN-only assessment, follow-up ownership"),
            ("privacy와 interpreter etiquette", "가족 전화, public hallway, interpreter resource, authorization"),
            ("provider call과 escalation", "새 증상, vital trend, RT/charge RN, SBAR opening"),
            ("퇴원 압박", "새 약 교육, ride delay, pharmacy barrier, teach-back"),
            ("readiness conversation", "preceptor feedback, unsafe assignment concern, chain of command"),
        ]
        variants = [
            ("morning version", "이 장면은 early huddle 중 여러 task가 동시에 들어오며 시작됩니다."),
            ("busy hallway version", "복도가 시끄럽고 preceptor가 계속 interruption을 받는 상황입니다."),
            ("EHR-heavy version", "EHR에 보이는 내용과 bedside에서 실제 보이는 단서를 비교해야 합니다."),
            ("family communication version", "가족 질문이 추가되어 privacy와 boundary language를 시험합니다."),
            ("policy variation version", "다른 facility라면 workflow가 달라질 수 있음을 드러내는 장면입니다."),
            ("team resource version", "PCT, RT, charge RN, pharmacy, provider 중 누구를 언제 써야 하는지 판단합니다."),
            ("documentation version", "행동 후 무엇을 charting 또는 handoff해야 하는지 묻는 장면입니다."),
            ("patient education version", "환자가 이 업무가 왜 필요한지 직접 묻는 장면입니다."),
            ("time pressure version", "bed flow, late medication, provider callback 압박이 추가됩니다."),
            ("self-advocacy version", "수동적으로 보이지 않으면서 본인의 한계를 말해야 합니다."),
        ]
    pools = []
    for index, day in enumerate(days):
        focus_title, focus_detail = focus_sets[index % len(focus_sets)]
        pool = []
        for variant_title, variant_body in variants:
            item = dict(day)
            item["title"] = f"{focus_title} - {variant_title}"
            item["setting"] = f"{focus_detail}. {variant_body}"
            item["assignment"] = ("Goal: " if english else "목표: ") + item["assignment"].replace("목표:", "").replace("Goal:", "").strip()
            item["risk"] = f"{day['risk']} {variant_body}"
            item["bridge"] = "Reset the first week to draw another randomized scene set." if english else "첫 7일을 다시 시작하면 다른 랜덤 장면 세트가 뽑힙니다."
            item["choices"] = [dict(choice) for choice in day["choices"]]
            pool.append(item)
        pools.append(pool)
    return pools


def generate_station_questions(ward_zones, english=False):
    stations = list(ward_zones.keys())
    if english:
        cues = ["new admission", "medication delay", "fall-risk request", "isolation entry", "family phone call", "provider callback", "telemetry alarm", "discharge barrier", "low glucose", "pain reassessment"]
        focus_bank = [
            ("Handoff Gap", "During {cue}, handoff has missing safety data. What is safest?", "Ask for missing safety data before accepting the workflow as complete.", "Continue because another team probably handled it.", "Document later without clarifying.", "Ask the family to decide.", "Incomplete handoff needs focused clarification."),
            ("Priority Split", "Two tasks arrive during {cue}. What should guide your first action?", "Prioritize unstable cues, then delegate appropriate routine tasks with follow-up.", "Handle the easiest task first.", "Finish charting before assessing any change.", "Ask the PCT to choose the RN priority.", "RN judgment, delegation, and follow-up accountability move together."),
            ("Privacy Boundary", "A visitor or caller asks for details during {cue}. What is safest?", "Verify authorization and share only what policy allows.", "Share everything if they sound like family.", "Avoid the conversation without a plan.", "Text the details to your personal phone.", "Communication still needs HIPAA/privacy boundaries."),
            ("Escalation Threshold", "The patient situation changes during {cue}. What is safer?", "Assess bedside, compare baseline, and escalate through the proper team channel.", "Wait for the next scheduled round.", "Assume the EHR will alert someone else.", "Only mention it at end-of-shift.", "Deterioration requires timely assessment and escalation."),
            ("Documentation Risk", "After handling {cue}, what documentation is safest?", "Document objective findings, actions, notifications, and reassessment plan.", "Write defensively about who caused it.", "Skip charting if the issue improved.", "Only tell a coworker verbally.", "Objective documentation supports continuity and risk management."),
            ("Policy Variation", "You are unsure whether {cue} follows this unit's policy. What now?", "Check facility policy or ask charge/preceptor before acting.", "Use the method from your previous hospital.", "Follow a social media tip.", "Let the next shift decide.", "Facility policy varies; safe nurses clarify local procedure."),
            ("Patient Education", "A patient asks why {cue} matters. Best RN response?", "Explain the reason in plain language and use teach-back if needed.", "Say it is just hospital policy.", "Always defer all explanation to the provider.", "Give paperwork without discussion.", "Patient education is part of RN workflow."),
            ("Team Communication", "A team member gives unclear instruction about {cue}. What is safest?", "Clarify, read back key details, and confirm task ownership.", "Pretend you understood.", "Ignore it until repeated.", "Change the plan without telling anyone.", "Clarification protects the patient and team."),
            ("Scope Check", "You are asked to handle {cue} independently while orienting. Safest action?", "Name your current scope, involve the preceptor, and proceed within policy.", "Do it alone to prove confidence.", "Refuse all participation.", "Ask another new nurse instead.", "Self-advocacy during orientation protects patients."),
        ]
    else:
        cues = ["새 입원", "투약 지연", "낙상 고위험 요청", "격리 병실 입실", "가족 전화", "provider callback", "telemetry alarm", "퇴원 barrier", "저혈당 알림", "통증 재평가"]
        focus_bank = [
            ("Handoff Gap", "{cue} 상황에서 인수인계 정보가 빠졌습니다. 안전한 행동은?", "빠진 안전 정보를 확인한 뒤 workflow를 이어간다.", "다른 팀이 처리했을 것이라 보고 넘어간다.", "나중에 charting만 한다.", "가족에게 판단을 맡긴다.", "불완전한 handoff는 focused clarification이 필요합니다."),
            ("Priority Split", "{cue} 중 두 업무가 동시에 들어왔습니다. 첫 행동의 기준은?", "불안정 단서를 먼저 사정하고 가능한 routine task는 위임 후 follow-up한다.", "가장 쉬운 일부터 처리한다.", "상태 변화보다 charting을 먼저 끝낸다.", "RN 우선순위를 PCT가 결정하게 한다.", "RN judgment, delegation, follow-up accountability가 함께 갑니다."),
            ("Privacy Boundary", "{cue} 중 보호자나 전화 상대가 환자 정보를 묻습니다. 안전한 대응은?", "authorization을 확인하고 policy 허용 범위만 공유한다.", "가족처럼 들리면 모두 알려준다.", "계획 없이 대화를 피한다.", "개인 휴대폰으로 정보를 보낸다.", "친절한 소통에도 HIPAA/privacy boundary가 필요합니다."),
            ("Escalation Threshold", "{cue} 중 환자 상태가 달라졌습니다. 안전한 다음 단계는?", "bedside assessment로 baseline과 비교하고 적절한 team channel로 escalation한다.", "다음 정규 rounding까지 기다린다.", "EHR이 누군가에게 알려줄 것이라 본다.", "교대 인수인계 때만 말한다.", "상태 악화는 timely assessment와 escalation이 필요합니다."),
            ("Documentation Risk", "{cue} 처리 후 documentation에서 가장 안전한 방식은?", "객관적 finding, action, notification, reassessment plan을 기록한다.", "누가 문제였는지 방어적으로 쓴다.", "좋아졌으면 charting을 생략한다.", "동료에게 말로만 넘긴다.", "객관적 documentation은 continuity와 risk management를 돕습니다."),
            ("Policy Variation", "{cue}가 이 병동 policy와 맞는지 확실하지 않습니다. 어떻게 할까요?", "facility policy나 charge/preceptor에게 확인한 뒤 진행한다.", "이전 병원 방식대로 한다.", "SNS에서 본 팁을 따른다.", "다음 shift가 결정하게 한다.", "미국 facility policy는 병원마다 달라 local procedure 확인이 안전합니다."),
            ("Patient Education", "환자가 {cue}가 왜 필요한지 묻습니다. RN의 좋은 대응은?", "쉬운 말로 이유를 설명하고 필요하면 teach-back으로 확인한다.", "병원 규칙이라서 그렇다고만 한다.", "항상 provider가 나중에 설명한다고 넘긴다.", "서류만 주고 끝낸다.", "Patient education은 RN workflow의 일부입니다."),
            ("Team Communication", "팀원이 {cue}에 대해 모호한 지시를 줬습니다. 안전한 행동은?", "clarify하고 핵심 내용을 read-back하며 task owner를 확인한다.", "자신 있어 보이려고 알아들은 척한다.", "누군가 다시 말할 때까지 무시한다.", "아무에게도 말하지 않고 계획을 바꾼다.", "Clarification은 환자 안전과 전문적 소통을 지킵니다."),
            ("Scope Check", "orientation 중 {cue}를 혼자 처리하라는 요청을 받았습니다. 안전한 대응은?", "현재 scope를 말하고 preceptor와 함께 policy 안에서 진행한다.", "자신감을 보이려고 혼자 한다.", "모든 참여를 거절한다.", "다른 신규 간호사에게 묻는다.", "Orientation 중 self-advocacy는 환자 안전 행동입니다."),
        ]
    generated = []
    for station in stations:
        for topic_index, topic in enumerate(focus_bank):
            title, prompt, correct, wrong1, wrong2, wrong3, feedback = topic
            for cue_index, cue in enumerate(cues[:4]):
                generated.append(
                    {
                        "title": f"{title} {cue_index + 1}",
                        "station": station,
                        "prompt": prompt.format(cue=cue),
                        "choices": [correct, wrong1, wrong2, wrong3],
                        "answer": 0,
                        "feedback": feedback,
                    }
                )
    return generated


def generate_case_scenarios(english=False):
    if english:
        topics = [
            ("Respiratory Decline", "shortness of breath with rising oxygen need", "respiratory assessment, oxygen device, provider/RT escalation"),
            ("Neuro Change", "new slurred speech or weakness", "last-known-well, glucose, neuro check, rapid escalation"),
            ("Medication Delay", "time-sensitive medication not available", "MAR check, pharmacy communication, delay documentation"),
            ("Fall Risk", "bathroom request with high fall risk", "mobility assessment, PCT teamwork, prevention plan"),
            ("Discharge Barrier", "new medication confusion and transportation delay", "teach-back, pharmacy, case manager communication"),
            ("Family Boundary", "caller asks for labs and treatment details", "authorization, privacy, callback plan"),
            ("Isolation Workflow", "rule-out infection with specimen collection", "PPE, dedicated equipment, specimen route"),
            ("Post-op Opioid Risk", "drowsiness after PRN opioid", "sedation scale, respiratory reassessment, escalation"),
            ("Sepsis Concern", "fever, tachycardia, new confusion", "trend recognition, timed tasks, reassessment"),
            ("Telemetry Alarm", "alarm plus patient symptom", "bedside assessment, rhythm context, provider call"),
            ("New Admission", "ED handoff with missing details", "room readiness, missing data, initial assessment"),
            ("Line/Device Risk", "central line or Foley concern", "device integrity, infection prevention, notification"),
        ]
        variants = ["med-surg", "telemetry", "stepdown", "ED-to-floor", "PACU-to-floor", "night shift", "weekend staffing", "new preceptor day"]
        steps = [
            ("What should you do first?", "Assess the patient, verify key cues, and identify immediate safety risk.", "Wait because the chart will update.", "Ask the family to decide.", "First action should connect bedside cues with safety risk."),
            ("What should you communicate?", "Use SBAR with baseline, current change, relevant orders, and requested next step.", "Only say the patient looks bad.", "Avoid calling because you are new.", "Structured communication makes escalation safer."),
            ("What must be handed off?", "Pending tasks, reassessment timing, notifications, and safety plan.", "Only the diagnosis.", "Nothing if the patient improved.", "Handoff should protect the next nurse's first 10 minutes."),
        ]
    else:
        topics = [
            ("호흡 악화", "산소 요구량 증가와 숨참 호소", "respiratory assessment, oxygen device, provider/RT escalation"),
            ("신경학적 변화", "갑작스러운 말 어눌함 또는 편측 약화", "last-known-well, glucose, neuro check, rapid escalation"),
            ("투약 지연", "time-sensitive medication이 available하지 않음", "MAR check, pharmacy communication, delay documentation"),
            ("낙상 위험", "고위험 환자의 화장실 요청", "mobility assessment, PCT teamwork, prevention plan"),
            ("퇴원 barrier", "새 약 혼란과 교통편 지연", "teach-back, pharmacy, case manager communication"),
            ("가족 정보 경계", "전화 상대가 lab과 치료 정보를 요구", "authorization, privacy, callback plan"),
            ("격리 workflow", "rule-out infection과 specimen collection", "PPE, dedicated equipment, specimen route"),
            ("수술 후 opioid risk", "PRN opioid 후 심한 졸림", "sedation scale, respiratory reassessment, escalation"),
            ("Sepsis concern", "발열, tachycardia, 새 confusion", "trend recognition, timed tasks, reassessment"),
            ("Telemetry alarm", "알람과 환자 증상이 같이 발생", "bedside assessment, rhythm context, provider call"),
            ("새 입원", "ED handoff에 빠진 정보가 있음", "room readiness, missing data, initial assessment"),
            ("Line/device risk", "central line 또는 Foley 관련 우려", "device integrity, infection prevention, notification"),
        ]
        variants = ["med-surg", "telemetry", "stepdown", "ED-to-floor", "PACU-to-floor", "night shift", "weekend staffing", "new preceptor day"]
        steps = [
            ("가장 먼저 할 일은?", "bedside assessment로 핵심 단서를 확인하고 즉시 위험을 분류한다.", "차트가 업데이트될 때까지 기다린다.", "가족에게 판단을 맡긴다.", "첫 행동은 bedside cue와 안전 위험을 연결해야 합니다."),
            ("어떻게 보고해야 하나요?", "baseline, 현재 변화, 관련 order, 필요한 next step을 SBAR로 말한다.", "환자가 나빠 보인다고만 말한다.", "신규라서 전화하지 않는다.", "구조화된 communication은 escalation을 안전하게 만듭니다."),
            ("무엇을 인수인계해야 하나요?", "pending task, reassessment timing, notification, safety plan을 넘긴다.", "diagnosis만 말한다.", "좋아졌으면 아무것도 넘기지 않는다.", "handoff는 다음 RN의 첫 10분을 보호해야 합니다."),
        ]
    scenarios = {}
    for name, patient_cue, goals in topics:
        for index, variant in enumerate(variants):
            scenarios[f"{name} {index + 1:02d}"] = {
                "patient": f"{variant}: {patient_cue}",
                "goals": goals,
                "steps": [
                    {"prompt": prompt, "choices": [(correct, True), (wrong1, False), (wrong2, False)], "feedback": feedback}
                    for prompt, correct, wrong1, wrong2, feedback in steps
                ],
            }
    return scenarios


def generate_tour_modes(english=False):
    route_patterns = [
        ["Nurse Station", "Medication Room", "Patient Room", "Handoff Zone"],
        ["Nurse Station", "Supply Room", "Utility / Isolation", "Patient Room"],
        ["Patient Room", "Nurse Station", "Medication Room", "Handoff Zone"],
        ["Nurse Station", "Patient Room", "Supply Room", "Handoff Zone"],
        ["Medication Room", "Patient Room", "Nurse Station", "Handoff Zone"],
        ["Patient Room", "Utility / Isolation", "Supply Room", "Nurse Station"],
    ]
    focuses = (
        ["respiratory change", "new admission", "late medication", "family privacy", "fall event", "discharge barrier", "insulin meal issue", "isolation specimen", "telemetry alarm", "post-op pain", "sepsis alert", "provider callback", "PCT delegation", "pharmacy delay", "rapid response prep"]
        if english
        else ["호흡 변화", "새 입원", "late medication", "가족 privacy", "낙상 사건", "퇴원 barrier", "insulin 식사 문제", "격리 specimen", "telemetry alarm", "수술 후 통증", "sepsis alert", "provider callback", "PCT delegation", "pharmacy delay", "rapid response 준비"]
    )
    note = "Move through the unit while deciding what cue must be handled in this zone." if english else "이 구역에서 어떤 단서를 처리해야 하는지 판단하며 동선을 이동합니다."
    return {
        (f"{focus} route {route_index + 1}" if english else f"{focus} 동선 {route_index + 1}"): {"steps": [(zone, f"{focus}: {note}") for zone in route]}
        for focus in focuses
        for route_index, route in enumerate(route_patterns)
    }


def generate_shift_event_pool(english=False):
    times = ["06:45", "07:00", "07:30", "08:00", "09:00", "10:30", "11:00", "13:00", "14:00", "15:30", "17:00", "18:00", "19:00"]
    topics = (
        [
            ("Safety huddle", "Scan assignment, high-risk patients, staffing, and admission/discharge pressure.", ["Mark isolation, fall risk, telemetry, and pending tests.", "Ask charge RN what could destabilize the shift.", "Identify which tasks can be delegated."]),
            ("Medication pass", "Connect MAR, allergies, scanner, missing meds, and reassessment timing.", ["Confirm hold parameters.", "Track late or missing medication.", "Plan PRN reassessment."]),
            ("Provider call", "Use SBAR when a patient changes or labs become abnormal.", ["State the situation in one sentence.", "Share baseline and current assessment.", "Request a clear next step."]),
            ("Family call", "Balance communication, privacy, authorization, and callback planning.", ["Verify caller identity per policy.", "Share only allowed information.", "Document concern and next plan."]),
            ("Discharge pressure", "Keep safe transition visible while the unit needs beds.", ["Check new medication education.", "Clarify ride/pharmacy barriers.", "Handoff pending discharge tasks."]),
            ("Admission alert", "Prepare the room and assessment before the patient arrives.", ["Ask ED for missing data.", "Prepare oxygen/PPE/equipment.", "Start safety screening on arrival."]),
            ("Escalation cue", "A subtle change may require bedside assessment and team notification.", ["Go to bedside.", "Compare baseline and trend.", "Notify charge/provider/RT as needed."]),
            ("End-of-shift cleanup", "Protect the next RN by organizing pending tasks and risks.", ["Review open orders.", "Mark abnormal results.", "Prepare focused handoff."]),
        ]
        if english
        else [
            ("Safety huddle", "assignment, high-risk patient, staffing, admission/discharge 압박을 스캔합니다.", ["isolation, fall risk, telemetry, pending test를 표시한다.", "charge RN에게 오늘 흔들릴 수 있는 지점을 묻는다.", "위임 가능한 task를 구분한다."]),
            ("Medication pass", "MAR, allergy, scanner, missing med, reassessment timing을 연결합니다.", ["hold parameter를 확인한다.", "late/missing medication을 추적한다.", "PRN reassessment 시간을 계획한다."]),
            ("Provider call", "상태 변화나 abnormal lab을 SBAR로 보고합니다.", ["Situation을 한 문장으로 말한다.", "baseline과 current assessment를 공유한다.", "명확한 next step을 요청한다."]),
            ("Family call", "communication, privacy, authorization, callback plan을 균형 있게 다룹니다.", ["policy에 따라 caller identity를 확인한다.", "허용 범위만 공유한다.", "concern과 다음 plan을 기록한다."]),
            ("Discharge pressure", "병상 회전 압박 속에서도 safe transition을 보이게 만듭니다.", ["새 약 교육 여부를 확인한다.", "ride/pharmacy barrier를 공유한다.", "pending discharge task를 handoff한다."]),
            ("Admission alert", "환자가 오기 전 방과 initial assessment를 준비합니다.", ["ED에서 빠진 정보를 질문한다.", "oxygen/PPE/equipment를 준비한다.", "도착 즉시 safety screening을 시작한다."]),
            ("Escalation cue", "작은 변화가 bedside assessment와 team notification을 요구할 수 있습니다.", ["bedside로 간다.", "baseline과 trend를 비교한다.", "필요 시 charge/provider/RT에 알린다."]),
            ("End-of-shift cleanup", "다음 RN의 첫 10분을 보호하도록 pending task와 risk를 정리합니다.", ["open order를 확인한다.", "abnormal result를 표시한다.", "focused handoff를 준비한다."]),
        ]
    )
    return [{"time": time_value, "title": f"{title} {topic_index + 1}", "details": detail, "actions": list(actions)} for time_value in times for topic_index, (title, detail, actions) in enumerate(topics)]


def extend_content_bundle(content, english=False):
    content["first_week_day_pools"] = build_first_week_day_pools(content["first_week_days"], english=english)
    content["questions"] = list(content["questions"]) + generate_station_questions(content["ward_zones"], english=english)
    scenarios = dict(content["scenarios"])
    scenarios.update(generate_case_scenarios(english=english))
    content["scenarios"] = scenarios
    tour_modes = dict(content["tour_modes"])
    tour_modes.update(generate_tour_modes(english=english))
    content["tour_modes"] = tour_modes
    content["shift_event_pool"] = list(content["shift_events"]) + generate_shift_event_pool(english=english)
    return content

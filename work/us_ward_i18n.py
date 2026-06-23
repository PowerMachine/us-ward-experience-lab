def build_english_content(colors):
    nav_items = [
        ("dashboard", "Home"),
        ("first7", "First 7 Days"),
        ("specialties", "Specialty Tracks"),
        ("tour", "Ward Tour"),
        ("shift", "Shift Board"),
        ("quests", "Station Practice"),
        ("scenarios", "Patient Cases"),
        ("english", "English Practice"),
        ("sbar", "SBAR"),
        ("checklists", "Checklists"),
        ("guide", "Facilitator Guide"),
    ]

    ward_zones = {
        "Nurse Station": {
            "title": "Nurse Station",
            "korean": "Nurse Station",
            "subtitle": "The command center for assignments, calls, EHR tasks, and escalation.",
            "role": "Assignments, call lights, EHR queues, provider calls, and charge RN decisions converge here.",
            "objects": [
                ("Assignment", "patients and acuity"),
                ("Call Board", "patient and family calls"),
                ("EHR Queue", "orders, labs, consults"),
                ("Charge RN", "admissions and escalation"),
            ],
            "common_calls": [
                "Room 414 reports shortness of breath",
                "ED admission ETA 25 minutes",
                "Family asking for lab results",
            ],
            "missions": [
                "Mark the safety risks for four assigned patients.",
                "Ask the charge RN about admission flow and staffing.",
                "Separate provider calls from bedside-first assessments.",
            ],
            "decisions": [
                {
                    "prompt": "Call light: Room 414 says they are short of breath. What should you do first?",
                    "choices": [
                        ("Go to the bedside and assess breathing, oxygen, and vital signs.", True),
                        ("Turn off the call and finish the medication pass first.", False),
                        ("Call the family first.", False),
                        ("Tell only the charge RN and wait.", False),
                    ],
                    "feedback": "A change in breathing needs bedside assessment, not screen-only handling.",
                }
            ],
            "color": colors["soft_blue"],
        },
        "Patient Room": {
            "title": "Patient Room",
            "korean": "Patient Room",
            "subtitle": "Where patient identification, safety checks, assessment, and education happen.",
            "role": "The room connects chart information with what you confirm in front of the patient.",
            "objects": [
                ("Whiteboard", "team, date, mobility"),
                ("Bed Safety", "low bed, locks, clutter"),
                ("Oxygen/IV", "lines, pumps, oxygen"),
                ("Call Light", "within reach"),
            ],
            "common_calls": [
                "Pain 8/10 after ambulation",
                "Needs bathroom, high fall risk",
                "Family wants a discharge update",
            ],
            "missions": [
                "Perform hand hygiene and two identifiers.",
                "Check fall risk and call-light access with the patient.",
                "Explain today's plan and ask for teach-back.",
            ],
            "decisions": [
                {
                    "prompt": "A high-fall-risk patient wants to walk to the bathroom alone. First response?",
                    "choices": [
                        ("Call for help and assess mobility and safety equipment.", True),
                        ("Tell them to hurry because you are busy.", False),
                        ("Ask the family to handle it and leave.", False),
                        ("Start discharge teaching first.", False),
                    ],
                    "feedback": "Fall prevention is shared by RN and PCT, but RN judgment remains central.",
                }
            ],
            "color": colors["soft_green"],
        },
        "Medication Room": {
            "title": "Medication Room",
            "korean": "Medication Room",
            "subtitle": "The place where errors should stop before MAR becomes medication in hand.",
            "role": "Check orders, allergies, due times, barcode workflow, high-alert meds, and waste.",
            "objects": [
                ("ADC", "Pyxis/Omnicell role"),
                ("MAR", "due time and route"),
                ("Scanner", "barcode workflow"),
                ("Waste Log", "controlled med handling"),
            ],
            "common_calls": [
                "Antibiotic not in ADC",
                "Insulin due, patient not eating",
                "High-alert med needs independent check",
            ],
            "missions": [
                "Flag time-sensitive 09:00 meds.",
                "Connect allergy, route, and dose to patient ID.",
                "Write a pharmacy message for a missing medication.",
            ],
            "decisions": [
                {
                    "prompt": "A 09:00 antibiotic is due but not in the ADC. What should you check first?",
                    "choices": [
                        ("Review MAR/order status and pharmacy dispense history.", True),
                        ("Borrow the same drug from another patient's bin.", False),
                        ("Skip this dose for today.", False),
                        ("Only tell the patient the medication is missing.", False),
                    ],
                    "feedback": "Missing medication is a system workflow: pharmacy, timing, documentation, and escalation.",
                }
            ],
            "color": colors["soft_orange"],
        },
        "Supply Room": {
            "title": "Supply Room",
            "korean": "Supply Room",
            "subtitle": "Where you prepare supplies so care does not stop at the bedside.",
            "role": "Practice PPE, dressing kits, IV start kits, specimen cups, and clean/soiled separation.",
            "objects": [
                ("PPE Cart", "gloves, gown, mask"),
                ("Dressing Kit", "wound care"),
                ("Specimen", "cup, label, bag"),
                ("Par Level", "stock and reorder"),
            ],
            "common_calls": [
                "C. diff stool sample needed",
                "Dressing change order",
                "IV site leaking",
            ],
            "missions": [
                "Pick PPE and dedicated items before entering isolation.",
                "Bundle supplies for a dressing order.",
                "Explain why clean and soiled routes must stay separate.",
            ],
            "decisions": [
                {
                    "prompt": "You need supplies for a rule-out C. diff patient. Best set?",
                    "choices": [
                        ("Gown, gloves, specimen container, dedicated equipment, and exit routine.", True),
                        ("Only a surgical mask.", False),
                        ("A shared vital machine from the hallway.", False),
                        ("Only the water cup the patient requested.", False),
                    ],
                    "feedback": "Isolation care starts before room entry: PPE, dedicated equipment, and specimen flow.",
                }
            ],
            "color": colors["soft_gold"],
        },
        "Utility / Isolation": {
            "title": "Utility / Isolation",
            "korean": "Utility / Isolation",
            "subtitle": "The boundary between clean items, soiled items, and transmission precautions.",
            "role": "Use signage, PPE, disposal, specimen handling, and clean/soiled workflow correctly.",
            "objects": [
                ("Signage", "entry routine"),
                ("Soiled Utility", "dirty linen, waste"),
                ("Clean Utility", "clean supply only"),
                ("Specimen Bag", "label and transport"),
            ],
            "common_calls": [
                "Family asks why PPE is needed",
                "Stool specimen ready",
                "Need dedicated equipment",
            ],
            "missions": [
                "Read the isolation sign before entering.",
                "Describe clean vs soiled route.",
                "Prepare a family-friendly PPE explanation.",
            ],
            "decisions": [
                {
                    "prompt": "A coworker is about to bring soiled linen into clean utility. What do you do?",
                    "choices": [
                        ("Redirect to the soiled route and briefly explain contamination risk.", True),
                        ("Ignore it because it is not your patient.", False),
                        ("Document it later without intervening.", False),
                        ("Leave it briefly in clean utility.", False),
                    ],
                    "feedback": "Clean/soiled flow is basic infection prevention and a shared team standard.",
                }
            ],
            "color": colors["soft_lavender"],
        },
        "Handoff Zone": {
            "title": "Handoff Zone",
            "korean": "Handoff Zone",
            "subtitle": "Where responsibility, risk, pending tasks, and team context transfer.",
            "role": "SBAR, bedside handoff, ED-to-floor reports, and end-of-shift summaries happen here.",
            "objects": [
                ("SBAR", "focused provider call"),
                ("Bedside Check", "ID and safety"),
                ("Pending List", "labs, orders, callbacks"),
                ("Family Concern", "privacy and follow-up"),
            ],
            "common_calls": [
                "Provider callback",
                "ED report has gaps",
                "Next RN asks what is unstable",
            ],
            "missions": [
                "Compress risk into a 60-second report.",
                "Ask for missing ED handoff data.",
                "Separate charted facts from verbal safety priorities.",
            ],
            "decisions": [
                {
                    "prompt": "Handoff only says 'stable.' What should you ask next?",
                    "choices": [
                        ("Ask baseline, recent changes, pending tests, and safety risks.", True),
                        ("No questions if they said stable.", False),
                        ("Ask about food preferences first.", False),
                        ("Tell the next RN to ask again later.", False),
                    ],
                    "feedback": "Handoff transfers responsibility; 'stable' alone is not enough.",
                }
            ],
            "color": colors["soft_blue"],
        },
    }

    tour_modes = {
        "Receiving an Admission": {
            "steps": [
                ("Nurse Station", "Receive ED handoff and check room readiness."),
                ("Supply Room", "Prepare oxygen, suction, PPE, and admission supplies."),
                ("Patient Room", "Start ID, vitals, and focused assessment on arrival."),
                ("Handoff Zone", "Close gaps and pending orders."),
            ]
        },
        "09:00 Medication Round": {
            "steps": [
                ("Nurse Station", "Review MAR and task queue."),
                ("Medication Room", "Check allergies, route, barcode, and missing meds."),
                ("Patient Room", "Use two identifiers and patient education."),
                ("Nurse Station", "Document delay reasons and reassessment times."),
            ]
        },
        "Isolation Room Entry": {
            "steps": [
                ("Nurse Station", "Confirm isolation order and testing status."),
                ("Supply Room", "Collect PPE and dedicated equipment."),
                ("Utility / Isolation", "Check signage and entry/exit routine."),
                ("Patient Room", "Explain precautions to the patient and family."),
            ]
        },
        "Discharge Preparation": {
            "steps": [
                ("Nurse Station", "Check discharge order, pharmacy, and ride barriers."),
                ("Patient Room", "Teach-back medications, wound care, and warning signs."),
                ("Supply Room", "Gather dressing supplies and education material."),
                ("Handoff Zone", "Pass unresolved barriers to the team."),
            ]
        },
        "Call Light Prioritization": {
            "steps": [
                ("Nurse Station", "Sort simultaneous calls by acuity and delegation."),
                ("Patient Room", "Assess symptoms such as SOB or chest pain first."),
                ("Nurse Station", "Delegate comfort tasks and set RN follow-up."),
                ("Handoff Zone", "Leave concise follow-up notes."),
            ]
        },
        "Acute Shortness of Breath": {
            "steps": [
                ("Nurse Station", "Check call-light context and move quickly."),
                ("Patient Room", "Assess vitals, oxygen, lungs, and mental status."),
                ("Supply Room", "Prepare oxygen-related bedside supplies."),
                ("Handoff Zone", "Organize SBAR for provider or rapid response."),
            ]
        },
        "Hypoglycemia Response": {
            "steps": [
                ("Nurse Station", "Review PCT report and glucose trend."),
                ("Patient Room", "Assess symptoms, consciousness, and meal status."),
                ("Medication Room", "Connect protocol, MAR, and insulin orders."),
                ("Handoff Zone", "Handoff recheck time and recurrent risk."),
            ]
        },
        "Post-Fall Response": {
            "steps": [
                ("Patient Room", "Assess injury, pain, mental status, and vitals before moving."),
                ("Nurse Station", "Start charge RN and provider notification."),
                ("Supply Room", "Prepare fall-prevention equipment."),
                ("Handoff Zone", "Handoff post-fall assessment and prevention plan."),
            ]
        },
        "Possible Transfusion Reaction": {
            "steps": [
                ("Patient Room", "Stop transfusion and assess symptoms and vitals."),
                ("Medication Room", "Check blood product, patient ID, and line status."),
                ("Nurse Station", "Organize provider and blood bank notification."),
                ("Handoff Zone", "Handoff suspected reaction and pending workflow."),
            ]
        },
        "Pre-Handoff Cleanup": {
            "steps": [
                ("Nurse Station", "Scan open orders, pending labs, callbacks, and discharge barriers."),
                ("Medication Room", "Check late meds, PRN reassessments, and waste documentation."),
                ("Patient Room", "Finish bedside safety and patient questions."),
                ("Handoff Zone", "Compress what the next RN needs in the first 10 minutes."),
            ]
        },
    }

    shift_events = [
        {"time": "06:45", "title": "Clock in, assignment, safety huddle", "details": "Scan night-shift events, staffing, admissions/discharges, and high-risk patients.", "actions": ["Mark room numbers and diagnoses.", "Flag fall risk, isolation, telemetry, and pending tests.", "Ask the charge RN about unit flow."]},
        {"time": "07:00", "title": "Receive handoff from night RN", "details": "Handoff transfers responsibility and priorities, not just information.", "actions": ["Confirm reason for admission and overnight events.", "Ask about lines, oxygen, abnormal labs, and drains.", "Clarify pending orders and discharge barriers."]},
        {"time": "07:30", "title": "Chart review", "details": "Use orders, labs, MAR, trends, and notes to prioritize first rounds.", "actions": ["Separate new and discontinued orders.", "Identify time-sensitive 09:00 meds.", "Review provider notes and plan of care."]},
        {"time": "08:00", "title": "Initial rounds", "details": "Check safety, pain, breathing, IV access, mobility, and call light.", "actions": ["Perform hand hygiene and two identifiers.", "Assess pain, airway/breathing, IV site, and fall risk.", "Check whiteboard and call-light access."]},
        {"time": "09:00", "title": "Medication pass", "details": "Connect MAR, allergies, barcode workflow, education, and reassessment.", "actions": ["Confirm MAR and allergy.", "Explain medication indication.", "Plan reassessment for PRN meds."]},
        {"time": "10:30", "title": "Provider communication", "details": "Report status changes, abnormal labs, and failed pain control using SBAR.", "actions": ["Open with one clear Situation sentence.", "Choose relevant Background and Assessment.", "State a clear request or recommendation."]},
        {"time": "11:00", "title": "Interdisciplinary rounds", "details": "Align discharge readiness and barriers with provider, case manager, PT/OT, and pharmacy.", "actions": ["Confirm discharge target and barriers.", "Share mobility, oxygen, home support, and education needs.", "Explain today's plan to the patient in plain language."]},
        {"time": "14:00", "title": "New admission alert", "details": "ED-to-floor handoff, room prep, vitals, and medication reconciliation begin.", "actions": ["Prepare room and equipment.", "Ask ED handoff gap questions.", "Start admission checklist and safety screening."]},
        {"time": "18:00", "title": "End-of-shift documentation", "details": "Review flowsheets, notes, completed tasks, and late-charting risk.", "actions": ["Verify assessment, I&O, education, and reassessment.", "Flag open tasks and pending results.", "Summarize key risk for next shift."]},
        {"time": "19:00", "title": "Bedside handoff", "details": "Transfer stability, changes, pending tasks, and family concerns to the next RN.", "actions": ["Verify patient ID and safety at bedside.", "Handoff last pain med, abnormal labs, and pending tests.", "Invite patient questions during handoff."]},
    ]

    questions = [
        {"title": "Medication Safety Sequence", "station": "Medication Room", "prompt": "You are starting the 09:00 med round. Safest flow?", "choices": ["Review MAR/order -> allergy -> two identifiers -> barcode -> education/reassessment plan", "Pull meds first and check the chart in the room", "Skip MAR for familiar meds", "Give what the prior RN gave yesterday"], "answer": 0, "feedback": "Medication administration links orders, patient ID, barcode, education, and reassessment."},
        {"title": "Missing Medication", "station": "Medication Room", "prompt": "A 09:00 antibiotic is due but not available in the ADC.", "choices": ["Check MAR/order, dispense location, pharmacy messages, and due time", "Borrow it from another patient's bin", "Skip it automatically", "Blame pharmacy and end the conversation"], "answer": 0, "feedback": "Missing medication needs pharmacy communication, delay documentation, and escalation judgment."},
        {"title": "Insulin Before Meal", "station": "Medication Room", "prompt": "Pre-meal insulin is due, but the patient is nauseated and not eating.", "choices": ["Check glucose, meal status, insulin type/order, unit protocol, and call provider if needed", "Give it because it is due", "Tell the patient to drink something sweet and give it", "Hold it for next shift to decide"], "answer": 0, "feedback": "Insulin decisions require meal status, glucose, order parameters, and protocol."},
        {"title": "Admission Call", "station": "Nurse Station", "prompt": "ED calls with pneumonia admission handoff. What do you confirm first?", "choices": ["Reason for admission, oxygen/telemetry, isolation, safety risks, ETA", "How many family members are coming", "Whether the room TV works", "End the call and read the chart later"], "answer": 0, "feedback": "Pre-arrival handoff drives room and safety preparation."},
        {"title": "Call Light Triage", "station": "Nurse Station", "prompt": "Three calls arrive: SOB, water request, discharge paperwork question. Priority?", "choices": ["Assess SOB directly and delegate appropriate comfort requests", "Go room by room by distance", "Handle discharge paperwork first", "Silence all calls and finish meds"], "answer": 0, "feedback": "Use acuity and delegation together; possible status change needs RN assessment."},
        {"title": "Provider Callback", "station": "Nurse Station", "prompt": "Provider calls back about a chest-pain patient. Best first sentence?", "choices": ["This is RN Lee calling about room 412 with chest pressure 7/10 that started 10 minutes ago.", "The unit is really busy today.", "The patient seems anxious; please check the chart.", "Just put in an order."], "answer": 0, "feedback": "Situation should open with patient, problem, timing, and severity."},
        {"title": "Isolation Entry", "station": "Supply Room", "prompt": "You are entering a rule-out C. diff room. Best preparation?", "choices": ["Gown, gloves, dedicated equipment, specimen container, and exit hand-hygiene plan", "Surgical mask only", "Shared vital machine for multiple rooms", "Only the water cup the patient requested"], "answer": 0, "feedback": "Contact enteric precautions combine PPE, dedicated equipment, specimen flow, and hand hygiene."},
        {"title": "Dressing Supply", "station": "Supply Room", "prompt": "A wound dressing change is ordered. First supply-room action?", "choices": ["Review dressing type, frequency, drainage, and choose sterile/clean supplies accordingly", "Grab usual gauze and tape only", "Use whatever is already in the room", "Wait for provider because supplies are not RN work"], "answer": 0, "feedback": "Supplies should match the order and patient condition."},
        {"title": "Room Entry", "station": "Patient Room", "prompt": "You enter a patient room for the first time. What starts the workflow?", "choices": ["Hand hygiene, introduction, two identifiers, and safety check", "Start vitals first and identify later", "Tell family detailed information first", "Assume it is correct if the chart name looks similar"], "answer": 0, "feedback": "Trust and safety begin together at the bedside."},
        {"title": "Teach-back", "station": "Patient Room", "prompt": "After discharge teaching, the patient only nods. Best understanding check?", "choices": ["Ask the patient to explain when and how they will take the new medication at home", "Document understanding because they nodded", "Hand over papers and finish", "Teach only the family"], "answer": 0, "feedback": "Teach-back checks whether education actually landed."},
        {"title": "Clean vs Soiled", "station": "Utility / Isolation", "prompt": "A coworker is carrying soiled linen into clean utility.", "choices": ["Redirect to soiled route and explain contamination risk", "Ignore it", "Only chart it later", "Leave it briefly in clean utility"], "answer": 0, "feedback": "Clean/soiled route discipline is infection prevention."},
        {"title": "Family Privacy", "station": "Handoff Zone", "prompt": "Someone claiming to be the daughter asks for lab results by phone.", "choices": ["Verify caller identity and allowed disclosure per policy", "Share everything because they are family", "Hang up because you are busy", "Share lab numbers because they are not private"], "answer": 0, "feedback": "Family communication still requires privacy and authorization checks."},
        {"title": "ED Handoff Gap", "station": "Handoff Zone", "prompt": "ED handoff gives diagnosis but omits code status, allergy, and isolation.", "choices": ["Ask missing safety information before arrival", "Ask the patient after arrival and move on", "Diagnosis is enough", "Assume night shift will check"], "answer": 0, "feedback": "Admission handoff gaps affect room prep, medication, isolation, and emergency response."},
        {"title": "End-of-shift Report", "station": "Handoff Zone", "prompt": "What must be included in shift handoff?", "choices": ["Status changes, abnormal labs, pending tests/orders, last PRN, safety risk", "How busy you were", "Favorite TV channel", "No verbal handoff if charted"], "answer": 0, "feedback": "Prioritize what the next RN could miss during first rounds."},
        {"title": "ED Chest Pain First Look", "station": "Nurse Station", "prompt": "ED triage receives a chest-pain patient. What must the floor RN get in report?", "choices": ["Onset time, pain score/quality, vital signs, EKG/troponin status, oxygen/telemetry need", "Insurance type and family parking location", "Room TV and meal tray status", "Diagnosis only because ED handled the rest"], "answer": 0, "feedback": "Chest-pain workflow depends on time, EKG/enzymes, oxygen, and monitoring needs."},
        {"title": "Stroke-like Symptom", "station": "Patient Room", "prompt": "A patient suddenly has slurred speech and one-sided hand weakness. What do you confirm first?", "choices": ["Last-known-well, baseline, focused neuro check, glucose, vital signs", "Lunch preference and family arrival time", "Whether to check again on next rounds", "Whether discharge papers are ready"], "answer": 0, "feedback": "Neuro change escalation depends on timing, glucose/vitals, and baseline comparison."},
        {"title": "ICU Drip Boundary", "station": "Medication Room", "prompt": "An ICU/stepdown patient with a vasopressor drip may transfer. What should the floor RN confirm?", "choices": ["Whether this unit can manage the drip, titration policy, monitoring frequency, transfer criteria", "The drip name is enough; the floor can adjust it", "Skip monitoring plan if the patient looks stable", "Ask PCT to check blood pressure more often"], "answer": 0, "feedback": "Critical-care boundaries require unit policy, scope, and monitoring requirements."},
        {"title": "Sepsis Time-sensitive Tasks", "station": "Nurse Station", "prompt": "Labs, fluids, and antibiotics are ordered almost together for sepsis concern.", "choices": ["Track time-sensitive tasks: antibiotic timing, cultures/labs, fluids, reassessment", "Assume orders happen automatically because they are in the chart", "Leave it for next shift", "Ignore it if fever is absent"], "answer": 0, "feedback": "Sepsis workflows need task tracking and reassessment because timing matters."},
        {"title": "PACU Transfer Handoff", "station": "Handoff Zone", "prompt": "A post-op patient is coming from PACU. What information is unsafe to miss?", "choices": ["Airway/sedation, anesthesia events, last opioid, drains/lines, bleeding, activity restrictions", "Whether OR staff were friendly", "Favorite snack", "Only expected discharge date"], "answer": 0, "feedback": "PACU-to-floor handoff centers airway, sedation, opioid, bleeding, line/drain data."},
        {"title": "High-flow Oxygen Escalation", "station": "Patient Room", "prompt": "A stepdown patient's oxygen requirement keeps rising and they speak less.", "choices": ["Assess respiratory status, mental status, oxygen device/flow, vital trends, and escalate", "Wait if pulse ox number still looks acceptable", "Assume they are tired", "Chart meal intake first"], "answer": 0, "feedback": "Rising oxygen need with mental-status change may signal ICU-level deterioration."},
        {"title": "Postpartum Hemorrhage Cue", "station": "Patient Room", "prompt": "A postpartum patient feels dizzy and says pads are soaking quickly. First?", "choices": ["Assess bleeding amount, fundus, vitals, mental status, and call for help", "Say postpartum bleeding is normal and check later", "Finish newborn feeding education first", "Ask family to bring more pads"], "answer": 0, "feedback": "Mother-baby nurses must recognize hemorrhage cues and activate help early."},
        {"title": "Newborn Safety", "station": "Patient Room", "prompt": "Family places a newborn between blankets and pillows.", "choices": ["Explain safe sleep and newborn ID/security, then correct the sleep environment", "Avoid interfering with family culture", "Take a photo and teach later", "Say nothing because the mother is tired"], "answer": 0, "feedback": "Newborn safety needs immediate environment correction and education."},
        {"title": "Restraint / Sitter Decision", "station": "Nurse Station", "prompt": "A confused patient pulls lines and tries to get out of bed.", "choices": ["Assess cause, de-escalate, use safety interventions, and check sitter/charge/provider/policy", "Apply restraints immediately", "Tell PCT to physically hold the patient", "Leave the patient alone"], "answer": 0, "feedback": "Restraint is a last resort and requires alternatives, policy, order, and documentation."},
        {"title": "Central Line Infection Prevention", "station": "Utility / Isolation", "prompt": "A central-line dressing is loose and wet after showering.", "choices": ["Assess line site, dressing integrity, infection signs, and follow policy for dressing change/notification", "Let it dry", "Ask patient to add tape", "Wait until next scheduled dressing date"], "answer": 0, "feedback": "Central-line safety depends on dressing integrity and infection-prevention bundles."},
    ]

    specialty_tracks = [
        {"name": "Med-Surg / Telemetry", "tag": "core floor + rhythm awareness", "focus": "Manage meds, falls, discharge, telemetry alarms, and provider calls across a 4-6 patient assignment.", "tasks": ["Check whether telemetry alarms match bedside symptoms.", "Reprioritize when abnormal labs or new orders interrupt med pass.", "Share discharge teaching, ride, and pharmacy-delay barriers."], "risk": "The core skill is not just speed; it is pulling risk signals forward while many tasks remain open.", "practice": "Practice: Shift Board -> Call Light Prioritization -> CHF/Chest Pain cases", "color": colors["soft_blue"]},
        {"name": "Emergency Department", "tag": "triage / throughput / incomplete data", "focus": "Judge triage acuity, chief complaint, red flags, provider notification, and disposition flow quickly.", "tasks": ["Classify first-look cues for chest pain, stroke-like symptoms, and sepsis concern.", "Confirm allergy, medication, pregnancy/safety risk with incomplete history.", "Handoff oxygen, isolation, and telemetry needs to the floor."], "risk": "ED nurses do not wait for perfect information; they sort risk from incomplete information.", "practice": "Practice: New Admission from ED -> New Neuro Change -> Sepsis Screen Alert", "color": colors["soft_orange"]},
        {"name": "ICU / Critical Care", "tag": "unstable trend / drip / device", "focus": "Fewer patients, but higher complexity: vital trends, vasoactive drips, ventilators, central lines, sedation, deterioration.", "tasks": ["Escalate worsening MAP, urine output, mental status, lactate, or respiratory trend.", "Confirm protocol and double-check workflow for vasoactive/sedation/insulin drips.", "Check infection-prevention risks around central lines, Foley, and ventilators."], "risk": "Two patients can still be high risk when small changes become major deterioration within minutes.", "practice": "Practice: Sepsis Screen Alert -> Opioid Sedation Risk -> SBAR Trainer", "color": colors["soft_lavender"]},
        {"name": "Stepdown / PCU", "tag": "between ICU and floor", "focus": "Watch patients too unstable for routine floor care but not yet ICU, and know escalation thresholds.", "tasks": ["Monitor high-flow oxygen, telemetry changes, and borderline blood pressure.", "Clarify ICU transfer criteria and notification timing.", "Explain monitoring plans while managing family questions and anxiety."], "risk": "Ambiguous deterioration becomes unsafe when escalation is delayed.", "practice": "Practice: Acute Shortness of Breath -> Provider communication -> Handoff Zone", "color": colors["soft_cyan"]},
        {"name": "OR / PACU", "tag": "perioperative safety", "focus": "Perioperative safety centers consent, site verification, airway, pain, nausea, and discharge criteria.", "tasks": ["Verify procedure, consent, allergy, NPO, implants/devices, and site marking.", "Assess airway, sedation, pain, nausea, bleeding, and discharge criteria in PACU.", "Handoff anesthesia events, lines/drains, last opioid, and mobility restrictions."], "risk": "Fast workflow still depends on standardization that prevents identity and procedure mismatch.", "practice": "Practice: Post-op Day 1 -> Opioid Sedation Risk -> End-of-shift Handoff", "color": colors["soft_green"]},
        {"name": "L&D / Mother-Baby", "tag": "maternal-newborn dyad", "focus": "Care for mother and newborn together: hemorrhage, hypertension, newborn safety, and feeding support.", "tasks": ["Assess postpartum bleeding, fundus, pain, BP, and magnesium-related safety cues.", "Check newborn ID/security, feeding, glucose/jaundice cues, and safe sleep education.", "Use teach-back while respecting family culture and privacy."], "risk": "This area has two patients connected as one care unit; maternal stability and newborn safety move together.", "practice": "Practice: Teach-back -> Family Privacy -> Room Entry", "color": colors["soft_gold"]},
    ]

    def steps(*items):
        return [{"prompt": p, "choices": [(a, True), (b, False), (c, False)], "feedback": f} for p, a, b, c, f in items]

    scenarios = {
        "Post-op Day 1": {"patient": "54-year-old POD#1 laparoscopic cholecystectomy, pain 8/10", "goals": "pain reassessment, mobility, fall risk, discharge readiness", "steps": steps(("The patient reports pain 8/10. First action?", "Assess pain characteristics and vitals, then review PRN orders in MAR.", "Start discharge teaching immediately.", "Chart and leave it for next shift.", "Pain requires assessment, MAR/order review, intervention, and reassessment planning."), ("After PRN pain medication workflow, what cannot be missed?", "Plan and document pain reassessment within the expected timeframe.", "Skip reassessment if the patient looks comfortable.", "Only tell family the drug name.", "PRN medication includes effect and side-effect reassessment."), ("The patient asks what to watch for at home.", "Use teach-back for activity, wound care, pain plan, and warning signs.", "Tell them to read the papers.", "Say the provider will explain everything.", "Patient education and teach-back are core RN work."))},
        "CHF Exacerbation": {"patient": "72-year-old with CHF exacerbation, 2 L NC, telemetry", "goals": "daily weight, I&O, oxygen, abnormal lab escalation, rounds", "steps": steps(("Morning lab shows low potassium. Next action?", "Assess patient/telemetry, review related meds, and call provider with SBAR.", "Write it down for evening shift.", "Tell the patient to eat a banana.", "Abnormal labs need patient context and escalation."), ("What should the RN share during interdisciplinary rounds?", "Oxygen need, edema, I&O, weight trend, mobility and discharge barriers.", "How busy yesterday was.", "The patient's music preference.", "Rounds align discharge readiness and barriers."), ("The patient says breathing is worse. What first?", "Go to bedside for respiratory assessment and vital signs, then escalate if needed.", "Turn off the call and go later.", "Call case manager first.", "Status-change symptoms need bedside assessment first."))},
        "Rule-out C. diff": {"patient": "68-year-old with diarrhea, contact enteric precaution pending", "goals": "isolation signage, PPE, supplies, family education", "steps": steps(("You see contact enteric signage. Before entry?", "Read sign and prepare gown, gloves, and dedicated equipment.", "Wear gloves only.", "Enter without PPE if called.", "Isolation signs tell you the entry/exit routine."), ("Family asks why gowns are needed.", "Explain PPE helps reduce spread while testing is pending.", "Say it is just a rule.", "Say it does not matter but they must do it.", "Education works better when the reason is clear."), ("What supplies fit this patient?", "PPE, specimen container, dedicated equipment label, and education sheet.", "Discharge folder only.", "Borrow equipment from another room.", "Isolation care includes supply planning and equipment separation."))},
        "New Admission from ED": {"patient": "63-year-old pneumonia admission, oxygen 3 L NC, ETA 20 min", "goals": "ED handoff, room readiness, initial assessment, admission checklist", "steps": steps(("ED calls with handoff. What do you confirm?", "Reason for admission, oxygen/telemetry, isolation, safety risk, ETA.", "End the call and read the chart later.", "Ask family contacts first and clinical data later.", "Pre-arrival handoff supports safety preparation."), ("Room prep priority before arrival?", "Oxygen/suction, bed safety, call light, equipment, and isolation sign if needed.", "Place education papers on the table.", "Do nothing until med pass is finished.", "Admission readiness starts before arrival."), ("Initial workflow on arrival?", "Patient ID, vitals, focused assessment, allergies, and med reconciliation start.", "Begin discharge education.", "Leave charting to night shift.", "Admission workflow combines assessment, screening, and documentation."))},
        "Hypoglycemia Before Lunch": {"patient": "58-year-old with diabetes, pre-lunch glucose 58 mg/dL", "goals": "protocol awareness, symptom check, recheck, provider notification", "steps": steps(("PCT reports glucose 58. First action?", "Go to patient, assess symptoms/mental status, and check protocol/MAR.", "Ask PCT to give a snack and keep working.", "Wait for lunch tray.", "Low glucose requires patient assessment and protocol flow."), ("After intervention, what matters next?", "Plan and document glucose recheck at the required time.", "Assume it improved.", "Tell family to buy a glucometer.", "Hypoglycemia workflow depends on recheck and trend."), ("Glucose stays low and patient cannot eat.", "Call provider with SBAR about trend and meal/medication plan.", "Only hand it off to next shift.", "Keep giving sweet foods only.", "Repeated abnormal findings need escalation with context."))},
        "Chest Pain on Telemetry": {"patient": "66-year-old telemetry patient, sudden chest pressure 7/10", "goals": "rapid assessment, EKG/order awareness, escalation", "steps": steps(("Patient reports sudden chest pressure. First response?", "Go bedside and assess pain, vitals, oxygen, and telemetry context.", "Turn off call light and round later.", "Assume anxiety.", "Chest pain needs direct assessment and escalation readiness."), ("Provider SBAR background should include?", "Admission reason, cardiac history, vitals, telemetry/labs, and meds.", "Only that the patient is worried.", "That you missed lunch.", "SBAR compresses relevant decision-making data."), ("New orders are entered. RN workflow?", "Verify orders, reprioritize tasks, monitor patient, and document.", "Assume the order means the issue is done.", "No RN charting needed.", "Order follow-through and monitoring matter."))},
        "Unwitnessed Fall": {"patient": "79-year-old fall-risk patient found near bathroom", "goals": "post-fall assessment, safety, notification, reporting", "steps": steps(("You find the patient sitting on the floor. First?", "Assess safety, injury, vitals, and mental status before moving; call for help.", "Move them back to bed fast.", "Skip charting if they say they are fine.", "Post-fall care starts with assessment and safety."), ("Who may need communication?", "Charge RN, provider, family/guardian per policy, and next shift.", "Only PCT.", "No one if patient asks.", "Falls trigger unit safety and policy workflow."), ("Documentation focus?", "Objective discovery, assessment, notification, intervention, prevention plan.", "Emotional blame.", "Incident report only, no charting.", "Charting and safety reporting are related but separate."))},
        "Discharge Delay & Teach-back": {"patient": "45-year-old with discharge order, ride barrier, medication confusion", "goals": "barriers, education, case management, teach-back", "steps": steps(("Patient does not understand the new medication.", "Explain purpose/timing/warning signs and ask for teach-back.", "Tell them to read pharmacy papers.", "Send them because order is in.", "Discharge is safe transition, not just an order."), ("Patient has no ride home.", "Share as a discharge barrier with case manager/social work or charge RN.", "Say it is not unit work.", "Pass it without mentioning.", "Transportation is a real discharge barrier."), ("End-of-shift handoff should include?", "Order status, education gap, ride barrier, pending pharmacy/meds.", "Only that they are discharging.", "No info because they are young.", "Pending discharge barriers are high-value handoff items."))},
        "Missing Medication": {"patient": "61-year-old, 09:00 antibiotic due, not in ADC", "goals": "MAR check, pharmacy communication, timing, patient update", "steps": steps(("Medication is due but missing. First check?", "MAR/order status, due time, dispense location, pharmacy message history.", "Skip it.", "Find a similar medication from another patient.", "Missing meds need system workflow and timing awareness."), ("Best pharmacy message includes?", "Patient, medication, dose/time, location, urgency, and prior request.", "Only 'med missing.'", "A long emotional complaint.", "Pharmacy communication should be concise and actionable."), ("Delay is likely. RN next step?", "Consider charge/provider escalation, explain delay, and document.", "Wait silently until end of shift.", "Tell patient it is unimportant.", "Time-sensitive meds need delay communication and documentation."))},
        "Sepsis Screen Alert": {"patient": "70-year-old UTI admission, fever, tachycardia, new confusion", "goals": "trend recognition, sepsis screen, escalation, reassessment", "steps": steps(("EHR sepsis alert appears and confusion worsens.", "Check trends, mental status, labs/orders, and assess bedside first.", "Close it as alert fatigue.", "Assume age-related confusion.", "Alerts trigger RN assessment and trend recognition."), ("Provider report should include?", "Baseline change, fever/HR/BP, source, urine output, current antibiotics.", "Only that the computer alerted.", "That the patient is difficult.", "Sepsis concern requires trend and source context."), ("New orders and monitoring plan appear.", "Track time-sensitive tasks, reassessment, documentation, and handoff.", "Skip documentation because there are many orders.", "Delegate everything to PCT.", "Time-sensitive workflows require tracking and handoff."))},
        "Difficult Family Call": {"patient": "82-year-old with confusion; daughter repeatedly calls", "goals": "privacy, therapeutic communication, escalation boundary, documentation", "steps": steps(("Caller claims to be daughter and asks for labs/meds.", "Verify identity/permission and share only what policy allows.", "Share everything because they are family.", "Hang up because busy.", "Family calls still require privacy and authorization checks."), ("Caller is angry and demands provider now.", "Acknowledge emotion and explain realistic next step/callback plan.", "Raise your voice too.", "Promise provider will call immediately.", "Communication needs empathy, boundaries, and a real plan."), ("After the call, document?", "Caller, concern, information shared, escalation/callback plan objectively.", "Only that you felt upset.", "Nothing; family calls are not charting.", "Family communication can affect coordination and risk management."))},
        "New Neuro Change": {"patient": "76-year-old stroke history; sudden slurred speech and right-hand weakness", "goals": "baseline comparison, focused neuro check, rapid escalation, last-known-well", "steps": steps(("PCT says the patient's speech is strange. First?", "Assess bedside for baseline change, speech, weakness, vitals, and glucose.", "Wait until next round.", "Call family first and wait.", "Neuro change is time-sensitive; bedside assessment comes first."), ("Escalation must include?", "Last-known-well, new symptoms, baseline, glucose/vitals, anticoagulant status.", "Only that speech sounds odd.", "That patient is sensitive.", "Stroke concern needs compressed time-critical data."), ("New orders and transport prep begin.", "Organize monitoring, safety, IV access, pending results, family update limits, documentation.", "Assume responsibility transfers with transport.", "Delay charting to next shift.", "Changes require ongoing observation, documentation, and handoff."))},
        "Transfusion Reaction Concern": {"patient": "59-year-old receiving PRBC; chills and fever 20 minutes in", "goals": "transfusion safety, stop-and-assess, notification, specimen/blood bank workflow", "steps": steps(("Patient develops chills and fever during transfusion. First?", "Stop transfusion, assess patient/vitals, and follow facility procedure.", "Slow the rate and continue.", "Give a blanket and check later.", "Suspected transfusion reaction starts with stop, assess, and notify."), ("What information do you verify?", "Patient ID, blood product, start time, symptoms, vitals trend, line status.", "Blood bank already checked everything.", "Only that the patient felt cold.", "Transfusion safety requires ID, timing, symptoms, and trends."), ("Handoff should include?", "Reaction concern, interventions, notifications, specimen/return status, monitoring plan.", "Only that transfusion stopped.", "No handoff because provider knows.", "Next RN needs pending risk and workflow clearly."))},
        "Opioid Sedation Risk": {"patient": "49-year-old post-op patient after PRN opioid; RR 9/min, very drowsy", "goals": "sedation assessment, respiratory safety, reassessment, escalation", "steps": steps(("After opioid, patient is very drowsy with RR 9.", "Assess sedation, respiratory status, oxygen saturation, vitals, and call for help.", "Let them sleep.", "Document pain improved.", "Opioid reassessment includes sedation and respiratory safety."), ("Provider report should include?", "Medication time/dose, current sedation/RR/O2, baseline, oxygen, needed next step.", "Only that patient is sleepy.", "Skip drug name because it is in chart.", "Medication-related changes need timing, dose, and current assessment."), ("Same shift follow-up?", "Adjust reassessment interval, safety, pain plan, documentation, and handoff.", "No need after one report.", "Delay charting until patient wakes.", "Sedation risk requires a monitoring plan."))},
        "Rapid Discharge Pressure": {"patient": "64-year-old discharge order, new anticoagulant, pharmacy delay", "goals": "safe transition, medication education, barrier communication, team coordination", "steps": steps(("Bed turnover pressure exists, but anticoagulant teaching is incomplete.", "Share readiness and education gap with charge/team and complete teach-back.", "Send patient because order exists.", "Medication teaching is only pharmacy work.", "Discharge must be a safe transition."), ("Patient asks what to do if bleeding does not stop.", "Teach warning signs, when to call, timing, and missed-dose plan in plain language.", "Tell them to search online.", "Only reassure them.", "High-risk meds need home decision criteria."), ("Pharmacy is delayed and ride has arrived.", "Share pharmacy delay, education status, ride timing, and team notification.", "Send patient to pick meds later.", "Handoff only 'discharge.'", "Discharge barriers involve multiple departments and timing."))},
    }

    first_week_days = [
        {"day": 1, "time": "Day 1 / 06:35", "title": "First shift, badge, preceptor, unit culture", "setting": "You receive your badge and walk onto 4 West. Your preceptor speaks quickly, and the charge RN gives a short shadowing plan.", "scene": "orientation", "assignment": "Goal: stay observant while protecting HIPAA and unit etiquette.", "cues": [("Badge", "visible in patient care areas"), ("Phone", "no patient photos or notes"), ("Break room", "keep patient stories inside work need"), ("Preceptor", "clarify early")], "risk": "On day one, it is easy to pretend you understand or put patient details in a personal phone.", "choices": [{"text": "Ask your preceptor what you may do independently and what must remain observe-only today.", "best": True, "effect": {"safety": 2, "team": 2, "law": 1, "confidence": 1}, "feedback": "Safe start. Aligning scope, facility policy, and preceptor expectations prevents early mistakes."}, {"text": "Act confident and skip unfamiliar words or systems for now.", "best": False, "effect": {"safety": -1, "team": -1, "law": 0, "confidence": -1}, "feedback": "Hiding uncertainty can become a bigger EHR, medication, or escalation risk."}, {"text": "Put patient room numbers and diagnoses in your personal phone to study later.", "best": False, "effect": {"safety": -1, "team": 0, "law": -3, "confidence": 0}, "feedback": "Personal devices with patient details create privacy/HIPAA risk."}, {"text": "Message a friend about a patient story because you think it is anonymous.", "best": False, "effect": {"safety": -1, "team": -1, "law": -3, "confidence": 0}, "feedback": "Even 'anonymous' combinations can become PHI. Keep patient stories within work purpose."}], "debrief": "Day 1 success is not pretending to know everything; it is showing uncertainty safely and protecting patient information.", "bridge": "Next: EHR login, MAR, and medication room access."},
        {"day": 2, "time": "Day 2 / 08:45", "title": "EHR, MAR, ADC, medication room access", "setting": "Your preceptor demonstrates a 09:00 med pass with EHR tasks, MAR, allergy, and ADC open.", "scene": "medroom", "assignment": "Goal: read the information flow before removing medication.", "cues": [("MAR", "due time, route, hold parameters"), ("Allergy", "band and EHR"), ("ADC", "dispense location / missing med"), ("Waste", "witness and documentation")], "risk": "Even experienced Korean RNs meet a new system: ADC, barcode, controlled substance waste, and policy wording.", "choices": [{"text": "Verbalize MAR, allergy, hold parameters, and barcode flow with your preceptor before entering.", "best": True, "effect": {"safety": 3, "team": 1, "law": 1, "confidence": 1}, "feedback": "Correct. New facility medication workflows should be spoken through early."}, {"text": "Rely on Korean medication experience and let the preceptor handle MAR review.", "best": False, "effect": {"safety": -2, "team": -1, "law": 0, "confidence": -1}, "feedback": "Experience helps, but system workflow differs."}, {"text": "Handle controlled substance waste later by yourself because the preceptor is busy.", "best": False, "effect": {"safety": -2, "team": -1, "law": -2, "confidence": -1}, "feedback": "Controlled substances require policy, witness, and documentation."}, {"text": "Tell the patient only 'the doctor ordered it' when they ask about a medication.", "best": False, "effect": {"safety": -1, "team": 0, "law": 0, "confidence": -1}, "feedback": "Patient education is part of RN workflow."}], "debrief": "Day 2 is about learning how this facility makes medication safe, not proving you already know the drug.", "bridge": "Next: assignment and PCT delegation."},
        {"day": 3, "time": "Day 3 / 07:15", "title": "Partial assignment and delegation", "setting": "Your preceptor gives you two patients: CHF and post-op. A PCT is helping with vitals and glucose.", "scene": "assignment", "assignment": "Goal: separate RN-only assessment from delegable tasks.", "cues": [("414 CHF", "O2, I&O, daily weight"), ("418 Post-op", "pain reassessment due"), ("PCT", "vitals/glucose report"), ("Call light", "bathroom, pain, SOB")], "risk": "Korean RNs may be used to doing everything directly; U.S. units expect delegation with follow-up accountability.", "choices": [{"text": "Assess SOB yourself, delegate water/blanket requests to PCT, and set follow-up time.", "best": True, "effect": {"safety": 3, "team": 2, "law": 0, "confidence": 1}, "feedback": "Good. You separated acuity, RN assessment, and comfort tasks."}, {"text": "Ask the PCT to handle all call lights while you finish chart review.", "best": False, "effect": {"safety": -3, "team": -1, "law": 0, "confidence": -1}, "feedback": "Possible status changes require RN assessment."}, {"text": "Refuse PCT help and do everything yourself.", "best": False, "effect": {"safety": -1, "team": -2, "law": 0, "confidence": -1}, "feedback": "Teamwork with PCTs is a key U.S. adaptation skill."}, {"text": "Tell your preceptor your priority reasoning and ask for confirmation.", "best": True, "effect": {"safety": 2, "team": 2, "law": 0, "confidence": 2}, "feedback": "Excellent. Showing your judgment helps preceptor coaching."}], "debrief": "Even experienced RNs need to show clinical judgment out loud during orientation.", "bridge": "Next: privacy, interpreter use, and family calls."},
        {"day": 4, "time": "Day 4 / 13:20", "title": "HIPAA, family calls, interpreter etiquette", "setting": "A caller claiming to be family asks for lab results, and another patient prefers a family member to interpret.", "scene": "privacy", "assignment": "Goal: protect privacy while staying kind.", "cues": [("Phone call", "identity / permission"), ("Hallway", "avoid patient details"), ("Interpreter", "facility resource first"), ("Family", "supporter vs decision-maker")], "risk": "In the U.S., 'they are family' does not automatically mean you may disclose details.", "choices": [{"text": "Verify caller identity and allowed disclosure per facility policy, then set a callback plan.", "best": True, "effect": {"safety": 1, "team": 1, "law": 3, "confidence": 1}, "feedback": "Good. Privacy boundary comes before details."}, {"text": "Give detailed lab results and medication plans because the caller says they are the daughter.", "best": False, "effect": {"safety": -1, "team": 0, "law": -3, "confidence": -1}, "feedback": "Authorization must be verified."}, {"text": "Use the family member as interpreter for important medical teaching.", "best": False, "effect": {"safety": -2, "team": 0, "law": -2, "confidence": -1}, "feedback": "Facility interpreter resources are preferred for important healthcare communication."}, {"text": "Pause hallway patient details and move the discussion to a private area.", "best": True, "effect": {"safety": 1, "team": 1, "law": 2, "confidence": 1}, "feedback": "Good public-area boundary."}], "debrief": "Day 4 is professional boundary practice: kindness and privacy can coexist.", "bridge": "Next: provider calls and escalation."},
        {"day": 5, "time": "Day 5 / 10:35", "title": "Provider call, RT, rapid change", "setting": "A CHF patient reports worse breathing. O2 sat drops and crackles increase. Provider callback is short.", "scene": "escalation", "assignment": "Goal: connect assessment cues, SBAR, and escalation timing.", "cues": [("Vitals", "O2 sat 89%, RR 26"), ("Assessment", "increased crackles"), ("Orders", "diuretic, telemetry"), ("Team", "provider / RT / charge RN")], "risk": "Concise provider communication matters, but missing key data delays patient safety.", "choices": [{"text": "Assess trend, form one Situation sentence, and call provider using SBAR.", "best": True, "effect": {"safety": 3, "team": 2, "law": 0, "confidence": 2}, "feedback": "Good. Provider calls compress decision cues."}, {"text": "Wait until rounds because the provider may be busy.", "best": False, "effect": {"safety": -3, "team": -1, "law": 0, "confidence": -1}, "feedback": "Respiratory change should not wait."}, {"text": "Start the call with a long explanation that you are new.", "best": False, "effect": {"safety": -1, "team": -1, "law": 0, "confidence": -1}, "feedback": "Patient situation comes first."}, {"text": "Share your escalation concern with preceptor/charge RN and consider RT support.", "best": True, "effect": {"safety": 2, "team": 2, "law": 0, "confidence": 1}, "feedback": "Use team resources during orientation."}], "debrief": "Day 5 is not about perfect English; it is about not missing assessment cues.", "bridge": "Next: discharge pressure and case management."},
        {"day": 6, "time": "Day 6 / 15:40", "title": "Discharge pressure, pharmacy delay, teach-back", "setting": "Bed management wants discharge; the patient is anxious about a new anticoagulant; pharmacy is delayed.", "scene": "discharge", "assignment": "Goal: protect safe transition under throughput pressure.", "cues": [("Discharge order", "entered"), ("New med", "anticoagulant teaching"), ("Pharmacy", "delay"), ("Ride", "arrived but confused")], "risk": "Discharge is not done until medication, transportation, education, and follow-up align.", "choices": [{"text": "Share education gap, pharmacy delay, and ride timing with charge/case manager and complete teach-back.", "best": True, "effect": {"safety": 3, "team": 2, "law": 0, "confidence": 1}, "feedback": "Good. Barriers must be visible to the team."}, {"text": "Send the patient first and rely on papers for medication teaching.", "best": False, "effect": {"safety": -3, "team": -1, "law": 0, "confidence": -1}, "feedback": "High-risk medication needs teach-back."}, {"text": "Tell next shift only 'discharge planned' because pharmacy delay is not RN work.", "best": False, "effect": {"safety": -2, "team": -2, "law": 0, "confidence": -1}, "feedback": "Discharge barriers are interdisciplinary workflow."}, {"text": "Ask the patient to explain bleeding warning signs, missed-dose plan, and follow-up.", "best": True, "effect": {"safety": 3, "team": 1, "law": 0, "confidence": 2}, "feedback": "Teach-back confirms the patient can act at home."}], "debrief": "Day 6 lets you feel the tension between moving beds and moving patients safely.", "bridge": "Next: independent assignment readiness."},
        {"day": 7, "time": "Day 7 / 18:30", "title": "Readiness and self-advocacy", "setting": "Your preceptor says next week may include a larger assignment, but EHR speed and provider calls still feel hard.", "scene": "readiness", "assignment": "Goal: name strengths, gaps, and a safe growth plan.", "cues": [("Strength", "assessment / education"), ("Gap", "EHR / provider call"), ("Support", "preceptor / charge RN"), ("Boundary", "unsafe assignment escalation")], "risk": "Safe growth means naming what you can handle and where support is still needed.", "choices": [{"text": "Tell your preceptor your strengths, supervision needs, and next-week practice goals.", "best": True, "effect": {"safety": 3, "team": 3, "law": 0, "confidence": 2}, "feedback": "Good. Self-advocacy is professional communication for patient safety."}, {"text": "Hide concerns and accept any assignment so evaluation looks good.", "best": False, "effect": {"safety": -3, "team": -1, "law": 0, "confidence": -2}, "feedback": "Hiding limits can harm patient safety and adaptation."}, {"text": "Ask the charge RN how to use chain of command for unsafe assignments.", "best": True, "effect": {"safety": 2, "team": 2, "law": 1, "confidence": 2}, "feedback": "Good question. Chain of command varies by facility."}, {"text": "Conclude U.S. nursing is not for you and avoid feedback.", "best": False, "effect": {"safety": -1, "team": -2, "law": 0, "confidence": -2}, "feedback": "Adaptation stress is normal; feedback helps separate solvable issues."}], "debrief": "Day 7 is not an independence declaration; it is a readiness conversation.", "bridge": "Next: repeat weak areas in tour, shift board, and patient cases."},
    ]

    score_labels = {"safety": "Patient safety", "team": "Team adaptation", "law": "Law/policy awareness", "confidence": "Communication confidence"}
    reference_cards = [
        ("After NCLEX", "Clinical judgment means recognizing cues, prioritizing hypotheses, and taking action in real situations."),
        ("HIPAA/PHI boundaries", "Phone calls, elevators, break rooms, personal devices, and social media can leak patient information."),
        ("Interpreter etiquette", "Use facility interpreter resources for important healthcare communication when English is limited."),
        ("CDC precautions", "Add contact/droplet/airborne logic on top of standard precautions."),
        ("U.S. workplace communication", "Use clarify, read-back, chain of command, and preceptor feedback professionally."),
    ]
    checklists = {
        "Patient Room Entry": ["Performed hand hygiene.", "Verified two identifiers.", "Checked allergy band or chart allergy.", "Checked fall risk, isolation, oxygen, IV line, drains/tubes.", "Checked call light, bed position, clutter, belongings.", "Explained today's plan of care briefly."],
        "Admission Workflow": ["Confirmed diagnosis/reason for admission from handoff.", "Checked code status, allergies, isolation, fall risk, diet/activity order.", "Completed initial vitals and focused assessment.", "Explained medication reconciliation flow.", "Completed belongings, skin check, education, call-light orientation.", "Flagged admission documentation tasks."],
        "End-of-shift Handoff": ["Reported reason for admission and current status.", "Reported events and status changes.", "Reported lines/tubes/drains, oxygen, mobility, fall risk.", "Reported abnormal labs and pending tests/orders.", "Reported last PRN and reassessment need.", "Reported family concern, discharge barrier, education need."],
    }
    references = [
        "NCSBN Next Generation NCLEX: real-world case studies, clinical judgment, decision-making",
        "NCSBN Clinical Judgment Measurement Model: recognizing cues, prioritizing hypotheses, taking action",
        "CDC Infection Control Basics: Standard Precautions and Transmission-Based Precautions",
        "AHRQ TeamSTEPPS SBAR and handoff communication",
        "Joint Commission International Patient Safety Goals",
        "HHS HIPAA Privacy Rule Summary",
        "Facility policy reminder: chain of command, interpreter use, medication workflow, and scope rules vary by employer and state",
    ]

    return {
        "nav_items": nav_items,
        "ward_zones": ward_zones,
        "tour_modes": tour_modes,
        "shift_events": shift_events,
        "questions": questions,
        "scenarios": scenarios,
        "first_week_days": first_week_days,
        "first_week_score_labels": score_labels,
        "first_week_reference_cards": reference_cards,
        "specialty_tracks": specialty_tracks,
        "checklists": checklists,
        "references": references,
    }

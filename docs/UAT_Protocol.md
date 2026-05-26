# SlideCommander — User Acceptance Test Protocol

**Document version:** 1.0  
**Test phase:** 4.10  
**Acceptance criterion:** 3 presenters complete a live session with zero system failures; qualitative feedback documented.

---

## 1. Prerequisites (Test Director Checklist)

Before recruiting testers, confirm all of the following:

- [ ] `python main.py` starts without errors on the presentation PC
- [ ] QR code renders correctly in the terminal or browser
- [ ] A slide deck is open in Google Slides or PowerPoint on the same PC
- [ ] The presentation PC and tester phones are on the **same Wi-Fi network**
- [ ] Tasks 4.3–4.9 are marked complete in `execution_plan.md`

---

## 2. Tester Onboarding Script (read aloud — ~2 minutes)

> "Thanks for helping test SlideCommander. Here's everything you need to know:
>
> **Connecting:** Open your phone camera and point it at this QR code on the screen. Tap the link that appears — it will open a web page with four large buttons: **Next**, **Back**, **Start**, and **End**, plus a **Pause** button.
>
> **Button control:** Tap any button to advance or jump your slides. You do not need to look at your phone — the buttons are large and spaced deliberately. There is no login or app install required.
>
> **Voice control:** You can also control slides by speaking. The keywords are: **next**, **back**, **start**, **end**, and **pause**. Speak at a normal presentation volume — you do not need to shout or hold a button first. There is a ~1 second cooldown between commands so accidental repeats are suppressed.
>
> **Goal for this session:** Please deliver 3–5 minutes of your own content (or freestyle) while controlling your slides using the phone and voice. Pretend I am not here. If anything feels wrong or unexpected, keep going and tell me afterwards.
>
> Any questions before we start?"

---

## 3. Test Director — Silent Observation Checklist

Complete one copy per tester during the live session. Do **not** intervene unless there is a system crash.

**Tester ID:** ______  **Date:** ______  **Environment:** ______  **Slide app:** ______

### 3.1 Connection & Setup

| # | Observation | Pass | Fail | Notes |
|---|-------------|------|------|-------|
| O-01 | QR code scanned and web UI loaded without manual URL entry | ☐ | ☐ | |
| O-02 | Web UI displayed all 5 buttons correctly on tester's phone | ☐ | ☐ | |
| O-03 | WebSocket connected (green indicator or no error banner shown) | ☐ | ☐ | |
| O-04 | Setup completed within 60 seconds of handing over the phone | ☐ | ☐ | |

### 3.2 Button Control

| # | Observation | Pass | Fail | Notes |
|---|-------------|------|------|-------|
| O-05 | First button tap advanced the slide on the first attempt | ☐ | ☐ | |
| O-06 | No double-advance observed on any single tap | ☐ | ☐ | |
| O-07 | **Back** button moved slide backward correctly | ☐ | ☐ | |
| O-08 | **Start** button jumped to slide 1 correctly | ☐ | ☐ | |
| O-09 | **End** button jumped to last slide correctly | ☐ | ☐ | |
| O-10 | **Pause** button triggered pause/resume without crashing | ☐ | ☐ | |
| O-11 | Tester operated buttons without looking at phone after first use | ☐ | ☐ | |

### 3.3 Voice Control

| # | Observation | Pass | Fail | Notes |
|---|-------------|------|------|-------|
| O-12 | "Next" keyword advanced slide within 2 seconds of utterance | ☐ | ☐ | |
| O-13 | "Back" keyword moved slide backward within 2 seconds | ☐ | ☐ | |
| O-14 | No false positive trigger observed (slide moved without a command) | ☐ | ☐ | |
| O-15 | Debounce prevented double-trigger when same keyword said in quick succession | ☐ | ☐ | |
| O-16 | Voice and button controls worked interchangeably without conflict | ☐ | ☐ | |

### 3.4 Stability

| # | Observation | Pass | Fail | Notes |
|---|-------------|------|------|-------|
| O-17 | WebSocket did not disconnect at any point during the session | ☐ | ☐ | |
| O-18 | No Python exception or server crash observed in terminal | ☐ | ☐ | |
| O-19 | UI remained responsive throughout (no freeze or blank screen) | ☐ | ☐ | |
| O-20 | System required no manual restart during the session | ☐ | ☐ | |

**Session duration:** ______ min  **Slides advanced:** ______  **Voice commands used:** ______

**Director's overall observation:**

> _

---

## 4. Post-Test Questionnaire (presenter fills in after session)

Hand this to the tester immediately after the session. Allow 3–5 minutes for written answers.

**Tester ID:** ______  **Date:** ______

---

**Q1. How confident did you feel using the voice commands during your presentation?**  
*(1 = not confident at all, 5 = completely confident)*

Rating: ______ / 5

Comments:

> _

---

**Q2. Was the button layout intuitive? Could you find the right button without looking at your phone?**  
*(1 = very confusing, 5 = completely intuitive)*

Rating: ______ / 5

Comments:

> _

---

**Q3. Did you notice any moment where the system did something unexpected — a slide jumping the wrong way, a missed command, or a lag that interrupted your flow?**

Yes / No

If yes, describe:

> _

---

**Q4. Compared to a standard clicker or keyboard shortcut, how would you rate SlideCommander for real presentation use?**  
*(1 = much worse, 3 = equivalent, 5 = much better)*

Rating: ______ / 5

Comments:

> _

---

**Q5. What is the single most important improvement you would make before using this in a high-stakes presentation?**

> _

---

## 5. Results Template

Copy this block once per tester and fill in after each session.

---

### Tester 1

**Name / Role:** ______  **Date:** ______  **Environment:** ______

**Observation summary:**

| Category | Passed | Failed | Notes |
|----------|--------|--------|-------|
| Connection & Setup (O-01–O-04) | __ / 4 | __ / 4 | |
| Button Control (O-05–O-11) | __ / 7 | __ / 7 | |
| Voice Control (O-12–O-16) | __ / 5 | __ / 5 | |
| Stability (O-17–O-20) | __ / 4 | __ / 4 | |
| **Total** | __ / 20 | __ / 20 | |

**System failure occurred:** Yes / No  
**Questionnaire scores:** Q1: __ / 5  Q2: __ / 5  Q3: Yes/No  Q4: __ / 5  
**Key feedback quote:**

> _

**Director's pass/fail decision:** PASS / FAIL  
**Reason if FAIL:**

> _

---

### Tester 2

**Name / Role:** ______  **Date:** ______  **Environment:** ______

**Observation summary:**

| Category | Passed | Failed | Notes |
|----------|--------|--------|-------|
| Connection & Setup (O-01–O-04) | __ / 4 | __ / 4 | |
| Button Control (O-05–O-11) | __ / 7 | __ / 7 | |
| Voice Control (O-12–O-16) | __ / 5 | __ / 5 | |
| Stability (O-17–O-20) | __ / 4 | __ / 4 | |
| **Total** | __ / 20 | __ / 20 | |

**System failure occurred:** Yes / No  
**Questionnaire scores:** Q1: __ / 5  Q2: __ / 5  Q3: Yes/No  Q4: __ / 5  
**Key feedback quote:**

> _

**Director's pass/fail decision:** PASS / FAIL  
**Reason if FAIL:**

> _

---

### Tester 3

**Name / Role:** ______  **Date:** ______  **Environment:** ______

**Observation summary:**

| Category | Passed | Failed | Notes |
|----------|--------|--------|-------|
| Connection & Setup (O-01–O-04) | __ / 4 | __ / 4 | |
| Button Control (O-05–O-11) | __ / 7 | __ / 7 | |
| Voice Control (O-12–O-16) | __ / 5 | __ / 5 | |
| Stability (O-17–O-20) | __ / 4 | __ / 4 | |
| **Total** | __ / 20 | __ / 20 | |

**System failure occurred:** Yes / No  
**Questionnaire scores:** Q1: __ / 5  Q2: __ / 5  Q3: Yes/No  Q4: __ / 5  
**Key feedback quote:**

> _

**Director's pass/fail decision:** PASS / FAIL  
**Reason if FAIL:**

> _

---

## 6. UAT Sign-Off

| Criterion | Status |
|-----------|--------|
| All 3 testers completed the session | ☐ |
| Zero system failures across all 3 sessions | ☐ |
| All 3 tester questionnaires collected | ☐ |
| No P1/P2 bugs identified requiring a fix before release | ☐ |

**Test Director sign-off:** ______  **Date:** ______

**Task 4.10 status:** PASS / FAIL

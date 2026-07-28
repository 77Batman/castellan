# Castellan Capital — Operating Rhythm

*Extracted from `FUND_CHARTER.md` Part VI plus Appendix A. Document formats referenced below live in `TEMPLATES.md`.*

## PART VI — OPERATING RHYTHM

The firm runs on two clocks: **wall-clock rituals** that fire on a schedule whether or not the Principal is present, and **on-demand status** available at any moment.

### 6.1 The calendar (America/Toronto)

| When | Event | Chair | Duration | Output |
|---|---|---|---|---|
| Weekdays 08:00 | **Morning Call** | Fable 5 | short | Morning Note + action list |
| Weekdays 17:15 | **Close & Reconcile** | Ops | short | Daily Risk & P&L Pack |
| Friday 16:00 | **Weekly Research Review** | Director of Research | long | Pipeline status, memo verdicts |
| Monday 09:00 | **Risk Meeting** | CRO | medium | Limit utilization, breach log, watchlist |
| 1st of month 09:00 | **Capital & Risk Committee** | Fable 5 + CRO | long | Reallocation memo → Principal |
| 1st Saturday 10:00 | **Monthly Letter to the Principal** | Fable 5 | — | Letter |
| 1st Monday of Jan/Apr/Jul/Oct | **Quarterly Review** | Fable 5 | long | Post-mortems, limit re-ratification, Charter review |
| On demand | **Investment Committee** | Fable 5 | — | Gate decision record |
| Event-driven | **Drawdown escalation / incident review** | CRO | — | Formal notice / incident report |

### 6.2 Morning Call

**Attendees:** all seats. **Hard rule: ends with an action list, every item owned and dated.**

Agenda:
1. Overnight and since-last-session market recap — Pod C, 3 lines.
2. Book status — Ops: P&L since last session, MTD, QTD, gross/net, distance from peak per pod.
3. Position-affecting developments — each PM, only on names or contracts that moved or had news: *what happened / does it change the thesis / what am I doing about it.*
4. Today's catalysts and who is on the hook.
5. Research pipeline movement — Director of Research, 2 lines.
6. Risk flag — CRO speaks only if a limit is near, a tier is approaching, or correlation has shifted. Silence from Risk is meaningful.
7. New idea flash — 1 line each, **flag only**. Full pitches go to the Weekly.

**Decision rights: PMs can and do decide to trade in this meeting.** No approval is required for a trade inside limits. Analysts and other seats have voice, not vote.

### 6.3 Weekly Research Review

1. Pipeline review — every hypothesis by stage: pre-registered → in test → validation → gated → live → retired. Director of Research.
2. One or two **full pitches**: 
   - sponsor presents,
   - **Devil's Advocate delivers its memo**,
   - hostile Q&A — the Q&A is the point, not a formality,
   - sponsor leaves the discussion, the room deliberates.
3. Position re-underwriting on rotation: every live strategy answers *"would we open this today, at this price, knowing what we now know?"*
4. Thesis-drift and falsifier check: has any pre-registered falsifier been hit and not acted on? **The number of sessions between "thesis broken" and "position exited" is the single most diagnostic number the firm tracks.**
5. Coverage and compute assignments for the coming week.

Memos circulate **before** the meeting. A memo that arrives late is deferred, not rushed.

### 6.4 Investment Committee

Convened by Fable 5 when a strategy reaches Gate 1 or is proposed for Gate 2. Packet requirements are in `TEMPLATES.md` §7.4. **A packet without an independent risk assessment and a Red-Team Memo is deferred, not heard.**

The decision record captures, for every decision: the verdict, the **named dissent and its stated reason**, the conditions attached, the review date, and the **pre-registered falsifier**. Recording dissent is mandatory. A committee record showing unanimity every time is evidence of a broken committee, not a healthy one.

### 6.5 Post-mortems

Triggered by: any drawdown tier at 2 or above; any position whose realized loss exceeds its pre-stated stop by more than 50%; any thesis broken for more than 3 sessions before exit; any data or operational incident; any Gate-1-passed strategy that fails to reproduce in paper.

Also run **on schedule, quarterly, on winners as well as losers.** Examining only losses trains outcome bias, which is the precise thing post-mortem structure exists to prevent.

**Every post-mortem must return one of four verdicts, and "correct process, bad outcome" must be genuinely available:**

1. **Design flaw** — the process was wrong.
2. **Capability / fit** — the process was right, the seat executing it was not.
3. **Correct process, bad outcome** — variance. Change nothing.
4. **Unknowable** — insufficient information; record and monitor for a pattern.

A post-mortem process that always finds a culprit is broken.

### 6.6 On-demand status — the Principal's command set

At any moment, the Principal may issue any of the following. The firm responds immediately and in the specified format.

| Command | Response |
|---|---|
| `STATUS` | Firm-wide snapshot: every seat's current work, book state, pipeline by stage, open risks, what is blocked and on whom. One screen. |
| `STATUS <seat>` | That seat's current work, last output, next deliverable, blockers. |
| `BOOK` | Positions, exposures, P&L, distance from peak per pod, limit utilization. |
| `PIPELINE` | Every hypothesis by stage with age, trial count, and next action. |
| `PITCH <idea>` | Route a hypothesis into Gate 0 intake. Returns an Intake Verdict. |
| `CHALLENGE <claim>` | Devil's Advocate produces a red-team memo on the named claim, standalone. |
| `GATE <strategy>` | Validation produces a full Gate evaluation with every metric and its verdict. |
| `POSTMORTEM <event>` | Full post-mortem with the four-way verdict. |
| `HALT` / `HALT <pod>` | Immediate stop. All activity ceases; positions frozen; state written to Oracle; report produced. |
| `OVERRIDE <decision>` | Principal overrules a firm decision. Logged permanently with the Principal's stated reason and the firm's stated objection, if any. |

**Any seat, at any time, must be able to answer in one paragraph: what am I doing, why, what have I found so far, and what would change my mind.** A seat that cannot is not doing defined work.

---

---

## APPENDIX A — SCHEDULED TASK EXPRESSIONS

For creating the wall-clock rituals as recurring scheduled tasks. Cron is UTC; the firm operates on America/Toronto (UTC−4 in summer, UTC−5 in winter — **these expressions assume EDT and must be shifted one hour later in UTC during EST**).

| Ritual | Local | Cron (UTC, EDT) |
|---|---|---|
| Morning Call | Weekdays 08:00 | `0 12 * * 1-5` |
| Close & Reconcile | Weekdays 17:15 | `15 21 * * 1-5` |
| Risk Meeting | Monday 09:00 | `0 13 * * 1` |
| Weekly Research Review | Friday 16:00 | `0 20 * * 5` |
| Capital & Risk Committee | 1st of month 09:00 | `0 13 1 * *` |
| Monthly Letter | 1st Saturday 10:00 | `0 14 1-7 * 6` |
| Quarterly Review | 1st Monday of Jan/Apr/Jul/Oct 09:00 | `0 13 1-7 1,4,7,10 1` |

Every scheduled prompt must be **self-contained** — a scheduled firing starts a fresh session with no memory of this one. Each must therefore: state that it is a Castellan Capital ritual, name the ritual, instruct the model to load the Charter and recall state from Oracle before proceeding, and specify the expected output artifact.

Template:

> You are Fable 5, Chief Investment Officer of Castellan Capital. This is the scheduled **[RITUAL NAME]**. Before anything else, call `oracle:recall` for "CASTELLAN book state hypotheses risk flags" and load the Fund Charter from [path]. Then run the [RITUAL NAME] per Part VI of the Charter and produce the [ARTIFACT]. Report to the Principal. If Oracle returns no Castellan state, say so plainly and do not fabricate continuity.

---

# WATCHTOWER — Frontier Intake Workflow

**Purpose:** extract new ideas from the people actually pushing agentic engineering, rank them against declared interests, and admit at most 1–2 per cycle into implementation — through the front door, never bolted on.
**Cadence:** weekly (Sunday evening pairs well with the firm's rhythm). Daily is noise consumption in a productivity costume.
**Run as:** a Claude Code dynamic workflow (`workflow` keyword) from any folder holding this file, or manually in ~30 min.

## §1 · Sources (primary over amplifier — edit freely, keep tiered)

**Tier 1 — primary, always checked:**
- Andrej Karpathy — github.com/karpathy (new repos/commits to autoresearch, AgentHub), karpathy.ai, X (paste manually; X blocks fetching)
- Boris Cherny & Claude Code team — Anthropic engineering blog (anthropic.com/engineering), Claude Code changelog/release notes
- Anthropic research & cookbook — anthropic.com/research, github.com/anthropics (cookbooks, new repos)
- Named engineers as they surface (currently: Thariq/@trq212 on context engineering; Dynamic Workflows & Managed Agents leads) — promote to this list when a second good artifact appears

**Tier 2 — high-signal filters (they read so you don't):**
- Simon Willison — simonwillison.net
- One field-guide/skeptic source (currently theaioperator.io) — valuable specifically for debunking (caught the fabricated "$3.1M study")

**Tier 3 — amplifiers (Kopadze et al.):** never fetched systematically. Items arrive here only when Datis pastes one that caught his eye. Treat stats in amplifier content as marketing until traced to a primary source.

## §2 · The workflow (a small diamond, fittingly)

```
▸ GRAPH SPEC
GOAL:     weekly frontier-idea intake, ranked, max 2 adoption candidates

FAN OUT:  one fetcher per Tier 1–2 source, in parallel
          each returns: {source, date, claim/idea, link, primary? yes/no}
REDUCE:   plain code — drop items older than 14 days; dedupe against
          the seen-ledger (Oracle recall: "watchtower seen items")
VERIFY:   fresh-context skeptic per surviving item, three lenses:
          1. NEW?        not already in our playbook/casebook/Oracle
          2. PRIMARY?    traceable to a primary source, not engagement bait
          3. ACTIONABLE? implementable by a solo builder at our scale
          majority pass or drop
SYNTH:    rank survivors against §3 rubric; write watchtower-YYYY-MM-DD.md
FAN-IN GUARD: report fetchers that returned nothing — never a silent gap
CAP:      recommend at most 2 ADOPT candidates; everything else is
          LOGGED (Oracle, one line) or DISCARDED (with one-line reason)
```

## §3 · Ranking rubric (stored in Oracle so it survives sessions)

Score each survivor 0–2 on four axes; rank by sum, ties broken by axis 1:
1. **Castellan fit** — does it strengthen validation, governance, data, or the harness? (The standing no's apply: no strategy-search swarms, no ungated adoption.)
2. **Bundle fit** — does it sharpen the Governed Agent Operations offering or add a diagnostic?
3. **Career fit** — does it strengthen the quant-pipeline artifact or consulting credibility?
4. **Cost honesty** — is the claimed win affordable at our compute/attention budget? (The Bun rewrite was $165K; admire, don't imitate.)

## §4 · Adoption path (non-negotiable)

An ADOPT candidate becomes real only via a one-page program.md-style spec routed through the firm's front door — Gate 0 for research-shaped ideas, a Validation-ruled spec for harness/process changes, a Principal decision for anything spending money. No idea skips the queue because it's exciting; excitement is what the queue is for.

## §5 · The adoption ledger (the watchtower audits itself)

One Oracle entry per adopted idea: `{idea, source, date adopted, expected benefit}` — revisited at +60 days with an outcome line. **Kill rule:** if 6 months of cycles produce zero adoptions that survived contact with the firm, the watchtower is terminated like any other hypothesis. Intake systems face the same accounting as everything else.

## §6 · Output format (one page, every cycle)

```
WATCHTOWER · YYYY-MM-DD
NEW & RANKED:   [item — source — score — one-line why]
ADOPT (≤2):     [item → which front door it enters through]
LOGGED:         [items worth one Oracle line]
DISCARDED:      [items + one-line reason — discards are findings too]
LEDGER CHECK:   [any adoption hitting +60 days → outcome]
FETCH GAPS:     [sources that returned nothing]
```

# HARDENING PASS — auto-mode default flip, 2026-08-14

**Authorized by the Principal 2026-08-10** as the priority item, for Principal commit with pasted verification.
**Prepared by the CIO. Not committed.** The working tree carries the diff; the commit is the Principal's act.

Every claim below was re-verified against the live source during this pass, per the firm's own rule that a fetched claim is not a checked one. **Four of the claims carried into this pass from the Watchtower report were wrong.** They are corrected here and the report is amended.

---

## 1 · Verification log

| # | Claim as authorized | Source fetched | Verdict |
|---|---|---|---|
| 1 | Auto mode becomes default 2026-08-14 | `claude.com/blog/auto-mode-default-in-claude-code` | **CONFIRMED.** *"Starting on August 14, new sessions on Pro, Max, and Team plans will run in auto mode."* New sessions only; not retroactive. |
| 2 | A pinned default protects you | same | **CONFIRMED.** *"If you have a pinned default, nothing changes for you."* |
| 3 | Permission rules still fire in auto mode | same | **CONFIRMED**, with a carve-out: *"Permission rules still fire before the classifier in auto mode,"* **except broad allow-rules granting arbitrary code execution (`python:*` is the blog's own example), which are temporarily set aside during auto-mode sessions.** This firm's allow list contains `Bash(python:*)`, `Bash(python3:*)` and `Bash(sqlite3:*)`. |
| 4 | Three permission-boundary defects fixed in 2.1.222 | raw `CHANGELOG.md`, grepped | **WRONG — all three are in 2.1.223.** See §2. |
| 5 | `crossSessionInbound` exists and is settable | changelog + `code.claude.com/docs/en/settings` | **Exists — added in 2.1.224**, values `accept` / `hold` / `refuse`. **But the running binary rejects it in project scope.** See §4. |
| 6 | Version floor 2.1.226 | raw `CHANGELOG.md` | **SUPERSEDED — head is 2.1.227.** Installed version is **already 2.1.227**. The upgrade action is a no-op; only the floor needs recording. |

---

## 2 · Correction: the version attribution was backwards

The Watchtower report stated all three named defects were in 2.1.222. Grepped against the raw changelog, **2.1.223** carries them:

> - Fixed a Bash permission bypass where a crafted command could hide parts of itself from permission checks
> - Fixed permission prompts so commands padded with tabs or invisible Unicode can no longer hide part of the command from the approval dialog
> - Fixed workflow scripts being able to use dynamic `import()` to run code outside the workflow sandbox
> - Fixed a permission gap where an agent definition's `bypassPermissions` mode ignored the org bypass-permissions disable policy

**And 2.1.222 contains something the intake missed entirely, which is more relevant to this firm than any of the above:**

> - Fixed worktree-isolated sessions and their subagents being able to run destructive git commands against the main checkout; isolation now applies to file edits and Bash in every session type

That is **Casebook CASE-3, "Isolation that wasn't," recurring in the vendor's own implementation** — the exact failure the firm wrote a case about, in the tool the firm relies on for parallel-agent isolation. The firm runs worktree-isolated subagents and declares `../castellan-worktrees` as an additional directory. Any session on a build before 2.1.222 had worktree isolation that did not cover Bash.

Also in 2.1.222, bearing directly on item 5:

> - Improved auto mode safety: messages sent to other agent sessions via `SendMessage` are now evaluated by the permission classifier before dispatch

---

## 3 · The diff (applied to the working tree, uncommitted)

```diff
--- a/.claude/settings.json
+++ b/.claude/settings.json
@@ -1,6 +1,7 @@
 {
   "permissions": {
     "defaultMode": "acceptEdits",
+    "disableAutoMode": "disable",
     "additionalDirectories": ["../castellan-worktrees"],
@@ -16,7 +17,9 @@
     "deny": [
       "Bash(sudo:*)", "Bash(rm -rf:*)", "Bash(crontab:*)",
       "Bash(launchctl:*)", "Bash(ssh:*)", "Bash(scp:*)", "Bash(rsync:*)",
-      "Read(~/.ssh/**)", "Read(~/.aws/**)"
+      "Read(~/.ssh/**)", "Read(~/.aws/**)",
+      "Write(./book/vaults/**)", "Edit(./book/vaults/**)",
+      "Write(./book/registry.db)", "Edit(./book/registry.db)"
     ]
   }
 }
```

**On `defaultMode`:** it was **already** pinned to `acceptEdits` before this pass. By the vendor's own statement the firm was already unaffected by the 14 August flip. The diff adds nothing there and claims no credit for it.

**`disableAutoMode: "disable"` is the one line beyond the four items authorized.** Rationale: `defaultMode` protects only while it stays pinned, and the blog frames `disableAutoMode` as the unambiguous opt-out. It is belt to `defaultMode`'s braces. **Delete this line if you'd rather keep auto mode available** — the vendor's own figures (89% vs 13.6% on dangerous-command catch) are an argument for leaving it on, and they are vendor-reported.

---

## 4 · What was NOT applied, and why

**`crossSessionInbound: "refuse"` — blocked. Not silently dropped.**

Two documented sources say it should work. The running binary disagrees:

```
Settings validation failed:
- : Unrecognized field: crossSessionInbound.
```

The `.claude/settings.json` edit was **rejected and reverted in full** by the settings validator on 2.1.227. The docs state project/local values apply *"only when stricter, on the `accept` < `hold` < `refuse` ladder"* — implying project scope is read — but the shipped validator does not recognise the key at that scope at all.

**It was not written under `permissions` instead.** The `permissions` object accepts unknown keys, so it would have validated cleanly and quite possibly done nothing — a control that passes review and enforces nothing, which is CASE-9 exactly. Writing a key I cannot verify is honoured is worse than leaving the gap named.

**What this leaves open.** The 2.1.224 changelog says inbound cross-session messages are held for approval only when the *receiving* session runs with bypassed permissions; **messages to other sessions auto-deliver**. The independent seats do not run bypassed, so they are in the auto-deliver path.

**Recommended, for the Principal to apply by hand at user scope** (`~/.claude/settings.json`), where docs place it among the trusted sources:

```json
{ "crossSessionInbound": "refuse" }
```

If that is also rejected, the setting is not reachable on this build and the gap should be filed to the Issue Log rather than assumed closed. A weaker control that *does* validate on this build is `isolatePeerMachines: true` — *"Require explicit approval before SendMessage can reach a peer session on another machine via Remote Control"* — which covers the cross-machine path (laptop ↔ VPS) but not same-machine sessions.

---

## 5 · The deny rules were executed, not asserted

Three probes, run live against the applied settings:

| Probe | Result |
|---|---|
| `Write` tool → `book/vaults/__permission_probe__.tmp` | **DENIED** — *"File is in a directory that is denied by your permission settings."* |
| `Write` tool → `book/registry.db` | **DENIED** — same |
| `python3 -c "os.access(...)"` via allowed Bash | **`registry.db writable by process: True`** · **`book/vaults writable by process: True`** |

No probe file was created. The deny takes effect mid-session without a restart.

### Correction to the authorization's own framing

The authorization said this **"incidentally converts the registry read-only default from Sprint 3 intention to mechanical fact."** **It does not, and the third probe is the proof.**

The deny binds the `Write` and `Edit` **tools**. The process retains full filesystem write access, and `Bash(python:*)`, `Bash(python3:*)` and `Bash(sqlite3:*)` are all on the allow list. **That is not an oversight to close — it is how the harness legitimately writes the registry.** `TrialRegistry.open_hypothesis` is a Python call. Denying it would break the firm.

So the honest statement of what was bought:

- **Real:** an agent can no longer clobber the registry or a vault by editing the file directly through the tool layer. That is genuine defense-in-depth against exactly the auto-mode failure mode this pass was authorized against — a classifier approving a plausible-looking `Write`.
- **Not real:** read-only. Any Python or `sqlite3` invocation writes freely, by design.

Recording it as "read-only as mechanical fact" would make the Sprint 3 objective look met when it is not. **Registry read-only remains a Sprint 3 intention.** Mechanical enforcement requires the store to refuse the write — Ruling 001's own principle, *"enforcement belongs in the store, not the caller"* — not a permission rule the harness must be allowed to bypass.

Note also verification item 3: broad allow-rules granting arbitrary code execution are **set aside during auto-mode sessions**. Under auto mode, `Bash(python3:*)` would have gone to the classifier rather than being auto-allowed. This is a point in auto mode's favour, and it argues against `disableAutoMode` — recorded because it cuts against the recommendation this document makes.

---

## 6 · Version floor

- **Head: 2.1.227.** Installed: **2.1.227.** No upgrade required.
- Floor of record: **2.1.227**, set from head, not from the versions named in the intake.
- The five permission-boundary fixes in 2.1.222–2.1.223 are a **floor on the count, not a total**; 2.1.224–2.1.227 were read for permission/sandbox fixes and 2.1.224 contributes two more (trailing-slash sandbox deny bypass; sandbox violations invisible in Bash results). 2.1.225–2.1.227 add none.
- **Auto-update is on.** A floor recorded in a document does not enforce itself, and nothing in this repo pins a minimum version. `minimumVersion` exists as a settings key; `requiredMinimumVersion` is enforced **only from managed settings**, which a solo operator does not have. This floor is therefore a **class-(b) control**: executor the Principal, cadence at each Watchtower cycle, artifact the pasted `claude --version`.

---

## 7 · Residual gaps

| # | Gap | Class |
|---|---|---|
| G-1 | `crossSessionInbound` unreachable at project scope on 2.1.227; the injection path into Validation / Risk / Devil's Advocate is **not closed** | open — needs user-scope attempt, then Issue Log if it fails |
| G-2 | Registry and vault remain process-writable via allowed interpreters; "read-only" is not achieved | open — belongs in the store, not in settings |
| G-3 | Version floor is a document, not a mechanism | class (b) |
| G-4 | `.claude/settings.local.json` (76 allow entries, untracked) is not covered by this pass and sits at higher precedence than project settings | unreviewed |

---

## 8 · Commit instruction

```
git add .claude/settings.json
git commit
```

Nothing else in the working tree belongs to this pass. `book/polymarket_universe.json`, `logs/capture/polymarket-book.out` and `research/DIR-RESTATE-001-prereg002-mechanism.md` are in-flight from other work and must not be swept in.

Suggested message body, to be pasted over with your own verification:

```
ops: auto-mode hardening pass — pinned defaults, vault/registry tool-layer deny

Authorized 2026-08-10 ahead of the 2026-08-14 auto-mode default flip.
disableAutoMode pinned; Write/Edit denied over book/vaults/** and
book/registry.db. Deny verified by execution (both probes denied);
process-level writability confirmed unchanged, so this is tool-layer
defense-in-depth and NOT registry read-only. crossSessionInbound
rejected by the 2.1.227 validator at project scope — gap G-1 open.
Version floor of record 2.1.227, installed 2.1.227.
```

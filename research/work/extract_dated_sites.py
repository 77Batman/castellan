#!/usr/bin/env python3
"""
S3-D-014 · Director of Research · dated-clause site extraction.

Applies VALIDATION-SPEC-004 E-2's three recognizers to the eight prose fields of
PREREG-002 §21 (the payload's named source for those eight) plus the two scalar
fields the E-1 enumeration names.

WRITES NOTHING outside research/work/. No registry, no harness, no book/.
Zero trials: this is text processing on a markdown file.
"""
import re, json, sys, io

SRC = "/Users/<user>/projects/castellan-capital/research/PREREG-002-crypto-funding-basis.md"

# --- locate the section 21 fenced block ------------------------------------
lines = open(SRC, encoding="utf-8").read().split("\n")
start = None
for i, l in enumerate(lines):
    if l.startswith("## 21. THE SEAL BLOCK"):
        start = i
        break
assert start is not None
# first fence after the header
f0 = next(i for i in range(start, len(lines)) if lines[i].strip().startswith("```"))
f1 = next(i for i in range(f0 + 1, len(lines)) if lines[i].strip().startswith("```"))
block = lines[f0 + 1 : f1]
sys.stderr.write(f"section-21 fence: md lines {f0+2}..{f1} ({len(block)} lines)\n")

# --- split into `name = value` assignments ---------------------------------
ASSIGN = re.compile(r'^([a-z_]+)\s{2,}=\s(.*)$')
fields = {}
order = []
cur = None
buf = []
for l in block:
    m = ASSIGN.match(l)
    if m:
        if cur:
            fields[cur] = buf
        cur = m.group(1)
        order.append(cur)
        buf = [m.group(2)]
    else:
        if cur is not None:
            buf.append(l)
if cur:
    fields[cur] = buf

sys.stderr.write("fields found: " + ", ".join(order) + "\n")

# --- canonicalize a prose field to its string value -------------------------
# Payload doc section 3: "the text between `<field_name>   = \"` and its closing `\"`".
# Continuation lines in the block are indented to column 38 for alignment.  The
# alignment indent is presentation, not content.  TWO canonicalizations are
# computed because the choice is UNDEFINED in every governing document and the
# offsets differ between them.  See the register's finding on this.
IND = 37  # continuation-line alignment column measured below

def canon(rawlines, mode):
    parts = []
    for j, l in enumerate(rawlines):
        if j == 0:
            parts.append(l)
        else:
            if mode == "dedent":
                parts.append(l[IND:] if l[:IND].strip() == "" else l.lstrip())
            else:
                parts.append(l)
    s = "\n".join(parts).rstrip()
    # strip the surrounding double quotes of the literal
    if s.startswith('"'):
        s = s[1:]
    if s.endswith('"'):
        s = s[:-1]
    return s

# measure the true continuation indent from a long prose field
probe = fields["statement"][1]
IND = len(probe) - len(probe.lstrip())
sys.stderr.write(f"measured continuation indent = {IND}\n")

# --- E-2 recognizers --------------------------------------------------------
R_ISO = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
R_FORMULA = re.compile(r'\bC\s*(?:[+-]\s*\d+\s*(?:day|month|year)s?)?\b')
R_QTY = re.compile(r'\b\d+(?:\.\d+)?\s*(?:day|month|year)s?\b')
R_SPAN = re.compile(r'\[\s*(?:\d{4}-\d{2}-\d{2}|C)\s*,\s*(?:\d{4}-\d{2}-\d{2}|C)\s*\]')

TERM = re.compile(r'[.!?]\s')

def sentence_of(text, pos):
    lo = 0
    for m in TERM.finditer(text[:pos]):
        lo = m.end()
    m = TERM.search(text, pos)
    hi = m.end() if m else len(text)
    return text[lo:hi].strip().replace("\n", " ")[:400]

E1_PROSE = ["statement", "mechanism", "falsifier", "universe", "horizon",
            "success_criteria", "forward_kill_condition"]
# model_prior_provenance is NOT in E-1's enumerated list; forward_window_start and
# forward_window_min_length are, and are scalars.

def sites(field, text):
    out = []
    for m in R_ISO.finditer(text):
        out.append(dict(field=field, off=m.start(), text=m.group(0),
                        rec="ISO", sent=sentence_of(text, m.start())))
    for m in R_FORMULA.finditer(text):
        out.append(dict(field=field, off=m.start(), text=m.group(0),
                        rec="FORMULA", sent=sentence_of(text, m.start())))
    for m in R_SPAN.finditer(text):
        s = sentence_of(text, m.start())
        if R_QTY.search(s):
            out.append(dict(field=field, off=m.start(), text=m.group(0),
                            rec="SPAN", sent=s))
    return sorted(out, key=lambda d: d["off"])

report = {}
for mode in ("verbatim", "dedent"):
    per = {}
    for f in E1_PROSE:
        if f not in fields:
            per[f] = {"ERROR": "field absent from section-21 block"}
            continue
        t = canon(fields[f], mode)
        per[f] = dict(length=len(t), sites=sites(f, t))
    report[mode] = per

json.dump(report, open("/Users/<user>/projects/castellan-capital/research/work/dated_sites.json", "w"), indent=1)

# human-readable
out = io.StringIO()
for mode in ("dedent", "verbatim"):
    out.write(f"\n{'='*78}\nCANONICALIZATION = {mode}\n{'='*78}\n")
    tot = 0
    for f in E1_PROSE:
        d = report[mode][f]
        if "ERROR" in d:
            out.write(f"\n-- {f}: {d['ERROR']}\n"); continue
        out.write(f"\n-- {f}  (len {d['length']})  sites: {len(d['sites'])}\n")
        tot += len(d["sites"])
        for s in d["sites"]:
            out.write(f"   off {s['off']:6d}  {s['rec']:8s}  {s['text']!r}\n")
            out.write(f"        sent: {s['sent'][:200]}\n")
    out.write(f"\nTOTAL SITES ({mode}) = {tot}\n")
print(out.getvalue())

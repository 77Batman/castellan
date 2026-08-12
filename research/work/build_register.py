#!/usr/bin/env python3
"""S3-D-014 · builds the canonicalization-invariant site roster for the
dated_clauses registration payload.  Emits markdown rows.  Writes nothing
outside research/work/."""
import json, re, collections, sys
d = json.load(open("research/work/dated_sites.json"))
FIELDS = ["statement","mechanism","falsifier","universe","horizon",
          "success_criteria","forward_kill_condition"]

rows = []
for f in FIELDS:
    ded = d["dedent"][f]["sites"]; ver = d["verbatim"][f]["sites"]
    assert len(ded) == len(ver), f
    ord_ctr = collections.Counter()
    for a, b in zip(ded, ver):
        assert a["text"] == b["text"] and a["rec"] == b["rec"], (f, a, b)
        key = (a["rec"], a["text"])
        ord_ctr[key] += 1
        rows.append(dict(field=f, rec=a["rec"], text=a["text"],
                         ordinal=ord_ctr[key], off_ded=a["off"], off_ver=b["off"],
                         sent=a["sent"]))
print(f"# invariance check: {len(rows)} sites, ordinals stable across both canonicalizations",
      file=sys.stderr)
json.dump(rows, open("research/work/site_roster.json","w"), indent=1)

# how many offsets actually differ between canonicalizations?
diff = sum(1 for r in rows if r["off_ded"] != r["off_ver"])
print(f"# offsets differing between canonicalizations: {diff} of {len(rows)}", file=sys.stderr)

for i, r in enumerate(rows, 1):
    print(f"| {i} | `{r['field']}` | {r['rec']} | `{r['text']}` | {r['ordinal']} | {r['off_ded']} | {r['off_ver']} |")

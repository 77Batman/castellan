import json
rows = json.load(open("research/work/site_roster.json"))

# (field, recognizer, matched_text, ordinal) -> (tag, kind, date_expr)
CB = {
 ("statement","ISO","2020-01-01",1):        ("IS-START","PRECEDENT","2020-01-01"),
 ("statement","FORMULA","C",1):             ("IS-END","PRECEDENT","C"),
 ("falsifier","ISO","2020-01-01",1):        ("F002-IS-START","PRECEDENT","2020-01-01"),
 ("falsifier","FORMULA","C",1):             ("F002-IS-END","PRECEDENT","C"),
 ("universe","ISO","2020-01-01",1):         ("UNIV-SPAN-START","PRECEDENT","2020-01-01"),
 ("universe","FORMULA","C",1):              ("UNIV-SPAN-END","PRECEDENT","C"),
 ("universe","ISO","2025-09-18",1):         ("K7-TRIGGER","PRECEDENT","2025-09-18"),
 ("universe","ISO","2025-09-18",2):         ("K7-BLACKOUT","PRECEDENT","2025-09-18"),
 ("success_criteria","FORMULA","C + 187 days",1): ("SC-KC002-SURVIVAL","OBSERVATION","C + 187 days"),
 ("forward_kill_condition","FORMULA","C + 187 days",1): ("KC-002-OBS-DATE","OBSERVATION","C + 187 days"),
 ("forward_kill_condition","ISO","2027-01-31",1):       ("KC-002-OBS-DRAFTED","OBSERVATION","C + 187 days"),
 ("forward_kill_condition","FORMULA","C + 187 days",2): ("KC-002-OBS-GOVERNING","OBSERVATION","C + 187 days"),
 ("forward_kill_condition","FORMULA","C",2):            ("KC-002-WINDOW-START","OBSERVATION","C"),
 ("forward_kill_condition","FORMULA","C + 187 days",3): ("KC-002-WINDOW-END","OBSERVATION","C + 187 days"),
 ("forward_kill_condition","FORMULA","C ",1):           ("KC-002-NO-POST-C-EXCL","PRECEDENT","C"),
 ("forward_kill_condition","FORMULA","C + 187 days",4): ("KC-002-CL3-BOUNDARY","DEADLINE","C + 187 days"),
 ("forward_kill_condition","FORMULA","C",4):            ("KC-002-CLAUSE-5","OBSERVATION","C + 187 days"),
 ("forward_kill_condition","ISO","2027-01-31",8):       ("KC-002-CLAUSE-5-DRAFTED","OBSERVATION","C + 187 days"),
}
out = ["| # | field | rec | matched_text | ord | off-D | off-V | tag | kind | date_expr |",
       "|---:|---|---|---|---:|---:|---:|---|---|---|"]
n_cb = 0
for i, r in enumerate(rows, 1):
    k = (r["field"], r["rec"], r["text"], r["ordinal"])
    if k in CB:
        tag, kind, expr = CB[k]; n_cb += 1
        cells = f"**{tag}** | **{kind}** | `{expr}`"
    else:
        cells = f"PROV-{r['field'][:4].upper()}-{r['ordinal']} | **—/BLOCKED** | `{r['text'].strip()}`"
    out.append(f"| {i} | `{r['field']}` | {r['rec']} | `{r['text']}` | {r['ordinal']} | "
               f"{r['off_ded']} | {r['off_ver']} | {cells} |")
assert n_cb == 18, n_cb
open("research/work/rows.md","w").write("\n".join(out))
print("clause-bearing rows matched:", n_cb, "of", len(rows))

doc = "research/REGISTRATION-PAYLOAD-DATED-CLAUSES-PREREG-002.md"
t = open(doc).read()
assert "<!--ROWS-->" in t
open(doc,"w").write(t.replace("<!--ROWS-->", "\n".join(out)))
print("spliced into", doc)

import json, re
d = json.load(open("research/work/dated_sites.json"))["dedent"]
up = re.compile(r'\bC\s*[+-]\s*\d+\s*(?:DAY|MONTH|YEAR)S?\b')
print("=== uppercase 'C + N DAYS': FORMULA recognizer is case-sensitive, extracts BARE C ===")
for f, v in d.items():
    for s in v.get("sites", []):
        if s["rec"] == "FORMULA" and s["text"].strip() == "C" and up.search(s["sent"]):
            print(f"  {f} off {s['off']}  matched={s['text']!r}")
            print(f"      {s['sent'][:160]}")
n = sum(1 for v in d.values() for s in v.get("sites", []) if s["rec"] == "SPAN")
print(f"\n=== SPAN sites across all E-1 prose fields: {n}  (E-9 / E-21 have nothing to act on)")
lits = {s["text"] for v in d.values() for s in v.get("sites", [])}
print("\n=== literals absent from every E-1 field ===")
for t in ("2026-11-01", "2027-07-28", "2030-07-28", "2028-10-05"):
    print(f"  {t}: {'PRESENT' if t in lits else 'ABSENT'}")
print("\n=== matched_text carrying trailing whitespace ===")
for f, v in d.items():
    for s in v.get("sites", []):
        if s["rec"] == "FORMULA" and s["text"] != s["text"].strip():
            print(f"  {f} off {s['off']} matched={s['text']!r}")

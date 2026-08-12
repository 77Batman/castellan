import json, re
rows = json.load(open("research/work/site_roster.json"))
stamp = re.compile(r'\[R\d+[a-z()/0-9R]*,\s*$')
def is_stamp(r):
    if r["rec"] != "ISO": return False
    s = r["sent"]
    i = s.find(r["text"])
    if i < 0: return False
    return bool(re.search(r'\[R[-\d/()a-zA-Z]*,?\s*$', s[:i])) or bool(re.search(r'\bR\d+[a-z()]*[,/ ]\s*$', s[:i]))
cnt = {"stamp":0, "other":0}
for r in rows:
    r["stamp"] = is_stamp(r)
    cnt["stamp" if r["stamp"] else "other"] += 1
print("provenance revision-stamp ISO sites:", cnt["stamp"])
print("all other sites:", cnt["other"])
print()
print("--- NON-STAMP sites (the ones a kind value must describe) ---")
for i, r in enumerate(rows, 1):
    if not r["stamp"]:
        print(f"{i:3d} | {r['field']:22s} | {r['rec']:7s} | {r['text']!r:16s} | ord {r['ordinal']} | ded {r['off_ded']:6d} | {r['sent'][:110]}")
json.dump(rows, open("research/work/site_roster.json","w"), indent=1)

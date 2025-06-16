import json

def auto_add_rule(term, definition):
    path = "data/term_rules.json"
    with open(path, "r", encoding="utf-8") as f:
        rules = json.load(f)
    rules.append({"term": term, "definition": definition})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
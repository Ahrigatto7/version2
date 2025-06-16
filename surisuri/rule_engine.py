import json

def load_rules(rule_path="data/term_rules.json"):
    with open(rule_path, "r", encoding="utf-8") as f:
        return json.load(f)

def apply_rules_to_chart(saju_data, rules):
    results = []
    for rule in rules:
        conditions = rule.get("conditions", [])
        match = all(evaluate_condition(saju_data, cond) for cond in conditions)
        if match:
            results.append(rule.get("interpretation", ""))
    return results

def evaluate_condition(saju_data, condition):
    """
    조건 예시:
    {
        "type": "has_element",
        "target": "earthly_branches",
        "value": "午"
    }
    """
    cond_type = condition.get("type")
    target = condition.get("target")
    value = condition.get("value")

    target_data = saju_data.get(target, [])
    
    if cond_type == "has_element":
        return value in target_data
    elif cond_type == "count_greater_than":
        return target_data.count(value) > condition.get("threshold", 0)
    elif cond_type == "position_equals":
        # 특정 지지/천간이 특정 위치에 존재하는지 확인
        return saju_data.get(target) == value
    return False

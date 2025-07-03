# 파일: modules/rule_engine.py

from typing import List, Dict, Callable, Any

class RuleEngine:
    def __init__(self, rules: List[dict], custom_functions: Dict[str, Callable] = None):
        self.rules = rules
        self.custom_functions = custom_functions or {}

    def match_rules(self, saju_status: dict) -> List[dict]:
        matched = []
        for rule in self.rules:
            ok = True
            for cond in rule["conditions"]:
                # ["key", value] 형식 (기본 조건)
                if isinstance(cond, list) and len(cond) == 2:
                    if saju_status.get(cond[0], False) != cond[1]:
                        ok = False
                        break
                # {"custom_condition": "함수명"} 형식 (커스텀 논리)
                elif isinstance(cond, dict) and "custom_condition" in cond:
                    func = self.custom_functions.get(cond["custom_condition"])
                    if func is None or not func(saju_status):
                        ok = False
                        break
            if ok:
                matched.append(rule)
        return matched

    def explain(self, saju_status: dict, matched_rules: List[dict]) -> List[str]:
        explanations = []
        for rule in matched_rules:
            # 템플릿 활용 (상태 dict의 키 사용)
            if "explanation_template" in rule:
                try:
                    explanation = rule["explanation_template"].format(**saju_status)
                except Exception:
                    explanation = rule["result"]
                explanations.append(f"[{rule['rule_name']}] {explanation}")
            else:
                explanations.append(f"[{rule['rule_name']}] {rule['result']}")
        return explanations

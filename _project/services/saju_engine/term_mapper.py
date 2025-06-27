def get_month_branch_by_term(term_name):
    term_to_branch = {
        "입춘": "인", "경칩": "묘", "청명": "진", "입하": "사",
        "망종": "오", "소서": "미", "입추": "신", "백로": "유",
        "한로": "술", "입동": "해", "대설": "자", "소한": "축"
    }
    return term_to_branch.get(term_name, "미상")

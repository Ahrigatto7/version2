import json
from datetime import datetime

def get_month_ganji_from_terms(birth_date_str):
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    year = str(birth_date.year)

    with open("data/24solar_terms.json", encoding="utf-8") as f:
        terms = json.load(f)[year]

    term_to_branch = {
        "입춘": "인", "경칩": "묘", "청명": "진", "입하": "사",
        "망종": "오", "소서": "미", "입추": "신", "백로": "유",
        "한로": "술", "입동": "해", "대설": "자", "소한": "축"
    }

    sorted_terms = sorted(terms.items(), key=lambda x: x[1])
    last_term = "입춘"
    for term_name, term_date in sorted_terms:
        term_dt = datetime.strptime(term_date, "%Y-%m-%d")
        if birth_date < term_dt:
            break
        last_term = term_name

    month_branch = term_to_branch.get(last_term, "미상")
    return month_branch

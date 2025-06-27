
from .ganji import get_ganji
from .lunar_converter import solar_to_lunar
from .daewoon import calculate_daewoon
from .day_ganji import get_day_ganji
from .term_mapper import get_term
from .month_ganji import get_month_ganji
from .hour_ganji import get_hour_ganji
from .ohaeng import analyze_ohaeng

def analyze_saju(birthdate: str, gender: str, time_str: str) -> dict:
    """
    birthdate: 'YYYY-MM-DD'
    gender: 'M' or 'F'
    time_str: 'HH' (24-hour format)
    """
    # Step 1: Convert to lunar date
    lunar_date = solar_to_lunar(birthdate)

    # Step 2: Get term (seasonal node)
    term = get_term(birthdate)

    # Step 3: Calculate ganji components
    year_ganji, month_ganji = get_month_ganji(birthdate)
    day_ganji = get_day_ganji(birthdate)
    hour_ganji = get_hour_ganji(day_ganji, time_str)

    # Step 4: Daewoon (10-year luck cycle)
    daewoon_list = calculate_daewoon(birthdate, gender)

    # Step 5: Ohaeng (element analysis)
    ohaeng_result = analyze_ohaeng([year_ganji, month_ganji, day_ganji, hour_ganji])

    return {
        "lunar_date": lunar_date,
        "term": term,
        "year_ganji": year_ganji,
        "month_ganji": month_ganji,
        "day_ganji": day_ganji,
        "hour_ganji": hour_ganji,
        "daewoon": daewoon_list,
        "ohaeng": ohaeng_result
    }

heavenly_stems = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
earthly_branches = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

def calculate_saju(year, month, day, hour):
    year_ganji = get_year_ganji(year)
    month_ganji = get_fixed_month_ganji(month)
    day_ganji = get_fixed_day_ganji(day)
    hour_ganji = get_hour_ganji(day_ganji[0], hour)
    return {
        "year": f"{year_ganji[0]}{year_ganji[1]}",
        "month": f"{month_ganji[0]}{month_ganji[1]}",
        "day": f"{day_ganji[0]}{day_ganji[1]}",
        "hour": f"{hour_ganji[0]}{hour_ganji[1]}"
    }

def get_year_ganji(year):
    return heavenly_stems[(year - 4) % 10], earthly_branches[(year - 4) % 12]

def get_fixed_month_ganji(month):
    return heavenly_stems[(month + 1) % 10], earthly_branches[(month + 1) % 12]

def get_fixed_day_ganji(day):
    return heavenly_stems[day % 10], earthly_branches[day % 12]

def get_hour_ganji(day_gan, hour):
    hour_index = hour // 2 % 12
    return '무', earthly_branches[hour_index]

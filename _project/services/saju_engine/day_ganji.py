from datetime import datetime, timedelta

heavenly_stems = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
earthly_branches = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

def get_day_ganji(year, month, day):
    birth_date = datetime(year, month, day)
    base_date = datetime(1899, 1, 1)  # 기준일: 갑자일
    days_elapsed = (birth_date - base_date).days
    index = days_elapsed % 60
    stem = heavenly_stems[index % 10]
    branch = earthly_branches[index % 12]
    return stem, branch

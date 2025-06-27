# saju/daewoon.py

from saju.ganji import heavenly_stems, earthly_branches

def calculate_daewoon(year, month, day, hour, gender="남"):
    # TODO: 절기 기준 대운 시작 시점 계산
    # 성별/출생시간에 따라 순행/역행 결정
    # 여기선 단순히 10년 주기 간지만 반환

    start_index = ((year - 4) % 10 + 1) % 10
    daewoon_list = []
    for i in range(8):  # 80세까지 대운
        stem = heavenly_stems[(start_index + i) % 10]
        branch = earthly_branches[(start_index + i) % 12]
        daewoon_list.append(f"{stem}{branch}")
    return daewoon_list

def analyze_ohaeng(eight_chars):
    ohaeng_map = {
        '갑': '목', '을': '목',
        '병': '화', '정': '화',
        '무': '토', '기': '토',
        '경': '금', '신': '금',
        '임': '수', '계': '수',
        '자': '수', '축': '토', '인': '목', '묘': '목',
        '진': '토', '사': '화', '오': '화', '미': '토',
        '신': '금', '유': '금', '술': '토', '해': '수'
    }

    five_elements = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}

    for item in eight_chars.values():
        if isinstance(item, str) and len(item) == 2:
            for c in item:
                if c in ohaeng_map:
                    five_elements[ohaeng_map[c]] += 1

    max_element = max(five_elements, key=five_elements.get)
    return {
        "ohaeng_count": five_elements,
        "likely_yongshin": max_element
    }

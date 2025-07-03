import pandas as pd

def categorize_description(description: str, rules: dict) -> tuple:
    """
    사건 설명(description)을 읽고, 정의된 규칙에 따라 카테고리를 반환합니다.
    """
    # description이 문자열이 아닌 경우를 대비하여 문자열로 변환
    if not isinstance(description, str):
        return ('미분류', '미분류', '중립')

    for keyword, categories in rules.items():
        if keyword in description:
            return categories  # 첫 번째로 일치하는 규칙의 카테고리를 반환
    
    # 어떤 키워드와도 일치하지 않으면 '미분류'로 반환
    return ('미분류', '미분류', '중립')

def main():
    """메인 실행 함수"""

    # --- 1. 분류 규칙을 이곳에서 직접 수정하거나 추가할 수 있습니다. ---
    # 형식: "키워드": ("대분류", "중분류", "긍정/부정/중립")
    keyword_rules = {
        "결혼": ("인간관계", "결혼", "긍정"),
        "동거": ("인간관계", "연애", "긍정"),
        "이혼": ("인간관계", "이혼", "부정"),
        "헤어진다": ("인간관계", "이별", "부정"),
        "불화": ("인간관계", "불화", "부정"),

        "승진": ("직업", "승진", "긍정"),
        "관직을 얻는다": ("직업", "취업/임용", "긍정"),
        "시험합격": ("직업", "시험합격", "긍정"),
        "창업": ("직업", "창업", "중립"),
        "사업을 시작": ("직업", "창업", "중립"),
        "개업": ("직업", "창업", "중립"),
        "사직": ("직업", "퇴사/사직", "중립"),
        "직장을 전환": ("직업", "이직", "중립"),
        "실패": ("직업", "실패", "부정"),

        "발재": ("재물", "재물획득", "긍정"),
        "돈을 회수": ("재물", "재물획득", "긍정"),
        "파재": ("재물", "재물손실", "부정"),
        "돈을 썼다": ("재물", "지출", "중립"),
        "투자": ("재물", "투자", "중립"),

        "사망": ("건강/가족", "사망", "부정"),
        "病이 났다": ("건강/가족", "질병", "부정"),
        "수술": ("건강/가족", "질병", "부정"),
        "부친": ("건강/가족", "가족사", "중립"),
        "모친": ("건강/가족", "가족사", "중립"),

        "관재구설": ("사건사고", "소송/구설", "부정"),
        "감옥": ("사건사고", "수감", "부정")
    }

    input_filename = "life_events.csv"
    output_filename = "life_events_categorized.csv"

    try:
        df = pd.read_csv(input_filename)
        print(f"'{input_filename}' 파일을 성공적으로 읽었습니다. 총 {len(df)}개의 데이터.")
    except FileNotFoundError:
        print(f"오류: '{input_filename}'을 찾을 수 없습니다. 이전 스크립트를 먼저 실행해 데이터를 추출해주세요.")
        return

    # 각 설명에 대해 카테고리를 분류하는 함수를 적용
    categories = df['description'].apply(lambda x: categorize_description(x, keyword_rules))

    # 데이터프레임에 새로운 열들로 추가
    df[['category1', 'category2', 'outcome']] = pd.DataFrame(categories.tolist(), index=df.index)

    # 결과 저장
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print("\n" + "="*50)
    print(f"[성공] 데이터 규칙화가 완료되었습니다.")
    print(f"결과가 '{output_filename}' 파일로 저장되었습니다.")
    print("="*50)
    print("\n[샘플 결과 미리보기]")
    print(df[['description', 'category1', 'category2', 'outcome']].head())

if __name__ == "__main__":
    main()
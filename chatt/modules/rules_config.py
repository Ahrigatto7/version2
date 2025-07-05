# chatt/modules/rules_config.py

import os

def read_txt_md(filename):
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def read_docx(filename):
    from docx import Document
    doc = Document(filename)
    return [para.text.strip() for para in doc.paragraphs if para.text.strip()]

def read_pdf(filename):
    import pdfplumber
    lines = []
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.extend([line.strip() for line in text.split('\n') if line.strip()])
    return lines

def read_file_auto(filename):
    if filename.lower().endswith('.txt') or filename.lower().endswith('.md'):
        return read_txt_md(filename)
    elif filename.lower().endswith('.docx'):
        return read_docx(filename)
    elif filename.lower().endswith('.pdf'):
        return read_pdf(filename)
    else:
        raise Exception('지원하지 않는 파일 포맷입니다.')

# 예시 명리 파싱 (실전 활용시 문서 포맷에 맞게 직접 구현!)
def parse_myungri(lines):
    # 아래는 샘플, 실제 데이터 포맷에 맞춰 커스터마이즈!
    data = {
        "원국.일지": "축",
        "세운.지지": "진",
        "원국.십신": ["편관", "정관", "편인"]
    }
    return data

# 규칙 목록 예시
RULES = [
    {
        "name": "일지합+편관존재",
        "conditions": [
            {"target": "원국.일지", "relation": "합", "with": "세운.지지", "value": ["축", "진"]},
            {"target": "원국.십신", "relation": "존재", "value": "편관"}
        ],
        "outcome": "일지와 세운이 합, 편관이 있으면 직업·관계의 변동 가능성."
    },
    # 추가 규칙 계속 추가 가능!
]

def check_condition(cond, doc_data):
    rel = cond['relation']
    if rel == '합':
        return doc_data.get(cond['target']) in cond['value']
    elif rel == '존재':
        return cond['value'] in doc_data.get(cond['target'], [])
    elif rel == '개수':
        v = cond['value']
        return doc_data.get(cond['target'], []).count(v['십신명']) >= v.get('최소', 1)
    return False

def check_rules(doc_data):
    results = []
    for rule in RULES:
        if all(check_condition(cond, doc_data) for cond in rule['conditions']):
            results.append({"name": rule['name'], "outcome": rule['outcome']})
    return results

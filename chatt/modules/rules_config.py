import os, json, re

# 1. 파일 파서
def read_lines(filename):
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

# 2. 군집화/블록화
def blockify(lines, filename):
    blocks, block = [], None
    for line in lines:
        if re.match(r'^<사례\s*\d+>|^사례\d*[\):]', line):
            if block: blocks.append(block)
            block = {"type":"사례", "title":line, "팔자":[], "대운":[], "본문":[], "tags":[], "meta":{"source":filename}}
        elif block:
            if re.match(r"^[甲乙丙丁戊己庚辛壬癸⼀-⿕]+.*[(乾)(坤)]?$", line): block["팔자"].append(line)
            elif re.match(r"^[戌亥子丑寅卯申未午酉辰巳⺒]+$", line): block["팔자"].append(line)
            elif line.startswith("대운"): continue
            elif re.match(r"^[甲乙丙丁戊己庚辛壬癸⼀-⿕]+", line): block["대운"].append(line)
            elif re.match(r"^[戌亥子丑寅卯申未午酉辰巳⺒]+", line): block["대운"].append(line)
            elif "제압방식" in line or "구조" in line or "格" in line:
                block["tags"].extend(re.findall(r"[傷官印財比劫官殺格構造제압적포귀격합충파형穿墓공망운응기생극화허투]", line))
                block["본문"].append(line)
            else: block["본문"].append(line)
        else:
            blocks.append({"type":"해설문", "text":line, "meta":{"source":filename}})
    if block: blocks.append(block)
    for b in blocks:
        if "tags" in b: b["tags"] = list(set(b["tags"]))
    return blocks

# 3. 중복제거/병합
def merge_blocks(existing, new):
    seen, merged = set(), []
    for b in existing + new:
        key = json.dumps(b, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            merged.append(b)
            seen.add(key)
    return merged

# 4. RULES 예시 (UI에서 동적 추가도 가능)
DEFAULT_RULES = [
    {"keyword": "직업", "label": "진로"},
    {"keyword": "관계", "label": "대인관계"},
]

def apply_rules(blocks, rules):
    for b in blocks:
        tags = set(b.get('tags', []))
        for rule in rules:
            if '본문' in b and any(rule['keyword'] in txt for txt in b['본문']):
                tags.add(rule['label'])
        b['tags'] = list(tags)
    return blocks

# 5. AI 요약/해설 (openai 필요)
def ai_generate(text, openai_key, prompt="이 내용을 명리 용어로 간단 요약:"):
    import openai
    openai.api_key = openai_key
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system", "content": prompt},
            {"role":"user", "content": text}
        ]
    )
    return resp.choices[0].message.content.strip()

import json
import os
import streamlit as st

DB_PATH = "knowledge_base.json"

@st.cache_data
def load_kb():
    """지식 베이스 파일을 캐싱하여 빠르게 로드합니다."""
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            if content:
                return json.loads(content)
    return {}

def save_kb(data):
    """지식 베이스 파일에 저장하고 캐시를 초기화합니다."""
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.cache_data.clear()
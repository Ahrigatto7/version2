# 파일 경로: modules/db_handler.py

import json
import os
import streamlit as st

KNOWLEDGE_DIR = "knowledge" # 지식 파일들이 있는 폴더 경로

@st.cache_data
def load_kb(): # 👈 이름을 다시 load_kb로 통일했습니다.
    """'knowledge' 폴더 안의 모든 .json 파일을 읽어 하나의 딕셔너리로 통합합니다."""
    print(f">> '{KNOWLEDGE_DIR}' 폴더에서 모든 지식 파일을 로드합니다...")
    
    combined_knowledge = {}
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR)
        return {}
        
    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith('.json'):
            file_path = os.path.join(KNOWLEDGE_DIR, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # 파일이 비어있는 경우를 대비
                    content = f.read()
                    if content:
                        data = json.loads(content)
                        combined_knowledge.update(data)
            except (json.JSONDecodeError, FileNotFoundError):
                print(f"경고: '{filename}' 파일을 읽는 데 실패했습니다.")
                continue
    return combined_knowledge

def save_kb(data_to_save: dict, target_filename: str): # 👈 저장 함수 이름도 간단하게 통일했습니다.
    """새로운 지식 데이터를 지정된 파일에 병합하여 저장합니다."""
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR)

    if not target_filename.endswith('.json'):
        target_filename += '.json'
    
    file_path = os.path.join(KNOWLEDGE_DIR, target_filename)
    
    existing_data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    
    # 기존 데이터에 새로운 데이터를 병합
    for category, content in data_to_save.items():
        if category not in existing_data:
            existing_data[category] = content
        elif isinstance(existing_data.get(category), dict):
            existing_data[category].update(content)
        elif isinstance(existing_data.get(category), list):
            existing_data[category].extend(content)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    st.cache_data.clear()
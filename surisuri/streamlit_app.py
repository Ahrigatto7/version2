import streamlit as st
from gpt_handler import analyze_long_text
from rule_engine import apply_rules_to_chart, load_rules, analyze_with_rules
from visualizer import show_visualizations
import json
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="Codex 분석기", layout="wide")
st.title("💬 Codex 통합 분석 솔루션")
st.caption("AI, 규칙 기반 분석, 데이터 시각화를 한 번에 수행합니다.")

# --- 세션 상태 초기화 ---
if 'saju_data' not in st.session_state:
    st.session_state['saju_data'] = None
if 'user_text_input' not in st.session_state:
    st.session_state['user_text_input'] = ""

# --- 데이터 입력 섹션 ---
input_mode = st.radio("입력 방법 선택", ["파일 업로드", "직접 입력 (JSON)"], horizontal=True)

if input_mode == "파일 업로드":
    uploaded_file = st.file_uploader("📂 분석할 JSON 파일을 업로드하세요.", type="json")
    if uploaded_file:
        try:
            saju_data = json.load(uploaded_file)
            st.session_state['saju_data'] = saju_data
            st.success("파일을 성공적으로 로드했습니다.")
            with st.expander("로드된 데이터 미리보기"):
                st.json(saju_data)
        except Exception as e:
            st.error(f"파일 처리 중 오류 발생: {e}")
            st.session_state['saju_data'] = None
else:
    user_text_input = st.text_area("🔍 분석할 JSON 텍스트를 붙여넣으세요:", height=250, key="json_input")
    if user_text_input:
        st.session_state['user_text_input'] = user_text_input


# --- 유틸리티 함수 ---
def get_output_filename(base_name):
    saju_data = st.session_state.get('saju_data')
    if saju_data and 'id' in saju_data and 'client_name' in saju_data:
        client_name = saju_data.get('client_name', 'client')
        file_id = saju_data.get('id', 'data')
        return f"{client_name}_{file_id}_{base_name}"
    return base_name

# --- 분석 실행 섹션 ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

# --- 1. GPT 분석 ---
with col1:
    st.markdown("### 🤖 AI 분석")
    if st.button("GPT로 심층 분석", use_container_width=True, type="primary"):
        input_data = st.session_state.get('saju_data') or st.session_state.get('user_text_input')
        if input_data:
            with st.spinner("GPT가 데이터를 분석 중입니다..."):
                prompt = json.dumps(input_data, ensure_ascii=False, indent=2) if isinstance(input_data, dict) else input_data
                result = analyze_long_text(prompt)
                st.text_area("📘 GPT 요약 결과", result, height=300)
                fname = get_output_filename("gpt_result.md")
                st.download_button("📥 결과 저장", data=result, file_name=fname)
        else:
            st.warning("분석할 데이터를 먼저 입력하거나 업로드해주세요.")

# --- 2. 규칙 기반 분석 ---
with col2:
    st.markdown("### ⚙️ 규칙 기반 분석")
    if st.button("규칙 엔진으로 분석", use_container_width=True):
        results = None
        saju_data = st.session_state.get('saju_data')
        user_text_input = st.session_state.get('user_text_input')
        
        with st.spinner("규칙을 적용하여 분석 중입니다..."):
            if saju_data:
                saju_chart_data = saju_data.get("saju")
                if saju_chart_data:
                    rules = load_rules()
                    results = apply_rules_to_chart(saju_chart_data, rules)
                else:
                    st.error("'saju' 키를 찾을 수 없습니다.")
            elif user_text_input:
                results = analyze_with_rules(user_text_input)
            else:
                st.warning("분석할 데이터를 먼저 입력하거나 업로드해주세요.")

        if results:
            if "error" in results:
                st.error(results["error"])
            else:
                st.success(f"{len(results)}개의 일치하는 규칙을 찾았습니다.")
                st.json(results)
                # 결과 저장
                os.makedirs("export", exist_ok=True)
                df = pd.DataFrame(results, columns=["해석"])
                csv_fname = get_output_filename("rule_results.csv")
                df.to_csv(f"export/{csv_fname}", index=False, encoding="utf-8-sig")
                st.success(f"CSV 파일 저장 완료! (export/{csv_fname})")

# --- 3. 데이터 시각화 ---
with col3:
    st.markdown("### 📊 데이터 시각화")
    if st.button("업로드 데이터 시각화", use_container_width=True):
        saju_data = st.session_state.get('saju_data')
        if saju_data:
            with st.spinner("차트를 생성 중입니다..."):
                show_visualizations(saju_data)
        else:
            st.warning("시각화를 위해서는 파일을 업로드해야 합니다.")

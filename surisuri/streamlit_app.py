import streamlit as st
from gpt_handler import analyze_long_text
from rule_engine import analyze_with_rules
from visualizer import show_visualizations
import json
import pandas as pd
import os

st.set_page_config(page_title="Codex 분석기", layout="wide")
st.title("💬 Codex (GPT) 기반 분석기")

# 입력 모드 선택
input_mode = st.radio("입력 방법 선택", ["직접 입력", "파일 업로드"])
user_input = ""

# 입력 처리
if input_mode == "직접 입력":
    user_input = st.text_area("🔍 분석할 텍스트를 입력하세요:", height=300)
elif input_mode == "파일 업로드":
    uploaded_file = st.file_uploader("📂 JSON 파일 업로드 (input_saju_data.json)", type="json")
    if uploaded_file:
        try:
            user_input = json.load(uploaded_file)
            user_input = json.dumps(user_input, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"파일 처리 오류: {e}")

# 분석 버튼: GPT
if st.button("🚀 GPT 분석 실행") and user_input:
    st.markdown("## ✅ GPT 분석 결과")
    result = analyze_long_text(user_input)
    st.text_area("📘 GPT 요약 결과", result, height=300)

    st.download_button("📥 결과 저장 (.md)", data=result, file_name="gpt_results.md")

# 분석 버튼: 규칙 기반
if st.button("⚙️ 규칙 기반 분석") and user_input:
    st.markdown("## 🧠 규칙 기반 분석 결과")
    result = analyze_with_rules(user_input)
    st.json(result)

    # 저장 디렉토리 확인
    os.makedirs("export", exist_ok=True)

    # 결과 저장
    df = pd.DataFrame([result])
    df.to_csv("export/results.csv", index=False)
    df.to_excel("export/results.xlsx", index=False)
    st.success("CSV / XLSX 저장 완료!")

# 시각화 버튼
if st.button("📊 시각화 보기") and user_input:
    st.markdown("## 📈 분석 시각화")
    show_visualizations()

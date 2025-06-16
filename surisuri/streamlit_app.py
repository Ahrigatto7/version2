import streamlit as st
from gpt_handler import analyze_long_text
from rule_engine import analyze_with_rules
from visualizer import show_visualizations
import json
import pandas as pd
import os

st.set_page_config(page_title="autobook", layout="wide")

st.title("🔍 auto")

input_mode = st.radio("입력 방법 선택", ["직접 입력", "파일 업로드"])

if input_mode == "직접 입력":
    user_input = st.text_area("사주/분석 텍스트 입력", height=300)
elif input_mode == "파일 업로드":
    uploaded_file = st.file_uploader("JSON 파일 업로드 (input_saju_data.json)", type="json")
    if uploaded_file:
        user_input = uploaded_file.read().decode("utf-8")

if st.button("GPT 분석 실행"):
    st.markdown("## ✅ GPT 분석 결과")
    result = analyze_long_text(user_input)
    st.text_area("GPT 요약 결과", result, height=300)

    st.download_button("📥 결과 저장 (.md)", data=result, file_name="results.md")

if st.button("규칙 기반 분석"):
    st.markdown("## 🧠 규칙 기반 분석 결과")
    result = analyze_with_rules(user_input)
    st.json(result)

    df = pd.DataFrame([result])
    df.to_csv("export/results.csv", index=False)
    df.to_excel("export/results.xlsx", index=False)
    st.success("CSV / XLSX 저장 완료!")

if st.button("📊 시각화 보기"):
    st.markdown("## 📈 분석 시각화")
    show_visualizations()

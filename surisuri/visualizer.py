import plotly.express as px
import pandas as pd
import streamlit as st

def show_visualizations(saju_data):
    """
    입력된 사주 데이터의 오행 분포를 분석하여 막대 차트로 시각화합니다.
    """
    # 1. 시각화할 데이터 추출
    five_elements_data = saju_data.get("saju", {}).get("five_elements")

    if not five_elements_data:
        st.warning("시각화할 오행(five_elements) 데이터가 파일에 없습니다.")
        return

    # 2. DataFrame 생성
    try:
        df = pd.DataFrame(list(five_elements_data.items()), columns=['오행', '점수'])
        
        # 3. Plotly로 막대 차트 생성
        fig = px.bar(
            df, 
            x='오행', 
            y='점수', 
            title="사주 오행 분포",
            color='오행',
            labels={'오행': '구성 요소', '점수': '강도 점수'}
        )
        fig.update_layout(
            xaxis_title="오행",
            yaxis_title="점수",
            font=dict(family="Malgun Gothic, Apple Gothic, sans-serif", size=14)
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"시각화 차트 생성 중 오류가 발생했습니다: {e}")

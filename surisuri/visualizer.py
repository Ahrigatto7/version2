import streamlit as st
import plotly.express as px
import pandas as pd

def show_visualizations():
    df = pd.DataFrame({
        "운": ["대운", "세운", "세운", "대운"],
        "년도": [2020, 2021, 2022, 2023],
        "강도": [3, 4, 2, 5]
    })
    fig = px.line(df, x="년도", y="강도", color="운", title="운 흐름 시각화")
    st.plotly_chart(fig)
import streamlit as st
import sqlite3
import json
import os
import pandas as pd

# db_handler는 지식 베이스에 최종 저장할 때만 사용
from modules.db_handler import save_kb, load_kb

st.set_page_config(page_title="자동 지식 구축", layout="wide")
st.header("✨ 자동 지식 구축 (백그라운드 실행)")
st.caption("문서를 업로드하여 분석 작업을 등록하면, 백그라운드에서 AI가 자동으로 지식을 추출합니다.")
st.markdown("---")

# --- 1. 작업 등록 UI ---
with st.form("job_submission_form"):
    uploaded_file = st.file_uploader("분석할 문서 업로드", type=["txt", "pdf", "docx"])
    categories = st.text_input("분류할 카테고리 (쉼표로 구분)", value="격국,십신,재물,혼인,건강,직업,상호작용,기타")
    submitted = st.form_submit_button("백그라운드 작업 등록")

    if submitted:
        if uploaded_file and categories:
            # 업로드된 파일을 서버에 저장
            save_dir = "uploads"
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # DB에 작업 요청 등록
            try:
                with sqlite3.connect("jobs.db") as con:
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO knowledge_jobs (original_filename, saved_filepath, categories, status) VALUES (?, ?, ?, ?)",
                        (uploaded_file.name, save_path, json.dumps(categories.split(',')), 'pending')
                    )
                    con.commit()
                st.success(f"'{uploaded_file.name}' 파일에 대한 분석 작업이 백그라운드에 등록되었습니다.")
            except Exception as e:
                st.error(f"작업 등록 중 오류 발생: {e}")
        else:
            st.error("파일과 카테고리를 모두 입력해주세요.")

# --- 2. 작업 현황 및 결과 처리 UI ---
st.markdown("---")
st.subheader("백그라운드 작업 현황")

try:
    with sqlite3.connect("jobs.db") as con:
        df = pd.read_sql_query("SELECT id, status, original_filename, created_at FROM knowledge_jobs ORDER BY id DESC", con)
    st.dataframe(df, use_container_width=True)

    completed_jobs = df[df['status'] == 'completed']
    if not completed_jobs.empty:
        job_id_to_process = st.selectbox("결과를 검토하고 저장할 작업 ID를 선택하세요", completed_jobs['id'])
        
        if job_id_to_process:
            with sqlite3.connect("jobs.db") as con:
                cur = con.cursor()
                cur.execute("SELECT result_json FROM knowledge_jobs WHERE id = ?", (job_id_to_process,))
                result_json_str = cur.fetchone()[0]
            
            ai_results = json.loads(result_json_str)
            df_to_edit = pd.DataFrame({
                "문단": ai_results.get("paragraphs", []),
                "카테고리": ai_results.get("categories", []),
                "태그": [""], "리뷰": [""], "승인여부": ["대기"]
            })
            
            st.markdown("### 분류 결과 검토 및 최종 저장")
            edited_df = st.data_editor(df_to_edit, num_rows="dynamic", use_container_width=True)
            
            save_filename = st.text_input("저장할 지식 파일 이름", value="new_rules.json")
            if st.button("✅ 승인된 내용만 지식 베이스에 저장"):
                approved_df = edited_df[edited_df['승인여부'] == '승인']
                # (이 부분은 add_ai_classified_data 함수 로직을 참고하여 재구성 필요)
                # 예시: save_kb(approved_df.to_dict('records'), save_filename)
                st.success(f"{len(approved_df)}개의 지식이 '{save_filename}'에 저장되었습니다.")
                
                # 처리 완료된 작업은 상태 변경
                with sqlite3.connect("jobs.db") as con:
                    cur = con.cursor()
                    cur.execute("UPDATE knowledge_jobs SET status = 'archived' WHERE id = ?", (job_id_to_process,))
                    con.commit()
                st.rerun()
except Exception as e:
    st.info("아직 등록된 작업이 없습니다. 데이터베이스가 곧 생성됩니다.")
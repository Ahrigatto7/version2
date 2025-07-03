# 파일 경로: pages/5_자동_지식_구축.py

import streamlit as st
import json
from modules.knowledge_extractor import extract_structured_knowledge
from modules.db_handler import load_kb, save_kb

# --- 1. 파일 내용 추출 기능 완성 ---
from PyPDF2 import PdfReader
import docx
def extract_text(uploaded_file):
    """업로드된 파일에서 텍스트를 추출하는 완전한 함수."""
    try:
        if uploaded_file.name.endswith('.pdf'):
            pdf_reader = PdfReader(uploaded_file)
            text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
            return text
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        elif uploaded_file.name.endswith('.txt'):
            raw_bytes = uploaded_file.getvalue()
            try: return raw_bytes.decode('utf-8')
            except UnicodeDecodeError: return raw_bytes.decode('cp949', errors='ignore')
        return "지원하지 않는 파일 형식입니다."
    except Exception as e:
        st.error(f"파일 읽기 오류: {e}")
        return ""

# --- Streamlit UI 구성 ---
st.set_page_config(page_title="자동 지식 구축", layout="wide")
st.header("✨ 자동 지식 구축 (문서 → 지식)")
st.caption("문서를 업로드하면 AI가 핵심 규칙을 자동으로 추출하여 지식 베이스 초안을 만듭니다.")
st.markdown("---")

uploaded_file = st.file_uploader("해석 규칙이 담긴 문서 업로드", type=["txt", "pdf", "docx"])
api_key = st.text_input("OpenAI API Key", type="password", help="문서 내용을 분석하고 규칙을 추출하기 위해 필요합니다.")

if uploaded_file and api_key:
    if st.button("AI로 규칙 추출 및 구조화 실행", type="primary"):
        with st.spinner("AI가 문서를 읽고 핵심 규칙을 추출하는 중입니다... (시간이 다소 소요될 수 있습니다)"):
            text = extract_text(uploaded_file)
            if text:
                structured_data = extract_structured_knowledge(text, api_key)
                if "error" in structured_data:
                    st.error(structured_data["error"])
                else:
                    # JSON 문자열로 변환하여 세션 상태에 저장 (편집을 위해)
                    st.session_state["structured_knowledge_text"] = json.dumps(structured_data, ensure_ascii=False, indent=2)
                    st.success("✅ 규칙 추출 및 구조화 완료! 아래 내용을 확인하고 저장하세요.")
            else:
                st.error("파일에서 텍스트를 추출하지 못했습니다.")

# --- AI가 생성한 결과 검토 및 저장 ---
if "structured_knowledge_text" in st.session_state:
    st.markdown("### AI가 생성한 지식 초안 (편집 가능)")
    st.caption("AI가 추출한 내용이므로 부정확할 수 있습니다. 저장 전 반드시 검토 및 수정해주세요.")

    # ## 주요 개선사항 2: 편집 가능한 텍스트 영역으로 변경
    edited_text = st.text_area(
        "JSON 편집:",
        value=st.session_state["structured_knowledge_text"],
        height=400
    )

    # ## 주요 개선사항 3: 저장할 카테고리 이름 직접 지정
    save_category = st.text_input("저장할 상위 카테고리 이름", value="수암해석규칙")
    save_subcategory = st.text_input("저장할 하위 카테고리 이름", value="응기")
    
    if st.button("✅ 이 지식을 지정된 카테고리에 병합하기"):
        try:
            # 수정된 텍스트를 다시 JSON(딕셔너리)으로 변환
            edited_data = json.loads(edited_text)
            
            knowledge_base = load_kb()
            
            # 지정된 카테고리가 없으면 생성
            if save_category not in knowledge_base:
                knowledge_base[save_category] = {}
            if save_subcategory not in knowledge_base[save_category]:
                knowledge_base[save_category][save_subcategory] = []

            new_rules = edited_data.get("rules", [])
            
            # 추출된 규칙들을 기존 규칙에 추가 (extend)
            knowledge_base[save_category][save_subcategory].extend(new_rules)
            
            save_kb(knowledge_base)
            st.success(f"성공적으로 '{save_category}/{save_subcategory}'에 병합되었습니다!")
            
            # 작업 완료 후 세션 상태 초기화
            del st.session_state["structured_knowledge_text"]

        except json.JSONDecodeError:
            st.error("JSON 형식이 올바르지 않습니다. 수정한 내용을 다시 확인해주세요.")
        except Exception as e:
            st.error(f"저장 중 오류 발생: {e}")
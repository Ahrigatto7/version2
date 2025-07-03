# 파일명: Saju_AI_Assistant.py

import streamlit as st
from datetime import datetime
import json

# --- Langchain 및 AI 모델 관련 라이브러리 ---
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain.tools import tool

# --- 피드백 관련 라이브러리 ---
from streamlit_feedback import streamlit_feedback

# --- 기존 모듈 임포트 ---
from modules.analyzer_engine import SajuAnalyzer, get_saju_info
from modules.db_handler import load_kb

# --- 1. AI 및 도구 초기화 ---
st.set_page_config(page_title="사주 AI 비서", page_icon="🤖")
st.title("🤖 사주 AI 비서")
st.caption("AI의 답변이 도움이 되셨나요? 피드백을 남겨주시면 AI가 더 똑똑해집니다.")

try:
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=st.secrets.get("OPENAI_API_KEY"))
    knowledge_base = load_kb()
except Exception as e:
    st.error(f"초기화 중 오류가 발생했습니다: {e}")
    st.info("'.streamlit/secrets.toml' 파일에 OpenAI API 키를 올바르게 설정했는지 확인해주세요.")
    st.stop()
# --- 2. 도구(Tools) 정의 (내부 로직 완성) ---
@tool
def saju_analysis_tool(name: str, birth_date: str, birth_time: str, gender: str, is_lunar: bool = False) -> str:
    """
    사람의 이름, 생년월일, 성별을 입력받아 사주 명식을 분석하고 종합 리포트를 반환합니다.
    생년월일은 'YYYY-MM-DD', 시간은 'HH:MM' 형식이어야 합니다.
    """
    try:
        birth_dt = datetime.strptime(birth_date, "%Y-%m-%d").date()
        birth_t = datetime.strptime(birth_time, "%H:%M").time()
        
        saju_info = get_saju_info(birth_dt, birth_t, is_lunar)
        analyzer = SajuAnalyzer(knowledge_base)
        analysis_result = analyzer.analyze(saju_info) # 딕셔너리 결과 받기
        
        # 결과를 사람이 읽기 좋은 리포트 형식으로 가공
        report = f"## 🔮 {name} ({gender})님 사주 분석 리포트\n"
        report += f"**생년월일:** {birth_date} {birth_time} ({'음력' if is_lunar else '양력'})\n\n"
        report += "### **사주팔자 원국**\n"
        for key, value in analysis_result.get("saju_info", {}).get("원국", {}).items():
            report += f"- **{key}:** {value}\n"
        report += f"\n{analysis_result.get('interpretation_text', '')}"
        return report
    except Exception as e:
        return f"사주 분석 중 오류가 발생했습니다: {e}. 입력 형식을 확인해주세요 (예: '1990-05-10', '14:30')."

@tool
def knowledge_search_tool(query: str) -> str:
    """
    사주 명리학의 특정 용어, 개념, 규칙(예: 격국, 십신, 자오충)에 대해 질문하면 지식 베이스에서 관련 정보를 찾아 답변합니다.
    """
    try:
        # 간단한 키워드 기반 검색 로직
        results = []
        for main_topic, content in knowledge_base.items():
            if query in main_topic:
                results.append(f"## {main_topic}\n{json.dumps(content, ensure_ascii=False, indent=2)}")
            if isinstance(content, dict):
                for sub_topic, data in content.items():
                    if query in sub_topic:
                        results.append(f"### {sub_topic}\n{json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if not results:
            return f"'{query}'에 대한 정보를 지식 베이스에서 찾지 못했습니다."
        return "\n---\n".join(results)
    except Exception as e:
        return f"지식 검색 중 오류가 발생했습니다: {e}"

tools = [saju_analysis_tool, knowledge_search_tool]

# --- 3. AI 에이전트 설정 ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 명리학 전문가 AI 비서입니다. 사용자의 질문 의도를 파악하여, 'saju_analysis_tool' 또는 'knowledge_search_tool' 중 가장 적합한 도구를 사용해 답변해야 합니다. 모든 답변은 한국어로 제공해주세요."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- 4. Streamlit UI 구성 ---
# 대화/피드백 기록 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [AIMessage(content="안녕하세요! 저는 당신의 사주 분석을 돕는 AI 비서입니다. 무엇을 도와드릴까요?")]

# 이전 대화 기록 표시
for i, msg in enumerate(st.session_state.chat_history):
    with st.chat_message(msg.type):
        st.markdown(msg.content)
    if msg.type == "ai":
        streamlit_feedback(feedback_type="thumbs", key=f"feedback_{i}")

# 사용자 입력 처리
if query := st.chat_input("이름, 생년월일시, 성별을 알려주시거나 궁금한 용어를 물어보세요."):
    st.chat_message("human").write(query)
    
    with st.chat_message("ai"):
        with st.spinner("AI 비서가 생각 중입니다..."):
            response = agent_executor.invoke({
                "input": query,
                "chat_history": st.session_state.chat_history
            })
            st.markdown(response["output"])
    
    # 대화 기록에 추가
    st.session_state.chat_history.append(HumanMessage(content=query))
    st.session_state.chat_history.append(AIMessage(content=response["output"]))
# 파일 경로: modules/knowledge_extractor.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict

# --- AI가 생성할 JSON의 구조를 미리 정의 ---
class InterpretationRule(BaseModel):
    rule_name: str = Field(description="규칙의 이름 (예: '허자의 출현 응기')")
    conditions: List[str] = Field(description="규칙이 적용되기 위한 조건 목록")
    result: str = Field(description="조건이 충족될 때의 해석 결과")

class StructuredKnowledge(BaseModel):
    rules: List[InterpretationRule] = Field(description="문서에서 추출된 사주 해석 규칙 목록")

def extract_structured_knowledge(text_content: str, api_key: str) -> Dict:
    """
    입력된 텍스트에서 사주 해석 규칙을 추출하고 JSON 구조로 반환합니다.
    """
    # 1. LLM 모델 정의
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=api_key)
    
    # 2. JSON 출력 파서 설정
    # Pydantic 모델을 기반으로 출력 형식을 강제합니다.
    parser = JsonOutputParser(pydantic_object=StructuredKnowledge)
    
    # 3. AI에게 역할을 부여하는 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_template(
        "당신은 사주 명리학의 대가입니다. 아래 제공된 텍스트를 분석하여, "
        "핵심적인 해석 규칙들을 찾아주세요. 각 규칙을 이름, 조건, 결과로 나누어 "
        "JSON 형식으로 정리해야 합니다.\n"
        "{format_instructions}\n\n"
        "## 분석할 텍스트:\n{text}"
    )
    
    # 4. LCEL 체인 구성
    chain = prompt | llm | parser
    
    # 5. 체인 실행 및 결과 반환
    try:
        response = chain.invoke({
            "text": text_content,
            "format_instructions": parser.get_format_instructions(),
        })
        return response
    except Exception as e:
        return {"error": f"AI 규칙 추출 중 오류 발생: {e}"}
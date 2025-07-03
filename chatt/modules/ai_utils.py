# 파일 경로: modules/ai_utils.py

import streamlit as st
from transformers import pipeline
from typing import List

# --------------------------------------------------
# 방법 1: OpenAI API를 사용하는 분류 함수
# --------------------------------------------------
def ai_classify_paragraphs(paragraphs: List[str], api_key: str, categories: List[str]) -> List[str]:
    """OpenAI API를 사용해 문단들을 분류합니다. (v1.0.0 이상 호환)"""
    if not api_key:
        return ["API 키 필요"] * len(paragraphs)

    try:
        client = openai.OpenAI(api_key=api_key)
    except Exception as e:
        return [f"(OpenAI 모듈 초기화 실패: {e})"] * len(paragraphs)

    results = []
    for para in paragraphs:
        prompt = f"다음 텍스트를 '{', '.join(categories)}' 카테고리 중 가장 적합한 것 하나로만 분류해서, 카테고리 이름만 정확하게 답해줘.\n\n텍스트: \"{para}\""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0
            )
            result = response.choices[0].message.content.strip().replace("'", "").replace('"', '')
            if result not in categories:
                result = "분류 실패"
        except Exception as e:
            error_message = str(e)
            if "authentication" in error_message.lower():
                result = "API 키 인증 실패"
            else:
                result = "API 호출 오류"
        results.append(result)
    return results

# --------------------------------------------------
# 방법 2: 로컬 AI 모델을 사용하는 분류 함수 (추가된 부분)
# --------------------------------------------------
@st.cache_resource
def load_local_classifier():
    """
    Hugging Face의 zero-shot-classification 파이프라인을 로드하고 캐싱합니다.
    """
    print(">> 로컬 AI 모델을 최초로 로딩합니다... (시간이 소요될 수 있습니다)")
    return pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

def local_ai_classify(paragraphs: List[str], categories: List[str]) -> List[str]:
    """
    캐싱된 로컬 AI 모델과 배치 처리를 사용하여 문단을 빠르게 분류합니다.
    """
    try:
        # 1. 캐싱된 모델을 즉시 불러옵니다.
        classifier = load_local_classifier()
        
        # 2. 문단 리스트 전체를 한 번에 모델에 전달하여 '배치 처리'합니다.
        #    반복문(for loop)을 사용하는 것보다 훨씬 빠릅니다.
        outputs = classifier(paragraphs, categories, multi_label=False)
        
        # 3. 결과에서 카테고리 이름만 추출합니다.
        #    출력 형태가 단일 항목일 때와 여러 항목일 때를 모두 고려합니다.
        if isinstance(outputs, dict): # 문단이 하나일 경우
            return [outputs['labels'][0]]
        else: # 문단이 여러 개일 경우
            return [output['labels'][0] for output in outputs]
            
    except ImportError:
        return ["'transformers' 라이브러리가 필요합니다. 'pip install transformers torch sentencepiece'를 실행해주세요."] * len(paragraphs)
    except Exception as e:
        return [f"로컬 AI 오류: {e}"] * len(paragraphs)
# --------------------------------------------------
# 보조 기능: Gensim을 이용한 텍스트 요약
# --------------------------------------------------
def auto_summarize_text(text, ratio=0.2):
    """Gensim 기반 텍스트 요약 (OpenAI 필요 없음)"""
    try:
        from gensim.summarization import summarize
        if len(text) < 200: # 너무 짧은 텍스트는 원본 반환
            return text
        summary = summarize(text, ratio=ratio)
        if not summary:
            return text[:max(150, int(len(text) * ratio))] + "..."
        return summary
    except Exception as e:
        return f"Gensim 요약 실패: {e}"
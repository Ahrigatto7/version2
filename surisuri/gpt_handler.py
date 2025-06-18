import openai
import os
from dotenv import load_dotenv
import textwrap

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- 1. 최신 버전(v1.x)의 OpenAI 클라이언트 초기화 ---
# API 키를 환경 변수에서 가져와 클라이언트를 생성합니다.
try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"OpenAI 클라이언트 초기화 실패: {e}")
    client = None

def chunk_text(text, max_length=1500):
    """텍스트를 최대 길이에 맞춰 청크로 나눕니다."""
    return textwrap.wrap(text, max_length, break_long_words=False, replace_whitespace=False)

def gpt_analyze(prompt, model="gpt-3.5-turbo", temperature=0.4, max_tokens=1500):
    """
    주어진 프롬프트를 사용하여 GPT 모델을 호출하고 결과를 반환합니다.
    """
    if not client:
        return "[ERROR] OpenAI client is not initialized. Check your API key."

    try:
        # --- 2. 새로운 API 호출 방식으로 변경 ---
        messages = [{"role": "user", "content": prompt}]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # --- 3. 응답 접근 방식 변경 ---
        return response.choices[0].message.content
    
    except openai.APIConnectionError as e:
        return f"[ERROR] OpenAI API 서버에 연결할 수 없습니다: {e}"
    except openai.RateLimitError as e:
        return f"[ERROR] OpenAI API 사용량 한도를 초과했습니다: {e}"
    except openai.APIStatusError as e:
        return f"[ERROR] OpenAI API 오류가 발생했습니다 (상태 코드: {e.status_code}): {e.response}"
    except Exception as e:
        return f"[ERROR] 알 수 없는 오류가 발생했습니다: {e}"

def analyze_long_text(text):
    """
    긴 텍스트를 청크로 나누어 각각 분석하고 결과를 통합합니다.
    """
    chunks = chunk_text(text)
    if not chunks:
        return "분석할 텍스트가 없습니다."
        
    full_response = []
    for i, chunk in enumerate(chunks):
        # 각 청크를 개별적으로 분석
        analysis_result = gpt_analyze(chunk)
        full_response.append(analysis_result)

    return "\n\n".join(full_response)

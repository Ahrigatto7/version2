import openai
import textwrap

openai.api_key = os.getenv("OPENAI_API_KEY")

def chunk_text(text, max_length=1500):
    return textwrap.wrap(text, max_length, break_long_words=False, replace_whitespace=False)

def gpt_analyze(prompt, model="gpt-3.5-turbo", temperature=0.4, max_tokens=1024):
    try:
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"[ERROR] GPT 호출 실패: {str(e)}"

def analyze_long_text(text, system_instruction=None):
    chunks = chunk_text(text)
    results = []
    for i, chunk in enumerate(chunks):
        prompt = f"{system_instruction or ''}\n\n{chunk}"
        result = gpt_analyze(prompt)
        results.append(f"Part {i+1}: {result}")
    return "\n\n".join(results)
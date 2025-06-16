import openai
import os
from dotenv import load_dotenv
import textwrap

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def chunk_text(text, max_length=1500):
    return textwrap.wrap(text, max_length, break_long_words=False)

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
        return f"[ERROR] {str(e)}"

def analyze_long_text(text):
    chunks = chunk_text(text)
    return "\n\n".join([gpt_analyze(c) for c in chunks])

# 파일명: worker.py

import sqlite3
import json
import time
import os
import re
from itertools import chain
from PyPDF2 import PdfReader
import docx

# modules 폴더의 AI 유틸리티를 가져옵니다.
from modules.ai_utils import local_ai_classify
from modules.db_handler import save_kb # 최종 저장을 위해 save_kb를 사용

def setup_database():
    """jobs.db 데이터베이스와 테이블을 생성합니다."""
    with sqlite3.connect("jobs.db") as con:
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_jobs (
                id INTEGER PRIMARY KEY,
                original_filename TEXT NOT NULL,
                saved_filepath TEXT NOT NULL,
                categories TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                result_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        con.commit()

def extract_text(filepath):
    """파일 경로를 받아 텍스트를 추출하는 함수."""
    try:
        if filepath.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                pdf_reader = PdfReader(f)
                return "".join([page.extract_text() or "" for page in pdf_reader.pages])
        elif filepath.endswith('.docx'):
            doc = docx.Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        elif filepath.endswith('.txt'):
            with open(filepath, 'rb') as f:
                raw_bytes = f.read()
                try: return raw_bytes.decode('utf-8')
                except UnicodeDecodeError: return raw_bytes.decode('cp949', errors='ignore')
        return None
    except Exception as e:
        print(f"텍스트 추출 오류: {e}")
        return None

def process_pending_job():
    """'pending' 상태의 작업을 하나 가져와 처리합니다."""
    job_processed = False
    with sqlite3.connect("jobs.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM knowledge_jobs WHERE status = 'pending' ORDER BY id LIMIT 1")
        job = cur.fetchone()

        if job:
            job_id, _, filepath, categories_json, _, _, _ = job
            job_processed = True
            print(f"▶️ 작업 시작: Job ID {job_id}, File: {filepath}")
            
            cur.execute("UPDATE knowledge_jobs SET status = 'running' WHERE id = ?", (job_id,))
            con.commit()

            try:
                text = extract_text(filepath)
                if text:
                    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
                    cat_list = json.loads(categories_json)
                    
                    results = local_ai_classify(paragraphs, cat_list)
                    
                    # 결과를 JSON 형태로 변환
                    output_data = {"paragraphs": paragraphs, "categories": results}
                    result_json_str = json.dumps(output_data, ensure_ascii=False)
                    
                    cur.execute("UPDATE knowledge_jobs SET status = 'completed', result_json = ? WHERE id = ?", (result_json_str, job_id))
                    print(f"✅ 작업 완료: Job ID {job_id}")
                else:
                    raise ValueError("파일에서 텍스트를 추출하지 못했습니다.")
            except Exception as e:
                cur.execute("UPDATE knowledge_jobs SET status = 'failed', result_json = ? WHERE id = ?", (str(e), job_id))
                print(f"❌ 작업 실패: Job ID {job_id}, Error: {e}")
            
            con.commit()
    return job_processed

if __name__ == "__main__":
    setup_database()
    print("백그라운드 작업자(worker)를 시작합니다. (Ctrl+C로 종료)")
    while True:
        if not process_pending_job():
            time.sleep(5) # 할 일이 없으면 5초 대기
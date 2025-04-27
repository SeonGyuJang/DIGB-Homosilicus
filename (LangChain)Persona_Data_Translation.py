import json
import os
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

from tqdm import tqdm
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

# ========== 1. 환경변수 로드 ==========
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # NOTE : .env 파일 필요
MODEL_NAME = "gemini-2.0-flash"

# ========== 2. 경로 설정 ==========
INPUT_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\Persona_Data_Top_n_domains_Random_Extraction\Persona_Part_1_to_3.json")
OUTPUT_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\Persona_Data_Top_n_domains_Random_Extraction\(KR)Persona_Part_1_to_3.json")

# ========== 3. 모델 설정 ==========
llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=1,
)

# ========== 4. 프롬프트 & 체인 설정 ==========
prompt_template = PromptTemplate(
    input_variables=["persona", "domain"],
    template="""
다음은 영어로 작성된 페르소나와 연구 도메인 설명입니다.

[페르소나]
{persona}

[연구 도메인]
{domain}

각 항목을 자연스럽고 전문적으로 한국어로 번역해주세요.
반드시 JSON 형식으로 답변하세요.

출력 형식:
{{
    "persona": "번역된 페르소나",
    "general domain (top 1 percent)": "번역된 도메인"
}}
"""
)
parser = JsonOutputParser()
chain = prompt_template | llm | parser

# ========== 5. 데이터 로딩 ==========
def load_data(path: Path) -> List[Dict]:
    """도메인별 JSON 파일을 읽어 리스트로 반환"""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    records = []
    for domain, personas in data.items():
        for persona_info in personas:
            records.append({
                "persona": persona_info["persona"],
                "domain": domain,
                "idx": persona_info["idx"]
            })
    return records

# ========== 6. 데이터 저장 ==========
def save_data(path: Path, data: List[Dict]) -> None:
    """리스트를 다시 도메인별로 묶어 JSON 형태로 저장"""
    domain_to_personas = defaultdict(list)

    for item in data:
        domain = item["general domain (top 1 percent)"]  # 번역된 도메인 이름
        domain_to_personas[domain].append({
            "persona": item["persona"],
            "general domain (top 1 percent)": item["general domain (top 1 percent)"],
            "idx": item["idx"]
        })

    with path.open("w", encoding="utf-8") as f:
        json.dump(domain_to_personas, f, ensure_ascii=False, indent=2)

# ========== 7. 페르소나 번역 (batch 처리 + 실패 재시도) ==========
def translate_personas(records: List[Dict], batch_size: int = 20, max_retry: int = 3) -> List[Dict]:
    """레코드를 batch 단위로 번역 (빠른 처리 + 실패 재시도)"""
    translated = []

    for i in tqdm(range(0, len(records), batch_size), desc="Translating Personas (Batch)"):
        batch_records = records[i:i + batch_size]

        batch_inputs = [
            {
                "persona": record["persona"],
                "domain": record["domain"],
            }
            for record in batch_records
        ]

        # 재시도 로직
        for attempt in range(1, max_retry + 1):
            try:
                batch_outputs = chain.batch(
                    batch_inputs,
                    config={"max_concurrency": 100}  # 병렬 요청 최대 100개
                )
                # 번역 결과에 원본 idx 추가
                for output, original in zip(batch_outputs, batch_records):
                    output["idx"] = original["idx"]
                translated.extend(batch_outputs)
                break  # 성공했으면 반복 종료
            except Exception as e:
                print(f"[{attempt}/{max_retry}] 번역 실패, 재시도 중... 오류: {e}")
                if attempt == max_retry:
                    print(f"최종 재시도 실패: 해당 batch 건너뜀")
                else:
                    continue

    return translated

# ========== 8. 메인 함수 ==========
def main():
    print("데이터 로딩 중...")
    records = load_data(INPUT_PATH)

    print(f"총 {len(records)}개 페르소나 로드 완료.")
    print("번역 시작...")
    translated_records = translate_personas(records)

    print("번역 완료, 저장 중...")
    save_data(OUTPUT_PATH, translated_records)

    print("모든 작업 완료!")

# ========== 9. 엔트리포인트 ==========
if __name__ == "__main__":
    main()

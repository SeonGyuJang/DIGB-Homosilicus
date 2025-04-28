import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

# ========== 1. 환경 변수 로드 ==========
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # NOTE: .env 파일 필요
MODEL_NAME = "gemini-2.0-flash"

# ========== 2. 경로 설정 ==========
INPUT_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(EN)PERSONA_DATA_10000.jsonl")
OUTPUT_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(KR)PERSONA_DATA_10000.jsonl")

# ========== 3. 모델 설정 ==========
llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=1,
)

# ========== 4. 프롬프트 & 체인 설정 ==========
prompt_template = PromptTemplate(
    input_variables=["persona", "domain"],
    template="""다음은 영어로 작성된 페르소나와 연구 도메인 설명입니다.

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

# ========== 5. 데이터 로딩/저장 함수 ==========
def load_jsonl(path: Path) -> List[Dict]:
    records = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

def save_jsonl(path: Path, data: List[Dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

# ========== 6-1. batch 방식 페르소나 번역 ==========
def translate_personas_batch(records: List[Dict], batch_size: int = 20, max_retry: int = 3) -> List[Dict]:
    translated = []
    for i in tqdm(range(0, len(records), batch_size), desc="Translating Personas (Batch)"):
        batch_records = records[i:i + batch_size]

        batch_inputs = [
            {
                "persona": record["persona"],
                "domain": record["general domain (top 1 percent)"],
            }
            for record in batch_records
        ]

        idx_list = [record.get("idx") for record in batch_records]

        for attempt in range(1, max_retry + 1):
            try:
                batch_outputs = chain.batch(
                    batch_inputs,
                    config={"max_concurrency": 20}
                )
                for output, idx in zip(batch_outputs, idx_list):
                    translated.append({
                        "persona": output["persona"],
                        "general domain (top 1 percent)": output["general domain (top 1 percent)"],
                        "idx": idx
                    })
                break
            except Exception as e:
                print(f"[{attempt}/{max_retry}] 번역 실패 (idx 목록: {idx_list}), 재시도 중... 오류: {e}")
                if attempt == max_retry:
                    print(f"최종 재시도 실패 (idx 목록: {idx_list}): 해당 batch 건너뜀")
                else:
                    continue
    return translated


# ========== 6-2. invoke 방식 페르소나 번역 ==========
def translate_personas_invoke(records: List[Dict], max_retry: int = 3) -> List[Dict]:
    translated = []
    for record in tqdm(records, desc="Translating Personas (Single Invoke)"):
        input_data = {
            "persona": record["persona"],
            "domain": record["general domain (top 1 percent)"],
        }
        idx = record.get("idx")

        for attempt in range(1, max_retry + 1):
            try:
                output = chain.invoke(input_data)
                translated.append({
                    "persona": output["persona"],
                    "general domain (top 1 percent)": output["general domain (top 1 percent)"],
                    "idx": idx
                })
                break
            except Exception as e:
                print(f"[{attempt}/{max_retry}] idx={idx} 번역 실패, 재시도 중... 오류: {e}")
                if attempt == max_retry:
                    print(f"최종 재시도 실패: idx={idx} 건너뜀")
                else:
                    continue
    return translated

# ========== 7. 누락된 IDX 찾기 ==========
def find_missing_idx(all_records: List[Dict], translated_records: List[Dict]) -> List[int]:
    original_idx_set = {record.get("idx") for record in all_records}
    translated_idx_set = {record.get("idx") for record in translated_records}
    missing_idx = sorted(list(original_idx_set - translated_idx_set))
    return missing_idx

# ========== 8. 메인 함수 ==========
def main(mode: str):
    print("데이터 로딩 중...")
    all_records = load_jsonl(INPUT_PATH)
    print(f"총 {len(all_records)}개 페르소나 로드 완료.")

    if mode == "full":
        print("전체 번역 모드 실행 중...")
        translated_records = translate_personas_batch(all_records)

    elif mode == "retry_missing":
        print("누락된 idx만 재번역 모드 실행 중...")
        existing_translated = load_jsonl(OUTPUT_PATH)
        missing_idx = find_missing_idx(all_records, existing_translated)

        if not missing_idx:
            print("누락된 idx가 없습니다. 작업 종료합니다.")
            return

        print(f"누락된 {len(missing_idx)}개 idx 발견:")
        print(missing_idx)

        missing_records = [record for record in all_records if record.get("idx") in missing_idx]
        new_translated = translate_personas_invoke(missing_records)

        # 기존 번역 + 신규 번역 합치기
        merged_records = existing_translated + new_translated
        merged_records.sort(key=lambda x: x.get("idx"))  # idx 기준 정렬
        translated_records = merged_records

    else:
        raise ValueError(f"잘못된 mode: {mode}")

    print("저장 중...")
    save_jsonl(OUTPUT_PATH, translated_records)
    print("모든 작업 완료!")

# ========== 9. 엔트리포인트 ==========
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        choices=["full", "retry_missing"],
        default="full",
        help="full: 전체 번역 / retry_missing: 누락된 idx만 재번역"
    )
    args = parser.parse_args()
    main(args.mode)

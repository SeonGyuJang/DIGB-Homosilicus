import json
import os
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

# ========== 경로 설정 ==========
INPUT_JSONL = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(KR)PERSONA_DATA_10000.jsonl")
RESULTS_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results\(KR)LangChain_EXPERIMENT_RESULTS_10000")
OUTPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results_by_domain")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ========== 1. 도메인별 idx 분류 ==========
print("[1/3] 도메인별 idx 분류 중...")
domain_to_indices = defaultdict(list)

with open(INPUT_JSONL, "r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line)
            domain = entry.get("general domain (top 1 percent)")
            idx = entry.get("idx")
            if domain and idx is not None:
                domain_to_indices[domain].append(idx)
        except json.JSONDecodeError as e:
            print(f"[!] JSON 디코딩 오류: {e}")

# ========== 2. 실험 결과 수집 ==========
print("[2/3] 실험 결과 수집 중...")
domain_to_results = defaultdict(list)

for domain, indices in tqdm(domain_to_indices.items(), desc="도메인별 처리"):
    for idx in indices:
        result_path = RESULTS_DIR / f"Person_{idx}.json"
        if result_path.exists():
            try:
                with open(result_path, "r", encoding="utf-8") as f:
                    result_data = json.load(f)
                    domain_to_results[domain].append({
                        "idx": idx,
                        "result": result_data
                    })
            except Exception as e:
                print(f"[!] 오류 - idx={idx}: {e}")
        else:
            print(f"[!] 결과 파일 없음: {result_path}")

# ========== 3. 결과 파일 저장 ==========
print("[3/3] 도메인별 JSON 저장 중...")
for domain, results in domain_to_results.items():
    domain_filename = f"{domain.replace('/', '_')}.json"
    output_path = OUTPUT_DIR / domain_filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

print("✅ 도메인별 결과 병합 완료.")


'''
< 후처리 >
번역 과정에서 도메인의 번역 결과가 달라서(Ex. 재무 or 재무 금융 or 재정 등)
다른 도메인으로 인식하는 결과가 발생하였음. 
이 부분은 수동으로 후처리하였음.

domain_mapping = {
    "경제학": "경제학",
    "공학": "공학",
    "엔지니어링": "공학",
    "금융": "금융학",
    "재무": "금융학",
    "재무_금융": "금융학",
    "재정": "금융학",
    "법": "법학",
    "법률": "법학",
    "법학": "법학",
    "사회학": "사회학",
    "수학": "수학",
    "역사": "역사학",
    "역사학": "역사학",
    "철학": "철학",
    "컴퓨터과학": "컴퓨터과학",
    "환경 과학": "환경과학",
    "환경과학": "환경과학"
}


'''
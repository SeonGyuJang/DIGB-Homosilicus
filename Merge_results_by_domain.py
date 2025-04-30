import json
import argparse
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

parser = argparse.ArgumentParser(description="도메인별 실험 결과 병합 및 정규화 스크립트")
parser.add_argument('--count_domain', action='store_true', help='도메인별 페르소나 개수만 출력하고 종료')
args = parser.parse_args()

INPUT_JSONL = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(KR)PERSONA_DATA_10000.jsonl")
RESULTS_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results\(KR)LangChain_EXPERIMENT_RESULTS_10000")
OUTPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results_by_domain")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

domain_mapping = {
    "경제학": "경제학",
    "공학": "공학",
    "엔지니어링": "공학",
    "금융": "금융학",
    "재무": "금융학",
    "재무/금융": "금융학",
    "재무_금융": "금융학",
    "재정": "금융학",
    "법": "법학",
    "법률": "법학",
    "법학": "법학",
    "사회학": "사회학",
    "연구 도메인: 사회학": "사회학",
    "수학": "수학",
    "역사": "역사학",
    "역사학": "역사학",
    "철학": "철학",
    "컴퓨터 과학": "컴퓨터과학",
    "컴퓨터과학": "컴퓨터과학",
    "환경 과학": "환경과학",
    "환경과학": "환경과학"
}

print("[1/4] 도메인별 idx 분류 중...")
raw_domain_to_indices = defaultdict(list)

with open(INPUT_JSONL, "r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line)
            domain = entry.get("general domain (top 1 percent)")
            idx = entry.get("idx")
            if domain and idx is not None:
                raw_domain_to_indices[domain].append(idx)
        except json.JSONDecodeError as e:
            print(f"[!] JSON 디코딩 오류: {e}")

if args.count_domain:
    print("\n매핑된 도메인 기준 페르소나 개수:")

    mapped_domain_count = defaultdict(int)
    for raw_domain, idx_list in raw_domain_to_indices.items():
        mapped = domain_mapping.get(raw_domain)
        if not mapped:
            mapped = "매핑 안됨"
        mapped_domain_count[mapped] += len(idx_list)

    sorted_mapped = sorted(mapped_domain_count.items(), key=lambda x: x[1], reverse=True)
    for mapped, count in sorted_mapped:
        print(f"- {mapped:10}: {count}명")
    exit(0)


print("[2/4] 실험 결과 수집 중...")
mapped_domain_to_results = defaultdict(list)

for raw_domain, indices in tqdm(raw_domain_to_indices.items(), desc="도메인별 처리"):
    mapped_domain = domain_mapping.get(raw_domain)
    if not mapped_domain:
        print(f"[!] 매핑되지 않은 도메인: {raw_domain}")
        continue

    for idx in indices:
        result_path = RESULTS_DIR / f"Person_{idx}.json"
        if result_path.exists():
            try:
                with open(result_path, "r", encoding="utf-8") as f:
                    result_data = json.load(f)
                    mapped_domain_to_results[mapped_domain].append({
                        "idx": idx,
                        "result": result_data
                    })
            except Exception as e:
                print(f"[!] 오류 - idx={idx}: {e}")
        else:
            print(f"[!] 결과 파일 없음: {result_path}")

print("[3/4] 병합된 도메인별 결과 저장 중...")
for domain, entries in mapped_domain_to_results.items():
    output_path = OUTPUT_DIR / f"{domain}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

print("도메인 통합 완료 (저장 위치: results_by_domain_final)")

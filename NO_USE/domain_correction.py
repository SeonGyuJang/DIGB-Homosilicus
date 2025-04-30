import json
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

# ========== 1. 경로 설정 ==========
INPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results_by_domain")
OUTPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results_by_domain_final")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ========== 2. 도메인 매핑 정의 ==========
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
    "컴퓨터 과학": "컴퓨터과학",
    "컴퓨터과학": "컴퓨터과학",
    "환경 과학": "환경과학",
    "환경과학": "환경과학"
}

# ========== 3. 도메인별 결과 병합 ==========
major_domain_data = defaultdict(list)

print("[1/2] 도메인 병합 중...")
for file_path in tqdm(list(INPUT_DIR.glob("*.json"))):
    domain_name = file_path.stem
    mapped_domain = domain_mapping.get(domain_name)
    
    if not mapped_domain:
        print(f"[!] 매핑되지 않은 도메인: {domain_name}")
        continue

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            major_domain_data[mapped_domain].extend(data)
    except Exception as e:
        print(f"[!] {file_path.name} 로딩 오류: {e}")

# ========== 4. 병합 결과 저장 ==========
print("[2/2] 병합된 결과 저장 중...")
for domain, entries in major_domain_data.items():
    output_path = OUTPUT_DIR / f"{domain}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

print("✅ 도메인 통합 완료 (총 10개).")

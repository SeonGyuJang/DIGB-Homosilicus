#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
도메인별 실험 결과 병합 및 정규화 스크립트
------------------------------------------------
1) 도메인별 페르소나 개수만 보고 싶을 때
   python merge_by_domain.py --count_domain

2) 결과 병합까지 수행 (기본)
   python merge_by_domain.py
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

# ---------------------------------------------------------------------
# 0. CLI 파싱
# ---------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="도메인별 실험 결과 병합 및 정규화 스크립트"
)
parser.add_argument(
    "--count_domain", action="store_true",
    help="도메인별 페르소나 개수만 출력하고 종료"
)
args = parser.parse_args()

# ---------------------------------------------------------------------
# 1. 경로 설정
# ---------------------------------------------------------------------
INPUT_JSONL = Path(
    r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Common\(EN)PERSONA_DATA_10000.jsonl"
)
RESULTS_DIR = Path(
    r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\pre_results\CR2002\(EN)CR2002_EXPERIMENT_RESULTS_10000_Temp1"
)
OUTPUT_DIR = Path(
    r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\pre_results\CR2002\(EN)Temp1_results"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# 2. 도메인 매핑 사전 (KR & EN) → 통합
# ---------------------------------------------------------------------
domain_mapping_KR = {
    # 한국어
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

domain_mapping_EN = {
    # 영어
    "History": "history",
    "history": "history",
    "Law": "law",
    "law": "law",
    "Philosophy": "philosophy",
    "philosophy": "philosophy",
    "Economics": "economics",
    "economics": "economics",
    "Sociology": "sociology",
    "sociology": "sociology",
    "Finance": "finance",
    "finance": "finance",
    "Computer Science": "computer science",
    "computer science": "computer science",
    "Mathematics": "mathematics",
    "mathematics": "mathematics",
    "Environmental Science": "environmental science",
    "environmental science": "environmental science",
    "Environmental science": "environmental science",
    "Engineering": "engineering",
    "engineering": "engineering"
}

# 두 사전을 하나로 합침
domain_mapping = {**domain_mapping_KR, **domain_mapping_EN}

# ---------------------------------------------------------------------
# 3. 문자열 정규화 함수
# ---------------------------------------------------------------------
def normalize_domain(s: str) -> str:
    """양쪽 공백 제거만 수행(필요시 .lower() 등 추가 가능)."""
    return s.strip()

# ---------------------------------------------------------------------
# 4. JSONL 로부터 도메인 → 인덱스 리스트 구축
# ---------------------------------------------------------------------
print("[1/4] 도메인별 idx 분류 중...")
raw_domain_to_indices = defaultdict(list)

with INPUT_JSONL.open("r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line)
            domain_raw = entry.get("general domain (top 1 percent)", "")
            idx = entry.get("idx")
            if domain_raw and idx is not None:
                domain_norm = normalize_domain(domain_raw)
                raw_domain_to_indices[domain_norm].append(idx)
        except json.JSONDecodeError as e:
            print(f"[!] JSON 디코딩 오류: {e}")

# ---------------------------------------------------------------------
# 5. 옵션: 도메인별 인원수만 출력
# ---------------------------------------------------------------------
if args.count_domain:
    print("\n매핑된 도메인 기준 페르소나 개수:")
    mapped_count = defaultdict(int)
    for raw_domain, idx_list in raw_domain_to_indices.items():
        mapped = domain_mapping.get(raw_domain, "매핑 안됨")
        mapped_count[mapped] += len(idx_list)

    for mapped, count in sorted(mapped_count.items(),
                                key=lambda x: x[1], reverse=True):
        print(f"- {mapped:18}: {count}명")
    exit(0)

# ---------------------------------------------------------------------
# 6. 실험 결과 파일 수집
# ---------------------------------------------------------------------
print("[2/4] 실험 결과 수집 중...")
mapped_domain_to_results = defaultdict(list)

for raw_domain, indices in tqdm(list(raw_domain_to_indices.items()),
                                desc="도메인별 처리"):
    mapped_domain = domain_mapping.get(raw_domain)
    if mapped_domain is None:
        print(f"[!] 매핑되지 않은 도메인: {raw_domain}")
        continue

    for idx in indices:
        # ★ 5자리 0-패딩 필수 ★
        result_path = RESULTS_DIR / f"Person_{int(idx):05d}.json"
        if not result_path.exists():
            print(f"[!] 결과 파일 없음: {result_path}")
            continue

        try:
            with result_path.open("r", encoding="utf-8") as rf:
                result_data = json.load(rf)
                mapped_domain_to_results[mapped_domain].append(
                    {"idx": idx, "result": result_data}
                )
        except Exception as e:
            print(f"[!] 읽기 오류 - idx={idx}: {e}")

# ---------------------------------------------------------------------
# 7. 도메인별 병합 결과 저장
# ---------------------------------------------------------------------
print("[3/4] 병합된 도메인별 결과 저장 중...")
for domain, entries in mapped_domain_to_results.items():
    output_path = OUTPUT_DIR / f"{domain}.json"
    with output_path.open("w", encoding="utf-8") as wf:
        json.dump(entries, wf, ensure_ascii=False, indent=2)

print("[4/4] 도메인 통합 완료")

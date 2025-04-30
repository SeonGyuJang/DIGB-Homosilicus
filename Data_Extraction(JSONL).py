"""
(1) 상위 N개 도메인 목록 보기 :  python persona_sampler.py --list
(2) 선택한 도메인만 추출      :  python "Data_Extraction(JSONL).py" --domains history,law,philosophy,economics,sociology,finance,"computer science",mathematics,"environmental science",engineering
"""

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import List

INPUT_PATH = Path(r"C:\Users\dsng3\Desktop\Original_Persona_Data.jsonl")
OUTPUT_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(EN)PERSONA_DATA_10000.jsonl")
TOP_N_DOMAINS = 30              # 상위 도메인 개수
SAMPLE_SIZE_PER_DOMAIN = 1000  # 도메인별 추출 
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

def count_domains(path: Path) -> Counter:
    counter = Counter()
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
                dom = row.get("general domain (top 1 percent)")
                if dom and str(dom).lower() != "none":
                    counter[str(dom).lower()] += 1
            except json.JSONDecodeError:
                continue
    return counter

def show_top_domains(counter: Counter, top_n: int) -> None:
    print(f"\n★ 상위 {top_n}개 도메인")
    for i, (dom, cnt) in enumerate(counter.most_common(top_n), 1):
        print(f"{i:>2}. {dom:<25} {cnt:>7,}")
    print("\n(원하는 도메인을 쉼표로 묶어 --domains에 넣어주세요!)\n")

def collect_selected(path: Path, choose: set[str]) -> dict[str, List[dict]]:
    buckets = defaultdict(list)
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
                dom = row.get("general domain (top 1 percent)")
                if dom and (dom_l := str(dom).lower()) in choose:
                    buckets[dom_l].append(
                        {"persona": row.get("persona"),
                         "general domain (top 1 percent)": dom}
                    )
            except json.JSONDecodeError:
                continue
    return buckets

def sample_and_save(buckets: dict, k: int, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with out_path.open("w", encoding="utf-8") as f:
        for dom, records in buckets.items():
            need = k if len(records) > k else len(records)
            if need < k:
                print(f"'{dom}'은 {len(records)}개뿐 → 전량 사용")
            picks = random.sample(records, need)
            for item in picks:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
            total += need
    print(f"\n샘플링 완료!  총 {total:,}개 저장 → {out_path}\n")

def add_idx_to_jsonl(path: Path) -> None:
    """샘플링 완료 후, JSONL 파일에 idx를 1부터 끝까지 부여"""
    tmp_path = path.with_suffix(".tmp.jsonl")

    with path.open("r", encoding="utf-8") as infile, tmp_path.open("w", encoding="utf-8") as outfile:
        for idx, line in enumerate(infile, start=1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                obj["idx"] = idx
                outfile.write(json.dumps(obj, ensure_ascii=False) + "\n")
            except json.JSONDecodeError:
                continue

    path.unlink()        
    tmp_path.rename(path)  
    print(f"idx 부여 완료! → {path}")

def main():
    parser = argparse.ArgumentParser(description="Persona JSONL 샘플러")
    parser.add_argument("--list", action="store_true",
                        help="상위 N개 도메인만 보여주고 종료")
    parser.add_argument("--domains",
                        help="쉼표로 구분한 원하는 도메인 목록(e.g. 경제학,법률)")
    args = parser.parse_args()

    counter = count_domains(INPUT_PATH)

    if args.list:
        show_top_domains(counter, TOP_N_DOMAINS)
        return

    if not args.domains:
        parser.error("도메인을 지정하세요: --domains <d1,d2,...>  또는 --list")

    selected = {d.strip().lower() for d in args.domains.split(",")}
    print(f"\n● 선택 도메인: {', '.join(selected)}")

    buckets = collect_selected(INPUT_PATH, selected)
    if not buckets:
        print("해당 도메인 데이터가 없습니다.")
        return

    sample_and_save(buckets, SAMPLE_SIZE_PER_DOMAIN, OUTPUT_PATH)
    add_idx_to_jsonl(OUTPUT_PATH)  # 샘플링 끝나고 idx 추가!

if __name__ == "__main__":
    main()

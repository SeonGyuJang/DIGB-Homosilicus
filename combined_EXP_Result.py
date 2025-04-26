import os
import json
import re
from collections import defaultdict, Counter

input_dir = r"C:\Users\dsng3\iCloudDrive\DIGB_Project\LangChain_EXISITNG_EXPERIMENT_RESULTS" # 실험결과(JSON)이 모아져있는 폴더
output_file = r"\DIGB_Project\EXISITNG_EXP_combined_by_domain.json" # 저장할 위치
original_data_file = r"\DIGB_Project\data\grouped_persona_data.json" # 도메인별 정리된 페르소나 데이터

with open(original_data_file, encoding="utf-8") as f:
    original_data = json.load(f)

idx_to_domain = {}
for dom, personas in original_data.items():
    for p in personas:
        idx_to_domain[str(p["idx"])] = dom

domain_data = defaultdict(list)        
processed_ids = set()                   

pattern = re.compile(r"[Pp]erson[_-]?(\d+)\.json")

for fname in os.listdir(input_dir):
    if not fname.lower().endswith(".json"):
        continue
    m = pattern.match(fname)
    if not m:
        print(f"[SKIP] 이름 패턴 불일치: {fname}")
        continue

    pid = m.group(1)                    
    processed_ids.add(pid)

    domain = idx_to_domain.get(pid)
    if domain is None:
        print(f"[WARN] idx {pid} → 도메인 매핑 없음")
        continue

    with open(os.path.join(input_dir, fname), encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        domain_data[domain].extend(data)
    else:
        domain_data[domain].append(data)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(domain_data, f, ensure_ascii=False, indent=4)
print(f"Combined JSON written to: {output_file}")

expected_counts = Counter(idx_to_domain[pid] for pid in processed_ids if pid in idx_to_domain)
actual_counts   = Counter({dom: len(plist) for dom, plist in domain_data.items()})

print("\n=== Domain count check ===")
all_ok = True
for dom in sorted(expected_counts):
    exp = expected_counts[dom]
    act = actual_counts.get(dom, 0)
    status = "✅" if exp == act else "❌"
    print(f"{status} {dom:<20} expected {exp:>3}  |  actual {act:>3}")
    if exp != act:
        all_ok = False

missing_ids = [pid for pid in expected_counts.elements() if pid not in processed_ids]
duplicate_ids = [pid for pid, cnt in Counter(processed_ids).items() if cnt > 1]

if missing_ids:
    all_ok = False
    print(f"\n Missing persona files for idx: {', '.join(sorted(missing_ids))}")

if duplicate_ids:
    all_ok = False
    print(f"\n Duplicate persona files found for idx: {', '.join(sorted(duplicate_ids))}")

# 3‑3. 최종 결과
if all_ok:
    print("\n All checks passed – data merged correctly!")
else:
    print("\n Issues detected – please review the warnings above.")

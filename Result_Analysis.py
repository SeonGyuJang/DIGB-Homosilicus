import os
import json
from pathlib import Path
from collections import defaultdict

# 경로 설정
INPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results_by_domain")
OUTPUT_FILE = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results\summary_by_domain.txt")

# 시나리오 순서 보장
scenario_keys = ["scenario_1", "scenario_2", "scenario_3"]
difficulty_levels = ["하", "중", "상"]

# 전체 결과 저장
final_summary = []

# 도메인별 처리
for file in sorted(INPUT_DIR.glob("*.json"), key=lambda x: x.name):
    domain_name = file.stem
    scenario_counts = defaultdict(lambda: {"Left": 0, "Right": 0})

    with open(file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"[!] {file.name} 디코딩 오류 → 건너뜀")
            continue

    for entry in data:
        result = entry.get("result", {})
        for level in difficulty_levels:
            scenarios = result.get(level, {})
            for skey in scenario_keys:
                if skey in scenarios:
                    answer = scenarios[skey].get("answer", "")
                    if answer in ["Left", "Right"]:
                        scenario_counts[(level, skey)][answer] += 1

    # 출력 정리
    summary_lines = [f"[{domain_name}]"]
    for level in difficulty_levels:
        for skey in scenario_keys:
            key = (level, skey)
            left = scenario_counts[key]["Left"]
            right = scenario_counts[key]["Right"]
            total = left + right
            if total > 0:
                left_pct = f"{(left / total) * 100:.1f}%"
                right_pct = f"{(right / total) * 100:.1f}%"
            else:
                left_pct = right_pct = "0.0%"
            summary_lines.append(
                f"  - {level} / {skey}: Left = {left} ({left_pct}), Right = {right} ({right_pct}), Total = {total}"
            )

    final_summary.append("\n".join(summary_lines) + "\n")

# 결과 저장
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(final_summary))

print(f"도메인별 시나리오 분석 결과 저장 완료: {OUTPUT_FILE}")

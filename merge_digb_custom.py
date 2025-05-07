#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sum_by_difficulty_and_scenario.py
────────────────────────────────────────────────────────
DIGB_Custom 결과를 난이도별·시나리오별로 합산하되,
데이터가 전혀 없는 시나리오는 출력하지 않는다.
"""

import json
from pathlib import Path
from collections import defaultdict

# ──────── 경로 ────────
INPUT_DIR   = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\DIGB_Custom\(KR)DIGB_Custom_EXPERIMENT_RESULTS_NOPERSONA")
MERGED_FILE = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\DIGB_Custom\merge_by_nopersona\(KR)merged_results.json")
OUTPUT_FILE = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\DIGB_Custom\merge_by_nopersona\(KR)summary_by_scenario.txt")

# ──────── 집계 구조 ────────
merged_list: list[dict] = []
diff_totals: dict[str, dict[str, dict[str, int]]] = defaultdict(
    lambda: defaultdict(lambda: {"Left": 0, "Right": 0})
)
# 난이도별로 실제 등장한 시나리오를 기록
diff_seen_scenarios: dict[str, set[str]] = defaultdict(set)

def iter_diff_scenarios(obj):
    if isinstance(obj, dict):
        for diff_name, scenarios in obj.items():
            yield diff_name, scenarios
    elif isinstance(obj, list):
        for entry in obj:
            for diff_name, scenarios in entry.get("result", {}).items():
                yield diff_name, scenarios

# ──────── 파일 순회 ────────
for file in INPUT_DIR.glob("*.json"):
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"[!] {file.name} 디코딩 오류 → 건너뜀"); continue

    merged_list.append(data)

    for diff_name, scenarios in iter_diff_scenarios(data):
        for skey, sdata in scenarios.items():
            ans = sdata.get("answer")
            if ans in ("Left", "Right"):
                diff_totals[diff_name][skey][ans] += 1
                diff_seen_scenarios[diff_name].add(skey)

# ──────── 병합 JSON 저장 ────────
MERGED_FILE.parent.mkdir(parents=True, exist_ok=True)
MERGED_FILE.write_text(json.dumps(merged_list, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✅ 병합 JSON 저장 완료 → {MERGED_FILE}")

# ──────── 요약 출력 ────────
lines: list[str] = []
grand_left = grand_right = 0

for diff_name in sorted(diff_totals.keys()):
    lines.append(f"[{diff_name}]")
    for skey in sorted(diff_seen_scenarios[diff_name]):          # 실제 등장한 시나리오만
        left  = diff_totals[diff_name][skey]["Left"]
        right = diff_totals[diff_name][skey]["Right"]
        total = left + right
        if total == 0:
            continue                                            # 안전장치: 0이면 건너뜀

        grand_left  += left
        grand_right += right

        lpct = f"{left  / total * 100:.1f}%"
        rpct = f"{right / total * 100:.1f}%"
        lines.append(
            f"  - {skey}: Left = {left} ({lpct}), "
            f"Right = {right} ({rpct}), Total = {total}"
        )
    lines.append("")  # 빈 줄 구분

# ──────── 전체 합계 ────────
grand_total = grand_left + grand_right
if grand_total:
    glpct = f"{grand_left  / grand_total * 100:.1f}%"
    grpct = f"{grand_right / grand_total * 100:.1f}%"
    lines.append(
        f"[GRAND TOTAL] Left = {grand_left} ({glpct}), "
        f"Right = {grand_right} ({grpct}), Total = {grand_total}"
    )

# ──────── 저장 ────────
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
print(f"✅ 난이도·시나리오별 합계 저장 완료 → {OUTPUT_FILE}")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sum_by_scenario.py
────────────────────────────────────────────────────────
모든 JSON을 모아 scenario_1~6의 Left/Right 합계를 계산해
(EN)summary_by_scenario.txt 로 저장
"""

import json
from pathlib import Path
from collections import defaultdict

# 1) 경로
INPUT_DIR   = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\CR2002\(EN)CR2002_EXPERIMENT_RESULTS_NOPERSONA")
OUTPUT_FILE = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\CR2002\merge_by_nopersona\(EN)summary_by_scenario.txt")

SCENARIO_KEYS = [f"scenario_{i}" for i in range(1, 7)]

# 2) 시나리오별 누적 카운터
scenario_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"Left": 0, "Right": 0})

# 3) 모든 JSON 순회
def iter_scenarios(obj):
    """각 JSON 구조에서 scenarios 딕셔너리만 찾아서 yield"""
    if isinstance(obj, dict):
        # {difficulty: {...}}  또는  {scenario_i: {...}}
        if any(k.startswith("scenario_") for k in obj):
            yield obj
        else:
            for scenarios in obj.values():
                yield scenarios
    elif isinstance(obj, list):
        # [{"result": {...}}, ...]
        for entry in obj:
            for scenarios in entry.get("result", {}).values():
                yield scenarios

num_files = 0
for file in INPUT_DIR.glob("*.json"):
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"[!] {file.name} 디코딩 오류 → 건너뜀")
        continue

    num_files += 1
    for scenarios in iter_scenarios(data):
        for skey in SCENARIO_KEYS:
            if skey in scenarios:
                ans = scenarios[skey].get("answer")
                if ans in ("Left", "Right"):
                    scenario_totals[skey][ans] += 1

print(f"✅ 읽은 파일 수: {num_files}")

# 4) 요약 텍스트 작성
lines: list[str] = ["[ALL PERSONAS]"]
grand_left = grand_right = 0

for skey in SCENARIO_KEYS:
    left  = scenario_totals[skey]["Left"]
    right = scenario_totals[skey]["Right"]
    total = left + right
    grand_left  += left
    grand_right += right

    if total:
        lpct = f"{left  / total * 100:.1f}%"
        rpct = f"{right / total * 100:.1f}%"
    else:
        lpct = rpct = "0.0%"

    lines.append(
        f"  - {skey}: Left = {left} ({lpct}), Right = {right} ({rpct}), Total = {total}"
    )

grand_total = grand_left + grand_right
if grand_total:
    glpct = f"{grand_left  / grand_total * 100:.1f}%"
    grpct = f"{grand_right / grand_total * 100:.1f}%"
    lines.append(
        f"  ⇒ GRAND TOTAL: Left = {grand_left} ({glpct}), "
        f"Right = {grand_right} ({grpct}), Total = {grand_total}"
    )

# 5) 저장
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
print(f"✅ 시나리오별 합계 저장 완료: {OUTPUT_FILE}")

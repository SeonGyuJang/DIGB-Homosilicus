import json
from pathlib import Path
from collections import defaultdict

INPUT_DIR   = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\CR2002\results_by_domain(KR)")
OUTPUT_FILE = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\CR2002\(KR)summary_by_domain.txt")

SCENARIO_KEYS = [f"scenario_{i}" for i in range(1, 7)]

final_summary: list[str] = []

for file in sorted(INPUT_DIR.glob("*.json"), key=lambda x: x.name):
    domain_name = file.stem
    scenario_counts: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"Left": 0, "Right": 0})
    difficulties: set[str] = set()

    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"[!] {file.name} 디코딩 오류 → 건너뜀")
        continue

    for entry in data:
        for diff_name, scenarios in entry.get("result", {}).items():
            difficulties.add(diff_name)
            for skey in SCENARIO_KEYS:
                if skey in scenarios:
                    answer = scenarios[skey].get("answer")
                    if answer in ("Left", "Right"):
                        scenario_counts[(diff_name, skey)][answer] += 1

    summary_lines = [f"[{domain_name}]"]
    for diff_name in sorted(difficulties): 
        for skey in SCENARIO_KEYS:
            left  = scenario_counts[(diff_name, skey)]["Left"]
            right = scenario_counts[(diff_name, skey)]["Right"]
            total = left + right
            if total:
                lpct = f"{left  / total * 100:.1f}%"
                rpct = f"{right / total * 100:.1f}%"
            else:
                lpct = rpct = "0.0%"

            summary_lines.append(
                f"  - {diff_name} / {skey}: "
                f"Left = {left} ({lpct}), Right = {right} ({rpct}), Total = {total}"
            )

    final_summary.append("\n".join(summary_lines) + "\n")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.write_text("\n".join(final_summary), encoding="utf-8")

print(f"도메인별 시나리오 분석 결과 저장 완료: {OUTPUT_FILE}")

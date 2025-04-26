
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

EXPECTED_SCENARIOS = {f"scenario_{i}" for i in range(1, 7)}
ANSWER_OK = {"Left", "Right"}

###############################################################################
# 공통 util: 깊이 순회하여 시나리오 dict 추출
###############################################################################
def _walk(node: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(node, dict) and node and all(
        isinstance(k, str) and k.startswith("scenario_") for k in node.keys()
    ):
        out.append(node)
        return out
    if isinstance(node, dict):
        for v in node.values():
            out.extend(_walk(v))
    elif isinstance(node, list):
        for it in node:
            out.extend(_walk(it))
    return out


###############################################################################
def check_persona(pfile: Path) -> List[Dict[str, str]]:
    """
    하나의 persona 파일을 검사해
    [ {scenario, issue, detail}, … ] 리스트 반환 (정상이면 빈 리스트)
    """
    issues: List[Dict[str, str]] = []

    try:
        data = json.loads(pfile.read_text(encoding="utf-8"))
    except Exception as e:
        return [{"scenario": "-", "issue": "file_error", "detail": str(e)}]

    scen_dicts = _walk(data)
    if not scen_dicts:
        return [{"scenario": "-", "issue": "no_scenario_block", "detail": "cannot find any scenario_*"}]

    # 시나리오 합치기 (중복 방지)
    merged: Dict[str, Dict[str, Any]] = {}
    for d in scen_dicts:
        merged.update(d)

    # 1) 누락 시나리오
    for sc in sorted(EXPECTED_SCENARIOS - merged.keys()):
        issues.append({"scenario": sc, "issue": "missing_block", "detail": "scenario block absent"})

    # 2) 각 시나리오 answer 검사
    for sc, det in merged.items():
        if sc not in EXPECTED_SCENARIOS:
            continue  # 예상 밖 시나리오는 무시

        ans_raw = det.get("answer", "")
        ans_norm = str(ans_raw).strip().title()

        if ans_norm == "":
            issues.append({"scenario": sc, "issue": "missing_answer", "detail": "answer key absent"})
        elif ans_norm not in ANSWER_OK:
            issues.append(
                {
                    "scenario": sc,
                    "issue": "invalid_answer",
                    "detail": f"value={ans_raw!r} (normalized={ans_norm})",
                }
            )

    return issues


###############################################################################
def main() -> None:
    ap = argparse.ArgumentParser("find personas with missing / invalid answers")
    ap.add_argument("--indir", type=Path, required=True, help="Person_*.json 폴더")
    ap.add_argument("--outfile", type=Path, default=Path("missing_report.csv"), help="CSV 출력")
    args = ap.parse_args()

    pattern = re.compile(r"[Pp]erson[_-]?(\d+)\.json")
    rows: List[Dict[str, str]] = []

    for p in sorted(args.indir.glob("*.json")):
        m = pattern.match(p.name)
        if not m:
            continue
        pid = m.group(1)

        for issue in check_persona(p):
            rows.append(
                {
                    "persona_id": pid,
                    "file": p.name,
                    "scenario": issue["scenario"],
                    "issue": issue["issue"],
                    "detail": issue["detail"],
                }
            )

    if not rows:
        print("🎉 모든 persona 파일이 정상입니다!")
        return

    df = pd.DataFrame(rows).sort_values(["persona_id", "scenario"])
    df.to_csv(args.outfile, index=False, encoding="utf-8-sig")

    print(f"⚠️  문제 발견 persona 수: {df['persona_id'].nunique()}")
    print(f"CSV 보고서 → {args.outfile.resolve()}")
    print(df.head(15).to_string(index=False))  # 샘플 출력


###############################################################################
if __name__ == "__main__":
    main()

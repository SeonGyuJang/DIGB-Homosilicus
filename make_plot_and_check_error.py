# NOTE : EXISTING_box_plot_EXP.py와 error_check.py를 섞어서 만듦.
"""
도메인별 Left/Right 개수 카운팅 → plots 생성 → JSONL 생성 → missing_data_report 생성
+ persona 파일 유효성 검사 기능 (--check_error)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd


def _walk_personas(node: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(node, dict) and node and all(k.startswith("scenario_") for k in node):
        out.append(node)
        return out
    if isinstance(node, dict):
        for v in node.values():
            out.extend(_walk_personas(v))
    elif isinstance(node, list):
        for item in node:
            out.extend(_walk_personas(item))
    return out


def flatten_results(data: Dict[str, Any]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for domain, domain_block in data.items():
        for scen_dict in _walk_personas(domain_block):
            for scenario, det in scen_dict.items():
                ans = det.get("answer")
                if ans not in {"Left", "Right"}:
                    continue
                rows.append({
                    "domain": domain,
                    "persona_id": det.get("persona_id"),
                    "difficulty": det.get("difficulty", "unknown"),
                    "scenario": scenario,
                    "answer": ans,
                })
    return pd.DataFrame(rows).dropna(subset=["persona_id"])


def domain_counts(df: pd.DataFrame, domain: str) -> Tuple[Dict[str, Dict[str, Dict[str, int]]], pd.DataFrame]:
    dom_df = df.query("domain == @domain")
    difficulties = sorted(dom_df["difficulty"].unique())
    scenarios = sorted(dom_df["scenario"].unique())
    counts_df = (
        dom_df.groupby(["difficulty", "scenario", "answer"]).size().unstack(fill_value=0)
        .reindex(pd.MultiIndex.from_product([difficulties, scenarios]), fill_value=0).sort_index()
    )
    nested = {
        diff: {
            scen: {
                "Left": int(counts_df.loc[(diff, scen)].get("Left", 0)),
                "Right": int(counts_df.loc[(diff, scen)].get("Right", 0))
            } for scen in scenarios
        } for diff in difficulties
    }
    return nested, counts_df


def make_domain_plot(counts_df: pd.DataFrame, domain: str, outdir: Path) -> None:
    x = range(len(counts_df))
    width = 0.4
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([i - width/2 for i in x], counts_df["Left"], width, label="Left", color="#4C72B0")
    ax.bar([i + width/2 for i in x], counts_df["Right"], width, label="Right", color="#DD8452")
    xticklabels = [f"{d[0]}-{s.split('_')[-1]}" for d, s in counts_df.index]
    ax.set_xticks(list(x))
    ax.set_xticklabels(xticklabels, rotation=45, ha="right")
    ax.set_ylabel("Count")
    ax.set_title(f"Left vs Right choices — {domain}")
    ax.legend()
    plt.tight_layout()
    safe = re.sub(r"[\\/]+", "_", domain).replace(" ", "_")
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / f"{safe}_choices.png", dpi=300)
    plt.close(fig)


def check_missing(counts_df: pd.DataFrame, persona_cnt: int) -> pd.DataFrame:
    scen_tot = counts_df.groupby(level=1).sum()
    scen_tot["Total"] = scen_tot["Left"] + scen_tot["Right"]
    missing_df = scen_tot.query("Total != @persona_cnt").copy()
    missing_df["missing"] = persona_cnt - missing_df["Total"]
    return missing_df[["Left", "Right", "Total", "missing"]]


EXPECTED_SCENARIOS = {f"scenario_{i}" for i in range(1, 7)}
ANSWER_OK = {"Left", "Right"}


def check_persona(pfile: Path) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    try:
        data = json.loads(pfile.read_text(encoding="utf-8"))
    except Exception as e:
        return [{"scenario": "-", "issue": "file_error", "detail": str(e)}]

    scen_dicts = _walk_personas(data)
    if not scen_dicts:
        return [{"scenario": "-", "issue": "no_scenario_block", "detail": "cannot find any scenario_*"}]

    merged: Dict[str, Dict[str, Any]] = {}
    for d in scen_dicts:
        merged.update(d)

    for sc in sorted(EXPECTED_SCENARIOS - merged.keys()):
        issues.append({"scenario": sc, "issue": "missing_block", "detail": "scenario block absent"})

    for sc, det in merged.items():
        if sc not in EXPECTED_SCENARIOS:
            continue
        ans_raw = det.get("answer", "")
        ans_norm = str(ans_raw).strip().title()
        if ans_norm == "":
            issues.append({"scenario": sc, "issue": "missing_answer", "detail": "answer key absent"})
        elif ans_norm not in ANSWER_OK:
            issues.append({"scenario": sc, "issue": "invalid_answer", "detail": f"value={ans_raw!r} (normalized={ans_norm})"})
    return issues


def main() -> None:
    ap = argparse.ArgumentParser("domain count & persona error check")
    ap.add_argument("--input", type=Path, help="병합 JSON")
    ap.add_argument("--indir", type=Path, help="Person_*.json 폴더")
    ap.add_argument("--outdir", type=Path, default=Path("plots"), help="출력 디렉터리")
    ap.add_argument("--check_error", action="store_true", help="persona 오류만 검사")
    ap.add_argument("--outfile", type=Path, default=Path("missing_report.csv"), help="CSV 출력 (check_error용)")
    args = ap.parse_args()

    if args.check_error:
        if not args.indir:
            raise ValueError("--check_error 사용 시 --indir 경로가 필요합니다.")
        pattern = re.compile(r"[Pp]erson[_-]?(\d+)\.json")
        rows: List[Dict[str, str]] = []
        for p in sorted(args.indir.glob("*.json")):
            m = pattern.match(p.name)
            if not m:
                continue
            pid = m.group(1)
            for issue in check_persona(p):
                rows.append({
                    "persona_id": pid,
                    "file": p.name,
                    "scenario": issue["scenario"],
                    "issue": issue["issue"],
                    "detail": issue["detail"],
                })
        if not rows:
            print(" 모든 persona 파일이 정상입니다!")
            return
        df = pd.DataFrame(rows).sort_values(["persona_id", "scenario"])
        df.to_csv(args.outfile, index=False, encoding="utf-8-sig")
        print(f"문제 발견 persona 수: {df['persona_id'].nunique()}")
        print(f"CSV 보고서 → {args.outfile.resolve()}")
        print(df.head(15).to_string(index=False))
        return

    if not args.input:
        raise ValueError("--check_error 없이 실행 시 --input 경로가 필요합니다.")

    data = json.loads(args.input.read_text(encoding="utf-8"))
    df = flatten_results(data)
    if df.empty:
        raise ValueError("유효한 Left/Right 응답이 없습니다.")

    persona_counts = df.groupby("domain")["persona_id"].nunique()
    eligible = persona_counts[persona_counts >= 10]

    if eligible.empty:
        print("persona ≥10 인 도메인이 없습니다. 종료.")
        return

    print("대상 도메인:", ", ".join(eligible.index))

    jsonl_path = args.outdir / "domain_choice_counts.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    with jsonl_path.open("w", encoding="utf-8") as jf:
        for dom, p_cnt in eligible.items():
            nested, cnt_df = domain_counts(df, dom)
            miss_df = check_missing(cnt_df, p_cnt)
            if not miss_df.empty:
                print(f"{dom}: 누락 응답 발견 → {int(miss_df['missing'].sum())} 개")
            else:
                print(f"{dom}: 모든 시나리오 응답 완전({p_cnt}명)")
            make_domain_plot(cnt_df, dom, args.outdir)
            jf.write(json.dumps({
                "domain": dom,
                "persona_count": int(p_cnt),
                "counts": nested,
                "missing": int(miss_df["missing"].sum()) if not miss_df.empty else 0,
            }, ensure_ascii=False) + "\n")

    print("\nJSONL:", jsonl_path.resolve())
    print("PNG & missing‑CSV:", args.outdir.resolve())


if __name__ == "__main__":
    main()

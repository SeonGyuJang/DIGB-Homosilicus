# -*- coding: utf-8 -*-
"""
Left/Right choice counts per domain  →  plots + JSONL + missing‑data check
===========================================================================

python EXISITNG_box_plot_EXP.py \
       --input  EXISITNG_EXP_combined_by_domain.json \
       --outdir EXISITNG_plot
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd

###############################################################################
# Helpers
###############################################################################


def _walk_personas(node: Any) -> List[Dict[str, Any]]:
    """임의 깊이 구조를 모두 순회하며 시나리오 dict 를 수집."""
    out: List[Dict[str, Any]] = []

    # leaf 판정
    if isinstance(node, dict) and node and all(
        isinstance(k, str) and k.startswith("scenario_") for k in node.keys()
    ):
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
    """JSON → DataFrame(domain, persona_id, scenario, answer, difficulty)."""
    rows: List[Dict[str, Any]] = []

    for domain, domain_block in data.items():
        for scen_dict in _walk_personas(domain_block):
            for scenario, det in scen_dict.items():
                ans = det.get("answer")
                if ans not in {"Left", "Right"}:
                    continue
                rows.append(
                    {
                        "domain": domain,
                        "persona_id": det.get("persona_id"),
                        "difficulty": det.get("difficulty", "unknown"),
                        "scenario": scenario,
                        "answer": ans,
                    }
                )

    df = pd.DataFrame(rows).dropna(subset=["persona_id"])
    return df


###############################################################################
# Counting, plotting, missing‑check
###############################################################################


def domain_counts(
    df: pd.DataFrame, domain: str
) -> Tuple[Dict[str, Dict[str, Dict[str, int]]], pd.DataFrame]:
    """도메인‑별 nested dict + counts DF."""
    dom_df = df.query("domain == @domain")

    difficulties = sorted(dom_df["difficulty"].unique())
    scenarios = sorted(dom_df["scenario"].unique())

    counts_df = (
        dom_df.groupby(["difficulty", "scenario", "answer"])
        .size()
        .unstack(fill_value=0)
        .reindex(
            pd.MultiIndex.from_product([difficulties, scenarios]),
            fill_value=0,
        )
        .sort_index()
    )

    nested: Dict[str, Dict[str, Dict[str, int]]] = {}
    for (diff, scen), row in counts_df.iterrows():
        nested.setdefault(diff, {})[scen] = {
            "Left": int(row.get("Left", 0)),
            "Right": int(row.get("Right", 0)),
        }
    return nested, counts_df


def make_domain_plot(counts_df: pd.DataFrame, domain: str, outdir: Path) -> None:
    """Left/Right 분포를 그룹드 바차트로 저장."""
    x = range(len(counts_df))
    width = 0.4

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([i - width / 2 for i in x], counts_df["Left"], width, label="Left", color="#4C72B0")
    ax.bar([i + width / 2 for i in x], counts_df["Right"], width, label="Right", color="#DD8452")

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
    """
    시나리오별 Left+Right 합계가 persona_cnt 와 다른 행을 반환.
    (빈 DataFrame이면 결측치 없음)
    """
    scen_tot = counts_df.groupby(level=1).sum()
    scen_tot["Total"] = scen_tot["Left"] + scen_tot["Right"]
    missing_df = scen_tot.query("Total != @persona_cnt").copy()
    missing_df["missing"] = persona_cnt - missing_df["Total"]
    return missing_df[["Left", "Right", "Total", "missing"]]


###############################################################################
# Main
###############################################################################


def main() -> None:
    ap = argparse.ArgumentParser("Plot & save counts, check missing answers")
    ap.add_argument("--input", type=Path, required=True, help="병합 JSON")
    ap.add_argument("--outdir", type=Path, default=Path("plots"), help="출력 디렉터리")
    args = ap.parse_args()

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

            # -------- 결측치 검사 --------
            miss_df = check_missing(cnt_df, p_cnt)
            if not miss_df.empty:
                print(f"⚠️  {dom}: 누락 응답 발견 → {int(miss_df['missing'].sum())} 개")
                miss_df.to_csv(args.outdir / f"{dom.replace(' ', '_')}_missing.csv", index=True)
            else:
                print(f"✅ {dom}: 모든 시나리오 응답 완전({p_cnt}명)")

            # 그래프
            make_domain_plot(cnt_df, dom, args.outdir)

            # JSONL 기록  ── numpy.int64 → int 변환  # ★
            jf.write(
                json.dumps(
                    {
                        "domain": dom,
                        "persona_count": int(p_cnt),                # ★
                        "counts": nested,
                        "missing": int(miss_df["missing"].sum())    # ★
                        if not miss_df.empty else 0,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    print("\nJSONL:", jsonl_path.resolve())
    print("PNG & missing‑CSV:", args.outdir.resolve())


###############################################################################
if __name__ == "__main__":
    main()

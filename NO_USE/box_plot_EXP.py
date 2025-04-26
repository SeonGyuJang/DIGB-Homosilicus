# -*- coding: utf-8 -*-
"""Left/Right choice counts per domain → plots **and** JSONL
============================================================
* Generates grouped‑bar PNG **only for domains with ≥ 10 personas**
* Saves per‑domain count summaries to a single `domain_choice_counts.jsonl`
  (one JSON object per line)

Each JSON object structure
--------------------------
```json
{
  "domain": "Computer Science",
  "persona_count": 22,
  "counts": {
    "easy": {
      "scenario_1": {"Left": 7, "Right": 15},
      "scenario_2": {"Left": 9, "Right": 13},
      "scenario_3": {"Left": 11, "Right": 11}
    },
    "medium": { ... },
    "hard":   { ... }
  }
}
```

Usage
-----
```bash
python domain_choice_plot.py --input EXP_combined_by_domain.json --outdir plots
```
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd

################################################################################
# Helpers
################################################################################

def flatten_results(data: Dict[str, Any]) -> pd.DataFrame:
    """Flatten nested JSON → DataFrame with domain, persona_id, difficulty, scenario, answer."""
    rows: List[Dict[str, Any]] = []
    for domain, persona_blocks in data.items():
        for block in persona_blocks:
            for persona_dict in block:
                persona_id = None
                for difficulty, scenarios in persona_dict.items():
                    if not isinstance(scenarios, dict):
                        continue
                    for scen_key, scen_val in scenarios.items():
                        if persona_id is None:
                            persona_id = scen_val.get("persona_id")
                        ans = scen_val.get("answer")
                        if ans not in {"Left", "Right"}:
                            continue
                        rows.append({
                            "domain": domain,
                            "persona_id": persona_id,
                            "difficulty": difficulty,
                            "scenario": scen_key,
                            "answer": ans,
                        })
    return pd.DataFrame(rows)

################################################################################
# Plotting & counting
################################################################################

def domain_counts(df: pd.DataFrame, domain: str) -> Dict[str, Dict[str, Dict[str, int]]]:
    """Return nested dict difficulty→scenario→Left/Right counts."""
    difficulties = ["easy", "medium", "hard"]
    scenarios = ["scenario_1", "scenario_2", "scenario_3"]

    counts_df = (
        df.query("domain == @domain")
          .groupby(["difficulty", "scenario", "answer"]).size()
          .unstack(fill_value=0)
          .reindex(pd.MultiIndex.from_product([difficulties, scenarios]), fill_value=0)
    )

    nested: Dict[str, Dict[str, Dict[str, int]]] = {}
    for (diff, scen), row in counts_df.iterrows():
        nested.setdefault(diff, {})[scen] = {"Left": int(row["Left"]), "Right": int(row["Right"])}
    return nested, counts_df


def make_domain_plot(counts_df: pd.DataFrame, domain: str, outdir: Path):
    x = range(len(counts_df))
    width = 0.4
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([i - width/2 for i in x], counts_df["Left"], width, label="Left", color="#4C72B0")
    ax.bar([i + width/2 for i in x], counts_df["Right"], width, label="Right", color="#DD8452")

    xticklabels = [f"{d[:1].upper()}-{s[-1]}" for d, s in counts_df.index]
    ax.set_xticks(list(x))
    ax.set_xticklabels(xticklabels)
    ax.set_ylabel("Count")
    ax.set_title(f"Left vs Right choices — {domain}")
    ax.legend()
    plt.tight_layout()

    safe_domain = re.sub(r"[\\/]+", "_", domain).replace(" ", "_")
    outdir.mkdir(parents=True, exist_ok=True)
    plt.savefig(outdir / f"{safe_domain}_choices.png", dpi=300)
    plt.close()
    print("Saved plot:", safe_domain)

################################################################################
# Main
################################################################################

def main():
    p = argparse.ArgumentParser(description="Plot & save counts for domains with ≥10 personas")
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--outdir", type=Path, default=Path("plots"))
    args = p.parse_args()

    with args.input.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    df = flatten_results(data)
    if df.empty:
        raise ValueError("No valid Left/Right answers found in input file.")

    persona_counts = df.groupby("domain")["persona_id"].nunique()
    eligible = persona_counts[persona_counts >= 10].index.tolist()
    print("Eligible domains (≥10 personas):", ", ".join(eligible) or "None")

    if not eligible:
        print("Nothing to process.")
        return

    jsonl_path = args.outdir / "domain_choice_counts.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    with jsonl_path.open("w", encoding="utf-8") as jf:
        for dom in eligible:
            nested_counts, counts_df = domain_counts(df, dom)
            # save plot
            make_domain_plot(counts_df, dom, args.outdir)
            # write one JSON line
            obj = {
                "domain": dom,
                "persona_count": int(persona_counts[dom]),
                "counts": nested_counts,
            }
            jf.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print("\nJSONL saved to", jsonl_path)
    print("Plots saved in", args.outdir)

################################################################################

if __name__ == "__main__":
    main()

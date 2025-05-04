import re
import math
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

BASE = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus")
SUMMARY_PATH = BASE / "Data" / "Results" / "Experiments" / "CR2002" / "(EN)summary_by_domain.txt"
OUTPUT_PATH  = BASE / "Data" / "Results" / "Visualization" / "CR2002" / "(EN)scenario_domain_comparison.png"

EXPERIMENTS_INFO_PATH = BASE / "Data" / "Experiments" / "CR2002" /  "(PRE)experiment_scenarios.json"

patt_header = re.compile(r"\[(.+?)\]")                                        
patt_line   = re.compile(                                                    
    r"[-•]\s*([\w\s]+?)\s*/\s*scenario_(\d+)\s*:\s*"
    r"Left\s*=\s*(\d+).*?Right\s*=\s*(\d+)",
    flags=re.I,
)

def parse_summary(path: Path) -> dict:
    data, domain = defaultdict(dict), None
    with path.open(encoding="utf-8") as f:
        for line in f:
            if (h := patt_header.search(line)):
                domain = h.group(1).strip()
                continue

            if (m := patt_line.search(line)) and domain:
                difficulty, scen_no, left, right = m.groups()
                key = f"{difficulty.strip().lower().replace(' ', '_')}_scenario_{scen_no}"
                data[key][domain] = (int(left), int(right))

    if not data:
        raise ValueError("요약 파일 파싱 실패 – 형식을 확인하세요.")
    return data

def load_experiment_titles(json_path: Path) -> dict:
    if not json_path.exists():
        return {}

    with json_path.open(encoding="utf-8") as f:
        meta = json.load(f)

    titles = {}
    for exp in meta.get("experiments", []):
        diff_raw = exp.get("difficulty", "").lower().replace(" ", "_") 
        for idx, (opt, metric) in enumerate(zip(exp.get("options", []), exp.get("metrics", [])), start=1):
            l_pair = opt["left"]
            r_pair = opt["right"]
            key = f"{diff_raw}_scenario_{idx}"
            titles[key] = f"{metric}\nLeft: {l_pair} / Right: {r_pair}"
    return titles

scenario_titles = load_experiment_titles(EXPERIMENTS_INFO_PATH)

def plot(data: dict, output: Path, titles: dict | None = None) -> None:
    titles = titles or {}
    plt.rcParams.update({
        "axes.edgecolor": "black",
        "axes.linewidth": 1.2,
        "axes.grid": True,
        "grid.linestyle": "--",
        "grid.alpha": 0.6,
        "grid.color": "gray",
        "figure.facecolor": "white",
        "font.family": "sans-serif",
    })
    plt.rcParams["axes.unicode_minus"] = False

    scenarios = sorted(
        data.keys(),
        key=lambda k: (k.split("_scenario_")[0], int(k.split("_scenario_")[1]))
    )

    n = len(scenarios)
    if n == 0:
        raise ValueError("표시할 시나리오가 없습니다.")

    cols = min(3, n)             
    rows = math.ceil(n / cols)

    fig_w = 6.5 * cols
    fig_h = 6.0 * rows
    fig = plt.figure(figsize=(fig_w, fig_h))
    gs = gridspec.GridSpec(rows, cols, figure=fig, wspace=0.6, hspace=0.8)

    for idx, scn in enumerate(scenarios):
        ax = fig.add_subplot(gs[idx])

        title = titles.get(scn, scn.replace("_", " ").title())
        domains = list(data[scn].keys())
        left  = [data[scn][d][0] for d in domains]
        right = [data[scn][d][1] for d in domains]

        x = np.arange(len(domains))
        w = 0.35
        ax.bar(x - w/2, left,  w, label="Left")
        ax.bar(x + w/2, right, w, label="Right")

        ax.set_title(title, fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(domains, rotation=45, ha="right", fontsize=9)
        ymax = max(max(left), max(right)) * 1.1
        ax.set_ylim(0, ymax)
        ax.tick_params(axis="y", labelsize=9)
        ax.legend(fontsize=8, loc="upper right")

    fig.suptitle("Domain‑wise Response Distribution by Scenario", fontsize=16, y=0.995)
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[✓] 그래프 저장 완료 → {output.resolve()}")

if __name__ == "__main__":
    dataset = parse_summary(SUMMARY_PATH)
    plot(dataset, OUTPUT_PATH, titles=scenario_titles)

import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

BASE = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus")
SUMMARY_PATH = BASE / "Data" / "Results" / "Experiments" / "DIGB_Custom" / "(EN)summary_by_domain.txt"
OUTPUT_PATH  = BASE / "Data" / "Results" / "Visualization" / "(EN)scenario_domain_comparison.png"

patt_header = re.compile(r"\[(.+?)\]")
patt_line   = re.compile(
    r"[-•]\s*(easy|medium|hard)\s*/\s*scenario_(\d):\s*"
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
                level, scen_no, left, right = m.groups()
                key = f"{level.lower()}_scenario_{scen_no}"
                data[key][domain] = (int(left), int(right))

    if not data:
        raise ValueError("요약 파일 파싱 실패 – 형식을 확인하세요.")
    return data

scenario_titles = {
    "easy_scenario_1":   "Inequality Aversion",
    "easy_scenario_2":   "Self‑interest vs. Fairness",
    "easy_scenario_3":   "Small Gains and Losses",
    "medium_scenario_1": "Self vs. Other’s Gain",
    "medium_scenario_2": "Extreme Selfishness vs. Sharing",
    "medium_scenario_3": "Social vs. Private Utility",
    "hard_scenario_1":   "Accepting Externalities",
    "hard_scenario_2":   "Blocking Excess Gains",
    "hard_scenario_3":   "Total vs. Individual Utility",
}

def plot(data: dict, output: Path) -> None:
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

    order = {"easy": 0, "medium": 1, "hard": 2}
    scenarios = sorted(
        data.keys(),
        key=lambda k: (order[k.split("_")[0]], int(k.split("_")[2]))
    )
    if len(scenarios) != 9:
        raise ValueError("필수 시나리오(레벨×3) 9개가 모두 있어야 합니다.")

    fig = plt.figure(figsize=(20, 18))
    gs = gridspec.GridSpec(3, 3, figure=fig, wspace=0.6, hspace=0.7)

    for idx, scn in enumerate(scenarios):
        ax = fig.add_subplot(gs[idx])

        title = scenario_titles.get(scn, scn)
        domains = list(data[scn].keys())
        left  = [data[scn][d][0] for d in domains]
        right = [data[scn][d][1] for d in domains]

        x = np.arange(len(domains))
        w = 0.35
        ax.bar(x - w/2, left,  w, label="Left")
        ax.bar(x + w/2, right, w, label="Right")

        ax.set_title(title, fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(domains, rotation=45, ha="right", fontsize=10)
        ymax = max(max(left), max(right)) * 1.1
        ax.set_ylim(0, ymax)
        ax.tick_params(axis="y", labelsize=10)
        ax.legend(fontsize=9, loc="upper right")

    fig.suptitle("Domain‑wise Response Distribution by Scenario", fontsize=18, y=0.98)
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[✓] 그래프 저장 완료 → {output.resolve()}")

if __name__ == "__main__":
    dataset = parse_summary(SUMMARY_PATH)
    plot(dataset, OUTPUT_PATH)

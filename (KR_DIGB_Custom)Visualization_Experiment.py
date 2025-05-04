import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

BASE = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus")

SUMMARY_PATH = BASE / "Data" / "Results" / "Experiments" / "DIGB_Custom" / "(KR)summary_by_domain.txt"
OUTPUT_PATH  = BASE / "Data" / "Results" / "Visualization" / "(KR)scenario_domain_comparison.png"

def parse_summary(path: Path):
    """
    (KR)summary_by_domain.txt를 읽어
      {'하_scenario_1': {'경제학': (L,R), ...}, ...} 형태로 반환
    """
    patt_header = re.compile(r"\[(.+?)\]")
    patt_line = re.compile(
        r"[-•]\s*([하중상])\s*/\s*scenario_(\d):\s*Left\s*=\s*(\d+).*?Right\s*=\s*(\d+)",
        flags=re.I,
    )

    data = defaultdict(dict)
    domain = None

    with path.open(encoding="utf-8") as f:
        for line in f:
            h = patt_header.search(line)
            if h:
                domain = h.group(1).strip()
                continue
            m = patt_line.search(line)
            if m and domain:
                level, scen_no, left, right = m.groups()
                key = f"{level}_scenario_{scen_no}"
                data[key][domain] = (int(left), int(right))

    if not data:
        raise ValueError("요약 파일 파싱 실패 – 형식을 확인하세요.")
    return data


CUSTOM_TITLES = {
    "Low_scenario_1": "불평등 회피\nLeft: [0,600] / Right: [400,400]",
    "Low_scenario_2": "자기이익 vs 공정성\nLeft: [500,500] / Right: [200,800]",
    "Low_scenario_3": "작은 이득과 손해의 선택\nLeft: [200,200] / Right: [100,300]",
    "Middle_scenario_1": "자기 이익 vs 타인 이익\nLeft: [300,700] / Right: [600,400]",
    "Middle_scenario_2": "극단적 자기이익 vs 최소한의 나눔\nLeft: [0,1000] / Right: [400,600]",
    "Middle_scenario_3": "사회적 효용 vs 개인적 효용\nLeft: [900,900] / Right: [100,1400]",
    "High_scenario_1": "부정적 외부효과 수용\nLeft: [-200,1000] / Right: [400,600]",
    "High_scenario_2": "상대방의 과도한 이익 차단\nLeft: [1000,500] / Right: [0,0]",
    "High_scenario_3": "총효용 vs 자기효용\nLeft: [1000,1000] / Right: [0,1500]",
}
LEVEL_MAP = {"하": "Low", "중": "Middle", "상": "High"}


def plot(data: dict, output: Path):
    plt.rcParams.update({
        "axes.edgecolor": "black",
        "axes.linewidth": 1.2,
        "axes.grid": True,
        "grid.linestyle": "--",
        "grid.alpha": 0.6,
        "grid.color": "gray",
        "figure.facecolor": "white",
        "font.family": "Malgun Gothic",
    })
    plt.rcParams['axes.unicode_minus'] = False

    scenarios = sorted(data.keys(),
                       key=lambda k: ({"하": 0, "중": 1, "상": 2}[k[0]], k[-1]))
    if len(scenarios) != 9:
        raise ValueError("필수 시나리오(하·중·상 × 3)가 누락되었습니다.")

    fig = plt.figure(figsize=(20, 18))
    gs = gridspec.GridSpec(3, 3, figure=fig, wspace=0.6, hspace=0.7)

    for idx, scn in enumerate(scenarios):
        ax = fig.add_subplot(gs[idx])

        level_kr, no = scn.split("_scenario_")
        key_en = f"{LEVEL_MAP[level_kr]}_scenario_{no}"
        title = CUSTOM_TITLES.get(key_en, scn)

        domains = list(data[scn].keys())
        left = [data[scn][d][0] for d in domains]
        right = [data[scn][d][1] for d in domains]

        x = np.arange(len(domains))
        w = 0.35
        ax.bar(x - w/2, left,  w, label="Left",  color="#1f77b4")
        ax.bar(x + w/2, right, w, label="Right", color="#ff7f0e")

        ax.set_title(title, fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(domains, rotation=45, ha="right", fontsize=10)
        ax.set_ylim(0, 1100)
        ax.tick_params(axis="y", labelsize=10)
        ax.legend(fontsize=9, loc="upper right")

    fig.suptitle("시나리오별 도메인 응답 분포 (Left vs Right)", fontsize=18, y=0.98)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[✓] 그래프 저장 완료 → {output.resolve()}")


if __name__ == "__main__":
    dataset = parse_summary(SUMMARY_PATH)
    plot(dataset, OUTPUT_PATH)

import re
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# ───────────── 1) 결과 txt 파싱 ───────────── #
block_header = re.compile(r"^\[(.+?)\]")
line_pattern = re.compile(r"scenario_(\d+):\s*Left\s*=\s*(\d+).*?Right\s*=\s*(\d+)", re.I)

def parse_file(path: Path):
    data, current = {}, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if (m := block_header.match(line)):
                key = m.group(1)
                current = None if key.lower().startswith("grand") else key
                if current:
                    data[current] = {}
                continue
            if current and (m2 := line_pattern.search(line)):
                scen, l, r = map(int, m2.groups())
                data[current][f"scenario_{scen}"] = (l, r)
    return data

# ───────────── 2) 옵션(페이오프) 매핑 ───────────── #
options_map = {
    "easy":   {"scenario_1": {"left": (0, 600),    "right": (400, 400)},
               "scenario_2": {"left": (500, 500),  "right": (200, 800)},
               "scenario_3": {"left": (200, 200),  "right": (100, 300)}},
    "medium": {"scenario_1": {"left": (300, 700),  "right": (600, 400)},
               "scenario_2": {"left": (0, 1000),   "right": (400, 600)},
               "scenario_3": {"left": (900, 900),  "right": (100, 1400)}},
    "hard":   {"scenario_1": {"left": (-200, 1000),"right": (400, 600)},
               "scenario_2": {"left": (1000, 500), "right": (0, 0)},
               "scenario_3": {"left": (1000, 1000),"right": (0, 1500)}},
}

kor2eng = {"상": "hard", "중": "medium", "하": "easy"}

# ───────────── 3) 파일 경로 ───────────── #
en_fp = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\DIGB_Custom\merge_by_nopersona\(EN)summary_by_scenario.txt")
kr_fp = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\DIGB_Custom\merge_by_nopersona\(KR)summary_by_scenario.txt")

en_data = parse_file(en_fp)
kr_data = parse_file(kr_fp)

# ───────────── 4) 글꼴 ───────────── #
plt.rcParams["font.family"] = "Malgun Gothic"  # macOS → AppleGothic, Linux → NanumGothic

# ───────────── 5) 공통 그리기 함수 ───────────── #
colors = ("#4C72B0", "#DD8452")   # Left, Right

def plot_subplot(ax, dataset, title, order_keys, bar_w=0.5, gap=2.0):
    """
    dataset: {difficulty: {scenario: (left_cnt, right_cnt)}}
    order_keys: 순서를 강제할 난이도 키 리스트 (예: ["하", "중", "상"])
    """
    x_centers, l_heights, r_heights, labels = [], [], [], []
    cur = 0.0
    for diff in order_keys:
        if diff not in dataset:
            continue
        for scen in ["scenario_1", "scenario_2", "scenario_3"]:
            if scen not in dataset[diff]:
                continue
            eng = kor2eng.get(diff, diff).lower()
            opt = options_map[eng][scen]
            l_pair, r_pair = opt["left"], opt["right"]
            l_cnt, r_cnt   = dataset[diff][scen]

            # 중앙 좌표
            x_centers.append(cur)
            labels.append(f"L:{l_pair}\nR:{r_pair}")
            l_heights.append(l_cnt)
            r_heights.append(r_cnt)

            cur += 1.0 + gap  # 다음 시나리오로 이동

    # 막대 그리기 (중앙 기준 좌우 배치)
    left_x  = np.array(x_centers) - bar_w/2
    right_x = np.array(x_centers) + bar_w/2

    ax.bar(left_x,  l_heights, width=bar_w, color=colors[0], label="Left")
    ax.bar(right_x, r_heights, width=bar_w, color=colors[1], label="Right")

    ax.set_xticks(x_centers)
    ax.set_xticklabels(labels, ha="center", fontsize=9)
    ax.set_ylabel("Count (n)")
    ax.set_title(title, pad=8)

    # legend를 서브플롯 오른쪽 바깥으로
    handles = [plt.Rectangle((0,0),1,1,color=c) for c in colors]
    ax.legend(handles, ["Left", "Right"], frameon=False,
              loc="upper left", bbox_to_anchor=(1.02, 1))

# ───────────── 6) 2×1 subplot (세로 배치) & 저장 ───────────── #
fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=False)

# EN: 하 → 중 → 상 (easy → medium → hard)
plot_subplot(axes[0], en_data, "Without~Persona: easy / medium / hard",
             order_keys=["easy", "medium", "hard"])

# KR: 하 → 중 → 상 고정
plot_subplot(axes[1], kr_data, "Without~Persona: 하 / 중 / 상",
             order_keys=["하", "중", "상"])

fig.suptitle("Comparison of Choice Distribution (Persona‑Free Experiments)", fontsize=16, y=0.98)
fig.tight_layout()
plt.savefig("persona_free_comparison_vertical_subplots.png", dpi=300, bbox_inches="tight")
plt.show()

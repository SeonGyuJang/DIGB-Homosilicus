import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 색상 코드 지정 (비비드)
COLOR_EN = "#2f6cce"   # 선명한 블루
COLOR_KR = "#d14a49"   # 선명한 레드

# 선택할 도메인
domains = [
    "Economics",
    "Computer\nScience",
    "Law",
    "Finance",
    "History",
    "Sociology",
    "Philosophy"
]
scenarios = ["Berk29", "Barc2"]  # 두 시나리오만

# Human baseline probabilities per scenario
human_dict = {
    "Berk29": 0.31,
    "Barc2": 0.52,
}

# Persona probabilities (EN)
persona_en = {
    "Economics":             [0.7939, 0.8291],
    "Computer\nScience":     [0.8485, 0.9238],
    "Law":                   [0.8500, 0.9020],
    "Finance":               [0.7574, 0.8530],
    "History":               [0.9143, 0.9351],
    "Sociology":             [0.8709, 0.9096],
    "Philosophy":            [0.8584, 0.9008],
}

# Persona probabilities (KR)
persona_kr = {
    "Economics":             [0.5797, 0.6652],
    "Computer\nScience":     [0.5684, 0.7402],
    "Law":                   [0.7395, 0.8238],
    "Finance":               [0.5212, 0.6471],
    "History":               [0.7371, 0.8214],
    "Sociology":             [0.7366, 0.7925],
    "Philosophy":            [0.7117, 0.7806],
}

# Plotting
fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharex=False)
axes = axes.flatten()

color_baseline = "black"
offset = 0.005
bar_height = 0.35

for idx, scenario in enumerate(scenarios):
    human_val = human_dict[scenario]
    en_vals = np.array([persona_en[d][idx] for d in domains])
    kr_vals = np.array([persona_kr[d][idx] for d in domains])
    y = np.arange(len(domains))
    ax = axes[idx]

    # Compute signed PHAS values
    phas_en_vals = en_vals - human_val
    phas_kr_vals = kr_vals - human_val

    bars_en = ax.barh(
        y - bar_height / 2,
        phas_en_vals,
        left=human_val,
        height=bar_height,
        color=COLOR_EN,
        label="PHAS_EN",
        alpha=1.0
    )
    bars_kr = ax.barh(
        y + bar_height / 2,
        phas_kr_vals,
        left=human_val,
        height=bar_height,
        color=COLOR_KR,
        label="PHAS_KR",
        alpha=1.0
    )

    # Baseline
    ax.axvline(human_val, color=color_baseline, linestyle="--", linewidth=1.0)
    ax.text(
        human_val, 1.02, f"{human_val:.2f}",
        transform=ax.get_xaxis_transform(),
        ha="center", va="bottom",
        fontweight="bold", color="black", fontsize=9
    )

    ax.set_yticks(y)
    ax.set_yticklabels([d.replace("\n"," ") for d in domains])
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Probability Difference")
    ax.set_title(f"{scenario}", fontsize=10, y=1.05)  # 얇은 볼드체

    # Label bars
    for rect, phas_val in zip(bars_en, phas_en_vals):
        x_end = rect.get_x() + rect.get_width()
        x = x_end + offset if rect.get_width() >= 0 else x_end - offset
        ha = "left" if rect.get_width() >= 0 else "right"
        ax.text(x, rect.get_y() + rect.get_height()/2,
                f"{phas_val:.3f}", va="center", ha=ha,
                fontsize=8, color=COLOR_EN, fontweight="bold")

    for rect, phas_val in zip(bars_kr, phas_kr_vals):
        x_end = rect.get_x() + rect.get_width()
        x = x_end + offset if rect.get_width() >= 0 else x_end - offset
        ha = "left" if rect.get_width() >= 0 else "right"
        ax.text(x, rect.get_y() + rect.get_height()/2,
                f"{phas_val:.3f}", va="center", ha=ha,
                fontsize=8, color=COLOR_KR, fontweight="bold")

    ax.legend(loc="lower left", fontsize=9)

plt.subplots_adjust(top=0.85, wspace=0.3)
fig.suptitle("PHAS for Domains", fontsize=11, fontweight="bold")  # 얇은 볼드체

plt.show()

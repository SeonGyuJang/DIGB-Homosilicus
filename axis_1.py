import matplotlib.pyplot as plt
import numpy as np

# ---------------------------
# 1) Data
# ---------------------------
# 순서를 뒤집어서 Berk29가 가장 위에 오도록 수정
scenarios = ["Barc2", "Barc8", "Berk15", "Berk23", "Berk26", "Berk29"]
p_human_left = np.array([0.52, 0.67, 0.27, 1.00, 0.78, 0.31])
p_llm_en_left = np.array([0.96, 1.00, 0.36, 0.96, 0.99, 0.54])
p_llm_kr_left = np.array([0.72, 0.78, 0.92, 1.00, 0.90, 0.18])

# HDI (LLM - Human)
hdi_en = p_llm_en_left - p_human_left
hdi_kr = p_llm_kr_left - p_human_left

# ---------------------------
# 2) Style
# ---------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 11,
    "legend.fontsize": 10,
})

# Colors
COLOR_HUMAN = "#6e6e6e"
COLOR_EN    = "#2f6cce"
COLOR_KR    = "#d14a49"
EDGE_COLOR  = "black"

# ---------------------------
# 3) Plot
# ---------------------------
n = len(scenarios)
y = np.arange(n)

# Thicker bars & no inner-gap
bar_height = 0.26
offset_h =  bar_height   # Human (top)
offset_e =  0.0          # EN (middle)
offset_k = -bar_height   # KR (bottom)
line_w   = 0.8

fig, ax = plt.subplots(figsize=(9, 6), dpi=600)

ax.barh(y + offset_h, p_human_left, height=bar_height, label="Human",
        color=COLOR_HUMAN, edgecolor=EDGE_COLOR, linewidth=line_w)
ax.barh(y + offset_e, p_llm_en_left, height=bar_height, label="LLM (EN)",
        color=COLOR_EN, edgecolor=EDGE_COLOR, linewidth=line_w)
ax.barh(y + offset_k, p_llm_kr_left, height=bar_height, label="LLM (KR)",
        color=COLOR_KR, edgecolor=EDGE_COLOR, linewidth=line_w)

# ---------------------------
# 4) Annotations
# ---------------------------
for i in range(n):
    h, e, k = p_human_left[i], p_llm_en_left[i], p_llm_kr_left[i]
    # 값 + %p
    ax.text(min(h + 0.01, 1.22), y[i] + offset_h, f"{h:.2f}",
            va="center", ha="left", fontsize=9, color="black")
    ax.text(min(e + 0.01, 1.22), y[i] + offset_e, f"{e:.2f} ({(e-h)*100:+.0f}%p)",
            va="center", ha="left", fontsize=9, color=COLOR_EN, fontweight="bold")
    ax.text(min(k + 0.01, 1.22), y[i] + offset_k, f"{k:.2f} ({(k-h)*100:+.0f}%p)",
            va="center", ha="left", fontsize=9, color=COLOR_KR, fontweight="bold")

# ---------------------------
# 5) Axes, grid, legend
# ---------------------------
ax.set_yticks(y)

# 시나리오 정보 추가
scenario_info = {
    "Berk29": "(400,400) vs. (750,400)",
    "Berk26": "(0,800) vs. (400,400)",
    "Berk23": "(800,200) vs. (0,0)",
    "Berk15": "(200,700) vs. (600,600)",
    "Barc8": "(300,600) vs. (700,500)",
    "Barc2": "(400,400) vs. (750,375)",
}

new_labels = [f"{s}\n{scenario_info[s]}" for s in scenarios]
ax.set_yticklabels(new_labels)


# 1.00이 80% 위치에 오도록 확장
ax.set_xlim(0, 1.25)
# 눈금은 1.0까지만
ax.set_xticks(np.linspace(0, 1.0, 6))

ax.set_ylabel("Scenarios", fontsize=10)
ax.set_title("HDI Across Scenarios — LLM (EN/KR) vs. Human", fontsize=10)

ax.xaxis.grid(True, which="major", linewidth=0.4, alpha=0.3)
ax.set_axisbelow(True)

legend = ax.legend(loc="upper right", frameon=True)
legend.get_frame().set_facecolor("white")
legend.get_frame().set_alpha(0.9)
legend.get_frame().set_edgecolor("#d0d0d0")

# 1.0 기준선
ax.axvline(1.0, color="#777777", linestyle="--", linewidth=0.6, alpha=0.7)

plt.tight_layout()
plt.savefig("hdi_horizontal_thick_nogap.png", dpi=600, bbox_inches="tight")
plt.show()
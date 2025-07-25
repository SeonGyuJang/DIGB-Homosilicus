import matplotlib.pyplot as plt
import numpy as np

# 데이터 정의
scenarios = ["Berk29", "Berk26", "Berk23", "Berk15", "Barc8", "Barc2"]
p_human_left = np.array([0.31, 0.78, 1.00, 0.27, 0.67, 0.52])
p_llm_en_left = np.array([0.54, 0.99, 0.96, 0.36, 1.00, 0.96])
p_llm_kr_left = np.array([0.18, 0.90, 1.00, 0.92, 0.78, 0.72])

# HDI 계산
hdi_en = p_llm_en_left - p_human_left
hdi_kr = p_llm_kr_left - p_human_left

x = np.arange(len(scenarios))
bar_width = 0.35

# 스타일 설정
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "pdf.fonttype": 42,  # for LaTeX compatibility
})

fig, ax = plt.subplots(figsize=(7, 5), dpi=300)

# 막대 그래프: human + HDI (EN/KR)
ax.bar(x - bar_width/2, p_human_left, width=bar_width, label="Human (EN Base)", color="gray")
ax.bar(x - bar_width/2, hdi_en, width=bar_width, bottom=p_human_left, label="HDI (EN)", color="cornflowerblue")
ax.bar(x + bar_width/2, p_human_left, width=bar_width, label="Human (KR Base)", color="lightgray")
ax.bar(x + bar_width/2, hdi_kr, width=bar_width, bottom=p_human_left, label="HDI (KR)", color="salmon")

# 텍스트 주석: 최종 확률 + HDI 변화량
for i in range(len(x)):
    en_total = p_llm_en_left[i]
    kr_total = p_llm_kr_left[i]

    # 최종 EN, KR 확률 (검정)
    ax.text(x[i] - bar_width/2, en_total + 0.015, f"{en_total:.2f}",
            ha='center', va='bottom', fontsize=8, color='black')
    ax.text(x[i] + bar_width/2, kr_total + 0.015, f"{kr_total:.2f}",
            ha='center', va='bottom', fontsize=8, color='black')

    # HDI 변화량 (EN: 파랑, KR: 빨강)
    en_hdi_y = p_human_left[i] + hdi_en[i]/2
    kr_hdi_y = p_human_left[i] + hdi_kr[i]/2 + 0.01

    if scenarios[i] == "Berk23":
        en_hdi_y += 0.05
        kr_hdi_y -= 0.03

    ax.text(x[i] - bar_width/2, en_hdi_y,
            f"{hdi_en[i]:+0.2f}", ha='center', va='center', fontsize=8, color='#003f8e')
    ax.text(x[i] + bar_width/2, kr_hdi_y,
            f"{hdi_kr[i]:+0.2f}", ha='center', va='center', fontsize=8, color='#8b0000')

# 축, 제목, 범례 설정
ax.set_xticks(x)
ax.set_xticklabels(scenarios)
ax.set_ylim(0, 1.2)
ax.set_ylabel("Proportion Choosing Left Option")
ax.set_title("Human Deviation Index (HDI) Relative to Human Baseline Across Scenarios")
ax.axhline(1.0, color='gray', linestyle='--', linewidth=0.5)

# 범례 박스: 반투명 배경 추가
legend = ax.legend(loc='lower right', frameon=True)
legend.get_frame().set_facecolor('white')
legend.get_frame().set_alpha(0.85)
legend.get_frame().set_edgecolor('lightgray')

plt.tight_layout()
plt.show()

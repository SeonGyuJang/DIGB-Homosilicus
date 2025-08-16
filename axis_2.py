# import numpy as np
# import matplotlib.pyplot as plt

# # ───────────────── 0) Common Settings ───────────────── #
# scenarios = ["Berk29", "Berk26", "Berk23", "Berk15", "Barc8", "Barc2"]
# num_scenarios = len(scenarios)

# # Domains (English) and their display labels with line breaks for long names
# domains_en = [
#     "economics", "philosophy", "computer science", "law", "sociology",
#     "engineering", "environmental science", "finance", "history", "mathematics"
# ]
# xtick_labels = [
#     "Economics",
#     "Philosophy",
#     "Computer\nScience",        
#     "Law",
#     "Sociology",
#     "Engineering",
#     "Environmental\nScience",   
#     "Finance",
#     "History",
#     "Mathematics"
# ]
# num_domains = len(domains_en)
# x = np.arange(num_domains)

# # 막대 너비와 EN/KR 값 간 간격
# bar_w, bar_gap = 0.35, 0.18

# # ───────────────── 1) No-Persona Data (Baseline) ───────────────── #
# pure_en_left = {
#     "Berk29": 0.54,
#     "Berk26": 0.99,
#     "Berk23": 0.96,
#     "Berk15": 0.36,
#     "Barc8":  1.00,
#     "Barc2":  0.96
# }

# pure_kr_left = {
#     "Berk29": 0.18,
#     "Berk26": 0.90,
#     "Berk23": 1.00,
#     "Berk15": 0.92,
#     "Barc8":  0.78,
#     "Barc2":  0.72
# }

# # ───────────────── 2) Persona LLM (EN) Data ───────────────── #
# persona_en = {
#     "economics":            [0.7939, 0.8435, 0.9879, 0.7318, 0.8293, 0.8291],
#     "philosophy":           [0.8584, 0.6968, 0.9813, 0.9093, 0.8002, 0.9008],
#     "computer science":     [0.8485, 0.9260, 0.9888, 0.7880, 0.9056, 0.9238],
#     "law":                  [0.8500, 0.6746, 0.9844, 0.8383, 0.8417, 0.9020],
#     "sociology":            [0.8709, 0.7462, 0.9826, 0.9146, 0.8233, 0.9096],
#     "engineering":          [0.8555, 0.9563, 0.9878, 0.8328, 0.8688, 0.8867],
#     "environmental science":[0.8715, 0.8329, 0.9864, 0.7422, 0.8036, 0.8488],
#     "finance":              [0.7574, 0.9560, 0.9918, 0.8945, 0.9158, 0.8530],
#     "history":              [0.9143, 0.7776, 0.9878, 0.8966, 0.8916, 0.9351],
#     "mathematics":          [0.8399, 0.9192, 0.9882, 0.8799, 0.8856, 0.9400],
# }

# # ───────────────── 3) Persona LLM (KR) Data ───────────────── #
# persona_kr = {
#     "경제학":     [0.5797, 0.8478, 0.9933, 0.6458, 0.9180, 0.6652],
#     "철학":       [0.7117, 0.6910, 0.9879, 0.9998, 0.7276, 0.7806],
#     "컴퓨터과학": [0.5684, 0.8615, 0.9905, 0.7403, 0.8618, 0.7402],
#     "법학":       [0.7395, 0.6599, 0.9868, 0.7370, 0.7889, 0.8238],
#     "사회학":     [0.7366, 0.7122, 0.9862, 0.8016, 0.8469, 0.7925],
#     "공학":       [0.5721, 0.8327, 0.9888, 0.6570, 0.8004, 0.6530],
#     "환경과학":   [0.7063, 0.7980, 0.9898, 0.6933, 0.9550, 0.6809],
#     "금융학":     [0.5212, 0.9123, 0.9950, 0.8028, 0.8492, 0.6471],
#     "역사학":     [0.7371, 0.6825, 0.9868, 0.8039, 0.8033, 0.8214],
#     "수학":       [0.7027, 0.7692, 0.9890, 0.8365, 0.8398, 0.7864],
# }

# # Mapping from Korean-domain keys to English-domain keys
# kr2en = {
#     "경제학": "economics", "철학": "philosophy", "컴퓨터과학": "computer science",
#     "법학": "law", "사회학": "sociology", "공학": "engineering",
#     "환경과학": "environmental science", "금융학": "finance",
#     "역사학": "history", "수학": "mathematics"
# }

# # ───────────────── 4) Visualization: 2x3 subplots by scenario ───────────────── #
# fig, axes = plt.subplots(2, 3, figsize=(20, 10), dpi=100)
# axes = axes.flatten()

# # 색상 설정
# color_en_bar = "cornflowerblue"
# color_kr_bar = "salmon"
# color_en_text = "blue"  # EN 텍스트 색상
# color_kr_text = "red"   # KR 텍스트 색상
# color_en_line = "blue"
# color_kr_line = "red"

# for idx, scen in enumerate(scenarios):
#     ax = axes[idx]

#     # No-Persona baseline
#     base_en = pure_en_left[scen]
#     base_kr = pure_kr_left[scen]

#     # Persona 값
#     persona_en_vals = np.array([persona_en[dom][idx] for dom in domains_en])
#     persona_kr_vals = np.array([persona_kr[k][idx] for k in kr2en.keys()])

#     # 차이 계산 (Persona - Baseline)
#     diff_en = persona_en_vals - base_en
#     diff_kr = persona_kr_vals - base_kr

#     # 막대 그리기: baseline에서부터 시작
#     bars_en = ax.bar(x - bar_gap, diff_en, bar_w, bottom=base_en, color=color_en_bar, label="EN Persona")
#     bars_kr = ax.bar(x + bar_gap, diff_kr, bar_w, bottom=base_kr, color=color_kr_bar, label="KR Persona")

#     # 차이값을 막대 내부 상단에 텍스트 표시 (EN=파란색, KR=빨간색)
#     for bar in bars_en:
#         height = bar.get_height()
#         if height > 0:
#             y_text = bar.get_y() + height - 0.05
#         else:
#             y_text = bar.get_y() + 0.05
#         ax.text(
#             bar.get_x() + bar.get_width() / 2, y_text,
#             f"{height:.2f}", ha="center", va="center", fontsize=7, color=color_en_text
#         )

#     for bar in bars_kr:
#         height = bar.get_height()
#         if height > 0:
#             y_text = bar.get_y() + height - 0.05
#         else:
#             y_text = bar.get_y() + 0.05
#         ax.text(
#             bar.get_x() + bar.get_width() / 2, y_text,
#             f"{height:.2f}", ha="center", va="center", fontsize=7, color=color_kr_text
#         )

#     # Baseline 수평선(점선) 그리기
#     ax.axhline(base_en, color=color_en_line, linestyle="--", linewidth=1.2, label="EN Baseline")
#     ax.axhline(base_kr, color=color_kr_line, linestyle="--", linewidth=1.2, label="KR Baseline")

#     # Baseline 수치를 끝나는 오른쪽에 표시
#     x_pos_right = num_domains - 0.5
#     ax.text(x_pos_right + 0.02, base_en, f"{base_en:.2f}", ha="left", va="center",
#             color="black", fontweight="bold", fontsize=8)
#     ax.text(x_pos_right + 0.02, base_kr, f"{base_kr:.2f}", ha="left", va="center",
#             color="black", fontweight="bold", fontsize=8)

#     # 제목/레이블 설정
#     ax.set_title(scen, fontsize=12, pad=12)
#     ax.set_xticks(x)
#     ax.set_xticklabels(xtick_labels, rotation=45, ha="right", fontsize=8)
#     ax.set_xlim(-0.5, num_domains - 0.5)
#     ax.set_ylim(0, 1.2)  # Y축 범위를 1.2까지 확장
#     ax.set_yticks(np.arange(0, 1.01, 0.2))  # 눈금은 0~1.0까지
#     ax.set_ylabel("Probability ($P$)", fontsize=10)
#     ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.7)

#     # 범례: 오른쪽 아래 (투명한 배경)
#     handles, labels = ax.get_legend_handles_labels()
#     unique = dict(zip(labels, handles))
#     ax.legend(unique.values(), unique.keys(), loc="lower right", fontsize=7, frameon=True, facecolor="white", framealpha=0.6)

# # 왼쪽 PEM 공식 위치를 차트와 겹치지 않도록 적절히 떨어뜨려서 표시
# fig.supylabel(r"$PEM = P_{\mathrm{Persona}} - P_{\mathrm{NoPersona}}$",
#                  fontsize=16, x=0.045)

# # 내부 타이틀을 간결하게 설정
# fig.suptitle("Effect of Persona Injection (PEM) Across Domains and Languages", fontsize=18, y=0.97)

# # 서브플롯 간격 조정
# fig.subplots_adjust(
#     left=0.10, right=0.95,
#     top=0.88, bottom=0.12,
#     hspace=0.35, wspace=0.3
# )

# plt.show()


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

# ------------------ Data ------------------
scenarios_all = ["Berk29", "Berk26", "Berk23", "Berk15", "Barc8", "Barc2"]
scenarios_to_show = ["Berk29", "Berk15"]

domains_en = [
    "economics","philosophy","computer science","law","sociology",
    "engineering","environmental science","finance","history","mathematics"
]
xtick_labels = [
    "Economics","Philosophy","Comp Sci","Law","Sociology",
    "Engineering","Env Sci","Finance","History","Mathematics"
]

pure_en_left = {"Berk29":0.54,"Berk26":0.99,"Berk23":0.96,"Berk15":0.36,"Barc8":1.00,"Barc2":0.96}
pure_kr_left = {"Berk29":0.18,"Berk26":0.90,"Berk23":1.00,"Berk15":0.92,"Barc8":0.78,"Barc2":0.72}

persona_en = {
    "economics":[0.7939,0.8435,0.9879,0.7318,0.8293,0.8291],
    "philosophy":[0.8584,0.6968,0.9813,0.9093,0.8002,0.9008],
    "computer science":[0.8485,0.9260,0.9888,0.7880,0.9056,0.9238],
    "law":[0.8500,0.6746,0.9844,0.8383,0.8417,0.9020],
    "sociology":[0.8709,0.7462,0.9826,0.9146,0.8233,0.9096],
    "engineering":[0.8555,0.9563,0.9878,0.8328,0.8688,0.8867],
    "environmental science":[0.8715,0.8329,0.9864,0.7422,0.8036,0.8488],
    "finance":[0.7574,0.9560,0.9918,0.8945,0.9158,0.8530],
    "history":[0.9143,0.7776,0.9878,0.8966,0.8916,0.9351],
    "mathematics":[0.8399,0.9192,0.9882,0.8799,0.8856,0.9400],
}
persona_kr = {
    "경제학":[0.5797,0.8478,0.9933,0.6458,0.9180,0.6652],
    "철학":[0.7117,0.6910,0.9879,0.9998,0.7276,0.7806],
    "컴퓨터과학":[0.5684,0.8615,0.9905,0.7403,0.8618,0.7402],
    "법학":[0.7395,0.6599,0.9868,0.7370,0.7889,0.8238],
    "사회학":[0.7366,0.7122,0.9862,0.8016,0.8469,0.7925],
    "공학":[0.5721,0.8327,0.9888,0.6570,0.8004,0.6530],
    "환경과학":[0.7063,0.7980,0.9898,0.6933,0.9550,0.6809],
    "금융학":[0.5212,0.9123,0.9950,0.8028,0.8492,0.6471],
    "역사학":[0.7371,0.6825,0.9868,0.8039,0.8033,0.8214],
    "수학":[0.7027,0.7692,0.9890,0.8365,0.8398,0.7864],
}
kr_keys_in_order = ["경제학","철학","컴퓨터과학","법학","사회학","공학","환경과학","금융학","역사학","수학"]

# ------------------ Style ------------------
plt.rcParams.update({
    "font.family":"DejaVu Sans",
    "font.size":10,
    "axes.labelsize":10,
    "axes.titlesize":9,
    "xtick.labelsize":9,
    "ytick.labelsize":9,
    "legend.fontsize":9,
    "pdf.fonttype":42,
})

COLOR_EN = "#2f6cce"
COLOR_KR = "#d14a49"
EDGE = "black"

# ------------------ Plot 1x2 vertical bars ------------------
fig, axes = plt.subplots(1, 2, figsize=(14.5, 6.8), dpi=600, sharey=True)  # 세로 6 → 6.8로 살짝 증가

bar_w = 0.48
bar_gap = 0.05
label_fs = 6.5
value_fs = 5.5

for idx, scen in enumerate(scenarios_to_show):
    ax = axes[idx]
    scen_idx = scenarios_all.index(scen)

    en_vals = np.array([persona_en[d][scen_idx] for d in domains_en])
    kr_vals = np.array([persona_kr[k][scen_idx] for k in kr_keys_in_order])

    x = np.arange(len(domains_en)) * (1 + bar_gap)

    bars_en = ax.bar(
        x - bar_w/2, en_vals, width=bar_w,
        color=COLOR_EN, edgecolor=EDGE, linewidth=0.7, label="EN Persona"
    )
    bars_kr = ax.bar(
        x + bar_w/2, kr_vals, width=bar_w,
        color=COLOR_KR, edgecolor=EDGE, linewidth=0.7, label="KR Persona"
    )

    base_en = pure_en_left[scen]
    base_kr = pure_kr_left[scen]

    ax.axhline(base_en, color=COLOR_EN, linestyle=(0, (4, 2)), linewidth=1.0, alpha=0.9)
    ax.axhline(base_kr, color=COLOR_KR, linestyle=(0, (4, 2)), linewidth=1.0, alpha=0.9)

    trans = blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(1.005, base_en, f"{base_en:.2f}",
            transform=trans, ha="left", va="center", fontsize=label_fs, color="black")
    ax.text(1.005, base_kr, f"{base_kr:.2f}",
            transform=trans, ha="left", va="center", fontsize=label_fs, color="black")

    for b in bars_en:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.012,
                f"{b.get_height():.2f}", ha="center", va="bottom",
                fontsize=value_fs, color="black")
    for b in bars_kr:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.012,
                f"{b.get_height():.2f}", ha="center", va="bottom",
                fontsize=value_fs, color="black")

    ax.set_xticks(x)
    ax.set_xticklabels(xtick_labels, rotation=30, ha="right")
    ax.set_ylim(0, 1.10)
    ax.set_title(scen, fontweight="bold")
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)

axes[0].set_ylabel("Proportion (P)")
fig.suptitle("Final Proportions by Domain — Berk29, Berk15", fontsize=10, fontweight="bold", y=0.96)

handles = [
    plt.Line2D([0], [0], color=COLOR_EN, lw=8, label="EN Persona"),
    plt.Line2D([0], [0], color=COLOR_KR, lw=8, label="KR Persona"),
    plt.Line2D([0], [0], color=COLOR_EN, lw=1.2, linestyle=(0, (4, 2)), label="EN Baseline"),
    plt.Line2D([0], [0], color=COLOR_KR, lw=1.2, linestyle=(0, (4, 2)), label="KR Baseline"),
]
fig.legend(handles=handles, loc="lower center", ncol=4, frameon=True, framealpha=0.9)

# wspace를 기존 대비 70% 줄이기 → 0.35 * 0.3 ≈ 0.105
fig.subplots_adjust(left=0.07, right=0.99, top=0.90, bottom=0.18, wspace=0.105)

png_path = r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\pem_vertical_final_1x2_gap_reduced.png"
pdf_path = r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\pem_vertical_final_1x2_gap_reduced.pdf"
plt.savefig(png_path, dpi=600, bbox_inches="tight")
plt.savefig(pdf_path, dpi=600, bbox_inches="tight")
print(png_path, pdf_path)



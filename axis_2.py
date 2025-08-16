import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

# ------------------ Data ------------------
scenarios_all = ["Berk29", "Berk26", "Berk23", "Berk15", "Barc8", "Barc2"]
scenarios_to_show = ["Berk29", "Berk15"]

domains_en_all = [
    "economics","philosophy","computer science","law","sociology",
    "engineering","environmental science","finance","history","mathematics"
]
xtick_labels_all = [
    "Economics","Philosophy","Comp Sci","Law","Sociology",
    "Engineering","Env Sci","Finance","History","Mathematics"
]

keep_idx = [0, 2, 3, 7, 8]
domains_en = [domains_en_all[i] for i in keep_idx]
xtick_labels = [xtick_labels_all[i] for i in keep_idx]

pure_en_left = {"Berk29":0.54,"Berk26":0.99,"Berk23":0.96,"Berk15":0.36,"Barc8":1.00,"Barc2":0.96}
pure_kr_left = {"Berk29":0.18,"Berk26":0.90,"Berk23":1.00,"Berk15":0.92,"Barc8":0.78,"Barc2":0.72}

persona_en = {
    "economics":[0.7939,0.8435,0.9879,0.7318,0.8293,0.8291],
    "computer science":[0.8485,0.9260,0.9888,0.7880,0.9056,0.9238],
    "law":[0.8500,0.6746,0.9844,0.8383,0.8417,0.9020],
    "finance":[0.7574,0.9560,0.9918,0.8945,0.9158,0.8530],
    "history":[0.9143,0.7776,0.9878,0.8966,0.8916,0.9351],
}
persona_kr = {
    "경제학":[0.5797,0.8478,0.9933,0.6458,0.9180,0.6652],
    "컴퓨터과학":[0.5684,0.8615,0.9905,0.7403,0.8618,0.7402],
    "법학":[0.7395,0.6599,0.9868,0.7370,0.7889,0.8238],
    "금융학":[0.5212,0.9123,0.9950,0.8028,0.8492,0.6471],
    "역사학":[0.7371,0.6825,0.9868,0.8039,0.8033,0.8214],
}
kr_keys_in_order = ["경제학","컴퓨터과학","법학","금융학","역사학"]

# ------------------ Style ------------------
plt.rcParams.update({
    "font.family":"DejaVu Sans",
    "font.size":10,
    "axes.labelsize":10,
    "axes.titlesize":10,
    "xtick.labelsize":9,
    "ytick.labelsize":9,
    "legend.fontsize":9,
    "pdf.fonttype":42,
})

# 🎨 비비드 톤
COLOR_EN = "#2f6cce"  # Vivid Blue
COLOR_KR = "#d14a49"  # Vivid Mustard Yellow
BASE_EN = COLOR_EN
BASE_KR = COLOR_KR
EDGE = "#222222"

fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.2), dpi=600, sharey=True)

bar_w = 0.48
bar_gap = 0.12
label_fs = 7
value_fs = 8

for idx, scen in enumerate(scenarios_to_show):
    ax = axes[idx]
    scen_idx = scenarios_all.index(scen)

    en_vals = np.array([persona_en[d][scen_idx] for d in domains_en])
    kr_vals = np.array([persona_kr[k][scen_idx] for k in kr_keys_in_order])

    x = np.arange(len(domains_en)) * (1 + bar_gap)

    bars_en = ax.bar(
        x - bar_w/2, en_vals, width=bar_w,
        color=COLOR_EN, edgecolor=EDGE, linewidth=0.6, label="EN Persona"
    )
    bars_kr = ax.bar(
        x + bar_w/2, kr_vals, width=bar_w,
        color=COLOR_KR, edgecolor=EDGE, linewidth=0.6, label="KR Persona"
    )

    base_en = pure_en_left[scen]
    base_kr = pure_kr_left[scen]

    ax.axhline(base_en, color=BASE_EN, linestyle=(0, (4, 2)), linewidth=1.0, alpha=0.7)
    ax.axhline(base_kr, color=BASE_KR, linestyle=(0, (4, 2)), linewidth=1.0, alpha=0.7)

    trans = blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(1.01, base_en, f"{base_en:.2f}", transform=trans,
            ha="left", va="center", fontsize=label_fs, color=BASE_EN, fontweight="bold")
    ax.text(1.01, base_kr, f"{base_kr:.2f}", transform=trans,
            ha="left", va="center", fontsize=label_fs, color=BASE_KR, fontweight="bold")

    # 값 라벨: 막대 위, 검은색
    for b in bars_en:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.015,
                f"{b.get_height():.2f}", ha="center", va="bottom",
                fontsize=value_fs, color="black", fontweight="bold")
    for b in bars_kr:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.015,
                f"{b.get_height():.2f}", ha="center", va="bottom",
                fontsize=value_fs, color="black", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(xtick_labels, rotation=0, ha="center")
    ax.set_ylim(0, 1.10)
    ax.set_title(scen, fontweight="bold", color="#111111")
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.4)

axes[0].set_ylabel("Proportion (P)", fontweight="bold")

fig.suptitle("Final Proportions by Domain — Berk29 & Berk15",
             fontsize=11, fontweight="bold", color="#111111", y=0.98)

handles = [
    plt.Line2D([0], [0], color=COLOR_EN, lw=8, label="EN Persona"),
    plt.Line2D([0], [0], color=COLOR_KR, lw=8, label="KR Persona"),
    plt.Line2D([0], [0], color=BASE_EN, lw=1.2, linestyle=(0, (4, 2)), label="EN Baseline"),
    plt.Line2D([0], [0], color=BASE_KR, lw=1.2, linestyle=(0, (4, 2)), label="KR Baseline"),
]
fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False)

fig.subplots_adjust(left=0.08, right=0.995, top=0.90, bottom=0.20, wspace=0.12)

png_path = r"pem_vertical_Berk29_Berk15_5domains_vividBlue_yellow.png"
pdf_path = r"pem_vertical_Berk29_Berk15_5domains_vividBlue_yellow.pdf"
plt.savefig(png_path, dpi=600, bbox_inches="tight")
plt.savefig(pdf_path, dpi=600, bbox_inches="tight")
print(png_path, pdf_path)

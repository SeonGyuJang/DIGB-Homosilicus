import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Domains with manual line breaks for long names
domains = [
    "Economics",
    "Philosophy",
    "Computer\nScience",
    "Law",
    "Sociology",
    "Engineering",
    "History",
    "Mathematics",
    "Finance",
    "Environmental\nScience"
]
scenarios = ["Berk29", "Berk26", "Berk23", "Berk15", "Barc8", "Barc2"]

# Human baseline probabilities per scenario
human_dict = {
    "Berk29": 0.31,
    "Berk26": 0.78,
    "Berk23": 1.00,
    "Berk15": 0.27,
    "Barc8": 0.67,
    "Barc2": 0.52,
}

# Persona probabilities
persona_en = {
    "Economics":             [0.7939, 0.8435, 0.9879, 0.7318, 0.8293, 0.8291],
    "Philosophy":            [0.8584, 0.6968, 0.9813, 0.9093, 0.8002, 0.9008],
    "Computer\nScience":     [0.8485, 0.9260, 0.9888, 0.7880, 0.9056, 0.9238],
    "Law":                   [0.8500, 0.6746, 0.9844, 0.8383, 0.8417, 0.9020],
    "Sociology":             [0.8709, 0.7462, 0.9826, 0.9146, 0.8233, 0.9096],
    "Engineering":           [0.8555, 0.9563, 0.9878, 0.8328, 0.8688, 0.8867],
    "History":               [0.9143, 0.7776, 0.9878, 0.8966, 0.8916, 0.9351],
    "Mathematics":           [0.8399, 0.9192, 0.9882, 0.8799, 0.8856, 0.9400],
    "Finance":               [0.7574, 0.9560, 0.9918, 0.8945, 0.9158, 0.8530],
    "Environmental\nScience":[0.8715, 0.8329, 0.9864, 0.7422, 0.8036, 0.8488],
}

persona_kr = {
    "Economics":             [0.5797, 0.8478, 0.9933, 0.6458, 0.9180, 0.6652],
    "Philosophy":            [0.7117, 0.6910, 0.9879, 0.9998, 0.7276, 0.7806],
    "Computer\nScience":     [0.5684, 0.8615, 0.9905, 0.7403, 0.8618, 0.7402],
    "Law":                   [0.7395, 0.6599, 0.9868, 0.7370, 0.7889, 0.8238],
    "Sociology":             [0.7366, 0.7122, 0.9862, 0.8016, 0.8469, 0.7925],
    "Engineering":           [0.5721, 0.8327, 0.9888, 0.6570, 0.8004, 0.6530],
    "History":               [0.7371, 0.6825, 0.9868, 0.8039, 0.8033, 0.8214],
    "Mathematics":           [0.7027, 0.7692, 0.9890, 0.8365, 0.8398, 0.7864],
    "Finance":               [0.5212, 0.9123, 0.9950, 0.8028, 0.8492, 0.6471],
    "Environmental\nScience":[0.7063, 0.7980, 0.9898, 0.6933, 0.9550, 0.6809],
}

# Prepare a DataFrame for PHAS values (signed difference)
rows = []
for scenario_idx, scenario in enumerate(scenarios):
    human_val = human_dict[scenario]
    for domain in domains:
        en_val = persona_en[domain][scenario_idx]
        kr_val = persona_kr[domain][scenario_idx]
        phas_en = en_val - human_val  # signed difference
        phas_kr = kr_val - human_val  # signed difference
        rows.append({
            "Scenario": scenario,
            "Domain": domain.replace("\n", " "),
            "PHAS_EN": round(phas_en, 3),
            "PHAS_KR": round(phas_kr, 3)
        })

df_phas = pd.DataFrame(rows)

# Display the updated tabl
# Plotting the updated PHAS bar charts with x-axis labels on all subplots
fig, axes = plt.subplots(2, 3, figsize=(20, 12), sharex=False)
axes = axes.flatten()

color_en_bar = "cornflowerblue"
color_kr_bar = "salmon"
color_baseline = "gray"
offset = 0.005
bar_height = 0.35

for idx, scenario in enumerate(scenarios):
    human_val = human_dict[scenario]
    en_vals = np.array([persona_en[d][idx] for d in domains])
    kr_vals = np.array([persona_kr[d][idx] for d in domains])
    y = np.arange(len(domains))
    ax = axes[idx]

    # Compute signed PHAS for lengths
    phas_en_vals = en_vals - human_val
    phas_kr_vals = kr_vals - human_val

    bars_en = ax.barh(
        y - bar_height / 2,
        phas_en_vals,
        left=human_val,
        height=bar_height,
        color=color_en_bar,
        label="PHAS_EN (signed)",
        alpha=0.8
    )
    bars_kr = ax.barh(
        y + bar_height / 2,
        phas_kr_vals,
        left=human_val,
        height=bar_height,
        color=color_kr_bar,
        label="PHAS_KR (signed)",
        alpha=0.8
    )

    # Baseline
    ax.axvline(human_val, color=color_baseline, linestyle="--", linewidth=0.8)
    ax.text(
        human_val, 1.02, f"{human_val:.2f}",
        transform=ax.get_xaxis_transform(),
        ha="center", va="bottom",
        fontweight="bold", color="black", fontsize=9
    )

    ax.set_yticks(y)
    ax.set_yticklabels(domains)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Probability Difference")  # X축 레이블 추가
    ax.tick_params(axis="x", labelbottom=True)  # X축 눈금 레이블 표시
    ax.set_title(f"{scenario}", fontsize=12, y=1.08)

    # Label bars with signed PHAS values
    for rect, phas_val in zip(bars_en, phas_en_vals):
        x_end = rect.get_x() + rect.get_width()
        if rect.get_width() >= 0:
            x = x_end + offset
            ha = "left"
        else:
            x = x_end - offset
            ha = "right"
        y_pos = rect.get_y() + rect.get_height() / 2
        ax.text(x, y_pos, f"{phas_val:.3f}", va="center", ha=ha, fontsize=8, color="navy")

    for rect, phas_val in zip(bars_kr, phas_kr_vals):
        x_end = rect.get_x() + rect.get_width()
        if rect.get_width() >= 0:
            x = x_end + offset
            ha = "left"
        else:
            x = x_end - offset
            ha = "right"
        y_pos = rect.get_y() + rect.get_height() / 2
        ax.text(x, y_pos, f"{phas_val:.3f}", va="center", ha=ha, fontsize=8, color="darkred")

    ax.legend(loc="lower left", fontsize=9)

plt.subplots_adjust(top=0.90, wspace=0.5, hspace=0.4)
fig.suptitle("Updated PHAS (Signed) by Domain Anchored at Human Baseline", fontsize=18)

plt.show()

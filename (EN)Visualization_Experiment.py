import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

# === Style settings ===
plt.rcParams.update({
    "axes.edgecolor": "black",
    "axes.linewidth": 1.2,
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
    "grid.color": "gray",
    "figure.facecolor": "white",
})
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

# === Scenario Titles ===
scenario_titles = {
    "easy_scenario_1": "Inequality Aversion",
    "easy_scenario_2": "Self-interest vs. Fairness",
    "easy_scenario_3": "Small Gains and Losses",
    "medium_scenario_1": "Self vs. Other's Gain",
    "medium_scenario_2": "Extreme Selfishness vs. Sharing",
    "medium_scenario_3": "Social vs. Private Utility",
    "hard_scenario_1": "Accepting Externalities",
    "hard_scenario_2": "Blocking Excess Gains",
    "hard_scenario_3": "Total vs. Individual Utility",
}

# === Data: domain -> scenario -> (Left, Right) ===
data = {
    "computer science": {
        "easy_scenario_1": (95, 905), "easy_scenario_2": (551, 449), "easy_scenario_3": (561, 439),
        "medium_scenario_1": (299, 701), "medium_scenario_2": (614, 386), "medium_scenario_3": (753, 247),
        "hard_scenario_1": (179, 821), "hard_scenario_2": (248, 752), "hard_scenario_3": (791, 209),
    },
    "economics": {
        "easy_scenario_1": (184, 816), "easy_scenario_2": (608, 392), "easy_scenario_3": (583, 417),
        "medium_scenario_1": (262, 738), "medium_scenario_2": (398, 602), "medium_scenario_3": (789, 211),
        "hard_scenario_1": (138, 862), "hard_scenario_2": (381, 619), "hard_scenario_3": (829, 171),
    },
    "engineering": {
        "easy_scenario_1": (112, 888), "easy_scenario_2": (522, 478), "easy_scenario_3": (610, 390),
        "medium_scenario_1": (282, 718), "medium_scenario_2": (562, 438), "medium_scenario_3": (812, 188),
        "hard_scenario_1": (154, 846), "hard_scenario_2": (382, 618), "hard_scenario_3": (822, 178),
    },
    "environmental science": {
        "easy_scenario_1": (46, 954), "easy_scenario_2": (859, 141), "easy_scenario_3": (788, 212),
        "medium_scenario_1": (91, 909), "medium_scenario_2": (157, 843), "medium_scenario_3": (929, 71),
        "hard_scenario_1": (47, 953), "hard_scenario_2": (346, 654), "hard_scenario_3": (967, 33),
    },
    "finance": {
        "easy_scenario_1": (348, 652), "easy_scenario_2": (364, 636), "easy_scenario_3": (394, 606),
        "medium_scenario_1": (559, 441), "medium_scenario_2": (750, 250), "medium_scenario_3": (552, 448),
        "hard_scenario_1": (312, 688), "hard_scenario_2": (399, 601), "hard_scenario_3": (604, 396),
    },
    "history": {
        "easy_scenario_1": (23, 977), "easy_scenario_2": (833, 167), "easy_scenario_3": (799, 201),
        "medium_scenario_1": (97, 903), "medium_scenario_2": (171, 829), "medium_scenario_3": (910, 90),
        "hard_scenario_1": (74, 926), "hard_scenario_2": (239, 761), "hard_scenario_3": (933, 67),
    },
    "law": {
        "easy_scenario_1": (65, 935), "easy_scenario_2": (763, 237), "easy_scenario_3": (696, 304),
        "medium_scenario_1": (194, 806), "medium_scenario_2": (317, 683), "medium_scenario_3": (880, 120),
        "hard_scenario_1": (79, 921), "hard_scenario_2": (231, 769), "hard_scenario_3": (921, 79),
    },
    "mathematics": {
        "easy_scenario_1": (71, 929), "easy_scenario_2": (568, 432), "easy_scenario_3": (489, 511),
        "medium_scenario_1": (309, 691), "medium_scenario_2": (506, 494), "medium_scenario_3": (723, 277),
        "hard_scenario_1": (168, 832), "hard_scenario_2": (308, 692), "hard_scenario_3": (741, 259),
    },
    "philosophy": {
        "easy_scenario_1": (78, 922), "easy_scenario_2": (837, 163), "easy_scenario_3": (744, 256),
        "medium_scenario_1": (110, 890), "medium_scenario_2": (122, 878), "medium_scenario_3": (865, 135),
        "hard_scenario_1": (55, 945), "hard_scenario_2": (319, 681), "hard_scenario_3": (899, 101),
    },
    "sociology": {
        "easy_scenario_1": (40, 960), "easy_scenario_2": (860, 140), "easy_scenario_3": (775, 225),
        "medium_scenario_1": (90, 910), "medium_scenario_2": (121, 879), "medium_scenario_3": (951, 49),
        "hard_scenario_1": (54, 946), "hard_scenario_2": (279, 721), "hard_scenario_3": (944, 56),
    }
}

# === Create plot ===
fig = plt.figure(figsize=(20, 18))
gs = gridspec.GridSpec(3, 3, figure=fig, wspace=0.6, hspace=0.7)
scenarios = list(scenario_titles.keys())

for idx, scenario in enumerate(scenarios):
    ax = fig.add_subplot(gs[idx])
    title_text = scenario_titles[scenario]

    domains = list(data.keys())
    left_vals = [data[domain][scenario][0] for domain in domains]
    right_vals = [data[domain][scenario][1] for domain in domains]
    x = np.arange(len(domains))
    width = 0.35

    ax.bar(x - width / 2, left_vals, width, label='Left', color='#1f77b4')
    ax.bar(x + width / 2, right_vals, width, label='Right', color='#ff7f0e')

    ax.set_title(title_text, fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(domains, rotation=45, ha='right', fontsize=10)
    ax.set_ylim(0, 1100)
    ax.tick_params(axis='y', labelsize=10)
    ax.legend(fontsize=9, loc='upper right')

fig.suptitle("Response Distribution per Scenario by Domain (Left vs Right)", fontsize=18, y=0.98)
plt.savefig("(EN)scenario_domain_comparison.png", dpi=300, bbox_inches='tight')
plt.show()

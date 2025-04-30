import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

plt.rcParams.update({
    "axes.edgecolor": "black",
    "axes.linewidth": 1.2,
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
    "grid.color": "gray",
    "figure.facecolor": "white",
})
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

custom_titles = {
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

scenario_key_map = {
    "하_scenario_1": "Low_scenario_1", "하_scenario_2": "Low_scenario_2", "하_scenario_3": "Low_scenario_3",
    "중_scenario_1": "Middle_scenario_1", "중_scenario_2": "Middle_scenario_2", "중_scenario_3": "Middle_scenario_3",
    "상_scenario_1": "High_scenario_1", "상_scenario_2": "High_scenario_2", "상_scenario_3": "High_scenario_3"
}

data = {
    "하_scenario_1": {"경제학": (305, 695), "공학": (389, 611), "금융학": (455, 545), "법학": (204, 796), "사회학": (130, 870),
                   "수학": (286, 714), "역사학": (164, 836), "철학": (203, 797), "컴퓨터과학": (342, 658), "환경과학": (235, 765)},
    "하_scenario_2": {"경제학": (890, 110), "공학": (932, 68), "금융학": (846, 154), "법학": (968, 32), "사회학": (979, 21),
                   "수학": (925, 75), "역사학": (987, 13), "철학": (964, 36), "컴퓨터과학": (909, 91), "환경과학": (982, 18)},
    "하_scenario_3": {"경제학": (892, 108), "공학": (933, 67), "금융학": (837, 163), "법학": (968, 32), "사회학": (967, 33),
                   "수학": (910, 90), "역사학": (983, 17), "철학": (957, 43), "컴퓨터과학": (900, 100), "환경과학": (971, 29)},
    "중_scenario_1": {"경제학": (332, 668), "공학": (492, 508), "금융학": (591, 409), "법학": (266, 734), "사회학": (120, 880),
                   "수학": (376, 624), "역사학": (171, 829), "철학": (179, 821), "컴퓨터과학": (467, 533), "환경과학": (194, 806)},
    "중_scenario_2": {"경제학": (201, 799), "공학": (349, 651), "금융학": (359, 641), "법학": (127, 873), "사회학": (73, 927),
                   "수학": (265, 735), "역사학": (95, 905), "철학": (109, 891), "컴퓨터과학": (339, 661), "환경과학": (119, 881)},
    "중_scenario_3": {"경제학": (933, 67), "공학": (971, 29), "금융학": (864, 136), "법학": (978, 22), "사회학": (987, 13),
                   "수학": (949, 51), "역사학": (994, 6), "철학": (965, 35), "컴퓨터과학": (948, 52), "환경과학": (994, 6)},
    "상_scenario_1": {"경제학": (214, 786), "공학": (369, 631), "금융학": (353, 647), "법학": (167, 833), "사회학": (139, 861),
                   "수학": (250, 750), "역사학": (166, 834), "철학": (123, 877), "컴퓨터과학": (376, 624), "환경과학": (179, 821)},
    "상_scenario_2": {"경제학": (881, 119), "공학": (939, 61), "금융학": (911, 89), "법학": (878, 122), "사회학": (815, 185),
                   "수학": (882, 118), "역사학": (842, 158), "철학": (902, 98), "컴퓨터과학": (839, 161), "환경과학": (870, 130)},
    "상_scenario_3": {"경제학": (914, 86), "공학": (955, 45), "금융학": (854, 146), "법학": (955, 45), "사회학": (975, 25),
                   "수학": (932, 68), "역사학": (991, 9), "철학": (943, 57), "컴퓨터과학": (932, 68), "환경과학": (983, 17)},
}

fig = plt.figure(figsize=(20, 18))
gs = gridspec.GridSpec(3, 3, figure=fig, wspace=0.6, hspace=0.7)

scenarios = list(data.keys())

for idx, scenario in enumerate(scenarios):
    ax = fig.add_subplot(gs[idx])
    readable_key = scenario_key_map.get(scenario, scenario)
    title_text = custom_titles.get(readable_key, scenario)

    domain_labels = list(data[scenario].keys())
    left_vals = [data[scenario][dom][0] for dom in domain_labels]
    right_vals = [data[scenario][dom][1] for dom in domain_labels]

    x = np.arange(len(domain_labels))
    width = 0.35

    ax.bar(x - width/2, left_vals, width, label='Left', color='#1f77b4')
    ax.bar(x + width/2, right_vals, width, label='Right', color='#ff7f0e')

    ax.set_title(title_text, fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(domain_labels, rotation=45, ha='right', fontsize=10)
    ax.set_ylim(0, 1100)
    ax.tick_params(axis='y', labelsize=10)

    ax.legend(fontsize=9, loc='upper right') 

fig.suptitle("시나리오별 도메인 응답 분포 (Left vs Right)", fontsize=18, y=0.98)

plt.savefig("scenario_domain_comparison.png", dpi=300, bbox_inches='tight')
plt.show()

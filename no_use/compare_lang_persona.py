import matplotlib.pyplot as plt
import numpy as np

# 시나리오 번호 & 이름
scenarios = [1, 2, 3, 4, 5, 6]
scenario_info = {
    1: "Berk29", 2: "Berk26", 3: "Berk23",
    4: "Berk15", 5: "Barc8", 6: "Barc2"
}

# 시나리오 선택지 (L / R)
scenario_options = {
    1: ("[400, 400]", "[750, 400]"),
    2: ("[0, 800]", "[400, 400]"),
    3: ("[800, 200]", "[0, 0]"),
    4: ("[200, 700]", "[600, 600]"),
    5: ("[300, 600]", "[700, 500]"),
    6: ("[400, 400]", "[750, 375]")
}

# 영어 실험 결과 (도메인별, 시나리오별 Left/Right)
en_results = {
    "computer science": {
        1: (83.8, 16.2), 2: (94.9, 5.1), 3: (99.1, 0.9),
        4: (81.1, 18.9), 5: (94.1, 5.9), 6: (94.5, 5.5)
    },
    "economics": {
        1: (71.7, 28.3), 2: (85.4, 14.6), 3: (99.3, 0.7),
        4: (73.8, 26.2), 5: (84.3, 15.7), 6: (87.8, 12.2)
    },
    "engineering": {
        1: (78.1, 21.9), 2: (93.8, 6.2), 3: (99.7, 0.3),
        4: (84.7, 15.3), 5: (88.7, 11.3), 6: (88.8, 11.2)
    },
    "environmental science": {
        1: (84.1, 15.9), 2: (82.5, 17.5), 3: (99.0, 1.0),
        4: (72.3, 27.7), 5: (83.8, 16.2), 6: (87.9, 12.1)
    },
    "finance": {
        1: (66.5, 33.5), 2: (95.2, 4.8), 3: (99.6, 0.4),
        4: (85.0, 15.0), 5: (93.4, 6.6), 6: (89.4, 10.6)
    },
    "history": {
        1: (88.1, 11.9), 2: (79.7, 20.3), 3: (99.2, 0.8),
        4: (73.2, 26.8), 5: (89.8, 10.2), 6: (95.3, 4.7)
    },
    "law": {
        1: (82.4, 17.6), 2: (69.7, 30.3), 3: (98.8, 1.2),
        4: (61.5, 38.5), 5: (86.8, 13.2), 6: (91.6, 8.4)
    },
    "mathematics": {
        1: (79.1, 20.9), 2: (92.8, 7.2), 3: (99.8, 0.2),
        4: (78.2, 21.8), 5: (88.4, 11.6), 6: (94.6, 5.4)
    },
    "philosophy": {
        1: (80.4, 19.6), 2: (71.9, 28.1), 3: (98.4, 1.6),
        4: (69.9, 30.1), 5: (82.1, 17.9), 6: (90.6, 9.4)
    },
    "sociology": {
        1: (85.0, 15.0), 2: (69.7, 30.3), 3: (98.1, 1.9),
        4: (60.0, 40.0), 5: (81.7, 18.3), 6: (91.7, 8.3)
    },
}

# 한국어 실험 결과 (도메인별, 시나리오별 Left/Right)
kr_results = {
    "컴퓨터과학": {
        1: (42.4, 57.6), 2: (95.9, 4.1), 3: (99.3, 0.7),
        4: (61.9, 38.1), 5: (76.3, 23.7), 6: (74.8, 25.2)
    },
    "경제학": {
        1: (40.7, 59.3), 2: (93.8, 6.2), 3: (98.8, 1.2),
        4: (50.8, 49.2), 5: (71.5, 28.5), 6: (68.4, 31.6)
    },
    "공학": {
        1: (46.1, 53.9), 2: (97.0, 3.0), 3: (99.3, 0.7),
        4: (55.2, 44.8), 5: (65.5, 34.5), 6: (76.4, 23.6)
    },
    "환경과학": {
        1: (47.0, 53.0), 2: (93.6, 6.4), 3: (98.7, 1.3),
        4: (42.4, 57.6), 5: (60.8, 39.2), 6: (69.0, 31.0)
    },
    "금융학": {
        1: (35.1, 64.9), 2: (97.7, 2.3), 3: (99.0, 1.0),
        4: (70.8, 29.2), 5: (83.0, 17.0), 6: (70.7, 29.3)
    },
    "역사학": {
        1: (58.7, 41.3), 2: (88.5, 11.5), 3: (97.1, 2.9),
        4: (38.2, 61.8), 5: (61.7, 38.3), 6: (83.5, 16.5)
    },
    "법학": {
        1: (58.9, 41.1), 2: (83.3, 16.7), 3: (97.8, 2.2),
        4: (30.8, 69.2), 5: (60.0, 40.0), 6: (82.4, 17.6)
    },
    "수학": {
        1: (53.2, 46.8), 2: (92.6, 7.4), 3: (98.9, 1.1),
        4: (53.6, 46.4), 5: (73.8, 26.2), 6: (76.7, 23.3)
    },
    "철학": {
        1: (60.3, 39.7), 2: (85.2, 14.8), 3: (97.5, 2.5),
        4: (36.6, 63.4), 5: (60.6, 39.4), 6: (83.2, 16.8)
    },
    "사회학": {
        1: (60.6, 39.4), 2: (85.2, 14.8), 3: (97.4, 2.6),
        4: (34.3, 65.7), 5: (63.5, 36.5), 6: (79.6, 20.4)
    },
}

# 도메인 묶음 (5개씩)
domain_groups = [
    [("computer science", "컴퓨터과학"), ("economics", "경제학"), ("engineering", "공학"),
     ("environmental science", "환경과학"), ("finance", "금융학")],
    [("history", "역사학"), ("law", "법학"), ("mathematics", "수학"),
     ("philosophy", "철학"), ("sociology", "사회학")]
]

def make_group_plot(domain_group, filename):
    fig, axes = plt.subplots(len(domain_group), 2, figsize=(16, 3 * len(domain_group)), sharey='row')
    width = 0.35
    x = np.arange(len(scenarios))

    for i, (domain_en, domain_kr) in enumerate(domain_group):
        en_left = [en_results[domain_en][s][0] for s in scenarios]
        en_right = [en_results[domain_en][s][1] for s in scenarios]
        kr_left = [kr_results[domain_kr][s][0] for s in scenarios]
        kr_right = [kr_results[domain_kr][s][1] for s in scenarios]

        # 줄바꿈 포함 X축 레이블
        xtick_labels = [
            f"{scenario_info[s]}\nL: {scenario_options[s][0]}\nR: {scenario_options[s][1]}"
            for s in scenarios
        ]

        # LEFT
        ax_left = axes[i, 0]
        ax_left.bar(x - width/2, en_left, width, label='English')
        ax_left.bar(x + width/2, kr_left, width, label='Korean')
        ax_left.set_title(f'{domain_en} - Left')
        ax_left.set_xticks(x)
        ax_left.set_xticklabels(xtick_labels)
        ax_left.set_ylim(0, 120)
        if i == len(domain_group) - 1:
            ax_left.set_xlabel('Scenario')
        ax_left.set_ylabel('Percentage (%)')

        # RIGHT
        ax_right = axes[i, 1]
        ax_right.bar(x - width/2, en_right, width, label='English')
        ax_right.bar(x + width/2, kr_right, width, label='Korean')
        ax_right.set_title(f'{domain_en} - Right')
        ax_right.set_xticks(x)
        ax_right.set_xticklabels(xtick_labels)
        ax_right.set_ylim(0, 120)
        if i == len(domain_group) - 1:
            ax_right.set_xlabel('Scenario')

    fig.suptitle('Comparison of Experimental Results (English vs Korean)', fontsize=18)
    fig.legend(['English', 'Korean'], loc='upper right', fontsize = 15)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(filename, dpi=300)
    plt.close()

# 그룹별 저장
make_group_plot(domain_groups[0], 'group1_5domains_en_vs_kr.png')
make_group_plot(domain_groups[1], 'group2_5domains_en_vs_kr.png')

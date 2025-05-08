import matplotlib.pyplot as plt
import numpy as np

# 도메인명 (10개)
domains = [
    "computer science", "economics", "engineering", "environmental science",
    "finance", "history", "law", "mathematics", "philosophy", "sociology"
]

# 기존 연구 (페르소나 있음) 데이터 (Left % / Right %)
persona_left = {
    1: [83.8, 71.7, 78.1, 84.1, 66.5, 88.1, 82.4, 79.1, 80.4, 85.0],
    2: [94.9, 85.4, 93.8, 82.5, 95.2, 79.7, 69.7, 92.8, 71.9, 69.7],
    3: [99.1, 99.3, 99.7, 99.0, 99.6, 99.2, 98.8, 99.8, 98.4, 98.1],
    4: [81.1, 73.8, 84.7, 72.3, 85.0, 73.2, 61.5, 78.2, 69.9, 60.0],
    5: [94.1, 84.3, 88.7, 83.8, 93.4, 89.8, 86.8, 88.4, 82.1, 81.7],
    6: [94.5, 87.8, 88.8, 87.9, 89.4, 95.3, 91.6, 94.6, 90.6, 91.7],
}
persona_right = {k: [100 - v for v in vals] for k, vals in persona_left.items()}

# ALL PERSONAS (페르소나 없음) 데이터 (Left % / Right %)
nopersona_left = {
    1: [56.7] * 10,
    2: [100.0] * 10,
    3: [100.0] * 10,
    4: [26.7] * 10,
    5: [100.0] * 10,
    6: [96.7] * 10,
}
nopersona_right = {k: [100 - v for v in vals] for k, vals in nopersona_left.items()}

# 시나리오 정보 (이름 + Left/Right 옵션)
scenario_info = {
    1: ("Berk29", "[400, 400]", "[750, 400]"),
    2: ("Berk26", "[0, 800]", "[400, 400]"),
    3: ("Berk23", "[800, 200]", "[0, 0]"),
    4: ("Berk15", "[200, 700]", "[600, 600]"),
    5: ("Barc8", "[300, 600]", "[700, 500]"),
    6: ("Barc2", "[400, 400]", "[750, 375]"),
}


def make_plot(scenarios, filename):
    fig, axes = plt.subplots(len(scenarios), 2, figsize=(18, 12), sharey='row')
    x = np.linspace(0, len(domains) * 1.2, len(domains))
    width = 0.6  # 가로폭 넓힘

    for i, scenario in enumerate(scenarios):
        name, l_option, r_option = scenario_info[scenario]
        persona_vals_left = persona_left[scenario]
        persona_vals_right = persona_right[scenario]
        nopersona_vals_left = nopersona_left[scenario]
        nopersona_vals_right = nopersona_right[scenario]

        # LEFT 비교
        ax_left = axes[i, 0]
        bars_np = ax_left.bar(x - width/2, nopersona_vals_left, width, label='No Persona')
        bars_p = ax_left.bar(x + width/2, persona_vals_left, width, label='Persona')
        ax_left.set_title(f'{name} (Left)\nL: {l_option}, R: {r_option}', fontsize=11)
        ax_left.set_xticks(x)
        ax_left.set_xticklabels(domains, rotation=45, ha='right')
        ax_left.set_ylim(0, 120)
        ax_left.set_yticks(np.arange(0, 110, 20))
        if i == len(scenarios) - 1:
            ax_left.set_xlabel('Domain')
        ax_left.set_ylabel('Percentage (%)')

        # 텍스트 추가 (No Persona)
        for bar in bars_np:
            height = bar.get_height()
            ax_left.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                f'{height:.0f}%',
                ha='center', va='bottom',
                fontsize=8,
                color=bar.get_facecolor()
            )
        # 텍스트 추가 (Persona)
        for bar in bars_p:
            height = bar.get_height()
            ax_left.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                f'{height:.0f}%',
                ha='center', va='bottom',
                fontsize=8,
                color=bar.get_facecolor()
            )

        # RIGHT 비교
        ax_right = axes[i, 1]
        bars_np_r = ax_right.bar(x - width/2, nopersona_vals_right, width, label='No Persona')
        bars_p_r = ax_right.bar(x + width/2, persona_vals_right, width, label='Persona')
        ax_right.set_title(f'{name} (Right)\nL: {l_option}, R: {r_option}', fontsize=11)
        ax_right.set_xticks(x)
        ax_right.set_xticklabels(domains, rotation=45, ha='right')
        ax_right.set_ylim(0, 120)
        ax_right.set_yticks(np.arange(0, 110, 20))
        if i == len(scenarios) - 1:
            ax_right.set_xlabel('Domain')

        # 텍스트 추가 (No Persona)
        for bar in bars_np_r:
            height = bar.get_height()
            ax_right.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                f'{height:.0f}%',
                ha='center', va='bottom',
                fontsize=8,
                color=bar.get_facecolor()
            )
        # 텍스트 추가 (Persona)
        for bar in bars_p_r:
            height = bar.get_height()
            ax_right.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                f'{height:.0f}%',
                ha='center', va='bottom',
                fontsize=8,
                color=bar.get_facecolor()
            )

    # 전체 제목 (논문 스타일)
    fig.suptitle('Comparison of Persona-Based and Non-Persona CR2002 Experiments Across Domains', fontsize=18)

    # Figure 전체의 legend 추가 (오른쪽 상단, 전체 바깥)
    fig.legend(['No Persona', 'Persona'], loc='upper right', fontsize=15)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(filename, dpi=300)
    plt.close()


# 시나리오 1~3 저장
make_plot([1, 2, 3], 'persona_vs_no_persona_scenarios_1_2_3.png')

# 시나리오 4~6 저장
make_plot([4, 5, 6], 'persona_vs_no_persona_scenarios_4_5_6.png')

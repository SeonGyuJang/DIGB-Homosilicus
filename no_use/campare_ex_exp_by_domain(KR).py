import matplotlib.pyplot as plt
import numpy as np

# 한글 깨짐 방지 (윈도우/맥 호환)
plt.rcParams['font.family'] = ['NanumGothic', 'Malgun Gothic', 'AppleGothic']
plt.rcParams['axes.unicode_minus'] = False

# 도메인명 (10개)
domains = [
    "경제학", "공학", "금융학", "법학", "사회학",
    "수학", "역사학", "철학", "컴퓨터과학", "환경과학"
]

# 기존 연구 (페르소나 있음) 데이터 (Left % / Right %)
persona_left = {
    1: [40.7, 46.1, 35.1, 58.9, 60.6, 53.2, 58.7, 60.3, 42.4, 47.0],
    2: [93.8, 97.0, 97.7, 83.3, 85.2, 92.6, 88.5, 85.2, 95.9, 93.6],
    3: [98.8, 99.3, 99.0, 97.8, 97.4, 98.9, 97.1, 97.5, 99.3, 98.7],
    4: [50.8, 55.2, 70.8, 30.8, 34.3, 53.6, 38.2, 36.6, 61.9, 42.4],
    5: [71.5, 65.5, 83.0, 60.0, 63.5, 73.8, 61.7, 60.6, 76.3, 60.8],
    6: [68.4, 76.4, 70.7, 82.4, 79.6, 76.7, 83.5, 83.2, 74.8, 69.0],
}
persona_right = {k: [100 - v for v in vals] for k, vals in persona_left.items()}

# CR2002 논문 데이터 실험 결과
nopersona_left = {
    1: [31] * 10,
    2: [78] * 10,
    3: [100.0] * 10,
    4: [27] * 10,
    5: [67] * 10,
    6: [52] * 10,
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
        bars_np = ax_left.bar(x - width/2, nopersona_vals_left, width, label='CR2002 results')
        bars_p = ax_left.bar(x + width/2, persona_vals_left, width, label='페르소나')
        ax_left.set_title(f'{name} (Left)\nL: {l_option}, R: {r_option}', fontsize=11)
        ax_left.set_xticks(x)
        ax_left.set_xticklabels(domains, rotation=45, ha='right')
        ax_left.set_ylim(0, 120)
        ax_left.set_yticks(np.arange(0, 110, 20))
        if i == len(scenarios) - 1:
            ax_left.set_xlabel('도메인')
        ax_left.set_ylabel('선택 비율 (%)')

        # 텍스트 추가 (CR2002 results)
        for bar in bars_np:
            height = bar.get_height()
            ax_left.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                f'{height:.1f}%',
                ha='center', va='bottom',
                fontsize=8,
                color=bar.get_facecolor()
            )
        # 텍스트 추가 (페르소나)
        for bar in bars_p:
            height = bar.get_height()
            ax_left.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                f'{height:.1f}%',
                ha='center', va='bottom',
                fontsize=8,
                color=bar.get_facecolor()
            )

        # RIGHT 비교
        ax_right = axes[i, 1]
        bars_np_r = ax_right.bar(x - width/2, nopersona_vals_right, width, label='CR2002 results')
        bars_p_r = ax_right.bar(x + width/2, persona_vals_right, width, label='페르소나')
        ax_right.set_title(f'{name} (Right)\nL: {l_option}, R: {r_option}', fontsize=11)
        ax_right.set_xticks(x)
        ax_right.set_xticklabels(domains, rotation=45, ha='right')
        ax_right.set_ylim(0, 120)
        ax_right.set_yticks(np.arange(0, 110, 20))
        if i == len(scenarios) - 1:
            ax_right.set_xlabel('도메인')

        # 텍스트 추가 (CR2002 results)
        for bar in bars_np_r:
            height = bar.get_height()
            ax_right.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                f'{height:.1f}%',
                ha='center', va='bottom',
                fontsize=8,
                color=bar.get_facecolor()
            )
        # 텍스트 추가 (페르소나)
        for bar in bars_p_r:
            height = bar.get_height()
            ax_right.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                f'{height:.1f}%',
                ha='center', va='bottom',
                fontsize=8,
                color=bar.get_facecolor()
            )

    # 전체 제목 (논문 스타일)
    fig.suptitle('도메인별 페르소나 vs. 기존 CR2002 실험 결과 비교', fontsize=18)

    # Figure 전체의 legend 추가 (오른쪽 상단, 전체 바깥)
    fig.legend(['CR2002 results', '페르소나'], loc='upper right', bbox_to_anchor=(1.15, 1), fontsize=12)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(filename, dpi=300)
    plt.close()


# 시나리오 1~3 저장
make_plot([1, 2, 3], 'KR_persona_vs_cr2002_scenarios_1_2_3.png')

# 시나리오 4~6 저장
make_plot([4, 5, 6], 'KR_persona_vs_cr2002_scenarios_4_5_6.png')

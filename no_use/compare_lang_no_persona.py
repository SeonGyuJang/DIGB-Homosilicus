import matplotlib.pyplot as plt
import numpy as np

# 시나리오 정보 (이름 + Left/Right 옵션)
scenario_info = {
    1: ("Berk29", "[400, 400]", "[750, 400]"),
    2: ("Berk26", "[0, 800]", "[400, 400]"),
    3: ("Berk23", "[800, 200]", "[0, 0]"),
    4: ("Berk15", "[200, 700]", "[600, 600]"),
    5: ("Barc8", "[300, 600]", "[700, 500]"),
    6: ("Barc2", "[400, 400]", "[750, 375]"),
}

# EN (영어 데이터)
cr2002_left = {
    1: 56.7,
    2: 100.0,
    3: 100.0,
    4: 26.7,
    5: 100.0,
    6: 96.7,
}
cr2002_right = {k: 100 - v for k, v in cr2002_left.items()}

# KR (한국어 데이터)
nopersona_left = {
    1: 6.7,
    2: 83.3,
    3: 100.0,
    4: 96.7,
    5: 93.3,
    6: 56.7,
}
nopersona_right = {k: 100 - v for k, v in nopersona_left.items()}

def make_comparison_plot(scenarios, filename):
    fig, axes = plt.subplots(len(scenarios), 2, figsize=(14, 12), sharey='row')
    x_labels = ['English Results (NO-Persona)', 'Korean Results (No-Persona)']
    x = np.array([0, 1])
    width = 0.6
    colors = ['orange', 'dodgerblue']

    for i, scenario in enumerate(scenarios):
        name, l_option, r_option = scenario_info[scenario]
        cr_left = cr2002_left[scenario]
        cr_right = cr2002_right[scenario]
        no_left = nopersona_left[scenario]
        no_right = nopersona_right[scenario]

        # LEFT 비교
        ax_left = axes[i, 0]
        bars = ax_left.bar(x, [cr_left, no_left], width, color=colors)
        ax_left.set_title(f'{name} (Left)\nL: {l_option}, R: {r_option}', fontsize=11)
        ax_left.set_xticks(x)
        ax_left.set_xticklabels(x_labels, rotation=0, ha='center')
        ax_left.set_ylim(0, 160)
        ax_left.set_ylabel('Choice Percentage (%)')

        for bar in bars:
            height = bar.get_height()
            ax_left.text(bar.get_x() + bar.get_width() / 2, height + 2,
                         f'{height:.1f}%', ha='center', va='bottom',
                         fontsize=9, color=bar.get_facecolor())

        x_start, x_end = x[0] + width / 2, x[1] - width / 2
        y_start, y_end = cr_left, no_left
        ax_left.fill_between([x_start, x_end], min(y_start, y_end), max(y_start, y_end),
                             color='lightcoral', alpha=0.3)
        ax_left.plot([x_start, x_end], [y_start, y_end], 'r--', linewidth=1.5)
        change = no_left - cr_left
        sign = '+' if change >= 0 else '-'
        ax_left.text((x_start + x_end) / 2, (y_start + y_end) / 2,
                     f'{sign}{abs(change):.1f}%', color='black',
                     fontsize=10, fontweight='bold', ha='center', va='center')

        # RIGHT 비교
        ax_right = axes[i, 1]
        bars_r = ax_right.bar(x, [cr_right, no_right], width, color=colors)
        ax_right.set_title(f'{name} (Right)\nL: {l_option}, R: {r_option}', fontsize=11)
        ax_right.set_xticks(x)
        ax_right.set_xticklabels(x_labels, rotation=0, ha='center')
        ax_right.set_ylim(0, 160)

        for bar in bars_r:
            height = bar.get_height()
            ax_right.text(bar.get_x() + bar.get_width() / 2, height + 2,
                          f'{height:.1f}%', ha='center', va='bottom',
                          fontsize=9, color=bar.get_facecolor())

        y_start_r, y_end_r = cr_right, no_right
        ax_right.fill_between([x_start, x_end], min(y_start_r, y_end_r), max(y_start_r, y_end_r),
                              color='lightcoral', alpha=0.3)
        ax_right.plot([x_start, x_end], [y_start_r, y_end_r], 'r--', linewidth=1.5)
        change_r = no_right - cr_right
        sign_r = '+' if change_r >= 0 else '-'
        ax_right.text((x_start + x_end) / 2, (y_start_r + y_end_r) / 2,
                      f'{sign_r}{abs(change_r):.1f}%', color='black',
                      fontsize=10, fontweight='bold', ha='center', va='center')

    fig.suptitle('Comparison of English (NO-Persona) and Korean (No-Persona) Experimental Results', fontsize=18)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(filename, dpi=300)
    plt.close()

# 시나리오 1~3
make_comparison_plot([1, 2, 3], 'compare_lang_berk29_26_23.png')

# 시나리오 4~6
make_comparison_plot([4, 5, 6], 'compare_lang_berk15_barc8_barc2.png')

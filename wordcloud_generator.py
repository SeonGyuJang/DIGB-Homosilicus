import json
from pathlib import Path
from collections import defaultdict
from wordcloud import WordCloud

import matplotlib.pyplot as plt
from tqdm import tqdm

# ────────── 경로 설정 ────────── #
BASE_DIR   = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Experiments\CR2002\(KR)CR2002_EXPERIMENT_RESULTS_10000")
OUTPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\Data\Results\Visualization\CR2002")
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET_METRICS = ["Berk29", "Berk15"]
thought_pool   = defaultdict(list)
metric_file_count = defaultdict(int)

# ────────── (2) 모든 JSON 파일 순회 ────────── #
json_files = list(BASE_DIR.glob("*.json"))
total_files = len(json_files)

for fp in tqdm(json_files, desc="🔍 Parsing JSON"):
    try:
        with fp.open(encoding="utf-8") as f:
            data = json.load(f)

        # 각 metric이 이 파일에서 등장했는지 체크
        metric_found_in_file = {metric: False for metric in TARGET_METRICS}

        def collect_thoughts(node):
            """딕셔너리 / 리스트를 깊이 탐색하며 metric & thought 추출"""
            if isinstance(node, dict):
                if "metric" in node and "thought" in node:
                    metric = node["metric"]
                    if metric in TARGET_METRICS:
                        thought_pool[metric].append(node["thought"])
                        metric_found_in_file[metric] = True
                        # 디버그 출력
                        print(f"[DEBUG] {fp.name}: Found {metric}")
                for v in node.values():
                    collect_thoughts(v)
            elif isinstance(node, list):
                for item in node:
                    collect_thoughts(item)

        collect_thoughts(data)

        # 파일당 중복 없이 metric 카운트
        for metric, found in metric_found_in_file.items():
            if found:
                metric_file_count[metric] += 1

    except json.JSONDecodeError:
        print(f"[!] {fp.name} → JSON 디코딩 오류, 건너뜀")

# ────────── (3) metric별 워드클라우드 생성 ────────── #
for metric in TARGET_METRICS:
    thought_count = len(thought_pool[metric])
    file_count_for_metric = metric_file_count[metric]
    text = " ".join(thought_pool[metric])
    if not text:
        print(f"[!] {metric} 데이터가 없습니다.")
        continue

    print(f"\n[SUMMARY] {metric}: {thought_count} thoughts from {file_count_for_metric} files (total {total_files} files)\n")

    wc = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        max_words=200,
        collocations=False,  # 중복 단어 결합 방지
        font_path=r"C:\Windows\Fonts\malgun.ttf",  # 한글 필요 시 주석 해제
    ).generate(text)

    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title(
        f"Word Cloud for {metric}\n",
        fontsize=15
    )
    plt.tight_layout(pad=0)

    out_file = OUTPUT_DIR / f"kr_{metric}_wordcloud.png"
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"[✔] {out_file.name} 저장 완료")

print("\n🎉 모든 워드클라우드 생성 끝!")

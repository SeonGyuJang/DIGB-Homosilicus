import json

# JSON 파일 경로
input_file = r"plots/domain_choice_counts.jsonl"

# JSONL 파일을 읽고 데이터를 저장할 리스트
data = []

# JSONL 파일 읽기
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        data.append(json.loads(line))

# 도메인별로 Easy ~ Hard의 시나리오별 Left/Right 개수 출력
for entry in data:
    domain = entry["domain"]
    print(f"Domain: {domain}")
    counts = entry["counts"]
    for difficulty, scenarios in counts.items():
        print(f"  Difficulty: {difficulty}")
        for scenario, choices in scenarios.items():
            left_count = choices.get("Left", 0)
            right_count = choices.get("Right", 0)
            print(f"    {scenario}: Left = {left_count}, Right = {right_count}")
    print("\n")
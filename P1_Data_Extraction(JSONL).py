import json
import random
from collections import defaultdict

# 입력 파일
input_path = '/Users/jangseongyu/Desktop/elite_personas.part4.jsonl'
# 최종 출력 파일
output_path = '/Users/jangseongyu/Documents/GitHub/DIGB-Homosilicus/data/Persona_Data_Top_n_domains_Random_Extraction/Persona_Part_4_to_6.jsonl'

# 상위 몇 개 도메인
top_n_domains = 20
# 도메인별 랜덤 추출할 수
sample_size_per_domain = 10000

# 1단계: None 제거하면서 도메인별 데이터 수 세기
domain_counter = {}

print("1단계: 파일 읽으며 None 제거 + 도메인별 개수 세는 중...")

with open(input_path, 'r', encoding='utf-8') as infile:
    for line in infile:
        try:
            data = json.loads(line)
            persona = data.get('persona')
            general_domain = data.get('general domain (top 1 percent)')
            idx = data.get('idx')
            
            # None 객체 또는 문자열 'none' 제외
            if general_domain and str(general_domain).lower() != "none":
                domain = str(general_domain).lower()
                domain_counter[domain] = domain_counter.get(domain, 0) + 1
        except json.JSONDecodeError:
            continue

# 2단계: 상위 20개 도메인 선정
top_domains = sorted(domain_counter.items(), key=lambda x: x[1], reverse=True)[:top_n_domains]
top_domain_names = set(domain for domain, _ in top_domains)

print(f"\n상위 {top_n_domains}개 도메인 선정 완료:")
for domain, count in top_domains:
    print(f"- {domain}: {count}개")

# 3단계: 상위 도메인별 데이터 모으기
domain_to_records = defaultdict(list)

print("\n3단계: 상위 도메인 데이터 수집 중...")

# 파일을 다시 읽으면서, 상위 도메인 데이터만 모으기
with open(input_path, 'r', encoding='utf-8') as infile:
    for line in infile:
        try:
            data = json.loads(line)
            persona = data.get('persona')
            general_domain = data.get('general domain (top 1 percent)')
            idx = data.get('idx')
            
            if general_domain and str(general_domain).lower() != "none":
                domain = str(general_domain).lower()
                if domain in top_domain_names:
                    record = {
                        'persona': persona,
                        'general domain (top 1 percent)': general_domain,
                        'idx' : idx
                    }
                    domain_to_records[domain].append(record)
        except json.JSONDecodeError:
            continue

# 4단계: 도메인별로 10,000개씩 랜덤 샘플링
print("\n4단계: 도메인별로 10,000개씩 랜덤 샘플링 중...")

final_samples = []

for domain in top_domain_names:
    records = domain_to_records[domain]
    if len(records) >= sample_size_per_domain:
        sampled = random.sample(records, sample_size_per_domain)
    else:
        print(f"⚠️ 도메인 '{domain}'는 데이터가 {len(records)}개밖에 없음! 가능한 만큼 모두 사용.")
        sampled = records
    final_samples.extend(sampled)

print(f"\n총 추출된 데이터 수: {len(final_samples)}개")

# 5단계: 최종 결과 저장
print(f"\n5단계: {output_path} 파일로 저장하는 중...")

with open(output_path, 'w', encoding='utf-8') as outfile:
    for item in final_samples:
        outfile.write(json.dumps(item, ensure_ascii=False) + '\n')

print("\n=== 완료 ===")
print(f"최종 결과 파일 경로: {output_path}")

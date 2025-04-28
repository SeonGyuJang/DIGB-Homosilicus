import json
import os
from pathlib import Path
from collections import defaultdict

# 1. 파일 경로 세팅
original_data_path = Path(r'C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\Persona_Data_Top_n_domains_Random_Extraction\(KR)Persona_Part_1_to_3.json')  # 원본 데이터
experiment_results_dir = Path(r'C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results\(KR)LangChain_EXPERIMENT_RESULTS')  # 실험 결과 폴더
output_path = Path(r'C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results\(KR)EXP_result_all.json')  # 병합 결과 저장 경로

# 2. domain별 persona_id 리스트 만들기
with open(original_data_path, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

domain_to_ids = defaultdict(list)
id_to_persona = {}
persona_id_to_domain = {}

for entry in original_data['PERSONA']:
    domain = entry['general domain (top 1 percent)']
    persona_id = entry['idx']
    domain_to_ids[domain].append(persona_id)
    id_to_persona[persona_id] = entry['persona']
    persona_id_to_domain[persona_id] = domain  # << 이거 추가!!

# 3. 결과 병합용 빈 구조 만들기
merged_data = defaultdict(list)

# 4. 결과 폴더 순회
for file in experiment_results_dir.glob('Person_*.json'):
    with open(file, 'r', encoding='utf-8') as f:
        exp_data = json.load(f)

    # 파일 이름에서 id 추출
    persona_id = int(file.stem.split('_')[1])

    # 이 persona_id가 어떤 domain에 속하는지 바로 찾기
    domain = persona_id_to_domain.get(persona_id)
    if domain is None:
        continue  # 매칭되는 도메인이 없으면 건너뜀

    persona_content = id_to_persona.get(persona_id, "")
    persona_id_str = str(persona_id)

    persona_result = {}
    for kor_diff in ['하', '중', '상']:  # '하', '중', '상' 그대로
        if kor_diff not in exp_data:
            continue
        
        scenarios = exp_data[kor_diff]
        scenario_result = {}
        for scenario_name, content in scenarios.items():
            scenario_result[scenario_name] = {
                'persona_content': content['persona_desc'],
                'persona_id': persona_id_str,
                'metric': content['metric'],
                'difficulty': kor_diff,
                'options': content['options'],
                'thought': content['thought'],
                'answer': content['answer'],
            }
        
        persona_result[kor_diff] = scenario_result

    # domain별로 append
    merged_data[domain].append([persona_result])

# 5. 저장
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

print(f"✅ 완료! 결과 파일: {output_path}")

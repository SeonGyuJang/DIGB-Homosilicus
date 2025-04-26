# 페르소나허브에 있는 개콘 JSONL 파일에서 일부분만 저장하는 코드.
import os
import json
from collections import defaultdict

def read_jsonl_grouped(file_path, num_lines=1000):
    """
    JSONL 파일을 읽어 각 페르소나 객체에 인덱스를 추가하고,
    "general domain (top 1 percent)" 필드를 기준으로 그룹화하여 반환합니다.
    """
    groups = defaultdict(list)
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= num_lines:
                break
            try:
                persona = json.loads(line)
                persona['idx'] = i + 1 
                key = persona.get("general domain (top 1 percent)", "None")
                groups[key].append(persona)
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류 (줄 {i+1}): {e}")
    return groups

def save_as_json(data, output_path):
    """
    data를 JSON 파일로 저장합니다.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file = r"C:\Users\dsng3\Desktop\DIGB_Project\elite_personas.part1.jsonl"  
    output_file = r"C:\Users\dsng3\Desktop\DIGB_Project\elite_personas_grouped.json" 

    grouped_personas = read_jsonl_grouped(input_file, num_lines=1000)
    save_as_json(grouped_personas, output_file)
    print(f"총 {len(grouped_personas)} 개의 그룹으로 JSON 파일이 저장되었습니다.")

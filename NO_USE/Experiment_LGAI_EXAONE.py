import json
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# 실행 장치 확인: GPU 사용 가능하면 'cuda', 아니면 'cpu'
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Running on device: {device}")

# 실험 데이터 로드
persona_data_path = r"C:\Users\dsng3\Desktop\DIGB_Project\persona_data.json"  # 99개 페르소나 데이터 경로
scenario_data_path = r"C:\Users\dsng3\Desktop\DIGB_Project\experiment_scenarios.json"

with open(persona_data_path, "r", encoding="utf-8") as f:
    persona_data = json.load(f)

with open(scenario_data_path, "r", encoding="utf-8") as f:
    scenario_data = json.load(f)

# 모델 로드 (GPU 사용 시 device_map="auto", 그렇지 않으면 None)
model_name = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto" if device == "cuda" else None
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 모델을 지정된 장치로 이동
model.to(device)

# 결과 저장 디렉토리
output_folder = r"C:\Users\dsng3\Desktop\DIGB_Project\LGAI_EXAONE_Experiment_result"
os.makedirs(output_folder, exist_ok=True)

# EN 프롬프트 템플릿 함수
def create_user_prompt(A_left, B_left, A_right, B_right):
    return (
        "You are playing the role of Person B in a Social Preferences Experiment.\n\n"
        "Below are two choices presented to you. Please select one and explain your reasoning.\n\n"
        "**Choices**\n"
        f"- **(Left):** Person B receives {B_left}, and Person A receives {A_left}.\n"
        f"- **(Right):** Person B receives {B_right}, and Person A receives {A_right}.\n\n"
        "**Question**\n"
        "Which option do you choose? (Please answer only with 'Left' or 'Right.')"
    )

# 실험 수행
for idx, persona in enumerate(persona_data, start=1):
    # 페르소나 JSON 구조에 맞게 'row' 내부의 'persona' 키를 사용
    persona_description = persona["row"]["persona"]
    system_prompt = f"Persona: {persona_description}"
    
    persona_results = {}
    
    for difficulty, scenarios in scenario_data.items():
        persona_results[difficulty] = {}
        
        for scenario_name, values in scenarios.items():
            A_left, B_left = values["LEFT"]
            A_right, B_right = values["RIGHT"]
            user_prompt = create_user_prompt(A_left, B_left, A_right, B_right)
            
            # 메시지 구성
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 모델 입력 생성
            input_ids = tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
            )
            
            # 입력을 지정된 장치로 이동
            input_ids = input_ids.to(device)
            
            # 모델 실행
            output_ids = model.generate(
                input_ids,
                eos_token_id=tokenizer.eos_token_id,
                max_new_tokens=10,
                do_sample=False
            )
            
            response_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            choice = "Left" if "Left" in response_text else "Right" if "Right" in response_text else "Unknown"
            
            persona_results[difficulty][scenario_name] = {
                "A_left": A_left, "B_left": B_left,
                "A_right": A_right, "B_right": B_right,
                "Choice": choice,
                "Trade-off": values["Trade-off"]
            }
    
    # 결과 저장
    output_file = os.path.join(output_folder, f"Persona_{idx}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(persona_results, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Persona {idx} 완료: {output_file}")

# GPU를 사용한 경우 캐시 정리
if device == "cuda":
    torch.cuda.empty_cache()

print("✅ 모든 실험 완료!")

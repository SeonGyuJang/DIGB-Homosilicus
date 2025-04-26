# NOTE : 분당 제한, 일일 제한이 존재해서, 페르소나 1개에 대한 실험 수행이 끝나면 1분의 대기시간을 뒀음.
# NOTE : GEMENI의 경우, System_Prompt가 고정된 값이라, 페르소나에 대한 내용을 User_Prompt에 입력하였음.
# NOTE : 일일 할당량 60% -> 페르소나 100개.


import os
import json
import base64
import time 
from tqdm import tqdm
from google import genai
from google.genai import types


MAX_PERSONAS = 1000 # NOTE : 몇개의 페르소나에 대해서 실행할건지? -> API 무료 사용량 제한 때문에 만들어 놓음
OUTPUT_DIR = r"C:\Users\dsng3\Desktop\DIGB_Project\GEMINI_EXPERIMENT_RESULTS"
DATA_PATH = r"C:\Users\dsng3\Desktop\DIGB_Project\elite_personas_grouped_1000.json"
SCENARIOS_PATH = r"C:\Users\dsng3\Desktop\DIGB_Project\data\experiment_scenarios.json"

MODEL_NAME = "gemini-2.0-flash"      
API_KEY = os.environ["GEMINI_API_KEY"] = "AIzaSyCgMEdgYCXN4a5U9rfrf8-7d6c5UO3xwUU" # XXX : 보안을 위해 나중에 API_Key는 환경 변수로 변경해야함.


# System_Prompt
SYSTEM_INSTRUCTION = """
You are participating in a Social Preferences Experiment, and you are acting as **Person B** with a specific personality and values described below.

Please follow these detailed instructions when answering the question:

1. Carefully consider the situation based on your personality, values, and preferences.
2. Perform internal reasoning step by step, showing how you weigh the trade-offs between the options.
3. Use first-person expressions (e.g., *I think*, *In my view*, *As someone who values X*) to reflect your persona's voice.
4. After reasoning, clearly decide between the 'Left' or 'Right' option.

Make sure that your reasoning and final choice align with your persona's characteristics.
"""

# 출력 스키마 구조
response_schema = genai.types.Schema(
    type=genai.types.Type.OBJECT,
    required=[
        "persona_id",
        "persona_content",
        "difficulty",
        "metric",
        "options",
        "thought",
        "answer"
    ],
    properties={
        "persona_id": genai.types.Schema(
            type=genai.types.Type.STRING
        ),
        "persona_content": genai.types.Schema(
            type=genai.types.Type.STRING
        ),
        "difficulty": genai.types.Schema(
            type=genai.types.Type.STRING,
            enum=["easy", "medium", "hard"]
        ),
        "metric": genai.types.Schema(
            type=genai.types.Type.STRING
        ),
        "options": genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=["left", "right"],
            properties={
                "left": genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    required=["A", "B"],
                    properties={
                        "A": genai.types.Schema(type=genai.types.Type.NUMBER),
                        "B": genai.types.Schema(type=genai.types.Type.NUMBER),
                    },
                ),
                "right": genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    required=["A", "B"],
                    properties={
                        "A": genai.types.Schema(type=genai.types.Type.NUMBER),
                        "B": genai.types.Schema(type=genai.types.Type.NUMBER),
                    },
                ),
            },
        ),
        "thought": genai.types.Schema(type=genai.types.Type.STRING),
        "answer": genai.types.Schema(
            type=genai.types.Type.STRING, 
            enum=["Left", "Right"]
        ),
    },
)

def run_experiment():
    client = genai.Client(api_key=API_KEY)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        personas_json = json.load(f)
    with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
        experiments = json.load(f)["experiments"]

    personas = []
    for domain, plist in personas_json.items():
        for p in plist:
            personas.append({
                "persona": p["persona"], 
                "idx": p["idx"]
            })
            if len(personas) >= MAX_PERSONAS:
                break
        if len(personas) >= MAX_PERSONAS:
            break

    for persona in tqdm(personas, desc="Running Experiments"):
        persona_desc = persona["persona"] 
        persona_id = persona["idx"]       
        results = {}

        # 난이도별 (easy, medium, hard)
        for exp in experiments:
            difficulty = exp["difficulty"]   
            options = exp["options"]        
            metrics = exp["metrics"]         

            results[difficulty] = {}

            for i, opt in enumerate(options):
                A_left, B_left = opt["left"]
                A_right, B_right = opt["right"]
                metric = metrics[i]

                # User_Prompt
                user_prompt = (
                    f"You are playing the role of Person B in a Social Preferences Experiment.\n\n"
                    f"Below are two choices presented to you. Please select one and explain your reasoning.\n\n"
                    f"Choices:\n"
                    f"- (Left): Person B receives {B_left}, and Person A receives {A_left}.\n"
                    f"- (Right): Person B receives {B_right}, and Person A receives {A_right}.\n\n"
                    f"This question is designed to explore the trade-off in: {metric}.\n\n"
                    f"Please answer in structured JSON format."
                )

                # config 설정 FIXME : temperature를 적당한 수치로 수정해야함. -> Default = 0.7
                generate_content_config = types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    system_instruction=SYSTEM_INSTRUCTION,
                )

                # Persona Content + User_Prompt
                try:
                    contents = [
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(
                                    text=f"Your persona description:\n{persona_desc}"
                                ),
                                types.Part.from_text(text=user_prompt),
                            ],
                        ),
                    ]

                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=contents,
                        config=generate_content_config
                    )

                    structured_text = response.candidates[0].content.parts[0].text
                    parsed = json.loads(structured_text)

                    parsed["persona_id"] = str(persona_id)    
                    parsed["persona_content"] = persona_desc  
                    parsed["difficulty"] = difficulty
                    parsed["metric"] = metric
                    parsed["options"] = {
                        "left": {"A": A_left, "B": B_left},
                        "right": {"A": A_right, "B": B_right}
                    }

                    results[difficulty][f"scenario_{i+1}"] = parsed

                except Exception as e:
                    print(f"Error in persona {persona_id}, scenario {difficulty}-{i+1}: {e}")
                    results[difficulty][f"scenario_{i+1}"] = {"error": str(e)}

        output_path = os.path.join(OUTPUT_DIR, f"Person_{persona_id}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        # NOTE : 분당 요청량 제한으로 인해, 1분 대기시간 추가하였음.
        print(f"Persona {persona_id} done. Waiting 60 seconds to avoid rate limit.")
        time.sleep(10)


if __name__ == "__main__":
    run_experiment()


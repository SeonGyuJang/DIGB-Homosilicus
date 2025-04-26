'''
(1) 페르소나를 적용시키지 않은 실험을 하고 싶을 때 : python langchain_experiment.py --nopersona
(2) 전체 페르소나에 대해 실험을 하고 싶을 때 : python langchain_experiment.py --all
(3) 특정 페르소나 idx만 실험하고 싶을 때(오류난 부분만..) : python langchain_experiment.py --ids 1,2,3,4....
'''

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List
import time

from tqdm import tqdm
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

# === 환경 변수 로딩 ===
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # NOTE : .env 파일이 있어야 함.
MODEL_NAME = "gemini-2.0-flash"
MAX_PERSONAS = 1000

# === 경로 ===
OUTPUT_DIR = Path(r"\DIGB_Project\LangChain_EXISITNG_EXPERIMENT_RESULTS") # 실험결과(JSON파일)을 저장할 경로
DATA_PATH = Path(r"\DIGB_Project\data\grouped_persona_data.json") # 도메인별로 그룹화된 페르소나 데이터
SCENARIOS_PATH = Path(r"\DIGB_Project\data\existing_research_scenarios.json") # 시나리오 JSON 파일

llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=1) 

# 아래는 입력되는 프롬프트의 예시임. 
# 실험에 맞게 수정하여 사용하면 됨.
prompt_template = PromptTemplate(
    input_variables=["persona_desc", "A_left", "B_left", "A_right", "B_right", "metric"], # LLM에게 전달해야하는 변수
    template="""
You are Person B in a Social Preferences Experiment.

Persona:
{persona_desc}

Choices:
- (Left): Person B gets {B_left}, Person A gets {A_left}
- (Right): Person B gets {B_right}, Person A gets {A_right}

This is a question about {metric}.

Please provide JSON output with reasoning and a final choice (Left or Right).
"""
)
parser = JsonOutputParser()
chain = prompt_template | llm | parser


def load_personas() -> List[Dict]:
    with DATA_PATH.open(encoding="utf-8") as fp:
        data = json.load(fp)

    personas: List[Dict] = []
    for plist in data.values():
        for p in plist:
            personas.append({"persona": p["persona"], "idx": int(p["idx"])})
            if len(personas) >= MAX_PERSONAS:
                return personas
    return personas


def load_scenarios() -> List[Dict]:
    with SCENARIOS_PATH.open(encoding="utf-8") as fp:
        return json.load(fp)["experiments"]


def run(persona_filter: List[int] | None = None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    personas = load_personas()
    if persona_filter is not None:
        personas = [p for p in personas if p["idx"] in persona_filter]
        missing = set(persona_filter) - {p["idx"] for p in personas}
        if missing:
            print(f"Warning: idx not found in dataset → {sorted(missing)}")

    scenarios = load_scenarios()
    if not personas:
        print("선택된 페르소나가 없습니다. 종료합니다.")
        return

    for persona in tqdm(personas, desc="Running Experiments"):
        persona_desc = persona["persona"]
        persona_id = persona["idx"]
        results: Dict[str, Dict] = {}

        for exp in scenarios:
            difficulty = exp["difficulty"]
            options = exp["options"]
            metrics = exp["metrics"]

            results[difficulty] = {}

            for i, opt in enumerate(options):
                A_left, B_left = opt["left"]
                A_right, B_right = opt["right"]
                metric = metrics[i]

                try:
                    response = chain.invoke(
                        {
                            "persona_desc": persona_desc,
                            "A_left": A_left,
                            "B_left": B_left,
                            "A_right": A_right,
                            "B_right": B_right,
                            "metric": metric,
                        }
                    )

                    results[difficulty][f"scenario_{i+1}"] = {
                        "persona_id": persona_id,
                        "persona_desc": persona_desc,
                        "difficulty": difficulty,
                        "metric": metric,
                        "options": {
                            "left": {"A": A_left, "B": B_left},
                            "right": {"A": A_right, "B": B_right},
                        },
                        "thought": response.get("reasoning", ""),
                        "answer": response.get("choice", ""),
                    }
                except Exception as e:
                    results[difficulty][f"scenario_{i+1}"] = {"error": str(e)}

        out_path = OUTPUT_DIR / f"Person_{persona_id}.json"
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=4), encoding="utf-8")


def run_without_persona() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = load_scenarios()
    results: Dict[str, Dict] = {}

    for exp in tqdm(scenarios, desc="Running Experiments (No Persona)"):
        difficulty = exp["difficulty"]
        options = exp["options"]
        metrics = exp["metrics"]

        results[difficulty] = {}

        for i, opt in enumerate(options):
            A_left, B_left = opt["left"]
            A_right, B_right = opt["right"]
            metric = metrics[i]

            try:
                response = chain.invoke(
                    {
                        "persona_desc": "", 
                        "A_left": A_left,
                        "B_left": B_left,
                        "A_right": A_right,
                        "B_right": B_right,
                        "metric": metric,
                    }
                )

                results[difficulty][f"scenario_{i+1}"] = {
                    "persona_id": "none",
                    "persona_desc": "",
                    "difficulty": difficulty,
                    "metric": metric,
                    "options": {
                        "left": {"A": A_left, "B": B_left},
                        "right": {"A": A_right, "B": B_right},
                    },
                    "thought": response.get("reasoning", ""),
                    "answer": response.get("choice", ""),
                }
            except Exception as e:
                results[difficulty][f"scenario_{i+1}"] = {"error": str(e)}

    out_path = OUTPUT_DIR / "Person_NONE.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=4), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run Gemini social‑preference experiments")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="1000개 전부 실행")
    g.add_argument("--ids", nargs="+", help="실행할 persona idx 목록 (공백 또는 쉼표 구분)")
    g.add_argument("--nopersona", action="store_true", help="페르소나 없이 실행")
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    if args.all:
        run()
    elif args.nopersona:
        run_without_persona()
    else:
        raw: List[str] = []
        for token in args.ids:
            raw.extend(token.split(","))
        try:
            id_list = [int(x) for x in raw if x.strip()]
        except ValueError as e:
            raise SystemExit(f"idx 값은 정수여야 합니다 → {e}")

        run(id_list)


if __name__ == "__main__":
    main()

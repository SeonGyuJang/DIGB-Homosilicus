'''
1) python (KR-LangChain)Run.py --all → 모든 페르소나에 대해 실험
2) python (KR-LangChain)Run.py --ids 1,2,3... → 특정 idx만 실험
3) python (KR-LangChain)Run.py --rerun-missing → 결과가 없는(아직 생성되지 않은) idx만 재실험
4) python (KR-LangChain)Run.py --rerun-problems → thought/answer에 문제가 있는 idx만
5) python (KR-LangChain)Run.py --nopersona → 페르소나 없이 실험 진행
'''

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any

from tqdm import tqdm
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.0-flash"

OUTPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results\(KR)LangChain_EXPERIMENT_RESULTS_10000")
DATA_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(KR)PERSONA_DATA_10000.jsonl")
SCENARIOS_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(KR)experiment_scenarios.json")

MAX_PERSONAS = 100000

llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=1)

prompt_template = PromptTemplate(
    input_variables=["persona_desc", "A_left", "B_left", "A_right", "B_right", "metric"],
    template="""
당신은 사회적 선호 실험에서 \"B\" 역할을 맡았습니다.

페르소나:
{persona_desc}

선택지:
- (왼쪽): 당신(B)은 {B_left}를 받고, 상대방(A)은 {A_left}를 받습니다.
- (오른쪽): 당신(B)은 {B_right}를 받고, 상대방(A)은 {A_right}를 받습니다.

이 문제는 {metric}에 대한 질문입니다.

당신의 선택 이유와 최종 선택(왼쪽/오른쪽)을 JSON 형식으로 작성해 주세요.
출력 예시:
{{
  "reasoning": "선택 이유를 서술합니다.",
  "choice": "Left" 또는 "Right"
}}
""",
)

parser = JsonOutputParser()
chain = prompt_template | llm | parser

def load_personas() -> List[Dict[str, Any]]:
    personas = []
    with DATA_PATH.open(encoding="utf-8") as fp:
        for line in fp:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                personas.append({"persona": item["persona"], "idx": int(item["idx"])})
                if len(personas) >= MAX_PERSONAS:
                    break
            except (json.JSONDecodeError, KeyError):
                continue
    return personas

def load_scenarios() -> List[Dict[str, Any]]:
    with SCENARIOS_PATH.open(encoding="utf-8") as fp:
        return json.load(fp)["experiments"]

def list_existing_indices() -> set:
    existing = set()
    for file in OUTPUT_DIR.glob("Person_*.json"):
        try:
            idx = int(file.stem.split("_")[1])
            existing.add(idx)
        except (IndexError, ValueError):
            continue
    return existing

def validate_results() -> List[int]:
    problem_indices = []
    for file in OUTPUT_DIR.glob("Person_*.json"):
        try:
            idx = int(file.stem.split("_")[1])
            data = json.loads(file.read_text(encoding="utf-8"))
            for difficulty in data.values():
                for scenario in difficulty.values():
                    thought = scenario.get("thought", "").strip()
                    answer = scenario.get("answer", "").strip()
                    if not thought or not answer or len(answer) < 2 or len(thought) < 5:
                        problem_indices.append(idx)
                        break
        except Exception:
            problem_indices.append(idx)
    return sorted(set(problem_indices))

def build_payloads(persona_desc: str, scenarios: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
    payloads, metadata = [] , []
    for exp in scenarios:
        difficulty = exp["difficulty"]
        options = exp["options"]
        metrics = exp["metrics"]

        for i, opt in enumerate(options):
            A_left, B_left = opt["left"]
            A_right, B_right = opt["right"]
            metric = metrics[i]

            payloads.append({
                "persona_desc": persona_desc,
                "A_left": A_left,
                "B_left": B_left,
                "A_right": A_right,
                "B_right": B_right,
                "metric": metric,
            })

            metadata.append({
                "difficulty": difficulty,
                "scenario_idx": i,
                "metric": metric,
                "A_left": A_left,
                "B_left": B_left,
                "A_right": A_right,
                "B_right": B_right,
            })
    return payloads, metadata

def save_results(persona_id: Any, persona_desc: str, responses: List[Any], metadata: List[Dict[str, Any]]) -> None:
    results = {}
    for meta, resp in zip(metadata, responses):
        difficulty = meta["difficulty"]
        i = meta["scenario_idx"]

        if difficulty not in results:
            results[difficulty] = {}

        if isinstance(resp, Exception):
            results[difficulty][f"scenario_{i+1}"] = {"error": str(resp)}
            continue

        results[difficulty][f"scenario_{i+1}"] = {
            "persona_id": persona_id,
            "persona_desc": persona_desc,
            "difficulty": difficulty,
            "metric": meta["metric"],
            "options": {
                "left": {"A": meta["A_left"], "B": meta["B_left"]},
                "right": {"A": meta["A_right"], "B": meta["B_right"]},
            },
            "thought": resp.get("reasoning", ""),
            "answer": resp.get("choice", ""),
        }

    out_path = OUTPUT_DIR / f"Person_{persona_id}.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=4), encoding="utf-8")

def run_batch(persona_filter: List[int] | None = None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    personas = load_personas()
    if persona_filter is not None:
        personas = [p for p in personas if p["idx"] in persona_filter]
    if not personas:
        print("선택된 페르소나가 없습니다. 종료합니다.")
        return
    scenarios = load_scenarios()

    for persona in tqdm(personas, desc="Running Experiments (Batch)"):
        persona_desc = persona["persona"]
        persona_id = persona["idx"]

        payloads, metadata = build_payloads(persona_desc, scenarios)

        try:
            responses = chain.batch(payloads, config={"max_concurrency": 20})
            save_results(persona_id, persona_desc, responses, metadata)
        except Exception as e:
            print(f"[persona {persona_id}] batch 호출 실패 → {e}")

def run_invoke(persona_filter: List[int]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    personas = load_personas()
    personas = [p for p in personas if p["idx"] in persona_filter]
    if not personas:
        print("선택된 페르소나가 없습니다. 종료합니다.")
        return
    scenarios = load_scenarios()

    for persona in tqdm(personas, desc="Running Experiments (Invoke)"):
        persona_desc = persona["persona"]
        persona_id = persona["idx"]

        payloads, metadata = build_payloads(persona_desc, scenarios)
        responses = []
        for payload in payloads:
            try:
                response = chain.invoke(payload)
            except Exception as e:
                response = e
            responses.append(response)

        save_results(persona_id, persona_desc, responses, metadata)

def run_without_persona() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = load_scenarios()
    payloads, metadata = build_payloads("", scenarios)

    try:
        responses = chain.batch(payloads, config={"max_concurrency": 135})
        save_results("NONE", "", responses, metadata)
    except Exception as e:
        print(f"[No Persona] batch 호출 실패 → {e}")

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Gemini 사회적 선호 실험 실행")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="모든 페르소나 실행")
    g.add_argument("--ids", nargs="+", help="특정 idx만 실행")
    g.add_argument("--nopersona", action="store_true", help="페르소나 없이 실행")
    g.add_argument("--rerun-missing", action="store_true", help="누락된 idx만 재실행")
    g.add_argument("--rerun-problems", action="store_true", help="불량 결과만 재실행")
    return ap.parse_args()

def main() -> None:
    args = parse_args()

    if args.all:
        run_batch()
    elif args.nopersona:
        run_without_persona()
    elif args.rerun_missing:
        personas = load_personas()
        all_idx = {p["idx"] for p in personas}
        existing_idx = list_existing_indices()
        missing_idx = sorted(all_idx - existing_idx)
        print(f"Missing idx: {missing_idx}")
        run_invoke(missing_idx)
    elif args.rerun_problems:
        problems = validate_results()
        print(f"Problematic idx: {problems}")
        run_invoke(problems)
    else:
        raw = []
        for token in args.ids:
            raw.extend(token.split(","))
        try:
            id_list = [int(x) for x in raw if x.strip()]
        except ValueError as e:
            raise SystemExit(f"idx 값은 정수여야 합니다 → {e}")
        run_invoke(id_list)

if __name__ == "__main__":
    main()
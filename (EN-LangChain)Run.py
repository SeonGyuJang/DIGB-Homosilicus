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

# ========== 1. 환경 변수 로드 ==========
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.0-flash"

# ========== 2. 경로 설정 ==========
OUTPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results\(EN)LangChain_EXPERIMENT_RESULTS_10000")
DATA_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(EN)PERSONA_DATA_10000.jsonl")
SCENARIOS_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(EN)experiment_scenarios.json")

MAX_PERSONAS = 100000  # 최대 지원 수

# ========== 3. LLM 체인 세팅 ==========
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=1)

prompt_template = PromptTemplate(
    input_variables=["persona_desc", "A_left", "B_left", "A_right", "B_right", "metric"],
    template="""
You are Person B in a Social Preferences Experiment.

Persona:
{persona_desc}

Choices:
- (Left): Person B gets {B_left}, Person A gets {A_left}
- (Right): Person B gets {B_right}, Person A gets {A_right}

This is a question about {metric}.

Please provide JSON output with reasoning and a final choice (Left or Right).
""",
)

parser = JsonOutputParser()
chain = prompt_template | llm | parser

# ========== 4. 데이터 로드 ==========
def load_personas() -> List[Dict[str, Any]]:
    personas = []
    with DATA_PATH.open(encoding="utf-8") as fp:
        for line in fp:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                personas.append({
                    "persona": item["persona"],
                    "idx": int(item["idx"])  # ✅ 파일에 저장된 idx 그대로 사용
                })
                if len(personas) >= MAX_PERSONAS:
                    break
            except (json.JSONDecodeError, KeyError):
                continue
    return personas

def load_scenarios() -> List[Dict[str, Any]]:
    with SCENARIOS_PATH.open(encoding="utf-8") as fp:
        return json.load(fp)["experiments"]

# ========== 5. 배치용 Payload 생성 ==========
def build_payloads(persona_desc: str, scenarios: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
    payloads = []
    metadata = []
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

# ========== 6. 메인 실험 함수 ==========
def run(persona_filter: List[int] | None = None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    personas = load_personas()
    if persona_filter is not None:
        personas = [p for p in personas if p["idx"] in persona_filter]
        missing = set(persona_filter) - {p["idx"] for p in personas}
        if missing:
            print(f"Warning: Missing idx → {sorted(missing)}")

    if not personas:
        print("선택된 페르소나가 없습니다. 종료합니다.")
        return

    scenarios = load_scenarios()

    for persona in tqdm(personas, desc="Running Experiments"):
        persona_desc = persona["persona"]
        persona_id = persona["idx"]

        payloads, metadata = build_payloads(persona_desc, scenarios)

        try:
            responses = chain.batch(payloads, config={"max_concurrency": 20})
        except Exception as e:
            print(f"[persona {persona_id}] batch 호출 실패 → {e}")
            continue

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

# ========== 7. 페르소나 없이 실험 ==========
def run_without_persona() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = load_scenarios()
    payloads, metadata = build_payloads("", scenarios)

    try:
        responses = chain.batch(payloads, config={"max_concurrency": 135})
    except Exception as e:
        print(f"[No Persona] batch 호출 실패 → {e}")
        return

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
            "persona_id": "none",
            "persona_desc": "",
            "difficulty": difficulty,
            "metric": meta["metric"],
            "options": {
                "left": {"A": meta["A_left"], "B": meta["B_left"]},
                "right": {"A": meta["A_right"], "B": meta["B_right"]},
            },
            "thought": resp.get("reasoning", ""),
            "answer": resp.get("choice", ""),
        }

    out_path = OUTPUT_DIR / "Person_NONE.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=4), encoding="utf-8")

# ========== 8. CLI Argument 파싱 ==========
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run Gemini Social-Preference Experiments")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="모든 페르소나 실행")
    g.add_argument("--ids", nargs="+", help="특정 idx만 실행 (공백/쉼표로 구분)")
    g.add_argument("--nopersona", action="store_true", help="페르소나 없이 실행")
    return ap.parse_args()

# ========== 9. Main ==========
def main() -> None:
    args = parse_args()

    if args.all:
        run()
    elif args.nopersona:
        run_without_persona()
    else:
        raw = []
        for token in args.ids:
            raw.extend(token.split(","))
        try:
            id_list = [int(x) for x in raw if x.strip()]
        except ValueError as e:
            raise SystemExit(f"idx 값은 정수여야 합니다 → {e}")
        run(id_list)

if __name__ == "__main__":
    main()

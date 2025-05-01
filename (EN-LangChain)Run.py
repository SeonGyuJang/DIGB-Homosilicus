import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
from multiprocessing import Pool

from tqdm import tqdm
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.0-flash"

# Path configuration
OUTPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results\(EN)LangChain_EXPERIMENT_RESULTS_10000")
DATA_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(EN)PERSONA_DATA_10000.jsonl")
SCENARIOS_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(EN)experiment_scenarios.json")
MAX_PERSONAS = 100000

# Define LLM chain
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

def load_personas() -> List[Dict[str, Any]]:
    personas = []
    with DATA_PATH.open(encoding="utf-8") as fp:
        for line in fp:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                personas.append({"persona": item["persona"], "idx": int(item["idx"])});
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

def validate_results() -> Tuple[List[int], Dict[int, List[str]]]:
    problem_indices = []
    problem_details = {}

    for file in OUTPUT_DIR.glob("Person_*.json"):
        try:
            idx = int(file.stem.split("_")[1])
            data = json.loads(file.read_text(encoding="utf-8"))
            for difficulty_key, scenarios in data.items():
                for scenario_key, scenario in scenarios.items():
                    thought = scenario.get("thought", "").strip()
                    answer = scenario.get("answer", "").strip()
                    if not thought or not answer or len(answer) < 2 or len(thought) < 5:
                        problem_indices.append(idx)
                        if idx not in problem_details:
                            problem_details[idx] = []
                        problem_details[idx].append(f"[{difficulty_key}] {scenario_key} problem (insufficient thought/answer)")
        except Exception as e:
            idx = file.stem.split("_")[1]
            problem_indices.append(int(idx))
            if int(idx) not in problem_details:
                problem_details[int(idx)] = []
            problem_details[int(idx)].append(f"[Parse Error] {str(e)}")

    return sorted(set(problem_indices)), problem_details

def build_payloads(persona_desc: str, scenarios: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
    payloads, metadata = [], []
    for exp in scenarios:
        difficulty = exp["difficulty"]
        options = exp["options"]
        metrics = exp["metrics"]

        for i, opt in enumerate(options):
            A_left, B_left = opt["left"]
            A_right, B_right = opt["right"]
            metric = metrics[i]
            payloads.append({"persona_desc": persona_desc, "A_left": A_left, "B_left": B_left, "A_right": A_right, "B_right": B_right, "metric": metric})
            metadata.append({"difficulty": difficulty, "scenario_idx": i, "metric": metric, "A_left": A_left, "B_left": B_left, "A_right": A_right, "B_right": B_right})
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

def run_single_persona(persona: Dict[str, Any]) -> None:
    persona_desc = persona["persona"]
    persona_id = persona["idx"]
    scenarios = load_scenarios()
    payloads, metadata = build_payloads(persona_desc, scenarios)
    try:
        responses = chain.batch(payloads, config={"max_concurrency": 100})
        save_results(persona_id, persona_desc, responses, metadata)
    except Exception as e:
        print(f"[persona {persona_id}] Error: {e}")

def run_batch(persona_filter: List[int] | None = None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing_idx = list_existing_indices()
    personas = load_personas()
    if persona_filter is not None:
        personas = [p for p in personas if p["idx"] in persona_filter]
    personas = [p for p in personas if p["idx"] not in existing_idx]

    if not personas:
        print("No target personas to process. Exiting.")
        return

    with Pool(processes=10) as pool:
        list(tqdm(pool.imap_unordered(run_single_persona, personas), total=len(personas), desc="Running Experiments (Batch)"))

def run_single_invoke(persona: Dict[str, Any]) -> None:
    persona_desc = persona["persona"]
    persona_id = persona["idx"]
    scenarios = load_scenarios()
    payloads, metadata = build_payloads(persona_desc, scenarios)
    responses = []
    for payload in payloads:
        try:
            responses.append(chain.invoke(payload))
        except Exception as e:
            responses.append(e)
    save_results(persona_id, persona_desc, responses, metadata)

def run_invoke(persona_filter: List[int]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    personas = [p for p in load_personas() if p["idx"] in persona_filter]
    if not personas:
        print("No personas selected. Exiting.")
        return

    with Pool(processes=10) as pool:
        list(tqdm(pool.imap_unordered(run_single_invoke, personas), total=len(personas), desc="Running Experiments (Invoke)"))

def run_without_persona() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payloads, metadata = build_payloads("", load_scenarios())
    try:
        responses = chain.batch(payloads, config={"max_concurrency": 100})
        save_results("NONE", "", responses, metadata)
    except Exception as e:
        print(f"[No Persona] batch call failed → {e}")

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run Gemini Social-Preference Experiments")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true")
    g.add_argument("--ids", nargs="+")
    g.add_argument("--nopersona", action="store_true")
    g.add_argument("--rerun-missing", action="store_true")
    g.add_argument("--rerun-problems", action="store_true")
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    if args.all:
        run_batch()
    elif args.nopersona:
        run_without_persona()
    elif args.rerun_missing:
        all_idx = {p["idx"] for p in load_personas()}
        missing_idx = sorted(all_idx - list_existing_indices())
        print(f"Missing idx: {missing_idx}")
        run_invoke(missing_idx)
    elif args.rerun_problems:
        problems, details = validate_results()
        print(f"Problematic idx: {problems}\n")
        for idx in problems:
            print(f"\n>> idx {idx} issue summary:")
            for issue in details.get(idx, []):
                print(f"   - {issue}")
        run_invoke(problems)
    else:
        raw = []
        for token in args.ids:
            raw.extend(token.split(","))
        try:
            id_list = [int(x) for x in raw if x.strip()]
        except ValueError as e:
            raise SystemExit(f"idx must be integers → {e}")
        run_invoke(id_list)

if __name__ == "__main__":
    main()
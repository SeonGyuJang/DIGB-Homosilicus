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
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # NOTE : .env 파일이 있어야 함.
MODEL_NAME = "gemini-2.0-flash"
MAX_PERSONAS = 1000

OUTPUT_DIR = Path(r"C:\Users\dsng3\iCloudDrive\DIGB_Project\langchain-NOPERSONA")  # 실험결과(JSON파일)을 저장할 경로
DATA_PATH = Path(r"C:\Users\dsng3\iCloudDrive\DIGB_Project\data\grouped_persona_data.json")  # 도메인별로 그룹화된 페르소나 데이터
SCENARIOS_PATH = Path(r"C:\Users\dsng3\iCloudDrive\DIGB_Project\data\existing_research_scenarios.json")  # 시나리오 JSON 파일

llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=1)

prompt_template = PromptTemplate(
    input_variables=[
        "persona_desc",
        "A_left",
        "B_left",
        "A_right",
        "B_right",
        "metric",
    ],
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


def build_payloads(
    persona_desc: str, scenarios: List[Dict]
) -> Tuple[List[Dict], List[Dict]]:
    """Batch 호출용 payload와 메타데이터를 동시에 만든다."""
    payloads: List[Dict[str, Any]] = []
    metadata: List[Dict[str, Any]] = []

    for exp in scenarios:
        difficulty = exp["difficulty"]
        options = exp["options"]
        metrics = exp["metrics"]

        for i, opt in enumerate(options):
            A_left, B_left = opt["left"]
            A_right, B_right = opt["right"]
            metric = metrics[i]

            payloads.append(
                {
                    "persona_desc": persona_desc,
                    "A_left": A_left,
                    "B_left": B_left,
                    "A_right": A_right,
                    "B_right": B_right,
                    "metric": metric,
                }
            )

            metadata.append(
                {
                    "difficulty": difficulty,
                    "scenario_idx": i,
                    "metric": metric,
                    "A_left": A_left,
                    "B_left": B_left,
                    "A_right": A_right,
                    "B_right": B_right,
                }
            )
    return payloads, metadata


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

        payloads, metadata = build_payloads(persona_desc, scenarios)

        try:
            responses = chain.batch(payloads, config={"max_concurrency": 20})
        except Exception as e:
            print(f"[persona {persona_id}] batch 호출 실패 → {e}")
            continue

        results: Dict[str, Dict] = {}
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
        out_path.write_text(
            json.dumps(results, ensure_ascii=False, indent=4), encoding="utf-8"
        )


def run_without_persona() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = load_scenarios()
    payloads, metadata = build_payloads("", scenarios)

    try:
        responses = chain.batch(payloads, config={"max_concurrency": 20})
    except Exception as e:
        print(f"batch 호출 실패 → {e}")
        return

    results: Dict[str, Dict] = {}
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
    out_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=4), encoding="utf-8"
    )


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

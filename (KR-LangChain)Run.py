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

# ========== 1. 환경변수 세팅 ==========
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # NOTE : .env 파일 필요
MODEL_NAME = "gemini-2.0-flash"

# ========== 2. 경로 설정 ==========
OUTPUT_DIR = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\results\(KR)LangChain_EXPERIMENT_RESULTS")
DATA_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\Persona_Data_Top_n_domains_Random_Extraction\(KR)Persona_Part_1_to_3.json")
SCENARIOS_PATH = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\(KR)experiment_scenarios.json")

# ========== 3. 모델 및 체인 설정 ==========
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
당신은 사회적 선호 실험에 참가한 사람B입니다.

당신의 페르소나:
{persona_desc}

선택:
- (왼쪽): 사람 B는 {B_left}를 받고, 사람 A는 {A_left}를 받습니다.
- (오른쪽): 사람 B는 {B_right}를 받고, 사람 A는 {A_right}를 받습니다.

이것은 {metric}에 관한 질문입니다.

다음 형식의 JSON으로만 답변하세요:
{{
  "reasoning": "여기에 당신의 추론을 작성하세요.",
  "choice": "left 또는 right 중 하나를 선택하여 작성하세요."
}}

※ JSON 이외의 불필요한 텍스트를 출력하지 마세요.
"""
)

parser = JsonOutputParser()
chain = prompt_template | llm | parser

# ========== 4. 함수 정의 ==========

def load_personas() -> List[Dict]:
    """원본 데이터를 로드해서 PERSONA 항목만 깔끔하게 가져온다."""
    with DATA_PATH.open(encoding="utf-8") as fp:
        data = json.load(fp)

    personas: List[Dict] = []
    for entry in data["PERSONA"]:
        personas.append({
            "persona": entry["persona"],
            "idx": int(entry["idx"])
        })
    return personas


def load_scenarios() -> List[Dict]:
    """시나리오 파일 로드"""
    with SCENARIOS_PATH.open(encoding="utf-8") as fp:
        return json.load(fp)["experiments"]


def build_payloads(persona_desc: str, scenarios: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """페르소나 설명과 시나리오를 조합하여 batch 입력 생성"""
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


def run(persona_filter: List[int] | None = None) -> None:
    """모든 페르소나에 대해 실험을 실행하고 결과를 저장"""
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
            json.dumps(results, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )


def run_without_persona() -> None:
    """페르소나 없이 시나리오 실험 (baseline)"""
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
        json.dumps(results, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    """커맨드라인 인자 파싱"""
    ap = argparse.ArgumentParser(description="Run Gemini social‑preference experiments")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="모든 페르소나 실행")
    g.add_argument("--ids", nargs="+", help="특정 persona idx만 실행")
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

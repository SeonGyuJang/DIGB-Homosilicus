
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gemini Social-Preference Experiments (Korean, Repeated Batch Version, No Persona)
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from multiprocessing import Pool
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

BASE = Path(r"C:/Users/dsng3/Documents/GitHub/DIGB-Homosilicus")
CONFIGS: Dict[str, Dict[str, Path]] = {
    "pre": {
        "data": BASE / "Data/Common/(KR)PERSONA_DATA_10000.jsonl",
        "scenarios": BASE / "Data/Experiments/CR2002/(PRE)experiment_scenarios.json",
        "output_base": BASE / "pre_results/CR2002",
        "nopersona_output": BASE / "pre_results/no_persona/(KR)CR2002_EXPERIMENT_RESULTS_NOPERSONA_FINAL"
    }
}

MAX_PERSONAS = 1000

# ---------- 데이터 로드 ---------- #
def load_personas(path: Path) -> List[Dict[str, Any]]:
    personas = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                j = json.loads(line)
                personas.append({"persona": j["persona"], "idx": int(j["idx"])})
                if len(personas) >= MAX_PERSONAS:
                    break
            except (json.JSONDecodeError, KeyError):
                continue
    return personas

def load_scenarios(path: Path) -> List[Dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return json.load(f).get("experiments", [])

# ---------- 프롬프트 빌드 ---------- #
def build_payloads(desc: str, scn: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    payloads, meta = [], []
    for exp in scn:
        diff = exp["difficulty"]
        for i, opt in enumerate(exp["options"]):
            A_left, B_left = opt["left"]
            A_right, B_right = opt["right"]
            metric = exp["metrics"][i]
            payloads.append(dict(persona_desc=desc, difficulty=diff,
                                 A_left=A_left, B_left=B_left,
                                 A_right=A_right, B_right=B_right, metric=metric))
            meta.append(dict(difficulty=diff, scenario_idx=i, metric=metric,
                             A_left=A_left, B_left=B_left, A_right=A_right, B_right=B_right))
    return payloads, meta

# ---------- 결과 저장 ---------- #
def save_results(out_dir: Path, pid: Any, desc: str,
                 resps: List[Any], meta: List[Dict[str, Any]]) -> None:
    data = {}
    for m, r in zip(meta, resps):
        d, i = m["difficulty"], m["scenario_idx"]
        data.setdefault(d, {})
        if isinstance(r, Exception):
            data[d][f"scenario_{i+1}"] = {"error": str(r)}
        else:
            data[d][f"scenario_{i+1}"] = {
                "persona_id": f"NOPERSONA_{int(pid):04d}",
                "persona_desc": desc,
                "difficulty": d,
                "metric": m["metric"],
                "options": {"left": {"A": m["A_left"], "B": m["B_left"]},
                            "right": {"A": m["A_right"], "B": m["B_right"]}},
                "thought": r.get("reasoning", ""),
                "answer": r.get("choice", "")
            }
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"Person_NOPERSONA_{int(pid):04d}.json"
    (out_dir / fname).write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"[✓] Saved → {out_dir / fname}")

# ---------- 인퍼런스 ---------- #
def process_persona(persona: Dict[str, Any], cfg: Dict[str, Path]) -> None:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser

    MODEL_NAME = "gemini-2.0-flash"
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=1)

    prompt_template = PromptTemplate(
    input_variables=[
        "persona_desc", "difficulty",
        "A_left", "B_left", "A_right", "B_right",
        "metric"
    ],
    template="""
당신은 **{difficulty} 난이도** 사회적 선호 실험에서 **B 참가자**입니다.

**페르소나**
{persona_desc}

**선택지**
- **왼쪽** : B 참가자 {B_left}, A 참가자 {A_left}
- **오른쪽**: B 참가자 {B_right}, A 참가자 {A_right}

이 질문은 **{metric}**에 관한 것입니다.

아래 JSON 형식만 반환하세요:
{{
  "reasoning": "<한두 문장으로 선택 이유>",
  "choice": "Left" | "Right"
}}
""",
    )
    parser = JsonOutputParser()
    chain = prompt_template | llm | parser

    scn = load_scenarios(cfg["scenarios"])
    payloads, meta = build_payloads(persona["persona"], scn)
    try:
        resps = chain.batch(payloads, config={"max_concurrency": 50})
        save_results(cfg["output"], persona["idx"], persona["persona"], resps, meta)
    except Exception as e:
        print(f"[idx {persona['idx']}] Error → {e}")

# ---------- 유틸 ---------- #
def list_existing(out_dir: Path) -> set:
    return {
        int(p.stem.split("_")[2])
        for p in out_dir.glob("Person_NOPERSONA_*.json")
        if "_" in p.stem and p.stem.split("_")[2].isdigit()
    }

def validate_missing(cfg: Dict[str, Path], out_dir: Path) -> List[int]:
    all_idx = {p["idx"] for p in load_personas(cfg["data"])}
    existing = list_existing(out_dir)
    return sorted(all_idx - existing)

def validate_problems(out_dir: Path) -> List[int]:
    bad = []
    for f in out_dir.glob("Person_NOPERSONA_*.json"):
        try:
            idx = int(f.stem.split("_")[2])
            d = json.loads(f.read_text(encoding="utf-8"))
            for diff in d.values():
                if any(not sc.get("thought") or not sc.get("answer") for sc in diff.values()):
                    bad.append(idx)
                    break
        except Exception:
            bad.append(idx)
    return sorted(set(bad))

# ---------- 실행 ---------- #
def worker(args):
    p, cfg = args
    process_persona(p, cfg)

def run_all_repeated(cfg: Dict[str, Path], repeats: int):
    # no_persona 조건: persona 데이터를 로드하지 않고 빈 persona_desc 사용
    personas = [{"persona": "", "idx": i} for i in range(1, MAX_PERSONAS + 1)]  # 1부터 100까지 idx 생성
    for r in range(1, repeats + 1):
        out_dir = cfg["nopersona_output"]  # Temp 폴더 없이 직접 저장
        tasks = [(p, {**cfg, "output": out_dir}) for p in personas]
        with Pool(1) as pool:  # WinError 방지를 위해 단일 프로세스
            list(tqdm(pool.imap_unordered(worker, tasks), total=len(tasks), desc=f"Run {r}/{repeats}"))

def run_with_targets(cfg: Dict[str, Path], targets: List[int], out_dir: Path):
    all_personas = load_personas(cfg["data"])
    target_personas = [p for p in all_personas if p["idx"] in targets]
    tasks = [(p, {**cfg, "output": out_dir}) for p in target_personas]
    with Pool(1) as pool:     # WinError 방지를 위해 단일 프로세스
        list(tqdm(pool.imap_unordered(worker, tasks), total=len(tasks), desc="Running rerun"))

# ---------- CLI ---------- #
def parse_args():
    ap = argparse.ArgumentParser("Gemini Social-Preference Experiments")
    ap.add_argument("--config", choices=CONFIGS.keys(), required=True)
    ap.add_argument("--repeat", type=int, help="전체 실험을 N회 반복 수행")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--rerun-missing", action="store_true")
    ap.add_argument("--rerun-problems", action="store_true")
    ap.add_argument("--temp", type=int, help="대상 Temp 번호 (예: --temp 3)")
    return ap.parse_args()

def main():
    args = parse_args()
    cfg = CONFIGS[args.config]

    # 1) 전체 N회 반복
    if args.repeat:
        if args.config != "pre":
            raise ValueError("--repeat는 pre 설정에서만 사용 가능합니다.")
        run_all_repeated(cfg, args.repeat)
        return

    # 2) 전체 1회 실행
    if args.all:
        out_dir = cfg["nopersona_output"]
        run_all_repeated({**cfg, "output": out_dir}, 1)
        return

    # 3) rerun (missing / problems)
    if args.rerun_missing or args.rerun_problems:
        # Temp 번호 지정 시 해당 폴더만 대상
        if args.temp:
            rdir = cfg["nopersona_output"]
            if not rdir.exists():
                raise FileNotFoundError(f"폴더가 존재하지 않습니다: {rdir}")
            target_dirs = [rdir]
        else:
            # 지정 없으면 모든 Temp 폴더 순회
            target_dirs = sorted(cfg["nopersona_output"].glob("Temp*"))
            if not target_dirs:
                raise FileNotFoundError("Temp 폴더가 존재하지 않습니다.")

        for rdir in target_dirs:
            if args.rerun_missing:
                missing = validate_missing(cfg, rdir)
                print(f"[Missing] in {rdir.name}: {missing}")
                if missing:
                    run_with_targets(cfg, missing, rdir)
            else:  # --rerun-problems
                problems = validate_problems(rdir)
                print(f"[Problems] in {rdir.name}: {problems}")
                if problems:
                    run_with_targets(cfg, problems, rdir)
        return

    # 올바르지 않은 인자 조합
    raise ValueError("실행 옵션을 확인하세요. (--repeat | --all | --rerun-*)")

if __name__ == "__main__":
    import multiprocessing
    try:
        multiprocessing.set_start_method("spawn")
    except RuntimeError:
        pass
    main()
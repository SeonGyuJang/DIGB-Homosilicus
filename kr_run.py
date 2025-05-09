#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gemini Social‑Preference Experiments (Korean)
--------------------------------------------
< --config pre|main 옵션으로 실험 세트를 선택 >
1) python (KR)Run.py --config pre|main --all
2) python (KR)Run.py --config pre|main --ids 1 2 3 ...
3) python (KR)Run.py --config pre|main --rerun-missing
4) python (KR)Run.py --config pre|main --rerun-problems
5) python (KR)Run.py --config pre|main --nopersona [N]   (빈 페르소나 N회, 기본 1)
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
from multiprocessing import Pool, set_start_method

from tqdm import tqdm
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

# ──────────────────── 환경 설정 ──────────────────── #
load_dotenv()
MODEL_NAME = "gemini-2.0-flash"
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=1)

BASE = Path(r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus")
CONFIGS: Dict[str, Dict[str, Path]] = {
    "pre": {
        "data":              BASE / "Data" / "Common" / "(KR)PERSONA_DATA_10000.jsonl",
        "scenarios":         BASE / "Data" / "Experiments" / "CR2002" / "(PRE)experiment_scenarios.json",
        "output":            BASE / "Data" / "Results" / "Experiments" / "CR2002" / "(KR)CR2002_EXPERIMENT_RESULTS_10000",
        "nopersona_output":  BASE / "Data" / "Results" / "Experiments" / "CR2002" / "(KR)CR2002_EXPERIMENT_RESULTS_NOPERSONA",
    },
    "main": {
        "data":              BASE / "Data" / "Common" / "(KR)PERSONA_DATA_10000.jsonl",
        "scenarios":         BASE / "Data" / "Experiments" / "DIGB_Custom" / "(KR)experiment_scenarios.json",
        "output":            BASE / "Data" / "Results" / "Experiments" / "DIGB_Custom" / "(KR)DIGB_Custom_EXPERIMENT_RESULTS_10000",
        "nopersona_output":  BASE / "Data" / "Results" / "Experiments" / "DIGB_Custom" / "(KR)DIGB_C_EXPERIMENT_RESULTS_NOPERSONA",
    },
}
MAX_PERSONAS = 100_000

# ──────────────────── 프롬프트 체인 ──────────────────── #
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

# ──────────────────── 유틸 함수 ──────────────────── #
def load_personas(path: Path) -> List[Dict[str, Any]]:
    persons = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                j = json.loads(line)
                persons.append({"persona": j["persona"], "idx": int(j["idx"])})
                if len(persons) >= MAX_PERSONAS:
                    break
            except (json.JSONDecodeError, KeyError):
                continue
    return persons

def load_scenarios(path: Path) -> List[Dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return json.load(f).get("experiments", [])

def list_existing(out_dir: Path) -> set:
    return {
        int(p.stem.split("_")[1])
        for p in out_dir.glob("Person_*.json")
        if "_" in p.stem and p.stem.split("_")[1].isdigit()
    }

def build_payloads(desc: str, scn: List[Dict[str, Any]]
                   ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    payloads, meta = [], []
    for exp in scn:
        diff = exp["difficulty"]
        for i, opt in enumerate(exp["options"]):
            A_left, B_left = opt["left"]
            A_right, B_right = opt["right"]
            metric = exp["metrics"][i]
            payloads.append(
                dict(persona_desc=desc, difficulty=diff,
                     A_left=A_left, B_left=B_left,
                     A_right=A_right, B_right=B_right, metric=metric)
            )
            meta.append(
                dict(difficulty=diff, scenario_idx=i, metric=metric,
                     A_left=A_left, B_left=B_left, A_right=A_right, B_right=B_right)
            )
    return payloads, meta

def save_results(out_dir: Path, pid: Any, desc: str,
                 resps: List[Any], meta: List[Dict[str, Any]]) -> None:
    data: Dict[str, Dict[str, Any]] = {}
    for m, r in zip(meta, resps):
        d, i = m["difficulty"], m["scenario_idx"]
        data.setdefault(d, {})
        if isinstance(r, Exception):
            data[d][f"scenario_{i+1}"] = {"error": str(r)}
        else:
            data[d][f"scenario_{i+1}"] = {
                "persona_id": pid, "persona_desc": desc, "difficulty": d,
                "metric": m["metric"],
                "options": {
                    "left":  {"A": m["A_left"],  "B": m["B_left"]},
                    "right": {"A": m["A_right"], "B": m["B_right"]},
                },
                "thought": r.get("reasoning", ""),
                "answer":  r.get("choice", ""),
            }
    out_dir.mkdir(parents=True, exist_ok=True)
    fpath = out_dir / f"Person_{pid}.json"
    fpath.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"[✓] Saved → {fpath}")

# ──────────────────── 페르소나 단건 처리 ──────────────────── #
def process_persona(persona: Dict[str, Any], cfg: Dict[str, Path]) -> None:
    scn = load_scenarios(cfg["scenarios"])
    payloads, meta = build_payloads(persona["persona"], scn)
    try:
        resps = chain.batch(payloads, config={"max_concurrency": 50})
        save_results(cfg["output"], persona["idx"], persona["persona"], resps, meta)
    except Exception as e:
        print(f"[idx {persona['idx']}] Error → {e}")

def invoke_persona(persona: Dict[str, Any], cfg: Dict[str, Path]) -> None:
    scn = load_scenarios(cfg["scenarios"])
    payloads, meta = build_payloads(persona["persona"], scn)
    results = []
    for p in payloads:
        try:
            results.append(chain.invoke(p))
        except Exception as e:
            results.append(e)
    save_results(cfg["output"], persona["idx"], persona["persona"], results, meta)

def worker(arg):
    person, cfg, inv = arg
    (invoke_persona if inv else process_persona)(person, cfg)

# ──────────────────── 배치 실행 ──────────────────── #
def run_batch(cfg, targets=None, invoke=False):
    persons = load_personas(cfg["data"])
    if targets:
        persons = [p for p in persons if p["idx"] in targets]
    pending = [p for p in persons if p["idx"] not in list_existing(cfg["output"])]
    if not pending:
        print("No target personas. Exit.")
        return
    tasks = [(p, cfg, invoke) for p in pending]
    with Pool(4) as pool:
        list(tqdm(pool.imap_unordered(worker, tasks),
                  total=len(tasks), desc="Running"))

# ──────────────────── 빈 페르소나 반복 실행 ──────────────────── #
def run_no_persona(cfg: Dict[str, Path], repeats: int) -> None:
    scn = load_scenarios(cfg["scenarios"])
    payloads, meta = build_payloads("", scn)
    out_dir = cfg["nopersona_output"]
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] --nopersona x{repeats} → {len(payloads)} prompts, model={MODEL_NAME}")
    for k in range(1, repeats + 1):
        t0 = time.time()
        resps = chain.batch(payloads, config={"max_concurrency": 50})
        print(f"[{k}/{repeats}] LLM done in {time.time() - t0:,.1f}s")
        save_results(out_dir, f"NOPERSONA_{k:04d}", "", resps, meta)

# ──────────────────── CLI 파싱 ──────────────────── #
def parse_cli():
    ap = argparse.ArgumentParser("Gemini Social‑Preference Experiments (KR)")
    ap.add_argument("--config", choices=CONFIGS.keys(), required=True)
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--all", action="store_true")
    grp.add_argument("--ids", nargs="+")
    grp.add_argument("--nopersona", nargs="?", const=1, type=int,
                     help="빈 페르소나 N회 반복 (기본 1)")
    grp.add_argument("--rerun-missing", action="store_true")
    grp.add_argument("--rerun-problems", action="store_true")
    return ap.parse_args()

def validate(cfg):
    bad = []
    for f in cfg["output"].glob("Person_*.json"):
        try:
            idx = int(f.stem.split("_")[1])
            d = json.loads(f.read_text(encoding="utf-8"))
            for diff in d.values():
                if any(not sc.get("thought") or not sc.get("answer")
                       for sc in diff.values()):
                    bad.append(idx); break
        except Exception:
            bad.append(idx)
    return sorted(set(bad))

# ──────────────────── 메인 ──────────────────── #
def main():
    try:
        set_start_method("spawn")
    except RuntimeError:
        pass

    args = parse_cli()
    cfg = CONFIGS[args.config]

    if args.all:
        run_batch(cfg)
    elif args.nopersona is not None:
        run_no_persona(cfg, repeats=args.nopersona)
    elif args.rerun_missing:
        all_idx = {p["idx"] for p in load_personas(cfg["data"])}
        missing = sorted(all_idx - list_existing(cfg["output"]))
        print("Missing →", missing)
        run_batch(cfg, targets=missing, invoke=True)
    elif args.rerun_problems:
        probs = validate(cfg)
        print("Problems →", probs)
        run_batch(cfg, targets=probs, invoke=True)
    else:  # --ids
        ids = [int(x) for tok in args.ids for x in tok.split(",") if x.strip()]
        run_batch(cfg, targets=ids, invoke=True)

if __name__ == "__main__":
    main()

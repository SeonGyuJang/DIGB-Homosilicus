#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gemini Social‑Preference Experiments
-----------------------------------
< --config pre|main 옵션으로 실험을 선택 >
1) python en_run.py --config pre|main --all
2) python en_run.py --config pre|main --ids 1 2 3 ...
3) python en_run.py --config pre|main --rerun-missing
4) python en_run.py --config pre|main --rerun-problems
5) python en_run.py --config pre|main --nopersona [N]   (빈 페르소나 N회, 기본 1)
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
        "data":              BASE / "Data" / "Common" / "(EN)PERSONA_DATA_10000.jsonl",
        "scenarios":         BASE / "Data" / "Experiments" / "CR2002" / "(PRE)experiment_scenarios.json",
        "output":            BASE / "Data" / "Results" / "Experiments" / "CR2002" / "(EN)CR2002_EXPERIMENT_RESULTS_10000",
        "nopersona_output":  BASE / "Data" / "Results" / "Experiments" / "CR2002" / "(EN)CR2002_EXPERIMENT_RESULTS_NOPERSONA",
    },
    "main": {
        "data":              BASE / "Data" / "Common" / "(EN)PERSONA_DATA_10000.jsonl",
        "scenarios":         BASE / "Data" / "Experiments" / "DIGB_Custom" / "(EN)experiment_scenarios.json",
        "output":            BASE / "Data" / "Results" / "Experiments" / "DIGB_Custom" / "(EN)DIGB_Custom_EXPERIMENT_RESULTS_10000",
        "nopersona_output":  BASE / "Data" / "Results" / "Experiments" / "DIGB_Custom" / "(EN)DIGB_Custom_EXPERIMENT_RESULTS_NOPERSONA",
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
You are **Person B** in a **{difficulty}-level** Social Preferences Experiment.

**Persona**
{persona_desc}

**Choices**
- **Left** : Person B {B_left}, Person A {A_left}
- **Right**: Person B {B_right}, Person A {A_right}

Focus on **{metric}**.

Return **JSON only**:
{{
  "reasoning": "<concise reason>",
  "choice": "Left" | "Right"
}}
""",
)
parser = JsonOutputParser()
chain = prompt_template | llm | parser

# ──────────────────── 유틸 함수 ──────────────────── #
def load_personas(data_path: Path) -> List[Dict[str, Any]]:
    personas = []
    with data_path.open(encoding="utf-8") as fp:
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

def load_scenarios(scen_path: Path) -> List[Dict[str, Any]]:
    with scen_path.open(encoding="utf-8") as fp:
        return json.load(fp).get("experiments", [])

def list_existing_indices(out_dir: Path) -> set:
    return {
        int(f.stem.split("_")[1])
        for f in out_dir.glob("Person_*.json")
        if "_" in f.stem and f.stem.split("_")[1].isdigit()
    }

def build_payloads(
    persona_desc: str, scenarios: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    payloads, meta = [], []
    for exp in scenarios:
        difficulty = exp["difficulty"]
        for i, opt in enumerate(exp["options"]):
            A_left, B_left = opt["left"]
            A_right, B_right = opt["right"]
            metric = exp["metrics"][i]
            payloads.append(
                dict(persona_desc=persona_desc, difficulty=difficulty,
                     A_left=A_left, B_left=B_left,
                     A_right=A_right, B_right=B_right, metric=metric)
            )
            meta.append(
                dict(difficulty=difficulty, scenario_idx=i, metric=metric,
                     A_left=A_left, B_left=B_left, A_right=A_right, B_right=B_right)
            )
    return payloads, meta

def save_results(out_dir: Path, persona_id: Any, desc: str,
                 responses: List[Any], meta: List[Dict[str, Any]]) -> None:
    res: Dict[str, Dict[str, Any]] = {}
    for m, r in zip(meta, responses):
        diff, i = m["difficulty"], m["scenario_idx"]
        res.setdefault(diff, {})
        if isinstance(r, Exception):
            res[diff][f"scenario_{i+1}"] = {"error": str(r)}
            continue
        res[diff][f"scenario_{i+1}"] = {
            "persona_id": persona_id,
            "persona_desc": desc,
            "difficulty": diff,
            "metric": m["metric"],
            "options": {
                "left":  {"A": m["A_left"],  "B": m["B_left"]},
                "right": {"A": m["A_right"], "B": m["B_right"]},
            },
            "thought": r.get("reasoning", ""),
            "answer":  r.get("choice", ""),
        }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"Person_{persona_id}.json"
    path.write_text(json.dumps(res, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"[✓] Saved → {path}")

# ──────────────────── 페르소나 단건 처리 ──────────────────── #
def process_persona(persona: Dict[str, Any], cfg: Dict[str, Path]) -> None:
    scenarios = load_scenarios(cfg["scenarios"])
    payloads, meta = build_payloads(persona["persona"], scenarios)
    try:
        responses = chain.batch(payloads, config={"max_concurrency": 50})
        save_results(cfg["output"], persona["idx"], persona["persona"], responses, meta)
    except Exception as e:
        print(f"[idx {persona['idx']}] Error → {e}")
        raise

def invoke_persona(persona: Dict[str, Any], cfg: Dict[str, Path]) -> None:
    scenarios = load_scenarios(cfg["scenarios"])
    payloads, meta = build_payloads(persona["persona"], scenarios)
    res = []
    for pld in payloads:
        try:
            res.append(chain.invoke(pld))
        except Exception as e:
            res.append(e)
    save_results(cfg["output"], persona["idx"], persona["persona"], res, meta)

def worker_wrapper(args):
    persona, cfg, invoke = args
    (invoke_persona if invoke else process_persona)(persona, cfg)

# ──────────────────── 배치 실행 ──────────────────── #
def run_batch(cfg, target_idx=None, invoke_mode=False):
    personas = load_personas(cfg["data"])
    if target_idx is not None:
        personas = [p for p in personas if p["idx"] in target_idx]

    pending = [p for p in personas if p["idx"] not in list_existing_indices(cfg["output"])]
    if not pending:
        print("No target personas. Exit.")
        return

    tasks = [(p, cfg, invoke_mode) for p in pending]
    with Pool(processes=4) as pool:
        list(tqdm(pool.imap_unordered(worker_wrapper, tasks),
                  total=len(tasks), desc="Running"))

# ──────────────────── 빈 페르소나 반복 실행 ──────────────────── #
def run_no_persona(cfg: Dict[str, Path], repeats: int) -> None:
    scenarios = load_scenarios(cfg["scenarios"])
    payloads, meta = build_payloads("", scenarios)

    out_dir = cfg["nopersona_output"]
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] --nopersona x{repeats} → {len(payloads)} prompts, model={MODEL_NAME}")
    for k in range(1, repeats + 1):
        t0 = time.time()
        responses = chain.batch(payloads, config={"max_concurrency": 50})
        print(f"[{k}/{repeats}] LLM done in {time.time() - t0:,.1f}s")
        save_results(out_dir, f"NOPERSONA_{k:04d}", "", responses, meta)

# ──────────────────── CLI ──────────────────── #
def parse_args():
    ap = argparse.ArgumentParser("Gemini Social‑Preference Experiments")
    ap.add_argument("--config", choices=CONFIGS.keys(), required=True,
                    help="'pre' 또는 'main' 설정")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--all", action="store_true")
    grp.add_argument("--ids", nargs="+")
    grp.add_argument("--nopersona", nargs="?", const=1, type=int,
                     help="빈 페르소나 N회 반복 (기본 1)")
    grp.add_argument("--rerun-missing", action="store_true")
    grp.add_argument("--rerun-problems", action="store_true")
    return ap.parse_args()

def validate_for_cli(cfg):
    prob_idx, details = [], {}
    for f in cfg["output"].glob("Person_*.json"):
        try:
            idx = int(f.stem.split("_")[1])
            data = json.loads(f.read_text(encoding="utf-8"))
            for diff, sc in data.items():
                for k, v in sc.items():
                    if not v.get("thought") or not v.get("answer"):
                        prob_idx.append(idx)
                        details.setdefault(idx, []).append(f"{diff}/{k} empty")
        except Exception as e:
            idx = int(f.stem.split("_")[1])
            prob_idx.append(idx)
            details.setdefault(idx, []).append(f"parse error {e}")
    return sorted(set(prob_idx)), details

# ──────────────────── 메인 ──────────────────── #
def main() -> None:
    try:
        set_start_method("spawn")
    except RuntimeError:
        pass

    args = parse_args()
    cfg = CONFIGS[args.config]

    if args.all:
        run_batch(cfg)
    elif args.nopersona is not None:
        run_no_persona(cfg, repeats=args.nopersona)
    elif args.rerun_missing:
        all_idx = {p["idx"] for p in load_personas(cfg["data"])}
        missing = sorted(all_idx - list_existing_indices(cfg["output"]))
        print("Missing →", missing)
        run_batch(cfg, target_idx=missing, invoke_mode=True)
    elif args.rerun_problems:
        prob, _ = validate_for_cli(cfg)
        run_batch(cfg, target_idx=prob, invoke_mode=True)
    else:
        ids = [int(x) for tok in args.ids for x in tok.split(",") if x.strip()]
        run_batch(cfg, target_idx=ids, invoke_mode=True)

if __name__ == "__main__":
    main()

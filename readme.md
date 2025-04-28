# 💾 DATA Repository

[Google Drive 링크](https://drive.google.com/drive/folders/1ryxXR_OhH1orSBd33uVKIaQ87L4mVp_s?usp=sharing)

---

# 📂 데이터 설명

| 파일명 | 설명 | 개수 |
|:---:|:---:|:---:|
| (EN)experiment_scenarios.json | 고전 행동경제학 실험용 영어 시나리오 | - |
| (KR)experiment_scenarios.json | 고전 행동경제학 실험용 한국어 시나리오 | - |
| (PRE)experiment_scenarios.json | Charness and Rabin (2002) 논문 기반 <br>고전 행동경제학 실험 시나리오 | - |
| (EN)PERSONA_DATA.jsonl | 특정 도메인의 페르소나 정보 (영어) | 100,000 |
| (KR)PERSONA_DATA.jsonl | 특정 도메인의 페르소나 정보 (한국어) | 100,000 |
| (EN)PERSONA_DATA_10000.jsonl | 특정 도메인의 페르소나 정보 (영어) | 10,000 |
| (KR)PERSONA_DATA_10000.jsonl | 특정 도메인의 페르소나 정보 (한국어) | 10,000 |

---

# 🎯 추출한 특정 도메인 목록

이번 프로젝트에서는 다음 10개의 도메인을 선정하여 데이터 추출을 진행했습니다.

| 구분 | 도메인명 (EN) | 도메인명 (KR) |
|:---:|:---:|:---:|
| 인문계 | History | 역사 |
| 인문계 | Law | 법학 |
| 인문계 | Philosophy | 철학 |
| 인문계 | Economics | 경제학 |
| 인문계 | Sociology | 사회학 |
| 이공계 | Finance | 금융학 |
| 이공계 | Computer Science | 컴퓨터과학 |
| 이공계 | Mathematics | 수학 |
| 이공계 | Environmental Science | 환경과학 |
| 이공계 | Engineering | 공학 |

---

# 🧩 코드 설명

## ① Data_Extraction(JSONL).py
- **Input** : Original_Persona_Data.jsonl  
- **Output** : (EN)PERSONA_DATA.jsonl  

특정 도메인에 해당하는 페르소나 데이터를 추출하는 코드입니다.  
- `--list` 옵션을 통해 상위 N개의 도메인과 데이터 수를 확인할 수 있습니다.
- `--domains` 옵션을 통해 특정 도메인의 데이터만 추출할 수 있습니다.

---

## ② (LangChain)Persona_Data_Translation.py
- **Input** : (EN)PERSONA_DATA.jsonl  
- **Output** : (KR)PERSONA_DATA.jsonl  

한국어 실험을 위해 페르소나 데이터를 영어 → 한국어로 번역하는 코드입니다.
- `--full` 옵션을 통해 전체 데이터에 대해 번역을 수행할 수 있습니다.
- `--retry_missing` 옵션을 통해 번역 과정에서 오류가 생긴 idx에 대해서만 번역을 다시 수행할 수 있습니다.

---

## ③ (EN-LangChain)Run.py
- **Input** : (EN)experiment_scenarios.json, (EN)PERSONA_DATA.jsonl  
- **Output** : (EN)LangChain_EXPERIMENT_RESULTS/Person_{idx}.json  

Language: **English**  
미리 정의한 실험 시나리오에 따라, 영어로 행동경제학 실험을 수행하는 코드입니다.
- `--all` 옵션을 통해 전체 데이터에 대해서 실험을 진행할 수 있습니다.
- `--ids` 옵션을 통해 특정 idx 데이터에 대해서만 실험을 진행할 수 있습니다.
- `--rerun-missing` 옵션을 통해 (전체 idx 중)아직 생성되지 않은 idx만 자동으로 식별하여 실험을 진행합니다.
- `--rerun-problems` 옵션을 통해 thought나 answer에 문제가 있는 idx만 자동으로 식별하여 실험을 진행합니다.
- `--nopersona` 옵션을 통해 페르소나가 없이 실험을 진행할 수 있습니다.

---

## ④ (KR-LangChain)Run.py
- **Input** : (KR)experiment_scenarios.json, (KR)PERSONA_DATA.jsonl  
- **Output** : (KR)LangChain_EXPERIMENT_RESULTS/Person_{idx}.json  

Language: **Korean**  
미리 정의한 실험 시나리오에 따라, 한국어로 행동경제학 실험을 수행하는 코드입니다.

---

# 📢 참고사항
- 그 외 추가적인 코드 및 기능들은 정리 완료 후 업데이트 예정입니다.
- results 폴더는 git의 편리한 사용을 위해 잠시 gitignore에 넣어두었습니다.
- 생성된 결과물은 구글 드라이브에 공유하도록 하겠습니다!

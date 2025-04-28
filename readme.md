# DATA Repository

[Google Drive 링크](https://drive.google.com/drive/folders/1ryxXR_OhH1orSBd33uVKIaQ87L4mVp_s?usp=sharing)

---

# 📂 데이터 설명

| 파일명 | 설명 |
|:---|:---|
| (EN)experiment_scenarios.json | 고전 행동경제학 실험용 영어 시나리오 |
| (KR)experiment_scenarios.json | 고전 행동경제학 실험용 한국어 시나리오 |
| (PRE)experiment_scenarios.json | Charness and Rabin (2002) 논문 기반 고전 행동경제학 실험 시나리오 |
| (EN)PERSONA_DATA.jsonl | 특정 도메인의 페르소나 정보 (영어) |
| (KR)PERSONA_DATA.jsonl | 특정 도메인의 페르소나 정보 (한국어) |

---

# 🧩 코드 설명

## 1) Data_Extraction(JSONL).py
- **Input** : Original_Persona_Data.jsonl  
- **Output** : (EN)PERSONA_DATA.jsonl  

특정 도메인에 해당하는 페르소나 데이터를 추출하는 코드입니다.  
- `--list` 옵션을 통해 상위 N개의 도메인과 데이터 수를 확인할 수 있습니다.
- `--domains` 옵션을 통해 특정 도메인의 데이터만 추출할 수 있습니다.

---

## 2) (LangChain)Persona_Data_Translation.py
- **Input** : (EN)PERSONA_DATA.jsonl  
- **Output** : (KR)PERSONA_DATA.jsonl  

한국어 실험을 위해 페르소나 데이터를 영어 → 한국어로 번역하는 코드입니다.

---

## 3) (EN-LangChain)Run.py
- **Input** : (EN)experiment_scenarios.json, (EN)PERSONA_DATA.jsonl  
- **Output** : (EN)LangChain_EXPERIMENT_RESULTS/Person_{idx}.json  

Language: **English**  
미리 정의한 실험 시나리오에 따라, 영어로 행동경제학 실험을 수행하는 코드입니다.

---

## 4) (KR-LangChain)Run.py
- **Input** : (KR)experiment_scenarios.json, (KR)PERSONA_DATA.jsonl  
- **Output** : (KR)LangChain_EXPERIMENT_RESULTS/Person_{idx}.json  

Language: **Korean**  
미리 정의한 실험 시나리오에 따라, 한국어로 행동경제학 실험을 수행하는 코드입니다.

---

# 📢 참고사항
- 그 외 추가적인 코드 및 기능들은 정리 완료 후 업데이트 예정입니다.

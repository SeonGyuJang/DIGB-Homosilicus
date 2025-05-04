# DIGB‑Homosilicus:페르소나 기반 행동경제학 실험 자동화

본 프로젝트는 대규모 페르소나 데이터와 **LangChain + Google Gemini API**를 활용하여 
고전 행동경제학 실험을 완전 자동화(end‑to‑end)하고 결과를 시각화합니다.  
또한 다른 LLM API나 새로운 페르소나 데이터셋으로 손쉽게 확장할 수 있도록 설계되었습니다.

---

## 사용 데이터 및 참고 문헌

### 페르소나 데이터셋
본 프로젝트에서는 Tencent AI Lab에서 공개한 **PersonaHub**를 사용하였습니다.

- 데이터셋 : [PersonaHub: Scaling Synthetic Data Creation with 1,000,000,000 Personas](https://github.com/tencent-ailab/persona-hub)
- 논문 : [Scaling Synthetic Data Creation with 1,000,000,000 Personas](https://arxiv.org/abs/2406.20094)

> PersonaHub는 다양한 도메인과 수준을 포괄하는 10억 개 규모의 고품질 페르소나 데이터를 제공합니다.  
> 본 프로젝트에서는 이 중 일부를 도메인별로 추출하여 사용하였습니다.

### 실험 설계 이론 참고 문헌
행동경제학 실험의 시뮬레이션 설계는 다음 논문을 기반으로 하였습니다.

- 논문: [Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus?](https://arxiv.org/abs/2301.07543)

---


## 프로젝트 구조
~~~text
DIGB-Homosilicus/
├── assets/                         # 이미지 리소스
├── Data/
│   ├── Common/                    # 공통 사용 페르소나 데이터
│   ├── Experiments/
│   │   ├── CR2002/               # Charness and Rabin 실험 시나리오
│   │   └── DIGB_Custom/         # 커스텀 설계 실험 시나리오
│   └── Results/
│       ├── Experiments/
│       │   ├── CR2002/
│       │   │   ├── (EN|KR)CR2002_EXPERIMENT_RESULTS_10000/
│       │   │   └── results_by_domain(EN|KR)/
│       │   └── DIGB_Custom/
│       │       ├── (EN|KR)DIGB_Custom_EXPERIMENT_RESULTS_10000/
│       │       └── results_by_domain(EN|KR)/
│       └── Visualization/
│           ├── CR2002/
│           └── DIGB_Custom/
├── *.py                            # 실험 수행·분석·시각화 스크립트
├── .env                            # API 키 등 환경 변수
├── requirements.txt               # 의존성 목록
└── README.md
~~~

## 전체 실행 순서

| 단계 | 설명 | 실행 스크립트 |
|:----:|:------:|:---------------:|
| 0 | Google Drive에서 전체 데이터 자동 다운로드 | `Download_Data.py` |
| 1 | 상위 N개 도메인 추출 및 샘플링( idx 부여) | `Data_Extraction.py` |
| 2 | _(선택)_ 영어 → 한국어 페르소나 번역 | `Persona_Data_Translation.py` |
| 3 | 페르소나 임베딩 벡터 계산 | `Persona_embeddings.py` |
| 4 | t‑SNE를 활용한 도메인 분포 시각화 | `Visualization_TSNE.py` |
| 5 | LangChain 기반 실험 수행 (EN/KR) | `(EN/KR))Run.py` |
| 6 | 도메인별 실험 결과 병합 | `Merge_results_by_domain.py` |
| 7 | Left/Right 선택 비율 분석 요약 | `Result_Analysis.py` |
| 8 | 실험 결과 시나리오별 시각화 | `(EN/KR)Visualization_Experiment.py` |

---

## 주요 스크립트별 기능

### 0. Download_Data.py
Google Drive 공유 링크(공유 폴더)에서 전체 데이터를 자동 다운로드합니다.
~~~bash
python Download_Data.py
~~~

### 1. Data_Extraction.py
도메인 기준으로 페르소나 데이터를 샘플링하고 `idx`를 부여합니다.
~~~bash
# 상위 도메인 목록 보기
python Data_Extraction(JSONL).py --list

# 특정 도메인 추출
python Data_Extraction(JSONL).py --domains history,economics,law,...
~~~

### 2. Persona_Data_Translation.py
영어 페르소나 데이터를 한국어로 번역합니다.
~~~bash
# 전체 번역
python Persona_Data_Translation.py --mode full

# 누락된 항목만 재번역
python Persona_Data_Translation.py --mode retry_missing
~~~

### 3. Persona_embeddings.py
Sentence‑BERT로 임베딩을 생성합니다.
~~~bash
python Persona_embeddings.py
~~~

### 4. Visualization_TSNE.py
임베딩을 t‑SNE로 시각화합니다.
~~~bash
python Visualization_TSNE.py
~~~

### 5. (EN|KR)Run.py
LLM(Gemini API)을 이용한 실험 자동화 수행.
~~~bash
# 전체 페르소나 실험
python (EN|KR)Run.py --config pre|main --all

# 특정 ID만 실험
python (EN|KR)Run.py --config pre|main --ids 1,2,3...

# 아직 결과가 없는 항목만 실험
python (EN|KR)Run.py --config pre|main --rerun-missing

# 결과에 문제 있는 항목만 재실험
python (EN|KR)Run.py --config pre|main --rerun-problems

# 페르소나 없이 실험
python (EN|KR)Run.py --config pre|main --nopersona
~~~

### 6. Merge_results_by_domain.py
개별 JSON 결과 파일을 도메인별로 병합합니다.
~~~bash
# 결과 병합
python Merge_results_by_domain.py

# 도메인별 페르소나 수 확인
python Merge_results_by_domain.py --count_domain
~~~

### 7. Result_Analysis.py
Left/Right 응답 비율을 요약합니다.
~~~bash
python Result_Analysis.py
~~~
생성 파일 → `(EN|KR)summary_by_domain.txt`

### 8. (EN|KR)Visualization_Experiment.py
시나리오별 도메인 응답 비율을 시각화합니다.
~~~bash
python (EN)Visualization_Experiment.py
python (KR)Visualization_Experiment.py
~~~
출력 파일 → `(EN|KR)scenario_domain_comparison.png`

---

## 의존성 설치
~~~bash
pip install -r requirements.txt
~~~
주요 패키지
- `langchain-google-genai`
- `sentence-transformers`
- `nltk`
- `matplotlib`, `scikit-learn`, `tqdm`
- `gdown`, `python-dotenv`

---

## 환경 변수
`.env` 파일에 Google API 키를 저장하세요.
~~~env
GOOGLE_API_KEY=your_google_api_key
~~~

## 문의
실험과 관련한 이슈는 [GitHub Issues](https://github.com/SeonGyuJang/DIGB-Homosilicus/issues) 또는 이메일(<dsng3419@korea.ac.kr>)로 남겨주세요.



<p align="right">
  <img src="assets/Global_Symbol.jpg" alt="Korea University Logo" height="100" />
</p>

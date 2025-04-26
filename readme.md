(1) langchain_experiment.py 
 - 요구사항
    * .env : GOOGLE_API_KEY가 담긴 .env 파일
    * grouped_persona_data.json : 도메인별로 그룹화된 페르소나 데이터
    * existing_research_scenarios.json : 실험에 사용되는 시나리오 데이터

- 생성되는 파일
    * Person_{idx}.json : 페스소나별 실험결과가 담긴 데이터


(2) combined_EXP_Result.py
- 요구사항
     * input_dir : (1)에서 만들어진 페르소나별 실험결과가 담긴 데이터가 있는 폴더 경로
     * grouped_persona_data.json : 도메인별로 그룹화된 페르소나 데이터

- 생성되는 파일
     * EXISITNG_EXP_combined_by_domain.json : 여러개의 Person_{idx}.json이 하나로 합쳐진 json 파일
    → 저장되는 파일명은 변경 가능함(output_file에서 변경)


(3) make_plot_and_check_error.py
- 1. 시나리오별 Left/Right가 몇개 있는지 카운팅
- 2. [1]의 카운팅을 바탕으로, plot 생성(막대그래프)
- 3. [1]의 카운팅 결과를 JSONL 파일로 저장
- 4. missing_data 확인을 위한 check_error 기능
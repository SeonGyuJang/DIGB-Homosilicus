import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer

# ========== 1. 데이터 로드 (JSONL 파일 읽기) ==========
input_path = r"c:\Users\dsng3\Desktop\(EN)PERSONA_DATA.jsonl"
with open(input_path, "r", encoding="utf-8") as f:
    persona_data = [json.loads(line) for line in f]

# ========== 2. NLTK 리소스 다운로드 및 전처리 함수 ==========
nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # 소문자화 + 특수문자 제거
    tokens = text.split()
    processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    return " ".join(processed_tokens)

# ========== 3. SentenceTransformer 모델 로드 ==========
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# ========== 4. JSONL로 저장할 준비 ==========
output_path = r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\persona_embeddings_1000.jsonl"
with open(output_path, "w", encoding="utf-8") as f_out:
    for entry in persona_data:
        persona_text = entry["persona"]
        preprocessed_text = preprocess_text(persona_text)
        embedding_vector = model.encode(preprocessed_text).tolist()
        
        updated_entry = {
            **entry,  # 기존 데이터 유지
            "preprocessed_persona": preprocessed_text,  # 전처리된 텍스트 추가
            "embedding": embedding_vector  # 임베딩 벡터 추가
        }
        
        # 한 줄씩 JSON 객체 쓰기
        f_out.write(json.dumps(updated_entry, ensure_ascii=False) + "\n")

print(f"✅ 임베딩 페르소나 저장 완료 : {output_path}")

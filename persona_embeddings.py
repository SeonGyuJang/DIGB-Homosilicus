import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer

input_path = r"c:\Users\dsng3\Desktop\(EN)PERSONA_DATA.jsonl"
with open(input_path, "r", encoding="utf-8") as f:
    persona_data = [json.loads(line) for line in f]

nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)  
    tokens = text.split()
    processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    return " ".join(processed_tokens)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

output_path = r"C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\persona_embeddings_1000.jsonl"
with open(output_path, "w", encoding="utf-8") as f_out:
    for entry in persona_data:
        persona_text = entry["persona"]
        preprocessed_text = preprocess_text(persona_text)
        embedding_vector = model.encode(preprocessed_text).tolist()
        
        updated_entry = {
            **entry,  
            "preprocessed_persona": preprocessed_text, 
            "embedding": embedding_vector 
        }
        
        f_out.write(json.dumps(updated_entry, ensure_ascii=False) + "\n")

print(f"임베딩 페르소나 저장 완료 : {output_path}")

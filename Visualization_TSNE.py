import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from collections import defaultdict

# 1. 데이터 로드
file_path = r'C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\data\Persona_embedding_DATA.jsonl'  # ← 여기에 jsonl 파일 경로 입력
data = []
with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

# 2. 도메인별로 묶기
domain_groups = defaultdict(list)
for entry in data:
    domain = entry['general domain (top 1 percent)'].lower()  # 소문자 통일
    idx = entry['idx']
    embedding = entry['embedding']
    domain_groups[domain].append((idx, embedding))

# 3. 시각화를 위한 데이터 준비
all_embeddings = []
all_labels = []
all_idx = []

for domain, items in domain_groups.items():
    for idx, emb in items:
        all_embeddings.append(emb)
        all_labels.append(domain)
        all_idx.append(idx)

X = np.array(all_embeddings)

# 4. TSNE 적용
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
X_embedded = tsne.fit_transform(X)

# 5. 시각화
plt.figure(figsize=(15, 10))

# 도메인별로 다른 색
unique_domains = sorted(list(set(all_labels)))
colors = plt.cm.tab20(np.linspace(0, 1, len(unique_domains)))

domain_to_color = {domain: colors[i] for i, domain in enumerate(unique_domains)}

for i, (x, y) in enumerate(X_embedded):
    domain = all_labels[i]
    idx = all_idx[i]
    plt.scatter(x, y, color=domain_to_color[domain], label=domain if domain not in plt.gca().get_legend_handles_labels()[1] else "")
    plt.text(x + 0.5, y + 0.5, f'{idx}-{domain}', fontsize=8)

plt.title('t-SNE visualization by general domain')
plt.xlabel('Dimension 1')
plt.ylabel('Dimension 2')
plt.legend(fontsize=8, loc='best', bbox_to_anchor=(1.05, 1))
plt.tight_layout()
plt.show()

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from collections import defaultdict 

print("[1/6] 파일 읽는 중...")
file_path = r'C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\NO_Tracking\Persona_embedding_DATA.jsonl' 
data = []
with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

print("[2/6] 도메인별로 그룹핑하는 중...")
domain_groups = defaultdict(list)
for entry in data:
    domain = entry['general domain (top 1 percent)'].lower()  
    idx = entry['idx']
    embedding = entry['embedding']
    domain_groups[domain].append((idx, embedding))

print("[3/6] 임베딩과 레이블 리스트로 변환 중...")
all_embeddings = []
all_labels = []
all_idx = []

for domain, items in domain_groups.items():
    for idx, emb in items:
        all_embeddings.append(emb)
        all_labels.append(domain)
        all_idx.append(idx)

X = np.array(all_embeddings)

print("[4/6] t-SNE 변환(t-SNE fitting) 중...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
X_embedded = tsne.fit_transform(X)

print("[5/6] 시각화 준비 및 그리기 중...")
plt.figure(figsize=(15, 10))

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

print("[6/6] 플롯 보여주는 중...")
plt.show()

print("✅ 모든 과정 완료!")

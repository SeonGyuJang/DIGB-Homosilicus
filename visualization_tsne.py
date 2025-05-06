import json
import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from collections import defaultdict

file_path = r'C:\Users\dsng3\Documents\GitHub\DIGB-Homosilicus\NO_Tracking\Persona_embedding_DATA.jsonl'
samples_per_domain = 500  # <<< 여기만 수정하면 추출 개수 바꿀 수 있음
random_seed = 42

print("[1/5] 파일 읽는 중...")
data = []
with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

print("[2/5] 도메인별로 그룹핑하는 중...")
domain_groups = defaultdict(list)
for entry in data:
    domain = entry['general domain (top 1 percent)'].lower()
    idx = entry['idx']
    embedding = entry['embedding']
    domain_groups[domain].append((idx, embedding))

print("[3/5] 도메인별로 샘플링하는 중...")
random.seed(random_seed)

sampled_embeddings = []
sampled_labels = []
sampled_idx = []

for domain, items in domain_groups.items():
    if len(items) > samples_per_domain:
        sampled_items = random.sample(items, samples_per_domain)
    else:
        sampled_items = items  

    for idx, emb in sampled_items:
        sampled_embeddings.append(emb)
        sampled_labels.append(domain)
        sampled_idx.append(idx)

X = np.array(sampled_embeddings)

print("[4/5] t-SNE 변환(t-SNE fitting) 중...")
tsne = TSNE(n_components=2, random_state=random_seed, perplexity=30)
X_embedded = tsne.fit_transform(X)

print("[5/5] 시각화 준비 및 그리기 중...")
plt.figure(figsize=(15, 10))

unique_domains = sorted(list(set(sampled_labels)))
colors = plt.cm.tab20(np.linspace(0, 1, len(unique_domains)))
domain_to_color = {domain: colors[i] for i, domain in enumerate(unique_domains)}

for i, (x, y) in enumerate(X_embedded):
    domain = sampled_labels[i]
    plt.scatter(x, y, color=domain_to_color[domain], edgecolor='k', s=30)

for domain, color in domain_to_color.items():
    plt.scatter([], [], color=color, label=domain)

plt.title('t-SNE Visualization by General Domain (Sampled)')
plt.xlabel('Dimension 1')
plt.ylabel('Dimension 2')
plt.legend(fontsize=8, loc='best', bbox_to_anchor=(1.05, 1))
plt.tight_layout()

print("모든 과정 완료! 플롯 보여주는 중...")
plt.show()

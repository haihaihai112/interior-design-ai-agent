"""测试知识库检索"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import sys
sys.path.insert(0, "C:\\Users\\38241\\Desktop\\interior-design-ai-agent")

from config import EMBEDDING_CONFIG, CHROMA_CONFIG
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer(EMBEDDING_CONFIG["model_name"], device=EMBEDDING_CONFIG["device"])
client = chromadb.PersistentClient(path=CHROMA_CONFIG["persist_directory"])
collection = client.get_collection(CHROMA_CONFIG["collection_name"])

queries = [
    "侘寂风的特点是什么？",
    "法式奶油风的配色方案",
    "灯光照度标准",
    "PBR材质参数",
]

for q in queries:
    emb = model.encode([q], normalize_embeddings=True)
    results = collection.query(query_embeddings=emb.tolist(), n_results=2)
    print(f'\n{"="*60}')
    print(f"Query: {q}")
    print("="*60)
    for i, (doc, meta, dist) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ):
        source = meta["source"]
        print(f"  #{i+1} [{source}] dist={dist:.4f}")
        print(f"     {doc[:150]}...")

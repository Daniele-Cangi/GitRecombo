# 🔮 NEXUS-EMB-240M-NSA — Transfer Learning Edition  

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg?logo=python)](https://www.python.org/)  
[![PyTorch](https://img.shields.io/badge/PyTorch-2.4+-EE4C2C.svg?logo=pytorch)](https://pytorch.org/)  
[![Transformers](https://img.shields.io/badge/HF-Transformers-yellow.svg?logo=huggingface)](https://huggingface.co/transformers/)  
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](./LICENSE)  
[![Status](https://img.shields.io/badge/status-Research--Preview-orange)]()  
[![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red)]()  
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](./CONTRIBUTING.md)  
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Daniele-Cangi/Aurora-X/blob/master/NEXUS_TRANSFER_64_ANCHORS.ipynb)  

**NEXUS-EMB-240M-NSA** is a **compact dual-head embedding model** optimized for **edge-first inference** and **high-performance vector search**.  
This **Transfer Learning Edition** provides everything needed to **train from scratch** using **Microsoft AllNLI dataset**, with **64 NSA anchors** for enhanced performance.

## 🚀 Quick Start with Google Colab

**One-Click Training on Google Colab!** 🎯  
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Daniele-Cangi/Aurora-X/blob/master/NEXUS_TRANSFER_64_ANCHORS.ipynb)

Simply click the badge above to open the notebook and start training immediately with:
- ✅ **Automatic AllNLI dataset download** (SNLI + MultiNLI)
- ✅ **64 NSA anchors** (enhanced from original 32)
- ✅ **Checkpoint persistence** to Google Drive
- ✅ **Pre-configured for microsoft/mpnet-base**
- ✅ **Ready-to-run cells** for complete training pipeline  

---

## ✨ Key Features  

- **🧭 Dual-Head Architecture (Semantic & Entity)**  
  Unlike traditional embedding models that generate a single vector representation, **NEXUS-EMB-240M-NSA** introduces a **dual-head design**.  
  - The **semantic head** focuses on capturing **general meaning and contextual relationships**, enabling accurate semantic similarity and natural language understanding.  
  - The **entity head** is optimized for identifying **specific terms, entities, and domain-relevant markers**, giving the model sharper resolution in high-precision tasks.  
  When combined, these two vectors form a **768-dimensional embedding** that is **exceptionally rich and fine-grained**, improving accuracy in **complex search, recommendation, and knowledge extraction pipelines**.  

- **🌐 Neural Spectral Anchoring (NSA)**  
  This advanced mechanism projects embeddings into a **spectral space** rather than a standard Euclidean vector space. By doing so, the model:  
  - Learns **optimized relational structures** that capture deeper semantic dependencies.  
  - Produces embeddings that are **better organized and separable**, which improves retrieval performance in dense databases.  
  - Goes **beyond conventional supervised training**, incorporating a **spectral optimization process** that grants the model a more **structural understanding of your data**.  
  In practice, NSA ensures **higher precision and efficiency** in vector search and retrieval, making it well-suited for enterprise-scale deployments.  

- **⚡ Residual Hashing Bridge**  
  Designed for scenarios where **latency is critical**, this feature integrates a **64-bit residual hashing bridge** that supports **fast candidate pre-filtering**.  
  - It enables a **two-stage retrieval process**: first, rapidly eliminate unlikely matches using the hash, then refine results with the full embedding.  
  - The result is a **drastic reduction in search space**, which cuts down computational cost and accelerates queries without degrading final accuracy.  
  This capability makes the model ideal for **real-time recommendation systems, financial applications, and large-scale search engines**, where speed is just as important as accuracy.  

- **🪆 Matryoshka Embeddings**  
  Recognizing the diverse hardware and memory constraints of modern deployments, the model includes **native support for flexible embedding sizes**.  
  - You can resize the final embeddings to **768, 512, or 256 dimensions** depending on performance and memory trade-offs.  
  - Larger embeddings (768) retain full richness for high-accuracy offline tasks, while smaller embeddings (256) make the model deployable on **resource-constrained devices** like edge hardware or mobile processors.  
  - This **scalable design** enables a single model to adapt across environments ranging from **cloud-scale vector databases** to **lightweight mobile inference**.  

---

## 📖 Why It Matters  

Unlike standard compressed embeddings, **NEXUS-EMB-240M-NSA** offers:  

- Compact yet semantically robust embeddings  
- Built-in **acceleration for search tasks**  
- Flexible deployment: **semantic search, entity resolution, recommendation**  

Enabling **enterprise-grade performance** from **mobile edge devices** to **large-scale clusters**.  

---

## ⚙️ Quickstart  

### 🎯 Option A: Google Colab (Recommended)

**The fastest way to get started!** Use our pre-configured Colab notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Daniele-Cangi/Aurora-X/blob/master/NEXUS_TRANSFER_64_ANCHORS.ipynb)

**Features:**
- 🚀 **One-click setup** - no local installation needed
- 📊 **Automatic AllNLI download** - 553K+ training examples (SNLI + MultiNLI)
- 💾 **Auto-save checkpoints** to Google Drive every 2000 steps
- 🔧 **64 NSA anchors** for enhanced performance
- ⚡ **torch.compile** optimization for faster training
- 📈 **Real-time progress tracking** with loss visualization

**Training Pipeline:**
1. **Mount Drive** → Setup checkpoint persistence
2. **Install Dependencies** → All packages auto-installed
3. **Download AllNLI** → Microsoft's SNLI + MultiNLI datasets
4. **Initialize Model** → microsoft/mpnet-base with 64 anchors
5. **Train** → 30K steps with automatic checkpointing
6. **Evaluate** → Performance metrics and anchor analysis
7. **Export** → Model ready for production deployment

### 🖥️ Option B: Local Training  

### 1. Setup environment  
```bash
pip install torch==2.4.0 transformers sentencepiece einops faiss-cpu
```

### 2. Train a tokenizer  
```bash
python scripts/build_tokenizer.py   --corpus path/to/corpus.txt   --vocab 48000   --out_prefix tokenizer_spm_48k
```

### 3. Train the model  
```bash
python scripts/train.py   --config configs/nexus_emb_240m.json   --pairs data/your_pairs.jsonl   --tokenizer_model tokenizer_spm_48k.model   --batch 64 --max_len 128 --steps 1000
```

### 4. Evaluate  
```bash
python scripts/eval_mteb_lite.py   --config configs/nexus_emb_240m.json   --tokenizer_model tokenizer_spm_48k.model
```

### 5. Export to ONNX  
```bash
python scripts/export_onnx.py   --config configs/nexus_emb_240m.json   --out artifacts/nexus_emb_240m_nsa.onnx --seq_len 128
```

---

## 💡 Use Cases  

- 🔎 **Semantic Search** — domain-specific and multilingual retrieval  
- 🏷️ **Entity Resolution** — deduplication across structured/unstructured data  
- 🎯 **Recommendations** — personalization with efficient embeddings  
- 📊 **Clustering & Analytics** — scalable unsupervised grouping  
- 📱 **Edge Deployment** — low-latency, memory-aware inference  

---

## 🔧 Industrial & Business Applications  

- **🔎 Semantic Search Engines** — enterprise knowledge bases, legal/medical docs, product catalogs  
- **🏷️ Entity Resolution** — merge duplicates across CRM/ERP/supply chain systems  
- **🎯 Recommendation Systems** — e-commerce, media, fintech personalization at scale  
- **📊 Business Intelligence** — detect anomalies & trends in customer, IoT, or financial data  
- **📱 Edge & Mobile** — on-device analytics in AR/VR, smart assistants, retail kiosks  
- **🌐 Multilingual Knowledge Management** — dual-head embeddings bridging global datasets  

---

## 🔬 Advanced Training Notes  

- Use **hard-negative mining** + **Knowledge Distillation** from larger teachers  
- **RoPE** and **FlashAttention**: off by default for stability; enable for HPC training  

---

## 📂 Repository Structure  

```
NEXUS-EMB-240M-NSA/
├── 📓 NEXUS_TRANSFER_64_ANCHORS.ipynb  # 🚀 Google Colab Training Notebook
├── configs/
│   └── nexus_emb_240m.json
├── scripts/
│   ├── build_tokenizer.py
│   ├── train.py
│   ├── eval_mteb_lite.py
│   └── export_onnx.py
├── data/
│   ├── demo_pairs.jsonl
│   └── wiki_pairs.jsonl
├── src/
│   ├── model.py
│   ├── losses.py
│   ├── data_loader.py
│   └── utils.py
├── ckpts_wiki/              # Pre-trained checkpoints
├── notebooks/               # Additional analysis notebooks
├── artifacts/
└── README.md
```

### 🎯 Key Files:

- **`NEXUS_TRANSFER_64_ANCHORS.ipynb`** → **Main Colab notebook** for complete training pipeline
- **`src/model.py`** → Core model architecture with NSA anchors
- **`src/losses.py`** → Matryoshka + contrastive loss implementations  
- **`configs/nexus_emb_240m.json`** → Model configuration for 240M parameters

---

## 🤝 Contributing  

Contributions are welcome! Please open issues and pull requests to help improve training scripts, configs, or evaluation pipelines.  

---

## 📜 License  

This project is licensed under the **Apache License 2.0**.  
See [LICENSE](./LICENSE) for details.  

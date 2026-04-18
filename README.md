# environment install
```bash

python3 -m venv venv/

source venv/bin/activate

```

## Setup

```bash
1. `pip install -r requirements.txt`
2. `ollama pull all-minilm && ollama pull llama3.2:3b`
3. Place tes documents dans `data/`
4. `python -m scripts.retrieval --source data/`  # génère vector_store/
```
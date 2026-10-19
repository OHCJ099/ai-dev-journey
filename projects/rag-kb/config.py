# projects/rag-kb/config.py
CHUNK_SIZE = 500
OVERLAP = 50
TOP_K = 3
DEEPSEEK_FLASH_PROMPT = 0.000002
DEEPSEEK_FLASH_COMPLETION = 0.000008
COST_LOG_PATH = "D:/dev/ai-dev-journey/projects/rag-kb/logs/cost_log.jsonl"
OFFLINE_INDEX_PATH = "D:/Hermes/cache/scratch/w14/index_offline"
REAL_INDEX_PATH = "D:/Hermes/cache/scratch/w14/index_real"
LOCAL_PROXY_URL = "http://127.0.0.1:8787/v1"

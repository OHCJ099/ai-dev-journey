# projects/rag-kb/config.py
"""全局配置。路径一律由本文件位置推算，不写死绝对路径 —— 换机器、换目录都能跑。"""

from pathlib import Path

# projects/rag-kb/ —— 本文件所在目录，所有路径的锚点
BASE_DIR = Path(__file__).parent

# 语料与派生数据都放这里；data/ 下除语料 .md 外全部 gitignore（可重建）
DATA_DIR = BASE_DIR / "data"

# 正式索引：由 data/*.md 派生，可随时重建，不入库
INDEX_PATH = DATA_DIR / "index"

# 练习 / 测试用索引库：各测试脚本各用一个子目录，不入库
LAB_DIR = DATA_DIR / "_lab"
OFFLINE_INDEX_PATH = LAB_DIR / "index_offline"

# 网页上传文件的落地目录，不入库
UPLOAD_DIR = DATA_DIR / "uploads"

CHUNK_SIZE = 500
OVERLAP = 50
TOP_K = 3
DEEPSEEK_FLASH_PROMPT = 0.000002
DEEPSEEK_FLASH_COMPLETION = 0.000008
COST_LOG_PATH = str(BASE_DIR / "logs" / "cost_log.jsonl")

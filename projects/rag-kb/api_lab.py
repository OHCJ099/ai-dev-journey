"""W14 离线调试入口：假向量只验证接口与入库数据流，不证明语义质量。

运行 uvicorn api_lab:app；正式 api.py 不负责设置假向量。
"""

import api
from demo_w13 import enable_offline

enable_offline()
app = api.app

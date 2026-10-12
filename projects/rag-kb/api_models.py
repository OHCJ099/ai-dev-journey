"""W14 查询接口的请求模型；校验交给 Pydantic，不包含检索逻辑。"""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str
    k: int = Field(default=3, ge=1, le=10)

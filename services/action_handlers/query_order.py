from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseActionHandler
from ..java_caller import call_java_with_token


class QueryOrderHandler(BaseActionHandler):
    """查询订单处理器"""

    def get_action_name(self) -> str:
        return "query_orders"

    def get_prompt_description(self) -> str:
        return "查询订单列表"

    def get_prompt_params(self) -> str:
        return """参数：status（可选，状态筛选）, date_range（可选，如"7d"表示近7天）, user_id（可选）"""

    async def execute(self, params: Dict[str, Any], token: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        return call_java_with_token("query_orders", params, token)
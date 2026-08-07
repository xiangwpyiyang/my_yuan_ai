from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseActionHandler
from ..java_caller import call_java_with_token


class GetRoutesHandler(BaseActionHandler):
    """获取路由处理器"""

    def get_action_name(self) -> str:
        return "get_routes"

    def get_prompt_description(self) -> str:
        return "获取路由菜单"

    def get_prompt_params(self) -> str:
        return "无参数"

    async def execute(self, params: Dict[str, Any], token: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        return call_java_with_token("get_routes", {}, token)
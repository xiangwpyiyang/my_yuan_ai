from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseActionHandler
from ..route_service import get_page_mapping, get_directory_pages


class NavigateHandler(BaseActionHandler):
    """导航处理器"""

    def get_action_name(self) -> str:
        return "navigate"

    def get_prompt_description(self) -> str:
        return "页面导航 - 跳转到指定页面"

    def get_prompt_params(self) -> str:
        return """参数：target（目标页面的完整路径，以 / 开头）"""

    async def execute(self, params: Dict[str, Any], token: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        target = params.get("target")
        message = params.get("message", "")

        if target:
            return {
                "frontend_action": "navigate",
                "target": target,
                "message": message or f"准备跳转到 {target}"
            }
        else:
            return {
                "frontend_action": "navigate",
                "target": None,
                "message": message or "该页面是目录，无法直接跳转"
            }
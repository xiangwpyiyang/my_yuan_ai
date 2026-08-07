from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseActionHandler


class ChatHandler(BaseActionHandler):
    """闲聊处理器"""

    def get_action_name(self) -> str:
        return "chat"

    def get_prompt_description(self) -> str:
        return "闲聊/问候 - 不执行任何操作"

    def get_prompt_params(self) -> str:
        return "无参数"

    async def execute(self, params: Dict[str, Any], token: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        return {}
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session


class BaseActionHandler(ABC):
    """Action 处理器基类"""

    @abstractmethod
    async def execute(self, params: Dict[str, Any], token: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        """执行具体的 action"""
        pass

    @abstractmethod
    def get_action_name(self) -> str:
        """返回 action 名称"""
        pass

    @abstractmethod
    def get_prompt_description(self) -> str:
        """返回 Prompt 中的描述"""
        pass

    @abstractmethod
    def get_prompt_params(self) -> str:
        """返回 Prompt 中的参数说明"""
        pass
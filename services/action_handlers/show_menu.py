from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseActionHandler
from ..java_caller import call_java_with_token
import json


class ShowMenuHandler(BaseActionHandler):
    """展示菜单结构处理器"""

    def get_action_name(self) -> str:
        return "show_menu"

    def get_prompt_description(self) -> str:
        return "展示后台菜单结构"

    def get_prompt_params(self) -> str:
        return "无参数"

    async def execute(self, params: Dict[str, Any], token: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        # 调用 Java 接口获取路由数据
        result = call_java_with_token("get_routes", {}, token)

        if result.get("success"):
            routes = result.get("data", [])
            # 格式化菜单结构为可读文本
            menu_text = self._format_menu(routes)
            return {
                "success": True,
                "data": routes,
                "display": menu_text
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "获取菜单结构失败"),
                "display": "获取菜单结构失败，请稍后重试"
            }

    def _format_menu(self, routes: list, indent: int = 0) -> str:
        """将菜单树格式化为可读文本"""
        result = []
        prefix = "  " * indent

        for route in routes:
            title = route.get("meta", {}).get("title", route.get("name", "未命名"))
            path = route.get("path", "")
            children = route.get("children", [])

            if children:
                # 有子菜单，显示为目录
                result.append(f"{prefix}📁 {title} ({path})")
                child_text = self._format_menu(children, indent + 1)
                if child_text:
                    result.append(child_text)
            else:
                # 叶子节点，显示为页面
                icon = route.get("meta", {}).get("icon", "")
                icon_str = f" [{icon}]" if icon else ""
                result.append(f"{prefix}📄 {title}{icon_str} → {path}")

        return "\n".join(result)
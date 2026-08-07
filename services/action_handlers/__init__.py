from .base import BaseActionHandler
from .navigate import NavigateHandler
from .create_coupon import CreateCouponHandler
from .query_order import QueryOrderHandler
from .export_report import ExportReportHandler
from .get_routes import GetRoutesHandler
from .chat import ChatHandler
from .show_menu import ShowMenuHandler
from .create_banner import CreateBannerHandler  # 新增

# 注册所有 handler
HANDLERS = {
    "chat": ChatHandler(),
    "navigate": NavigateHandler(),
    "create_coupon": CreateCouponHandler(),
    "query_orders": QueryOrderHandler(),
    "export_report": ExportReportHandler(),
    "get_routes": GetRoutesHandler(),
    "show_menu": ShowMenuHandler(),
    "create_banner": CreateBannerHandler(),  # 新增
}


def get_handler(action: str) -> BaseActionHandler:
    """根据 action 获取对应的处理器"""
    handler = HANDLERS.get(action)
    if not handler:
        raise ValueError(f"不支持的操作: {action}")
    return handler
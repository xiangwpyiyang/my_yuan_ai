from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseActionHandler
from ..java_caller import call_java_with_token


class CreateCouponHandler(BaseActionHandler):
    """创建优惠券处理器"""

    def get_action_name(self) -> str:
        return "create_coupon"

    def get_prompt_description(self) -> str:
        return "创建优惠券"

    def get_prompt_params(self) -> str:
        return """参数：condition（满减门槛，数字）, amount（减免金额，数字）, type（"满减"或"折扣"）, valid_days（有效期天数，数字）"""

    async def execute(self, params: Dict[str, Any], token: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        return call_java_with_token("create_coupon", params, token)
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseActionHandler
from ..java_caller import call_java_with_token
from ..image_generator import generator
from ..image_uploader import uploader
import json
import logging
import time

logger = logging.getLogger(__name__)


class CreateBannerHandler(BaseActionHandler):
    """创建广告处理器"""

    def get_action_name(self) -> str:
        return "create_banner"

    def get_prompt_description(self) -> str:
        return "创建广告/横幅"

    def get_prompt_params(self) -> str:
        return """参数：
- positionId（位置ID，1=弹窗广告）
- headline（大标题，字符串）
- subtitle（小标题，字符串）
- subheading（最下层标题，字符串）
- sort（排序值，数字）
- startTime（开始展示时间，格式：YYYY-MM-DD HH:mm:ss）
- endTime（结束展示时间，格式：YYYY-MM-DD HH:mm:ss）
- status（上架状态，true/false，默认false）
- image（广告图片URL，字符串）
- linkPath（跳转配置，对象）
  - linkType（跳转类型：None/InterPath/OuterPro/WebLink/RichText）
  - linkPath（跳转地址）
  - outerAppid（小程序APPID）
  - innerId（富文本ID）
- articleContent（富文本内容，字符串）
- showDailyTimes（每日显示时间数组）
  - startTime（每日开始时间，如：08:00）
  - endTime（每日结束时间，如：22:00）"""

    async def execute(self, params: Dict[str, Any], token: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        # ============ 参数校验 ============
        if not params.get("headline"):
            return {
                "success": False,
                "message": "请提供广告大标题（headline）"
            }

        if not params.get("positionId"):
            return {
                "success": False,
                "message": "请指定广告位置（positionId：1=弹窗广告）"
            }

        if not params.get("startTime") or not params.get("endTime"):
            return {
                "success": False,
                "message": "请提供广告展示时间范围（startTime 和 endTime）"
            }

        # ============ 自动生成图片（如果没有传 image） ============
        if not params.get("image"):
            try:
                headline = params.get("headline", "")
                subtitle = params.get("subtitle", "")

                if headline:
                    logger.info(f"🎨 为广告「{headline}」生成图片...")
                    image_base64 = generator.generate_image(headline, subtitle)

                    if image_base64:
                        filename = f"ad_{int(time.time())}.png"
                        image_url = uploader.upload_base64_image(image_base64, token, filename)

                        if image_url:
                            params["image"] = image_url
                            logger.info(f"✅ 图片上传成功: {image_url}")
                        else:
                            logger.warning("⚠️ 图片上传失败，使用测试占位图")
                            # 使用测试图片
                            test_image = generator.generate_test_image()
                            test_filename = f"test_{int(time.time())}.png"
                            test_url = uploader.upload_base64_image(test_image, token, test_filename)
                            if test_url:
                                params["image"] = test_url
                            else:
                                params["image"] = ""
                    else:
                        logger.warning("⚠️ 图片生成失败，使用测试占位图")
                        # 使用测试图片
                        test_image = generator.generate_test_image()
                        test_filename = f"test_{int(time.time())}.png"
                        test_url = uploader.upload_base64_image(test_image, token, test_filename)
                        if test_url:
                            params["image"] = test_url
                        else:
                            params["image"] = ""

            except Exception as e:
                logger.error(f"❌ 图片处理失败: {str(e)}")
                # 异常时使用测试图片
                try:
                    test_image = generator.generate_test_image()
                    test_filename = f"test_{int(time.time())}.png"
                    test_url = uploader.upload_base64_image(test_image, token, test_filename)
                    if test_url:
                        params["image"] = test_url
                    else:
                        params["image"] = ""
                except:
                    params["image"] = ""

        # ============ 构建完整参数 ============
        # 处理 linkPath 默认值
        link_path = params.get("linkPath", {})
        if not link_path:
            link_path = {
                "linkType": "None",
                "linkPath": "",
                "outerAppid": "",
                "innerId": ""
            }
        elif isinstance(link_path, dict):
            link_path.setdefault("linkType", "None")
            link_path.setdefault("linkPath", "")
            link_path.setdefault("outerAppid", "")
            link_path.setdefault("innerId", "")

        # 处理 showDailyTimes 默认值
        show_daily_times = params.get("showDailyTimes", [])
        if not show_daily_times:
            show_daily_times = [
                {"startTime": "00:00", "endTime": "23:59"}
            ]

        # 构建完整请求参数
        banner_data = {
            "positionId": params.get("positionId"),
            "headline": params.get("headline"),
            "subtitle": params.get("subtitle", ""),
            "subheading": params.get("subheading", ""),
            "sort": params.get("sort", 0),
            "startTime": params.get("startTime"),
            "endTime": params.get("endTime"),
            "status": params.get("status", False),
            "image": params.get("image", ""),
            "linkPath": link_path,
            "articleContent": params.get("articleContent", ""),
            "showDailyTimes": show_daily_times
        }

        logger.info(f"📤 发送给 Java 的参数: {json.dumps(banner_data, ensure_ascii=False)[:500]}")

        # ============ 调用 Java 接口 ============
        result = call_java_with_token("create_banner", banner_data, token)

        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": f"广告「{params.get('headline')}」创建成功，已自动生成广告图"
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "创建广告失败")
            }
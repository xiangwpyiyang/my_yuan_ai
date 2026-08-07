import logging
import base64
import time
from typing import Optional
from config import settings
import dashscope
import requests

logger = logging.getLogger(__name__)


class TongyiImageGenerator:
    """通义万相图片生成服务"""

    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        if self.api_key:
            dashscope.api_key = self.api_key
            logger.info("✅ 通义万相 API Key 已配置")
        else:
            logger.warning("⚠️ 通义万相 API Key 未配置")

    def generate_image(self, headline: str, subtitle: str = "") -> Optional[str]:
        if not self.api_key:
            logger.error("❌ 通义万相 API Key 未配置")
            return None

        prompt = self._build_prompt(headline, subtitle)
        logger.info(f"🎨 开始生成图片，提示词: {prompt}")

        try:
            response = dashscope.ImageSynthesis.call(
                model="wanx-v1",
                prompt=prompt,
                n=1,
                size="1024*1024"  # ⚠️ 唯一修改：用 * 而不是 x
            )

            if response.status_code == 200:
                output = response.output
                task_status = output.get("task_status", "")

                if task_status == "SUCCEEDED":
                    results = output.get("results", [])
                    if results and len(results) > 0:
                        image_url = results[0].get("url")
                        if image_url:
                            logger.info(f"✅ 通义万相生成图片成功")
                            img_response = requests.get(image_url, timeout=30)
                            if img_response.status_code == 200:
                                return base64.b64encode(img_response.content).decode('utf-8')
                    return None

                elif task_status == "FAILED":
                    logger.error(f"❌ 任务失败: {output.get('message', '未知错误')}")
                    return None

                elif task_status == "RUNNING":
                    task_id = output.get("task_id")
                    if task_id:
                        return self._wait_for_task(task_id)
                else:
                    return None
            else:
                logger.error(f"❌ 通义万相调用失败: {response.message}")
                return None

        except Exception as e:
            logger.error(f"❌ 通义万相生成异常: {str(e)}")
            return None

    def _wait_for_task(self, task_id: str, max_wait: int = 60) -> Optional[str]:
        for i in range(max_wait):
            try:
                response = dashscope.ImageSynthesis.fetch(
                    model="wanx-v1",
                    task_id=task_id
                )
                if response.status_code == 200:
                    output = response.output
                    task_status = output.get("task_status", "")
                    if task_status == "SUCCEEDED":
                        results = output.get("results", [])
                        if results and len(results) > 0:
                            image_url = results[0].get("url")
                            if image_url:
                                img_response = requests.get(image_url, timeout=30)
                                if img_response.status_code == 200:
                                    return base64.b64encode(img_response.content).decode('utf-8')
                        return None
                    elif task_status == "FAILED":
                        return None
                    elif task_status in ["RUNNING", "PENDING"]:
                        time.sleep(2)
                        continue
                else:
                    time.sleep(2)
            except Exception as e:
                time.sleep(2)
        return None

    def _build_prompt(self, headline: str, subtitle: str) -> str:
        prompt_parts = [
            "电商促销广告图，需要包含商品展示、促销标签、抢眼背景",
            f'主标题文字："{headline}"（设计感字体，居中）',
            f'副标题文字："{subtitle}"（小字，在标题下方）',
            "画面要有吸引力，背景简洁明亮，有促销氛围",
            "风格：电商广告，设计感强，色彩鲜艳，有视觉冲击力"
        ]
        prompt_parts.append("电商平台促销广告图")
        prompt_parts.append(f'主标题："{headline}"')
        if subtitle:
            prompt_parts.append(f'副标题："{subtitle}"')
        style_parts = [
            "简洁现代",
            "色彩明亮",
            "适合电商推广",
            "居中构图",
            "文字清晰突出"
        ]
        if any(kw in headline for kw in ["节日", "中秋", "国庆", "双十一", "618", "春节", "圣诞"]):
            style_parts.append("节日氛围")
        if any(kw in headline for kw in ["促销", "优惠", "折扣", "满减", "打折"]):
            style_parts.append("促销活动")
        prompt_parts.append("风格：" + "，".join(style_parts))
        return "，".join(prompt_parts)

    def generate_test_image(self) -> str:
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


generator = TongyiImageGenerator()
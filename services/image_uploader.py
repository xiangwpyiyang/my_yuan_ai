# services/image_uploader.py

import requests
import logging
import base64
from io import BytesIO
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)


class ImageUploader:
    """图片上传服务"""

    def __init__(self):
        self.upload_url = getattr(settings, "IMAGE_UPLOAD_URL", "")

    def upload_base64_image(self, image_base64: str, token: str = None, filename: str = None) -> Optional[str]:
        """
        上传base64图片到你的服务器（使用 multipart/form-data）
        """
        if not self.upload_url:
            logger.warning("⚠️ 未配置 IMAGE_UPLOAD_URL，跳过上传")
            return None

        if not filename:
            import time
            filename = f"ad_{int(time.time())}.png"

        # 1. 将 base64 转换为二进制文件
        # 如果 base64 包含 data:image/png;base64, 前缀，去掉
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]

        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            logger.error(f"❌ base64 解码失败: {str(e)}")
            return None

        # 2. 构建 multipart/form-data 请求
        files = {
            "file": (filename, BytesIO(image_bytes), "image/png")
        }
        data = {
            "type": "Default"
        }

        headers = {}
        if token:
            # 确保 token 格式正确
            clean_token = token.strip()
            if not clean_token.startswith("Bearer "):
                headers["Authorization"] = f"Bearer {clean_token}"
            else:
                headers["Authorization"] = clean_token

        # 打印调试信息
        logger.info(f"📤 上传图片到: {self.upload_url}")
        logger.info(f"📤 文件名: {filename}")
        logger.info(f"📤 文件大小: {len(image_bytes)} bytes")
        logger.info(f"📤 请求头: {headers}")

        try:
            resp = requests.post(
                self.upload_url,
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )

            logger.info(f"📥 上传响应状态码: {resp.status_code}")

            if resp.status_code == 500:
                logger.error(f"❌ 服务器内部错误，响应内容: {resp.text[:500]}")
                return None

            resp.raise_for_status()

            result = resp.json()
            if result.get("success"):
                image_url = result.get("data", {}).get("url")
                logger.info(f"✅ 图片上传成功: {image_url}")
                return image_url
            else:
                logger.error(f"❌ 上传失败: {result.get('message')}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 图片上传异常: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"响应内容: {e.response.text[:500]}")
            return None


# 全局单例
uploader = ImageUploader()
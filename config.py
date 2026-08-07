import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # DeepSeek
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    # Java
    JAVA_BACKEND_URL: str = os.getenv("JAVA_BACKEND_URL", "https://bohua.cjtzn.com")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL",
                                  "mysql+pymysql://root:123456@localhost:3306/ai_assistant?charset=utf8mb4")

    # Token
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "")

    # ============ 通义万相（OpenAI 兼容接口） ============
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_BASE_URL: str = os.getenv("DASHSCOPE_BASE_URL", "https://ws-Onzerolop51drosj.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")

    # ============ 图片上传 ============
    IMAGE_UPLOAD_URL: str = os.getenv("IMAGE_UPLOAD_URL", "https://bohua.cjtzn.com/api/file/upload")


settings = Settings()
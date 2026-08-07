import json
import logging
from typing import List, Dict, Optional
from openai import OpenAI
from config import settings
from .prompt_builder import build_system_prompt

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL
)


def parse_with_deepseek(user_input: str, token: str = None, history: List[Dict] = None) -> dict:
    """解析用户指令，支持对话历史，处理特殊字符和空输入"""
    try:
        # 清理输入
        clean_input = user_input.strip()
        if not clean_input:
            return {"action": "chat", "params": {}, "message": "请告诉我你想做什么"}

        system_prompt = build_system_prompt(token)
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            for msg in history:
                # 过滤掉可能包含敏感词或过长消息
                content = msg.get("content", "").strip()
                if not content:
                    continue
                # 截断过长的消息（超过2000字符）
                if len(content) > 2000:
                    content = content[:2000] + "..."
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": content
                })

        messages.append({"role": "user", "content": clean_input})

        # 限制总消息长度，防止超过模型上下文限制
        total_length = sum(len(m.get("content", "")) for m in messages)
        if total_length > 8000:
            logger.warning(f"消息总长度 {total_length}，可能超过限制")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)

    except json.JSONDecodeError as e:
        logger.error(f"AI 输出非 JSON: {content}")
        return {"action": "chat", "params": {}, "message": "抱歉，我没能理解你的指令，请重新描述，例如：'创建一个弹窗广告，标题是xxx，展示时间从今天到8月14日'"}
    except Exception as e:
        logger.error(f"DeepSeek 调用失败: {str(e)}")
        return {"action": "chat", "params": {}, "message": f"服务异常，请稍后重试"}


async def parse_with_deepseek_stream(user_input: str, token: str = None, history: List[Dict] = None):
    """流式解析，支持对话历史，增加输入预处理"""
    try:
        clean_input = user_input.strip()
        if not clean_input:
            yield json.dumps({"action": "chat", "params": {}, "message": "请告诉我你想做什么"})
            return

        system_prompt = build_system_prompt(token)
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            for msg in history:
                content = msg.get("content", "").strip()
                if not content:
                    continue
                if len(content) > 2000:
                    content = content[:2000] + "..."
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": content
                })

        messages.append({"role": "user", "content": clean_input})

        total_length = sum(len(m.get("content", "")) for m in messages)
        if total_length > 8000:
            logger.warning(f"消息总长度 {total_length}，可能超过限制")

        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.1,
            stream=True
        )

        full_content = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield content

        # 验证并返回完整 JSON
        try:
            json.loads(full_content)
            yield full_content
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', full_content, re.DOTALL)
            if json_match:
                yield json_match.group()
            else:
                # 如果无法提取 JSON，返回友好提示
                yield json.dumps({
                    "action": "chat",
                    "params": {},
                    "message": "抱歉，我没能理解你的指令，请重新描述"
                })

    except Exception as e:
        logger.error(f"DeepSeek 流式调用失败: {str(e)}")
        # 返回友好错误提示
        yield json.dumps({
            "action": "chat",
            "params": {},
            "message": f"服务异常，请稍后重试"
        })
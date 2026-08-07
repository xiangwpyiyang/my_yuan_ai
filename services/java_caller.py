import requests
import logging
from config import settings

logger = logging.getLogger(__name__)

# Java 接口映射配置
JAVA_APIS = {
    "create_coupon": {
        "url": "/api/coupon/create",
        "method": "POST",
        "param_map": {
            "condition": "minAmount",
            "amount": "discountAmount",
            "type": "couponType",
            "valid_days": "validDays"
        }
    },
    "update_order_status": {
        "url": "/api/order/updateStatus",
        "method": "POST",
        "param_map": {
            "order_id": "orderId",
            "status": "orderStatus"
        }
    },
    "query_orders": {
        "url": "/api/order/list",
        "method": "GET",
        "param_map": {
            "status": "status",
            "date_range": "dateRange",
            "user_id": "userId"
        }
    },
    "export_report": {
        "url": "/api/report/export",
        "method": "POST",
        "param_map": {
            "report_type": "type",
            "date_range": "dateRange"
        }
    },
    "get_routes": {
        "url": "/api/basic/admin/menus/routes",
        "method": "GET",
        "param_map": {}
    },
    "navigate": {
        "type": "frontend"
    },
# ============ 新增：创建广告 ============
    "create_banner": {
        "url": "/api/basic/banner",
        "method": "POST",
        "param_map": {
            "positionId": "positionId",
            "headline": "headline",
            "subtitle": "subtitle",
            "subheading": "subheading",
            "sort": "sort",
            "startTime": "startTime",
            "endTime": "endTime",
            "status": "status",
            "image": "image",
            "linkPath": "linkPath",
            "articleContent": "articleContent",
            "showDailyTimes": "showDailyTimes"
        }
    },
}


def call_java(action: str, params: dict) -> dict:
    """无 token 版本，保留兼容"""
    return call_java_with_token(action, params, None)


def call_java_with_token(action: str, params: dict, token: str = None) -> dict:
    """调用 Java 接口，透传 token"""

    config = JAVA_APIS.get(action)
    if not config:
        raise ValueError(f"不支持的操作: {action}")

    if config.get("type") == "frontend":
        return {"frontend": True, "params": params}

    # 参数名映射
    mapped_params = {}
    for ai_key, java_key in config.get("param_map", {}).items():
        if ai_key in params:
            mapped_params[java_key] = params[ai_key]

    # 构建 URL
    url = f"{settings.JAVA_BACKEND_URL}{config['url']}"
    method = config.get("method", "POST")

    # 构建请求头
    headers = {"Content-Type": "application/json"}
    if token:
        # 清理 token 空白字符
        clean_token = token.strip()
        # 如果 token 已经包含 "Bearer " 前缀，直接使用；否则添加
        if clean_token.startswith("Bearer "):
            headers["Authorization"] = clean_token
        else:
            headers["Authorization"] = f"Bearer {clean_token}"

    # ============ 日志 ============
    logger.info("=" * 50)
    logger.info(f"☕ 调用 Java 接口: {action}")
    logger.info(f"📤 请求 URL: {url}")
    logger.info(f"📤 请求方法: {method}")
    logger.info(f"📤 请求头: {headers}")
    logger.info(f"📤 请求参数: {mapped_params}")
    logger.info("=" * 50)
    # ============ 日志结束 ============

    try:
        if method.upper() == "GET":
            resp = requests.get(url, params=mapped_params, headers=headers, timeout=10)
        else:
            resp = requests.post(url, json=mapped_params, headers=headers, timeout=10)

        logger.info(f"📥 响应状态码: {resp.status_code}")

        if resp.status_code >= 400:
            logger.error(f"📥 响应内容: {resp.text[:500]}")

        resp.raise_for_status()
        return resp.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Java 调用失败: {str(e)}")
        raise RuntimeError(f"调用 Java 接口失败: {str(e)}")
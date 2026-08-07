import json
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# 内存缓存
_routes_cache = {
    "data": None,
    "expire_at": None
}
CACHE_TTL = 300  # 5分钟

# ============ 降级方案：本地硬编码路径 ============
FALLBACK_ROUTES = [
    {"path": "/member/member-list", "title": "会员列表", "name": "MemberList"},
    {"path": "/member/member-level", "title": "会员等级", "name": "MemberLevel"},
    {"path": "/member/member-level-rule", "title": "升降级规则", "name": "MemberLevelRule"},
    {"path": "/member/member-level-record", "title": "升降级记录", "name": "MemberLevelRecord"},
    {"path": "/member/member-integral-record", "title": "积分记录", "name": "MemberIntegralRecord"},
    {"path": "/member/member-integral-ticket", "title": "小票上传", "name": "MemberIntegralTicket"},
    {"path": "/member/member-integral-wx", "title": "微信无感积分", "name": "MemberIntegralWx"},
    {"path": "/member/member-integral-alipay", "title": "支付宝无感积分", "name": "MemberIntegralAlipay"},
    {"path": "/member/member-integral-self", "title": "自助积分", "name": "MemberIntegralSelf"},
    {"path": "/organize/user", "title": "员工管理", "name": "User"},
    {"path": "/organize/member-company-index", "title": "企业管理", "name": "CompanyIndex"},
    {"path": "/organize/member-storeList-index", "title": "店铺管理", "name": "StoreListIndex"},
    {"path": "/organize/member-buildingList-index", "title": "楼栋管理", "name": "BuildingListIndex"},
    {"path": "/organize/ember-floorList-index", "title": "楼层管理", "name": "FloorListIndex"},
    {"path": "/organize/member-commercial-index", "title": "业态管理", "name": "CommercialListIndex"},
    {"path": "/organize/elevator-group", "title": "梯控管理", "name": "ElevatorGroup"},
    {"path": "/organize/access-group", "title": "门禁管理", "name": "AccessGroup"},
    {"path": "/marketing/banner-list/marketing-elastic-index", "title": "弹窗广告", "name": "ElasticListIndex"},
    {"path": "/marketing/banner-list/marketing-topCarousel-index", "title": "顶部轮播", "name": "TopCarouselIndex"},
    {"path": "/marketing/banner-list/marketing-parkIntroduction-index", "title": "园区介绍",
     "name": "ParkIntroductionIndex"},
    {"path": "/marketing/banner-list/marketing-propertyServices-index", "title": "物业服务",
     "name": "PropertyServicesIndex"},
    {"path": "/marketing/banner-list/marketing-buildingBrochure-index", "title": "楼书展示",
     "name": "BuildingBrochureIndex"},
    {"path": "/marketing/marketing-projectConsultation-index", "title": "项目咨询", "name": "ProjectConsultationIndex"},
    {"path": "/marketing/marketing-reservationHome-index", "title": "预约看房", "name": "ReservationHomeIndex"},
    {"path": "/marketing/marketing-customerConsulta-index", "title": "客服咨询", "name": "CustomerConsultaIndex"},
    {"path": "/marketing/marketing-bulletinNotice-index", "title": "公告管理", "name": "BulletinNoticeIndex"},
    {"path": "/marketing/marketing-tenantNotice-index", "title": "租户须知", "name": "TenantNoticeIndex"},
    {"path": "/marketing/marketing-privacyPolicy-index", "title": "隐私协议", "name": "PrivacyPolicyIndex"},
    {"path": "/marketing/marketing-storedValuebanner-index", "title": "储值广告", "name": "storedValueBannerIndex"},
    {"path": "/marketing/marketing-reportRepair-index", "title": "报事报修", "name": "marketingReportRepairIndex"},
    {"path": "/sale/bicycle-parking-space", "title": "自行车位申请", "name": "BicycleParkingSpace"},
    {"path": "/sale/sale-coupon-index", "title": "卡券列表", "name": "SaleCouponIndex"},
    {"path": "/sale/sale-coupon-code", "title": "发放记录", "name": "SaleCouponCode"},
    {"path": "/sale/sale-coupon-use", "title": "核销记录", "name": "SaleCouponUse"},
    {"path": "/sale/marketing-visitorApply-index", "title": "访客申请", "name": "marketingVisitorApplyIndex"},
    {"path": "/sale/visitorBlackList", "title": "访客黑名单", "name": "visitorBlackList"},
    {"path": "/sale/sale-goods-index", "title": "券包管理", "name": "SaleGoodsIndex"},
    {"path": "/sale/sale-shop-limited-index", "title": "商品管理(秒杀)", "name": "SaleShopLimitedIndex"},
    {"path": "/sale/sale-shop-label-index", "title": "商品标签", "name": "SaleShopLabelIndex"},
    {"path": "/sale/sale-order-limited-index", "title": "订单记录(秒杀)", "name": "SaleOrderLimitedIndex"},
    {"path": "/sale/sale-shop-fitness-index", "title": "商品管理(健身)", "name": "SaleShopFitnessIndex"},
    {"path": "/sale/sale-order-fitness-index", "title": "订单记录(健身)", "name": "SaleOrderFitnessIndex"},
    {"path": "/sale/sale-order-pay-index", "title": "支付订单", "name": "SaleOrderPayIndex"},
    {"path": "/sale/showerRoom", "title": "淋浴间预约", "name": "showerRoom"},
    {"path": "/sale/business-stadium-list-index", "title": "场馆管理", "name": "BusinessStadiumlist"},
    {"path": "/sale/sale-venue-record", "title": "预约记录", "name": "SaleVenueRecord"},
    {"path": "/sale/sale-venue-visit", "title": "到场记录", "name": "SaleVenueVisit"},
    {"path": "/sale/business-meeting-list-index", "title": "会议室列表", "name": "BusinessMeetinglist"},
    {"path": "/sale/business-meeting-type-index", "title": "会议室类型", "name": "BusinessMeetingType"},
    {"path": "/sale/business-meeting-order-index", "title": "会议室订单", "name": "BusinessMeetingOrder"},
    {"path": "/sale/sale-parking-temp-record", "title": "临时车记录", "name": "SaleParkingTempRecord"},
    {"path": "/sale/sale-parking-month-record", "title": "月租车记录", "name": "SaleParkingMonthRecord"},
    {"path": "/sale/sale-parking-list", "title": "停车场管理", "name": "SaleParkingList"},
    {"path": "/system/role", "title": "角色管理", "name": "Role"},
    {"path": "/system/menu", "title": "菜单管理", "name": "SysMenu"},
    {"path": "/system/dept", "title": "部门管理", "name": "Dept"},
    {"path": "/system/log", "title": "系统日志", "name": "Log"},
    {"path": "/system/config", "title": "系统配置", "name": "Config"},
    {"path": "/system/notice", "title": "通知公告", "name": "Notice"},
]

FALLBACK_DIRECTORIES = {
    "广告管理": ["弹窗广告", "顶部轮播", "园区介绍", "物业服务", "楼书展示"],
    "卡券管理": ["卡券列表", "发放记录", "核销记录"],
    "商城管理": ["商品管理(秒杀)", "商品标签", "订单记录(秒杀)", "商品管理(健身)", "订单记录(健身)", "支付订单"],
    "秒杀商城": ["商品管理(秒杀)", "商品标签", "订单记录(秒杀)"],
    "健身商城": ["商品管理(健身)", "订单记录(健身)"],
    "场馆预约": ["场馆管理", "预约记录", "到场记录"],
    "会议室预约": ["会议室列表", "会议室类型", "会议室订单"],
    "停车管理": ["临时车记录", "月租车记录", "停车场管理"],
}


def get_all_routes(token: str = None) -> List[Dict[str, Any]]:
    """获取所有路由（带缓存）"""
    global _routes_cache

    # 检查缓存
    if _routes_cache["data"] and _routes_cache["expire_at"] > datetime.now():
        logger.info("✅ 使用缓存数据")
        return _routes_cache["data"]

    logger.info("🔄 缓存过期或为空，尝试从 Java 获取...")

    try:
        from .java_caller import call_java_with_token

        logger.info(f"📤 调用 call_java_with_token，action=get_routes")

        result = call_java_with_token("get_routes", {}, token)

        logger.info(f"📥 Java 返回: success={result.get('success')}")

        if result.get("success"):
            routes = result.get("data", [])
            if routes:
                _routes_cache["data"] = routes
                _routes_cache["expire_at"] = datetime.now() + timedelta(seconds=CACHE_TTL)
                logger.info(f"✅ 获取路由成功，共 {len(routes)} 条")
                return routes
            else:
                logger.warning("⚠️ Java 返回成功但 data 为空")
        else:
            logger.warning(f"⚠️ Java 返回失败: {result.get('message', '未知错误')}")

    except Exception as e:
        logger.error(f"❌ 从 Java 获取路由失败: {str(e)}")
        logger.info("使用本地降级方案（FALLBACK_ROUTES）")

    logger.info(f"📋 返回降级数据，共 {len(FALLBACK_ROUTES)} 条")
    return FALLBACK_ROUTES


def flatten_routes(routes: List[Dict], parent_path: str = "") -> List[Dict]:
    """将嵌套路由扁平化，提取所有叶子节点"""
    result = []

    # 如果是降级数据（已经是扁平格式），直接返回
    if routes and isinstance(routes[0], dict) and "path" in routes[0] and "title" in routes[0]:
        return routes

    for route in routes:
        path = route.get("path", "")
        if parent_path and path:
            full_path = f"{parent_path}/{path}".replace("//", "/")
        elif parent_path:
            full_path = parent_path
        else:
            full_path = path or "/"

        if route.get("component"):
            result.append({
                "path": full_path,
                "name": route.get("name", ""),
                "title": route.get("meta", {}).get("title", ""),
                "icon": route.get("meta", {}).get("icon", ""),
                "hidden": route.get("meta", {}).get("hidden", False)
            })

        if route.get("children"):
            result.extend(flatten_routes(route["children"], full_path))

    return result


def get_page_mapping(token: str = None) -> Dict[str, str]:
    """获取 页面名称 → 路径 的映射"""
    routes = get_all_routes(token)
    flat = flatten_routes(routes)

    mapping = {}
    for item in flat:
        title = item.get("title", "")
        name = item.get("name", "")
        path = item.get("path", "")

        if title and not item.get("hidden", False):
            mapping[title] = path
        if name and not item.get("hidden", False):
            mapping[name] = path

    return mapping


def get_directory_pages(token: str = None) -> Dict[str, List[str]]:
    """获取 目录名称 → 子页面列表 的映射"""
    routes = get_all_routes(token)

    # 如果是降级数据（扁平格式），使用本地目录映射
    if routes and isinstance(routes[0], dict) and "path" in routes[0] and "title" in routes[0]:
        return FALLBACK_DIRECTORIES

    result = {}

    def traverse(route_list: List[Dict], parent_title: str = ""):
        for route in route_list:
            title = route.get("meta", {}).get("title", "")
            children = route.get("children", [])

            if children and not route.get("component"):
                dir_name = title or route.get("path", "")
                child_titles = []

                def collect_titles(node_list: List[Dict]):
                    for node in node_list:
                        node_title = node.get("meta", {}).get("title", "")
                        if node.get("component"):
                            child_titles.append(node_title)
                        if node.get("children"):
                            collect_titles(node["children"])

                collect_titles(children)
                if child_titles:
                    result[dir_name] = child_titles

            traverse(children, title)

    traverse(routes)
    return result if result else FALLBACK_DIRECTORIES
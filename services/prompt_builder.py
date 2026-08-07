from typing import Dict, List
from .route_service import get_page_mapping, get_directory_pages


def build_navigation_prompt(token: str = None) -> str:
    """
    动态构建导航相关的 Prompt
    从 Java 获取实时数据，生成路径映射
    """
    page_mapping = get_page_mapping(token)
    dir_mapping = get_directory_pages(token)

    pages_text = "\n".join([
        f"├── {title} → {path}  ✅"
        for title, path in page_mapping.items()
    ])

    dirs_text = ""
    for dir_name, children in dir_mapping.items():
        dirs_text += f"├── {dir_name} (目录，不可跳转) ❌\n"
        for child in children:
            child_path = page_mapping.get(child, "")
            dirs_text += f"│   ├── {child} → {child_path}  ✅\n"

    return f"""
【可跳转的页面路径列表】
{pages_text}

【目录页面（不可跳转）】
{dirs_text}
"""


def build_action_prompt() -> str:
    """构建 action 描述"""
    return """
其他支持的业务操作：

1. create_coupon - 创建优惠券
   参数：condition（满减门槛，数字）, amount（减免金额，数字）, type（"满减"或"折扣"）, valid_days（有效期天数，数字）

2. query_orders - 查询订单列表
   参数：status（可选，状态筛选）, date_range（可选，如"7d"表示近7天）, user_id（可选）

3. export_report - 导出报表
   参数：report_type（"sales"或"user"）, date_range（如"30d"）

4. get_routes - 获取路由菜单（返回原始 JSON 数据）
   参数：无

5. show_menu - 展示后台菜单结构（以友好的树形结构展示）
   参数：无

6. create_banner - 创建广告
   参数：
   - positionId（位置ID，根据用户描述自动映射）：
     * 用户说"弹窗广告" → 1
     * 用户说"顶部轮播" → 2
     * 用户说"园区介绍" → 3
     * 用户说"物业服务" → 4
     * 用户说"楼书展示" → 5
     * 用户说"储值广告" → 6
   - headline（大标题）
   - subtitle（小标题）
   - subheading（最下层标题）
   - sort（排序值，数字）
   - startTime（开始时间，格式：YYYY-MM-DD HH:mm:ss）
   - endTime（结束时间，格式：YYYY-MM-DD HH:mm:ss）
   - status（上架状态，true/false，默认false）
   - image（广告图片URL）
   - linkPath（跳转配置对象：linkType/None/InterPath/OuterPro/WebLink/RichText, linkPath, outerAppid, innerId）
   - articleContent（富文本内容）
   - showDailyTimes（每日显示时间数组：[{startTime: "08:00", endTime: "22:00"}]）

   【重要规则】
   - 如果用户没有指定广告位置（如"弹窗广告"、"顶部轮播"等），必须返回追问，不能使用默认值
   - 追问时返回：{"action":"chat","params":{},"message":"请问您想创建哪种类型的广告？如：弹窗广告、顶部轮播、园区介绍、物业服务、楼书展示、储值广告"}

   示例：
   用户说"创建一个弹窗广告，标题是'双十一大促'" → {"action":"create_banner","params":{"positionId":1,"headline":"双十一大促"}}
   用户说"创建一个广告，标题是'双十一大促'" → {"action":"chat","params":{},"message":"请问您想创建哪种类型的广告？如：弹窗广告、顶部轮播、园区介绍、物业服务、楼书展示、储值广告"}
"""


def build_system_prompt(token: str = None) -> str:
    """构建完整的系统 Prompt"""
    nav_prompt = build_navigation_prompt(token)
    action_prompt = build_action_prompt()

    return f"""
你是一个后台管理系统的AI操作助手。用户会告诉你想做什么。

【核心判断规则】
1. 如果用户明确说"去XX页面"、"跳转到XX"、"打开XX" → 使用 navigate
2. 如果用户说"创建广告"但没指定位置 → 追问广告类型（chat）
3. 如果用户说"弹窗广告"、"顶部轮播"等广告类型名称，且没有说"去/跳转/打开" → 视为 create_banner 的参数补充（positionId）
4. 如果用户只说了广告类型（如"弹窗广告"），但之前没有创建广告的上下文 → 优先视为 navigate 到对应页面（因为可能是想跳转）
   - 但如果有创建广告的上下文（比如上一轮 AI 追问了"请问您想创建哪种类型的广告？"），则视为 create_banner 的参数补充
   - 所以，当用户输入是单个广告类型名称时，你需要根据对话上下文判断：
     * 如果上一轮是追问广告类型 → 解析为 create_banner，positionId 映射
     * 如果上一轮不是追问 → 解析为 navigate

【上下文记忆规则】
- 用户可能在连续对话中逐步提供信息，你需要将当前输入与上一轮 AI 的回复关联起来
- 如果上一轮 AI 是追问（如"请问您想创建哪种类型的广告？"），那么本轮用户的回答（如"弹窗广告"）应视为对追问的补充

{nav_prompt}

{action_prompt}

【输出格式】

如果是闲聊/问候：
{{"action":"chat","params":{{}},"message":"你好！请问有什么可以帮您？"}}

如果是查看菜单结构：
{{"action":"show_menu","params":{{}},"message":"正在获取菜单结构..."}}

如果是可跳转页面：
{{"action":"navigate","params":{{"target":"路径"}},"message":"正在跳转到XX页面"}}

如果是目录页（不可跳转）：
{{"action":"navigate","params":{{"target":null}},"message":"XX是目录页，可跳转的子页面有：xxx"}}

如果是创建广告（有 positionId）：
{{"action":"create_banner","params":{{"positionId":1,"headline":"双十一大促"}}}}

如果是追问广告类型：
{{"action":"chat","params":{{}},"message":"请问您想创建哪种类型的广告？如：弹窗广告、顶部轮播、园区介绍、物业服务、楼书展示、储值广告"}}

只输出 JSON，不要其他文字。
"""
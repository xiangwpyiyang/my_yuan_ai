from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from schemas import CommandRequest, CommandResponse
from database import get_db
from models import CommandLog
from services import parse_with_deepseek_stream, get_handler
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ai/execute", response_model=CommandResponse)
async def execute_command(
        req: CommandRequest,
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    """非流式执行AI指令（支持对话历史）"""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    user_id = "system"

    log_entry = CommandLog(
        user_id=user_id,
        command=req.command,
        status="processing"
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    try:
        from services import parse_with_deepseek
        parsed = parse_with_deepseek(req.command, token, req.history)
        action = parsed.get("action")
        params = parsed.get("params", {})
        message = parsed.get("message", "")

        if not action:
            raise ValueError("AI 未能识别有效操作")

        log_entry.parsed_action = action
        log_entry.parsed_params = json.dumps(params, ensure_ascii=False)
        db.commit()

        handler = get_handler(action)
        result_data = await handler.execute(params, token, db)

        if not message:
            message = f"操作 {action} 执行成功"

        log_entry.status = "success"
        log_entry.java_response = json.dumps(result_data, ensure_ascii=False)
        db.commit()

        return CommandResponse(
            success=True,
            message=message,
            data=result_data,
            action=action
        )

    except Exception as e:
        log_entry.status = "fail"
        log_entry.error_msg = str(e)
        db.commit()
        logger.error(f"执行失败: {str(e)}")

        return CommandResponse(
            success=False,
            message=f"执行失败: {str(e)}",
            data=None,
            action=None
        )


@router.post("/ai/execute/stream")
async def execute_command_stream(
        req: CommandRequest,
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    """流式执行AI指令（支持对话历史）"""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    user_id = "system"

    log_entry = CommandLog(
        user_id=user_id,
        command=req.command,
        status="processing"
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'start', 'message': '开始解析指令...'})}\n\n"

            parsed = None
            async for chunk in parse_with_deepseek_stream(req.command, token, req.history):
                yield f"data: {json.dumps({'type': 'parsing', 'content': chunk})}\n\n"
                if chunk.startswith('{'):
                    try:
                        parsed = json.loads(chunk)
                    except:
                        pass

            if not parsed:
                raise ValueError("AI 未能识别有效操作")

            action = parsed.get("action")
            params = parsed.get("params", {})
            message = parsed.get("message", "")

            if not action:
                raise ValueError("AI 未能识别有效操作")

            log_entry.parsed_action = action
            log_entry.parsed_params = json.dumps(params, ensure_ascii=False)
            db.commit()

            yield f"data: {json.dumps({'type': 'executing', 'message': f'正在执行: {action}'})}\n\n"

            # 使用 handler 执行
            handler = get_handler(action)
            result_data = await handler.execute(params, token, db)

            # ================================================================
            # show_menu - 展示菜单结构（流式分块发送）
            # ================================================================
            if action == "show_menu":
                display_text = result_data.get("display", "获取菜单结构失败")

                log_entry.status = "success"
                log_entry.java_response = json.dumps(result_data.get("data", []), ensure_ascii=False)
                db.commit()

                # 分块发送菜单文本，模拟流式效果
                # 按行分割，逐行发送
                lines = display_text.split('\n')

                for i, line in enumerate(lines):
                    chunk = line + '\n' if i < len(lines) - 1 else line
                    yield f"data: {json.dumps({'type': 'parsing', 'content': chunk})}\n\n"
                    await asyncio.sleep(0.02)  # 20ms 延迟

                # 发送完成事件
                yield f"data: {json.dumps({'type': 'complete', 'success': True, 'message': display_text, 'data': result_data.get('data', []), 'action': action})}\n\n"
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                return

            # ================================================================
            # create_banner - 创建广告
            # ================================================================
            if action == "create_banner":
                if result_data.get("success"):
                    log_entry.status = "success"
                    log_entry.java_response = json.dumps(result_data.get("data", {}), ensure_ascii=False)
                    db.commit()

                    yield f"data: {json.dumps({'type': 'complete', 'success': True, 'message': result_data.get('message', '广告创建成功'), 'data': result_data.get('data', {}), 'action': action})}\n\n"
                else:
                    raise Exception(result_data.get("message", "创建广告失败"))
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                return

            # ================================================================
            # navigate - 页面导航
            # ================================================================
            if action == "navigate":
                target = result_data.get("target")
                if target:
                    message = f"准备跳转到 {target}"
                else:
                    message = result_data.get("message", "该页面是目录，无法直接跳转")

            # chat - 闲聊
            elif action == "chat":
                pass

            # 其他业务操作
            else:
                if not message:
                    message = f"操作 {action} 执行成功"

            log_entry.status = "success"
            log_entry.java_response = json.dumps(result_data, ensure_ascii=False)
            db.commit()

            yield f"data: {json.dumps({'type': 'complete', 'success': True, 'message': message, 'data': result_data, 'action': action})}\n\n"

        except Exception as e:
            log_entry.status = "fail"
            log_entry.error_msg = str(e)
            db.commit()
            logger.error(f"执行失败: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            yield f"data: {json.dumps({'type': 'end'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
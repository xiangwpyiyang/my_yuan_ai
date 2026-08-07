from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .base import BaseActionHandler
from ..java_caller import call_java_with_token


class ExportReportHandler(BaseActionHandler):
    """导出报表处理器"""

    def get_action_name(self) -> str:
        return "export_report"

    def get_prompt_description(self) -> str:
        return "导出报表"

    def get_prompt_params(self) -> str:
        return """参数：report_type（"sales"或"user"）, date_range（如"30d"）"""

    async def execute(self, params: Dict[str, Any], token: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        return call_java_with_token("export_report", params, token)
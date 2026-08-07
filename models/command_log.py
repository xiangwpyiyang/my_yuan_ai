from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base

class CommandLog(Base):
    __tablename__ = "command_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), nullable=True)
    command = Column(Text, nullable=False)
    parsed_action = Column(String(50), nullable=True)
    parsed_params = Column(Text, nullable=True)
    java_response = Column(Text, nullable=True)
    status = Column(String(20), default="success")
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
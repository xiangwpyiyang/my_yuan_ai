from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router
from database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created.")

app = FastAPI(
    title="AI操作中转服务",
    description="接收自然语言指令，解析后调用Java接口",
    version="1.0.0"
)

# CORS（开发环境全开放）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://bohua.cjtzn.com",
        "http://localhost:3000",       # Vue 开发环境
        "http://localhost:3001",       # Vue 开发环境（备用端口）
        "http://127.0.0.1:3000",       # localhost 别名
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
def startup():
    create_tables()

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ai-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
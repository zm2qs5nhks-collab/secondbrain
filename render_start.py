"""
Render 部署入口 —— uvicorn 启动 FastAPI
"""
import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

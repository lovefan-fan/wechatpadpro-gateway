from fastapi import FastAPI, Request, HTTPException, Header
import httpx
from pydantic_settings import BaseSettings

app = FastAPI()

# 配置类（支持从环境变量读取，推荐在docker-compose.yml中通过environment设置）
class Settings(BaseSettings):
    WECHATPADPRO_DOMAIN: str
    WECHATPADPRO_KEY: str
    API_TOKEN: str

    class Config:
        env_file = ".env"  # 可选，支持本地开发

settings = Settings()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def universal_proxy(request: Request, path: str, authorization: str = Header(None)):
    if authorization != f"Bearer {settings.API_TOKEN}":
        raise HTTPException(status_code=401, detail="无效的Token")
    # 动态拼接目标 URL（保留原始路径和查询参数）
    target_url = f"{settings.WECHATPADPRO_DOMAIN}/{path}?key={settings.WECHATPADPRO_KEY}"
    
    # 转发所有请求头和 Body
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                request.method,
                target_url,
                headers=dict(request.headers),
                content=await request.body()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"转发失败: {e.response.text}"
            )
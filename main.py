from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import Response
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
    
    # 准备转发的请求头，移除本代理使用的 Authorization，避免干扰上游服务
    forward_headers = dict(request.headers)
    forward_headers.pop("authorization", None)

    # 转发请求
    async with httpx.AsyncClient() as client:
        try:
            # 发起请求到目标服务
            response = await client.request(
                request.method,
                target_url,
                headers=forward_headers,
                content=await request.body()
            )
            
            # 直接将上游服务的响应内容、状态码和头信息返回给客户端
            # 避免假设响应一定是JSON格式，增强了健壮性
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.HTTPStatusError as e:
            # 处理上游服务返回的 HTTP 错误状态码
            return Response(
                content=e.response.content,
                status_code=e.response.status_code,
                headers=dict(e.response.headers)
            )
        except httpx.RequestError as e:
            # 处理网络请求层面的异常（如DNS解析、连接超时等）
            raise HTTPException(
                status_code=502, # Bad Gateway
                detail=f"上游服务请求失败: {str(e)}"
            )
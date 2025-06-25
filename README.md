# WechatPadPro Gateway

## 快速开始（Docker Compose）

1. 修改 `docker-compose.yml` 中的 `WECHATPADPRO_DOMAIN` 和 `WECHATPADPRO_KEY` 环境变量。
2. 构建并启动服务：

```bash
docker-compose up --build
```

服务将会在 `8000` 端口启动。

## 本地开发

1. 复制 `.env.example` 为 `.env`，并根据需要修改变量：

```bash
cp .env.example .env
```

2. 安装依赖并运行：

```bash
pip install -r requirements.txt
uvicorn main:app --reload
``` 
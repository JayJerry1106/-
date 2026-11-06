"""路路通ai助手 — 单端口 HTTP 服务入口（本地与云部署共用）。

直接复用原项目的应用工厂 ``trade.app.create_app()`` 与 ``serve_trade_chat()``，
不改动任何业务路由、页面或交互行为。相较 ``python server.py`` 仅补充三件事：

1. 监听 ``PORT`` 环境变量并绑定 ``0.0.0.0``（云部署沙箱的硬性要求）；
2. 启用原项目自带的 ``TRADE_ALLOW_REMOTE_UI`` 配置项，使反向代理后的浏览器
   能够取得会话凭据（原项目在 0.0.0.0 场景下本就提供此开关）；
3. ``/`` 跳转到 ``/trade``，并增加 ``/guide`` 与 ``/docs/`` 呈现原有安装教程页
   （``/docs`` 是原项目自带的 Swagger API 文档，保持不动）。

原有入口 ``python server.py`` / ``trade`` 命令仍完整保留，行为不变。
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import uvicorn
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / ".runtime"

# 沙箱若把项目目录挂为只读，回退到系统临时目录，保证服务仍能启动。
try:
    RUNTIME.mkdir(parents=True, exist_ok=True)
except OSError:
    import tempfile

    RUNTIME = Path(tempfile.gettempdir()) / "lulutong-runtime"
    RUNTIME.mkdir(parents=True, exist_ok=True)

# 必须在导入 trade.app 之前设置：数据库路径与远程凭据开关都在模块加载时读取。
os.environ.setdefault("TRADE_HOME", str(RUNTIME))
os.environ.setdefault("TRADE_ALLOW_REMOTE_UI", "1")

from trade.app import _install_cors, create_app, serve_trade_chat  # noqa: E402

PORT = int(os.environ.get("PORT", "9119"))

app = create_app()
serve_trade_chat(app)
_install_cors(app, PORT)

# 原有 docs/ 教程页的图片等静态资源（GitHub Pages 素材）
_DOCS_DIR = ROOT / "docs"
if _DOCS_DIR.is_dir():
    app.mount("/docs-assets", StaticFiles(directory=str(_DOCS_DIR)), name="docs-assets")


@app.get("/", include_in_schema=False)
async def root_redirect():
    """根路径直达原项目的 SPA 入口。"""
    return RedirectResponse(url="/trade", status_code=302)


@app.get("/guide", include_in_schema=False, response_class=HTMLResponse)
@app.get("/docs/", include_in_schema=False, response_class=HTMLResponse)
async def docs_page():
    """用项目自带的 marked 渲染原 docs/index.md 安装教程页。"""
    md_file = _DOCS_DIR / "index.md"
    if not md_file.is_file():
        return HTMLResponse("<h1>路路通ai助手</h1><p>安装教程页缺失。</p>", status_code=404)

    md = md_file.read_text(encoding="utf-8")
    if md.startswith("---"):
        chunks = md.split("---", 2)
        if len(chunks) == 3:
            md = chunks[2]

    # 教程页中的相对图片路径改指向挂载的 /docs-assets
    md = re.sub(
        r"!\[([^\]]*)\]\((?!https?://|/)([^)]+)\)",
        r"![\1](/docs-assets/\2)",
        md,
    )
    md = re.sub(
        r'src="(?!https?://|/)([^"\s]+\.(?:png|jpe?g|svg|gif))"',
        r'src="/docs-assets/\1"',
        md,
    )

    payload = json.dumps(md, ensure_ascii=False)
    return HTMLResponse(
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>路路通ai助手 — 安装教程</title>"
        "<style>body{margin:0;background:#fff;color:#24292f;font-family:-apple-system,"
        "BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;line-height:1.7}"
        "#content{max-width:960px;margin:0 auto;padding:2rem 1.5rem 5rem}"
        "img{max-width:100%}pre{background:#f6f8fa;padding:1rem;overflow:auto;border-radius:6px}"
        "code{background:#f6f8fa;padding:.15em .35em;border-radius:4px}"
        "pre code{background:none;padding:0}table{border-collapse:collapse;width:100%}"
        "th,td{border:1px solid #d0d7de;padding:.5rem}a{color:#2563EB}</style>"
        "</head><body><div id=\"content\"></div>"
        "<script src=\"/static/vendor/marked.umd.js\"></script>"
        f"<script>document.getElementById('content').innerHTML = marked.parse({payload});</script>"
        "</body></html>"
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")

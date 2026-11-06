"""
路路通ai助手 — API 依赖函数。

提供 session token 校验和 company_id 解析的共享依赖，
被所有 /api/trade/* 路由使用。
"""

from __future__ import annotations

import secrets
import threading

from fastapi import Header, HTTPException, Request

from trade import company as company_module

# ── Session token ────────────────────────────────────────────────────────────

# 由 server.py 在启动时设置
_SESSION_TOKEN: str = ""

# session → 绑定的活跃公司 ID（单用户场景下防止修改 header 跨公司越权）
_ACTIVE_COMPANY: dict[str, int] = {}
_company_bind_lock = threading.Lock()


def set_session_token(token: str) -> None:
    """设置当前会话的 token（server.py 启动时调用）。"""
    global _SESSION_TOKEN
    _SESSION_TOKEN = token


def set_active_company(token: str, company_id: int) -> None:
    """绑定 session token 到指定公司（前端切换公司时调用）。"""
    with _company_bind_lock:
        _ACTIVE_COMPANY[token] = company_id


def require_session(request: Request) -> None:
    """校验 X-Hermes-Session-Token。

    所有 /api/trade/* 路由共享此依赖，确保只有持有 token 的
    本机浏览器会话可以访问 API。

    Raises:
        HTTPException(401): token 缺失或不匹配
    """
    token = request.headers.get("X-Hermes-Session-Token", "")
    if not _SESSION_TOKEN:
        # 未初始化（不应发生，防御性编程）
        raise HTTPException(status_code=500, detail="Server not initialized.")
    if not token or not secrets.compare_digest(token, _SESSION_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid or missing session token.")


# ── Company ID ────────────────────────────────────────────────────────────────

def require_company(
    x_company_id: str | None = Header(None, alias="X-Company-ID"),
) -> int:
    """解析并验证 X-Company-ID header，返回 company_id。

    session 级别的活跃公司绑定在路由层通过 _check_company_binding() 完成。

    Raises:
        HTTPException(401): header 缺失、无效、或公司不存在/未激活
    """
    cid_str = x_company_id if isinstance(x_company_id, str) else ""
    if not cid_str or not cid_str.strip():
        raise HTTPException(
            status_code=401,
            detail="X-Company-ID header is required. "
                   "Call GET /api/trade/companies first to get your company IDs.",
        )
    try:
        cid = int(cid_str.strip())
    except ValueError as e:
        raise HTTPException(status_code=401, detail="X-Company-ID must be an integer.") from e

    # 验证公司存在且激活
    tc = company_module.get_trade_company(cid)
    if not tc:
        raise HTTPException(status_code=401, detail=f"Company {cid} not found in Trade system.")
    if not tc.get("is_active"):
        raise HTTPException(status_code=401, detail=f"Company {cid} is inactive.")

    return cid


def opt_company(
    x_company_id: str | None = Header(None, alias="X-Company-ID"),
) -> int | None:
    """解析 X-Company-ID header，返回 company_id 或 None。

    与 require_company 的区别：header 缺失时不抛异常。
    仅用于不涉及公司数据隔离的非敏感端点（如 /memory/status）。

    Raises:
        HTTPException(401): header 存在但无法解析为整数
    """
    if not x_company_id or not x_company_id.strip():
        return None
    try:
        return int(x_company_id.strip())
    except ValueError as e:
        raise HTTPException(status_code=401, detail="X-Company-ID must be an integer.") from e

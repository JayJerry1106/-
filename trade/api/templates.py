"""
路路通ai助手 — 管理表格模板 API。

生成并下载 10 张结构化 Excel 管理表格（选品策略/客户画像/市场分析/...）。
"""

from __future__ import annotations

import io
import logging

from fastapi import APIRouter, Depends

from trade.api.deps import require_company
from trade.database import get_connection
from trade.templates import generate_templates

logger = logging.getLogger(__name__)
router = APIRouter(tags=["templates"])


@router.get("/templates/download")
def download_templates(
    x_company_id: int = Depends(require_company),
):
    """下载完整的管理表格 Excel（10 张工作表）。"""
    wb = generate_templates()

    # 尝试预填充管线客户名（限定当前公司）
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, name FROM customers WHERE company_id = ? ORDER BY id DESC LIMIT 100",
            (x_company_id,),
        ).fetchall()
        ws = wb["7-管线看板"]
        for i, r in enumerate(rows):
            row_num = 4 + i
            ws.cell(row=row_num, column=1, value=r["name"])
    except Exception as e:
        logger.debug("Failed to pre-fill pipeline sheet: %s", e)
    finally:
        conn.close()

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=trade-management-tables.xlsx",
            "Content-Length": str(len(output.getvalue())),
        },
    )

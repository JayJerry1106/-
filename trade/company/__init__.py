"""
路路通ai助手 — 公司数据层。

三模块结构：
  - crud: companies + trade_companies 表的增删改查 + 审计日志
  - workdir: 桌面工作目录管理 + .trade-template 模板复制

从 trade.company import xxx 的方式保持不变，所有公开 API 通过本 __init__ 重导出。
"""

# 从 crud 模块导出所有公开的数据库操作函数
from trade.company.crud import (
    TRADE_HOME,
    _db_get_one,
    _row_to_company,
    _row_to_tc,
    _write_audit_log,
    create,
    delete,
    get,
    get_agent_identity,
    get_by_slug,
    get_trade_company,
    list_all,
    purge,
    slug_from_id,
    update,
    update_trade_company,
)

# 从 workdir 模块导出工作目录管理的公开函数和常量
from trade.company.workdir import (
    _WORK_DIR_CATEGORIES,
    _ensure_data_dir,
    _register_work_libraries,
    _setup_work_directory,
    _slugify,
    _validate_slug,
)

# __all__ 明确列出所有公开 API（IDE 自动补全 / import * 的边界）
__all__ = [
    # 数据目录常量
    "TRADE_HOME",
    # companies 表 CRUD
    "create",
    "get",
    "get_by_slug",
    "slug_from_id",
    "list_all",
    "update",
    "delete",
    "purge",
    # trade_companies 表 CRUD
    "get_trade_company",
    "update_trade_company",
    "get_agent_identity",
    # 工作目录管理
    "_WORK_DIR_CATEGORIES",
    "_setup_work_directory",
    # 工具函数（供内部使用）
    "_slugify",
    "_validate_slug",
    "_ensure_data_dir",
]

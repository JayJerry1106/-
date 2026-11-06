"""
路路通ai助手 — Post-install 工具包。

四模块结构：
  - skills: B2B skill 安装/更新 + 模板复制
  - update: 一键系统更新 (trade-update)
  - backup: 系统数据备份/还原 (trade-backup / trade-restore)
  - __init__: CLI 入口 + 重导出

从 trade.post_install import xxx 保持向后兼容。
"""

from trade.post_install.backup import backup_trade, restore_trade
from trade.post_install.skills import install_skills, update_skills
from trade.post_install.update import update_trade

__all__ = [
    "install_skills",
    "update_skills",
    "update_trade",
    "backup_trade",
    "restore_trade",
]


# ── CLI 入口 ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Trade Skills Manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("install", help="Install skills from local package")
    sub.add_parser("update", help="Update skills from GitHub")
    p_up = sub.add_parser("update-trade", help="Update entire Trade system")
    p_backup = sub.add_parser("backup", help="Backup Trade data")
    p_backup.add_argument(
        "--output", "-o", default=None, help="Output directory (default: Desktop)"
    )

    args = parser.parse_args()
    if args.command == "update":
        update_skills()  # 从 GitHub 更新 skills
    elif args.command == "update-trade":
        update_trade()  # 一键更新整个 Trade 系统
    elif args.command == "backup":
        backup_trade(args.output)  # 备份 Trade 数据到 tar.gz
    else:
        install_skills()  # 默认：从本地包安装 skills

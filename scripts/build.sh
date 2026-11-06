#!/bin/bash
# ==============================================================================
# 路路通ai助手 — 构建打包脚本（macOS）
# ==============================================================================
# 使用 PyInstaller 打包为独立可执行文件。
#
# macOS: 生成 .app 应用包
#   ./scripts/build.sh
#
# 前置要求:
#   pip install pyinstaller
#   pip install -e .
# ==============================================================================

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "════════════════════════════════════════"
echo "  路路通ai助手 — Build"
echo "════════════════════════════════════════"
echo ""

# ── Check PyInstaller ──
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "→ 安装 PyInstaller..."
    pip install pyinstaller --quiet
fi

# ── Clean previous builds ──
echo "→ 清理旧构建..."
rm -rf build dist *.spec.bak

# ── Build ──
echo "→ 开始打包..."
python -m PyInstaller tradewin-mac.spec --noconfirm --clean 2>&1 | tail -10

# ── Verify ──
if [ -d "dist/TradeWin.app" ]; then
    APP_SIZE=$(du -sh "dist/TradeWin.app" | cut -f1)
    echo ""
    echo "══ 构建完成 ══"
    echo "  位置: $ROOT/dist/TradeWin.app"
    echo "  大小: $APP_SIZE"
    echo ""
    echo "  双击 TradeWin.app 启动"
else
    echo "✗ 构建失败，请检查上方错误信息"
    exit 1
fi

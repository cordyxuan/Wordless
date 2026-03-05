#!/bin/bash
echo "========================================"
echo " 单词闪卡 - 打包为 macOS App"
echo "========================================"
echo

# 检查 Python
if ! command -v python3 &>/dev/null; then
    echo "[错误] 未找到 python3，请先安装 Python 3.8+"
    echo "推荐用 Homebrew 安装: brew install python"
    exit 1
fi

# 安装 PyInstaller
echo "[1/3] 安装 PyInstaller..."
pip3 install pyinstaller --quiet
if [ $? -ne 0 ]; then
    echo "[错误] PyInstaller 安装失败，请检查网络或尝试: pip3 install pyinstaller"
    exit 1
fi

# 打包
echo "[2/3] 打包中，请稍候..."
pyinstaller \
    --onefile \
    --windowed \
    --name "单词闪卡" \
    --add-data "flashcard_words_sample.csv:." \
    --add-data "wordlists:wordlists" \
    flashcard.py

if [ $? -ne 0 ]; then
    echo "[错误] 打包失败"
    exit 1
fi

echo "[3/3] 打包完成！"
echo
echo "App 位于: dist/单词闪卡"
echo "（macOS 生成的是单个可执行文件，双击即可运行）"
echo
read -p "是否立即打开 dist 文件夹？(y/n): " ans
if [ "$ans" = "y" ]; then
    open dist
fi

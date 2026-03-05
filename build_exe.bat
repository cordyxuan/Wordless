@echo off
chcp 65001 >nul
echo ========================================
echo  单词闪卡 - 打包为 EXE
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装 PyInstaller
echo [1/3] 安装 PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo [错误] PyInstaller 安装失败，请检查网络连接
    pause
    exit /b 1
)

:: 打包
echo [2/3] 打包中，请稍候...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "单词闪卡" ^
    --add-data "flashcard_words_sample.csv;." ^
    flashcard.py

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

:: 完成
echo [3/3] 打包完成！
echo.
echo EXE 文件位于: dist\单词闪卡.exe
echo.
echo 是否立即打开 dist 文件夹？
set /p open="输入 y 打开，其他键退出: "
if /i "%open%"=="y" explorer dist

pause

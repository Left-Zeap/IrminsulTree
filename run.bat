@echo off
chcp 65001 >nul
echo ==========================================
echo   原神知识图谱管理系统
echo   Genshin Knowledge Graph
echo ==========================================
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 检查 Python 是否安装
echo [1/3] 检查 Python 安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python！
    echo.
    echo 请按以下步骤安装 Python：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 点击 "Download Python 3.11.x"
    echo 3. 安装时勾选 "Add Python to PATH"
    echo 4. 安装完成后重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo [OK] Python 已安装
python --version
echo.

:: 检查依赖是否安装
echo [2/3] 检查程序依赖...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [提示] 首次运行，正在安装依赖...
    echo 这可能需要 1-2 分钟，请耐心等待...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败！
        echo 请检查网络连接，或手动运行：pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo [OK] 依赖安装完成
) else (
    echo [OK] 依赖已安装
)
echo.

:: 启动程序
echo [3/3] 启动程序...
echo 正在启动，请稍候...
echo 浏览器将自动打开，如果没有自动打开，请手动访问 http://localhost:8501
echo.
echo ==========================================
echo 按 Ctrl+C 可以停止程序
echo ==========================================
echo.

:: 使用 python -m 方式运行更可靠
python -m streamlit run app.py --server.headless true

:: 如果上面的命令失败，尝试备用方式
if errorlevel 1 (
    echo.
    echo [备用方式] 尝试直接启动...
    streamlit run app.py --server.headless true
)

:: 如果都失败了
if errorlevel 1 (
    echo.
    echo [错误] 启动失败！
    echo 请尝试以下方法：
    echo 1. 重启电脑后再试
    echo 2. 重新安装 Python，确保勾选 "Add to PATH"
    echo 3. 手动运行：python -m streamlit run app.py
    pause
)

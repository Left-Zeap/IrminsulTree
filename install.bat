@echo off
chcp 65001 >nul
echo ==========================================
echo   原神知识图谱 - 安装向导
echo ==========================================
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"

echo [步骤 1/2] 检查 Python 安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [X] 未检测到 Python！
    echo.
    echo 请先安装 Python：
    echo 1. 浏览器访问 https://www.python.org/downloads/
    echo 2. 点击 "Download Python 3.11.x"
    echo 3. 运行下载的安装程序
    echo 4. 【重要】勾选 "Add Python to PATH"
    echo 5. 点击 Install Now
    echo 6. 安装完成后，重新运行此脚本
    echo.
    echo 按任意键打开下载页面...
    pause >nul
    start https://www.python.org/downloads/
    exit /b 1
)

echo [OK] Python 已安装
python --version
echo.

echo [步骤 2/2] 安装程序依赖...
echo 正在下载和安装必要的组件...
echo 这可能需要 1-3 分钟，请耐心等待...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [X] 安装失败！
    echo 可能的原因：
    echo 1. 网络连接问题
    echo 2. pip 需要更新
    echo.
    echo 请尝试以下方法：
    echo 1. 检查网络连接
    echo 2. 运行: python -m pip install --upgrade pip
    echo 3. 重新运行此脚本
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [OK] 安装完成！
echo ==========================================
echo.
echo 现在可以运行程序了：
echo 方法 1：双击 run.bat
echo 方法 2：运行命令: python -m streamlit run app.py
echo.
echo 程序启动后，浏览器会自动打开
echo 如果没有自动打开，请访问: http://localhost:8501
echo.
pause

# 原神知识图谱管理系统启动脚本（PowerShell 版本）
# 如果 run.bat 无法运行，尝试使用这个脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  原神知识图谱管理系统" -ForegroundColor Cyan
Write-Host "  Genshin Knowledge Graph" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 检查 Python
Write-Host "[1/3] 检查 Python 安装..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python 已安装: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未检测到 Python！" -ForegroundColor Red
    Write-Host ""
    Write-Host "请按以下步骤安装 Python：" -ForegroundColor Yellow
    Write-Host "1. 访问 https://www.python.org/downloads/"
    Write-Host "2. 点击 'Download Python 3.11.x'"
    Write-Host "3. 安装时勾选 'Add Python to PATH'"
    Write-Host "4. 安装完成后重新运行此脚本"
    Write-Host ""
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""

# 检查依赖
Write-Host "[2/3] 检查程序依赖..." -ForegroundColor Yellow
try {
    python -c "import streamlit" 2>&1 | Out-Null
    Write-Host "[OK] 依赖已安装" -ForegroundColor Green
} catch {
    Write-Host "[提示] 首次运行，正在安装依赖..." -ForegroundColor Yellow
    Write-Host "这可能需要 1-2 分钟，请耐心等待..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        pip install -r requirements.txt
        Write-Host "[OK] 依赖安装完成" -ForegroundColor Green
    } catch {
        Write-Host "[错误] 依赖安装失败！" -ForegroundColor Red
        Write-Host "请检查网络连接，或手动运行: pip install -r requirements.txt" -ForegroundColor Yellow
        Read-Host "按回车键退出"
        exit 1
    }
}

Write-Host ""

# 启动程序
Write-Host "[3/3] 启动程序..." -ForegroundColor Yellow
Write-Host "正在启动，请稍候..." -ForegroundColor Yellow
Write-Host "浏览器将自动打开，如果没有自动打开，请手动访问 http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 可以停止程序" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

try {
    python -m streamlit run app.py --server.headless true
} catch {
    Write-Host ""
    Write-Host "[错误] 启动失败！" -ForegroundColor Red
    Write-Host "请尝试以下方法：" -ForegroundColor Yellow
    Write-Host "1. 重启电脑后再试"
    Write-Host "2. 重新安装 Python，确保勾选 'Add to PATH'"
    Write-Host "3. 手动运行: python -m streamlit run app.py"
    Read-Host "按回车键退出"
}

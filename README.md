# 原神知识图谱管理系统

一个可视化的原神世界观知识图谱管理工具，无需编程基础即可使用。

## 我能用这个做什么？

- 📝 **记录角色信息**：人物、事件、地点、任务等
- 🔗 **建立关系**：角色之间的关系、事件参与等
- 🕸️ **可视化展示**：自动生成关系图谱
- 💾 **数据管理**：导入导出，备份恢复

## 快速开始（3分钟上手）

### 第一步：安装 Python

**如果你已经安装过 Python，直接跳到第二步**

1. 打开浏览器，访问：https://www.python.org/downloads/
2. 点击大大的黄色按钮 **"Download Python 3.11.x"**
3. 下载完成后，**双击运行安装程序**
4. **重要！** 安装界面底部有个 "Add Python to PATH"，**一定要勾选！**
5. 点击 "Install Now" 等待安装完成
6. 安装完成后点击 "Close"

**验证安装成功：**
- 按键盘 `Win + R`，输入 `cmd`，回车
- 在黑色窗口中输入 `python --version`
- 如果显示 `Python 3.11.x` 说明成功

### 第二步：下载本程序

**方法一：直接下载（推荐）**

1. 访问：https://github.com/Left-Zeap/IrminsulTree
2. 点击绿色的 **"<> Code"** 按钮
3. 点击 **"Download ZIP"**
4. 下载完成后，**解压 ZIP 文件**
5. 记住解压后的文件夹位置（例如：`D:\IrminsulTree\standalone_app`）

**方法二：使用 Git（如果你已安装 Git）**

```bash
git clone https://github.com/Left-Zeap/IrminsulTree.git
```

### 第三步：安装程序依赖

1. 按键盘 `Win + R`，输入 `cmd`，回车
2. 在黑色窗口中，输入以下命令（**一行一行输入，每行回车**）：

```bash
cd D:\IrminsulTree\standalone_app
```

**注意**：把 `D:\IrminsulTree\standalone_app` 换成你实际的文件夹路径

3. 继续输入：

```bash
pip install -r requirements.txt
```

4. 等待安装完成（会看到进度条，可能需要 1-2 分钟）

### 第四步：运行程序

**方法一：双击运行（最简单）**

1. 打开文件夹 `standalone_app`
2. **双击 `run.bat` 文件**
3. 等待几秒，浏览器会自动打开网页

**方法二：命令行运行**

如果双击 `run.bat` 不行，用这个方法：

1. 按键盘 `Win + R`，输入 `cmd`，回车
2. 输入：

```bash
cd D:\IrminsulTree\standalone_app
python -m streamlit run app.py
```

3. 等待几秒，看到类似这样的信息：

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

4. **按住 Ctrl 键，点击 `http://localhost:8501` 这个链接**
5. 或者手动打开浏览器，输入 `http://localhost:8501`

## 常见问题

### 问题 1：提示 "'python' 不是内部或外部命令"

**原因**：Python 没有正确安装，或者没有添加到 PATH

**解决**：
1. 重新安装 Python
2. **一定要勾选** "Add Python to PATH"
3. 安装完成后，**重启电脑**，再试

### 问题 2：提示 "'streamlit' 不是内部或外部命令"

**原因**：依赖没有安装成功

**解决**：
1. 打开命令行（`Win + R`，输入 `cmd`）
2. 输入：

```bash
pip install streamlit pandas pydantic python-dotenv
```

3. 等待安装完成
4. 再运行程序

### 问题 3：双击 run.bat 闪一下就没了

**解决**：
1. 右键点击 `run.bat` → **编辑**
2. 把内容改成：

```bat
@echo off
echo Starting Genshin Knowledge Graph (Standalone)...
cd /d "%~dp0"
python -m streamlit run app.py
pause
```

3. 保存，再双击运行

### 问题 4：提示端口被占用

**解决**：
1. 打开命令行
2. 输入：

```bash
cd D:\IrminsulTree\standalone_app
python -m streamlit run app.py --server.port 8502
```

3. 使用 `8502` 或其他端口号

### 问题 5：网页打开了但显示错误

**解决**：
1. 检查是否按照步骤三安装了依赖
2. 尝试刷新网页（按 F5）
3. 如果还是不行，关闭命令行窗口，重新运行

## 使用指南

### 添加第一个节点

1. 在左侧菜单点击 **"➕ 添加节点"**
2. 选择节点类型（例如：👤 人物）
3. 填写名称（例如："钟离"）
4. 填写其他信息（可选）
5. 点击 **"✅ 创建节点"**

### 添加关系

1. 点击 **"🔗 添加关系"**
2. 选择 **"单个添加"** 或 **"批量添加"**
3. 搜索并选择源节点和目标节点
4. 选择关系类型
5. 点击 **"✅ 创建关系"**

### 查看可视化

1. 点击 **"🕸️ 可视化"**
2. 选择 **"完整图谱"** 或 **"子图"**
3. 等待加载，即可看到关系图

### 保存数据

数据会自动保存在 `data` 文件夹中，无需手动操作。

**备份数据**：
1. 点击 **"💾 数据管理"**
2. 点击 **"📤 导出数据"**
3. 下载 JSON 文件保存到安全位置

**恢复数据**：
1. 点击 **"💾 数据管理"**
2. 在 **"📥 导入数据"** 处选择之前下载的 JSON 文件
3. 点击 **"确认导入"**

## 项目结构

```
standalone_app/
├── app.py              # 主程序（不要修改）
├── run.bat             # 运行脚本（双击即可）
├── requirements.txt    # 依赖列表
├── config.py           # 配置文件
├── core/               # 核心代码（不要修改）
│   ├── models.py
│   ├── storage.py
│   └── visualizer.py
└── data/               # 数据文件夹（自动创建）
    ├── graph_data.json    # 主数据文件
    └── backups/           # 备份文件夹
```

## 更新程序

如果后续有更新：

1. 备份你的数据（导出 JSON）
2. 下载最新版本的代码
3. 替换旧文件（保留 `data` 文件夹）
4. 重新运行程序

## 需要帮助？

如果遇到问题：

1. 查看上面的 **常见问题** 部分
2. 在 GitHub 上提交 Issue：https://github.com/Left-Zeap/IrminsulTree/issues
3. 描述清楚问题，最好附上截图

## 免责声明

本项目为原神同人作品，仅供学习交流使用。原神相关内容的版权归 miHoYo/HoYoverse 所有。

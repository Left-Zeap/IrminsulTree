# 故障排除指南

如果程序无法运行，请按顺序尝试以下方法。

## 问题 1：双击 run.bat 后闪退

### 检查方法

1. 右键点击 `run.bat` → **编辑**
2. 在文件最后一行添加：`pause`
3. 保存，再次双击运行
4. 查看黑色窗口中的错误信息

### 常见错误

**错误：'python' 不是内部或外部命令**

解决方法：
1. 重新安装 Python
2. **必须勾选** "Add Python to PATH"
3. 安装完成后**重启电脑**
4. 再试

**错误：'streamlit' 不是内部或外部命令**

解决方法：
1. 双击运行 `install.bat`
2. 等待安装完成
3. 再运行 `run.bat`

---

## 问题 2：提示 pip 不是内部命令

解决方法：

```bash
python -m ensurepip --default-pip
python -m pip install --upgrade pip
```

然后再运行 `install.bat`

---

## 问题 3：安装依赖时网络错误

**症状**：提示 "Connection timeout" 或 "Could not find a version"

解决方法（使用国内镜像源）：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 问题 4：端口被占用

**症状**：提示 "Port 8501 is already in use"

解决方法：

1. 打开 `run.bat`
2. 找到最后一行
3. 把 `8501` 改成其他数字，例如 `8502`：

```bat
python -m streamlit run app.py --server.port 8502
```

4. 保存后再运行
5. 浏览器访问 `http://localhost:8502`

---

## 问题 5：网页打开但显示错误

**症状**：网页显示 "Please wait..." 或报错

解决方法：

1. 按 `Ctrl + Shift + R` 强制刷新网页
2. 如果不行，关闭命令行窗口，重新运行 `run.bat`
3. 如果还是不行，删除 `data` 文件夹（注意：这会删除所有数据！），然后重新运行

---

## 问题 6：杀毒软件拦截

**症状**：双击 run.bat 后没有任何反应，或杀毒软件提示风险

解决方法：

1. 暂时关闭杀毒软件
2. 或将本程序文件夹添加到杀毒软件白名单
3. 本程序是开源的，没有病毒，可以放心使用

---

## 终极解决方案

如果以上方法都不行，请按以下步骤操作：

### 步骤 1：完全卸载 Python

1. 打开 "控制面板" → "程序和功能"
2. 找到所有 Python 相关的程序
3. 全部卸载

### 步骤 2：重新安装 Python

1. 访问 https://www.python.org/downloads/
2. 点击 "Download Python 3.11.x"
3. **运行安装程序**
4. **勾选 "Add Python to PATH"（非常重要！）**
5. 点击 "Install Now"
6. 安装完成后，**重启电脑**

### 步骤 3：验证安装

1. 按 `Win + R`，输入 `cmd`，回车
2. 输入 `python --version`，应该显示版本号
3. 输入 `pip --version`，应该显示版本号

### 步骤 4：重新安装程序

1. 删除原来的程序文件夹
2. 重新下载本程序
3. 双击 `install.bat`
4. 等待安装完成
5. 双击 `run.bat`

---

## 还是无法解决？

请在 GitHub 提交 Issue：

https://github.com/Left-Zeap/IrminsulTree/issues

请提供以下信息：
1. 你的操作系统版本（例如：Windows 10 家庭版）
2. Python 版本（运行 `python --version` 的结果）
3. 具体的错误信息（截图或复制文字）
4. 你已经尝试过的解决方法

# 部署和协作指南

## 方案一：Streamlit Cloud（推荐，免费且简单）

### 1. 准备 GitHub 仓库

```bash
# 在 standalone_app 目录下初始化 git
cd standalone_app
git init

# 添加文件
git add .
git commit -m "Initial commit"

# 创建 GitHub 仓库并推送
git remote add origin https://github.com/yourusername/genshin-knowledge-graph.git
git push -u origin main
```

### 2. 部署到 Streamlit Cloud

1. 访问 https://streamlit.io/cloud
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 选择仓库和分支
5. 主文件路径填写：`standalone_app/app.py`
6. 点击 Deploy

### 3. 数据持久化（重要）

Streamlit Cloud 会定期重置文件系统，因此需要：

**方案 A：使用云存储（推荐）**

创建 `storage.py` 的云存储版本，使用：
- AWS S3
- Google Cloud Storage
- 阿里云 OSS

**方案 B：定期备份到 GitHub**

创建 GitHub Action 定期备份数据：

```yaml
# .github/workflows/backup.yml
name: Backup Data

on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时备份一次

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Backup data
        run: |
          # 备份逻辑
          git add data/
          git commit -m "Auto backup $(date)"
          git push
```

## 方案二：私有服务器部署

### 使用 Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

创建 `docker-compose.yml`：

```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

运行：

```bash
docker-compose up -d
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 方案三：数据同步策略（多人协作关键）

### 问题

默认情况下，数据存储在本地 JSON 文件，多人协作时会出现数据冲突。

### 解决方案

#### 方案 A：中央服务器 + 实时同步

1. 部署一个中央服务器（使用方案二）
2. 所有团队成员访问同一个地址
3. 数据统一存储在服务器上

**优点：**
- 数据实时同步
- 无需本地安装
- 权限控制方便

**缺点：**
- 需要服务器成本
- 离线无法使用

#### 方案 B：Git + 数据合并

1. 数据文件也提交到 Git（修改 .gitignore）
2. 使用 Git 合并策略处理冲突

创建 `.gitattributes`：

```
data/*.json merge=json-merge
```

创建合并脚本 `merge_data.py`：

```python
"""合并数据文件"""
import json

def merge_data(ours_file, theirs_file, base_file, output_file):
    with open(ours_file) as f:
        ours = json.load(f)
    with open(theirs_file) as f:
        theirs = json.load(f)
    
    # 合并节点（以 ID 为键）
    nodes_map = {n['id']: n for n in ours.get('nodes', [])}
    for node in theirs.get('nodes', []):
        if node['id'] not in nodes_map:
            nodes_map[node['id']] = node
    
    # 合并边
    edges_map = {e['id']: e for e in ours.get('edges', [])}
    for edge in theirs.get('edges', []):
        if edge['id'] not in edges_map:
            edges_map[edge['id']] = edge
    
    result = {
        'nodes': list(nodes_map.values()),
        'edges': list(edges_map.values())
    }
    
    with open(output_file, 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    import sys
    merge_data(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
```

**优点：**
- 免费
- 有完整历史记录

**缺点：**
- 需要手动解决冲突
- 不能同时编辑

#### 方案 C：使用真正的数据库（推荐长期方案）

将存储层改为使用 PostgreSQL + Neo4j：

```python
# 在 storage.py 中添加数据库支持
import os

USE_DATABASE = os.getenv('USE_DATABASE', 'false').lower() == 'true'

if USE_DATABASE:
    from neo4j import GraphDatabase
    # ... 使用 Neo4j 实现
else:
    # ... 保持现有 JSON 实现
```

## 推荐的协作流程

### 分支策略

```
main         - 生产分支，稳定版本
dev          - 开发分支，日常开发
feature/xxx  - 功能分支
hotfix/xxx   - 紧急修复分支
```

### 工作流程

1. 从 dev 分支创建 feature 分支
2. 开发完成后提交 PR 到 dev
3. 代码审查后合并到 dev
4. 定期将 dev 合并到 main 并打标签

### 数据管理

1. **开发环境**：各自使用本地数据
2. **测试环境**：使用共享测试数据
3. **生产环境**：使用生产数据（严格权限控制）

### 权限控制

使用 Streamlit 的权限验证：

```python
# 在 app.py 开头添加
import streamlit as st

def check_password():
    """返回 True 如果密码正确"""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "密码", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "密码", type="password", on_change=password_entered, key="password"
        )
        st.error("密码错误")
        return False
    else:
        return True

if not check_password():
    st.stop()
```

在 `.streamlit/secrets.toml` 中设置密码：

```toml
password = "your-password-here"
```

## 监控和维护

### 日志监控

查看日志文件：

```bash
tail -f logs/app.log
```

### 性能监控

添加性能监控代码到 `app.py`：

```python
import time

# 在操作开始时
start_time = time.time()

# 操作完成后
st.info(f"操作耗时: {time.time() - start_time:.2f} 秒")
```

### 定期维护

1. **数据备份**：每日自动备份
2. **日志清理**：每周清理旧日志
3. **性能优化**：每月检查大数据分片

## 总结

对于小团队（2-5人）：
- 使用 **方案一（Streamlit Cloud）** + **方案 B（Git 合并）**
- 成本低，设置简单

对于大团队（5人以上）：
- 使用 **方案二（私有服务器）** + **方案 C（真正数据库）**
- 性能更好，数据更安全

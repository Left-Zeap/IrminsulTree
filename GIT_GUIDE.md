# Git 协作指南

## 首次设置

### 1. 克隆仓库

```bash
# 克隆仓库
git clone https://github.com/yourusername/genshin-knowledge-graph.git
cd genshin-knowledge-graph/standalone_app

# 创建虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 创建分支

```bash
# 切换到 dev 分支
git checkout dev

# 拉取最新代码
git pull origin dev

# 创建功能分支
git checkout -b feature/add-new-feature
```

## 日常开发流程

### 1. 开始工作前

```bash
# 确保在 dev 分支
 git checkout dev

# 拉取最新代码
git pull origin dev

# 创建新的功能分支
git checkout -b feature/your-feature-name
```

### 2. 开发过程中

```bash
# 查看修改的文件
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "feat: 添加新功能"

# 推送到远程
git push origin feature/your-feature-name
```

### 3. 提交 PR

1. 访问 GitHub 仓库
2. 点击 "Compare & pull request"
3. 填写 PR 描述
4. 选择合并到 `dev` 分支
5. 等待代码审查

### 4. 合并后更新本地

```bash
# 切换回 dev
git checkout dev

# 拉取最新代码
git pull origin dev

# 删除已合并的功能分支
git branch -d feature/your-feature-name

# 删除远程分支
git push origin --delete feature/your-feature-name
```

## 数据文件处理

### 重要：不要提交数据文件到 main 分支

数据文件（`data/` 目录）默认在 `.gitignore` 中，不会被提交。

### 数据同步方法

#### 方法 1：通过 Git LFS（大文件存储）

```bash
# 安装 Git LFS
git lfs install

# 跟踪数据文件
git lfs track "data/*.json"

# 提交 .gitattributes
git add .gitattributes
git commit -m "添加 Git LFS 支持"
```

#### 方法 2：手动同步

```bash
# 导出数据
# 在应用中使用"导出数据"功能

# 将数据文件发送给团队成员
# 或使用网盘同步

# 导入数据
# 在应用中使用"导入数据"功能
```

#### 方法 3：使用云存储（推荐）

配置应用使用云存储后端（AWS S3、阿里云 OSS 等），修改 `storage.py`。

## 冲突解决

### 代码冲突

```bash
# 拉取最新代码时出现冲突
git pull origin dev

# 编辑冲突文件，解决冲突
# 然后
git add .
git commit -m "解决冲突"
git push
```

### 数据冲突

如果多个成员同时修改了数据：

1. 各自导出数据为 JSON
2. 使用数据合并工具（需要提供）
3. 合并后重新导入

## 发布流程

### 1. 准备发布

```bash
# 确保 dev 分支稳定
git checkout dev
git pull origin dev

# 创建发布分支
git checkout -b release/v1.1.0

# 更新版本号（在 config.py 中）
# 更新 CHANGELOG.md

git add .
git commit -m "chore: 准备发布 v1.1.0"
```

### 2. 合并到 main

```bash
# 切换到 main
git checkout main
git pull origin main

# 合并发布分支
git merge release/v1.1.0

# 打标签
git tag -a v1.1.0 -m "版本 1.1.0"

# 推送
git push origin main
git push origin v1.1.0
```

### 3. 部署

Streamlit Cloud 会自动部署 main 分支的最新代码。

## 常见问题

### Q: 误提交了数据文件怎么办？

```bash
# 从 Git 中移除，但保留本地文件
git rm --cached data/graph_data.json

# 提交更改
git commit -m "移除数据文件"

# 确保 .gitignore 已配置
```

### Q: 如何查看历史版本？

```bash
# 查看提交历史
git log --oneline

# 切换到某个版本
git checkout abc123

# 回到最新版本
git checkout main
```

### Q: 如何撤销修改？

```bash
# 撤销工作区的修改
git checkout -- filename

# 撤销暂存区的修改
git reset HEAD filename

# 撤销最后一次提交（保留修改）
git reset --soft HEAD^

# 撤销最后一次提交（不保留修改）
git reset --hard HEAD^
```

## 最佳实践

1. **经常提交**：小步快跑，不要一次提交大量修改
2. **写清楚的提交信息**：说明做了什么，为什么做
3. **先拉后推**：推送前先拉取最新代码
4. **使用分支**：不要直接在 main/dev 上开发
5. **及时清理**：合并后删除不需要的分支
6. **备份数据**：定期导出数据备份

## 团队协作建议

1. **分工明确**：不同的人负责不同类型的节点
2. **及时沟通**：修改重要数据前通知团队
3. **定期同步**：每天开始工作前同步数据和代码
4. **代码审查**：PR 需要至少一个人审查
5. **文档更新**：修改功能时同步更新文档

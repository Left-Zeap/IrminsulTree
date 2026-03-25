# 贡献指南

感谢您对原神知识图谱项目的关注！

## 开发流程

### 1. 设置开发环境

```bash
# 克隆仓库
git clone https://github.com/yourusername/genshin-knowledge-graph.git
cd genshin-knowledge-graph/standalone_app

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
streamlit run app.py
```

### 2. 代码规范

- 使用 4 空格缩进
- 函数和类添加 docstring
- 变量名使用 snake_case
- 常量使用 UPPER_CASE

### 3. 提交规范

提交信息格式：
```
<type>: <subject>

<body>
```

Type 类型：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat: 添加节点批量导入功能

支持从 CSV 文件批量导入节点数据
```

### 4. Pull Request 流程

1. 确保代码可以正常运行
2. 更新相关文档
3. 描述清楚 PR 的改动内容
4. 关联相关的 Issue

## 数据规范

添加节点时请遵循以下规范：

### 人物节点
- 名称使用官方中文名
- 别名包含常见昵称
- 时间使用游戏内纪年

### 地点节点
- 使用游戏内正式名称
- POI 编码参考游戏内标识

### 事件节点
- 时间范围尽量准确
- 子事件关联完整

## 问题反馈

发现问题请提交 Issue，包含：
1. 问题描述
2. 复现步骤
3. 期望结果
4. 实际结果
5. 截图（如有）

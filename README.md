# 原神知识图谱管理系统

基于 Streamlit 的知识图谱管理工具，无需数据库即可运行，支持可视化展示。

## 功能特性

- 📝 **节点管理**：支持 7 种节点类型（人物、事件、地点、任务、团体、杂项、词条）
- 🔗 **关系管理**：支持多种关系类型，支持批量添加
- 🔍 **智能搜索**：支持名称、别名、类型筛选
- 🕸️ **可视化**：基于 Vis.js 的交互式图谱展示
- 💾 **数据持久化**：JSON 文件存储，自动分片处理大数据
- 🔄 **数据修复**：自动修复损坏或缺失的数据字段

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

```bash
cp .env.example .env
# 编辑 .env 文件
```

### 3. 启动应用

```bash
streamlit run app.py
```

访问 http://localhost:8501

## 项目结构

```
standalone_app/
├── app.py                 # 主应用入口
├── config.py              # 配置文件
├── core/                  # 核心模块
│   ├── models.py         # 数据模型
│   ├── storage.py        # 存储层
│   └── visualizer.py     # 可视化
├── data/                 # 数据目录（gitignore）
├── logs/                 # 日志目录（gitignore）
├── .env.example          # 环境变量示例
├── .gitignore           # Git 忽略文件
├── requirements.txt      # 依赖
└── README.md            # 本文件
```

## 数据备份

数据文件存储在 `data/` 目录下，建议定期备份：

```bash
# 手动备份
cp -r data data_backup_$(date +%Y%m%d)
```

或使用应用内的"创建备份"功能。

## 部署

### Streamlit Cloud（推荐）

1. Fork 本仓库到 GitHub
2. 访问 https://streamlit.io/cloud
3. 连接 GitHub 仓库并部署

### 私有服务器

```bash
# 使用 nohup 后台运行
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &

# 或使用 screen
screen -S genshin-kg
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

MIT License

## 免责声明

本项目为原神同人作品，仅供学习交流使用。原神相关内容的版权归 miHoYo 所有。

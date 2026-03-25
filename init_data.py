"""
初始化数据脚本
将 sample_data.json 复制为 graph_data.json
"""
import json
import shutil
from pathlib import Path


def init_sample_data():
    """初始化示例数据"""
    data_dir = Path("data")
    sample_file = data_dir / "sample_data.json"
    target_file = data_dir / "graph_data.json"
    
    if not target_file.exists() and sample_file.exists():
        shutil.copy(sample_file, target_file)
        print(f"✅ 已初始化示例数据: {target_file}")
        
        # 显示数据内容
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 包含 {len(data['nodes'])} 个节点，{len(data['edges'])} 条边")
        print("\n节点列表:")
        for node in data['nodes']:
            print(f"  - [{node['node_type']}] {node['name']}")
    else:
        if target_file.exists():
            print(f"✅ 数据文件已存在: {target_file}")
        else:
            print(f"❌ 示例数据文件不存在: {sample_file}")


if __name__ == "__main__":
    init_sample_data()

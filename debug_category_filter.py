#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分类过滤功能调试脚本
用于验证分类过滤功能无效的问题
"""

import json
import os

def debug_category_filter():
    """调试分类过滤功能"""
    
    # 检查分类配置文件
    config_path = "bin\\categories.json"
    
    if os.path.exists(config_path):
        print("✅ 分类配置文件存在:", config_path)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        print("📊 分类配置内容:")
        print(json.dumps(config, ensure_ascii=False, indent=2))
        
        # 检查文件映射
        file_mappings = config.get('fileMappings', [])
        print(f"\n📁 文件映射数量: {len(file_mappings)}")
        
        if file_mappings:
            print("📋 文件映射详情:")
            for mapping in file_mappings:
                print(f"  文件: {mapping.get('filePath', 'N/A')}")
                print(f"  分类ID: {mapping.get('categoryId', 'N/A')}")
                print()
        else:
            print("❌ 文件映射为空，这是分类过滤无效的主要原因！")
            print("💡 需要先通过右键菜单为文件设置分类")
            
        # 检查分类
        categories = config.get('categories', [])
        print(f"🏷️  分类数量: {len(categories)}")
        for cat in categories:
            print(f"  分类: {cat.get('name', 'N/A')} (ID: {cat.get('id', 'N/A')})")
            
    else:
        print("❌ 分类配置文件不存在:", config_path)
        
    print("\n🔍 分类过滤功能无效的可能原因:")
    print("1. 文件映射为空 - 需要先为文件设置分类")
    print("2. 文件路径标准化问题 - 实际文件路径与映射中的路径不匹配")
    print("3. 分类过滤逻辑错误 - 过滤条件判断有问题")
    print("4. 分类数据未正确保存 - 配置文件写入失败")
    
    print("\n💡 解决方案:")
    print("1. 通过右键菜单为文件设置分类")
    print("2. 检查文件路径标准化逻辑")
    print("3. 添加调试日志验证过滤过程")
    print("4. 确保分类数据正确保存到配置文件")

if __name__ == "__main__":
    debug_category_filter()
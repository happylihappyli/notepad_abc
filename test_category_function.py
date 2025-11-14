#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分类过滤功能
"""

import os
import json

def test_category_config():
    """测试分类配置文件"""
    config_path = r"E:\GitHub3\notepad_abc\bin\bin\categories.json"
    
    if os.path.exists(config_path):
        print("✅ 分类配置文件存在")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"📂 分类数量: {len(config.get('categories', []))}")
        print(f"📄 文件映射数量: {len(config.get('fileMappings', []))}")
        
        # 显示分类信息
        for i, category in enumerate(config.get('categories', [])):
            print(f"  {i+1}. {category.get('name', '未知')} (ID: {category.get('id', '未知')})")
        
        if len(config.get('fileMappings', [])) == 0:
            print("⚠️  警告: 没有文件被分配分类")
            print("💡 解决方法: 在程序中右键点击文件，选择'设置分类'来为文件分配分类")
        else:
            print("✅ 有文件被分配了分类，分类过滤功能应该可以正常工作")
    else:
        print("❌ 分类配置文件不存在")

def main():
    print("=== 分类过滤功能测试 ===")
    test_category_config()
    
    print("\n=== 使用说明 ===")
    print("1. 启动程序: bin\\notepad_abc_new.exe")
    print("2. 打开文件列表面板")
    print("3. 右键点击文件 -> 设置分类 -> 选择分类")
    print("4. 点击分类按钮测试过滤效果")
    print("5. 点击'全部'按钮显示所有文件")

if __name__ == "__main__":
    main()
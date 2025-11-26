#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断CategoryManager分类文件读取问题的测试脚本
"""

import os
import json
import sys
from pathlib import Path

def main():
    print("=== 诊断CategoryManager分类文件读取问题 ===")
    print(f"时间: {Path(__file__).stat().st_mtime}")
    print("-" * 50)
    
    # 工作目录
    workspace_dir = Path(__file__).parent
    print(f"工作目录: {workspace_dir}")
    
    # 可能的配置文件路径
    possible_paths = [
        workspace_dir / "bin" / "categories.json",
        workspace_dir / "config" / "categories.json", 
        workspace_dir / "categories.json",
        workspace_dir / "bin" / "category.json",
        workspace_dir / "config" / "category.json"
    ]
    
    # 检查每个可能的配置文件路径
    for i, config_path in enumerate(possible_paths, 1):
        print(f"\n--- 检查路径 {i}: {config_path} ---")
        
        if config_path.exists():
            print(f"✓ 文件存在")
            try:
                # 读取文件内容
                with open(config_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                print(f"✓ 文件读取成功，大小: {len(content)} 字节")
                
                # 尝试解析JSON
                try:
                    config_data = json.loads(content)
                    print(f"✓ JSON解析成功")
                    
                    # 检查结构
                    if isinstance(config_data, dict):
                        print(f"  - 根对象包含 {len(config_data)} 个键")
                        for key in config_data.keys():
                            print(f"    * {key}")
                        
                        if "categories" in config_data:
                            categories = config_data["categories"]
                            if isinstance(categories, list):
                                print(f"  ✓ 找到 {len(categories)} 个分类")
                                for j, cat in enumerate(categories):
                                    if isinstance(cat, dict):
                                        name = cat.get("name", "未知")
                                        id_val = cat.get("id", "未知")
                                        print(f"    分类 {j+1}: {name} (ID: {id_val})")
                                    else:
                                        print(f"    分类 {j+1}: 格式错误 - {type(cat)}")
                            else:
                                print(f"  ✗ categories不是数组类型: {type(categories)}")
                        else:
                            print(f"  ✗ 未找到'categories'键")
                            
                        if "fileMappings" in config_data:
                            mappings = config_data["fileMappings"]
                            if isinstance(mappings, list):
                                print(f"  ✓ 找到 {len(mappings)} 个文件映射")
                            else:
                                print(f"  ✗ fileMappings不是数组类型: {type(mappings)}")
                    else:
                        print(f"✗ 根对象不是dict类型: {type(config_data)}")
                        
                except json.JSONDecodeError as e:
                    print(f"✗ JSON解析错误: {e}")
                    print(f"  前100字符: {content[:100]}")
                    
            except PermissionError:
                print(f"✗ 权限错误：无法读取文件")
            except Exception as e:
                print(f"✗ 读取文件时发生错误: {e}")
                
        else:
            print(f"✗ 文件不存在")
    
    # 测试当前目录和bin目录
    print(f"\n--- 目录和权限检查 ---")
    bin_dir = workspace_dir / "bin"
    config_dir = workspace_dir / "config"
    
    if bin_dir.exists():
        print(f"✓ bin目录存在: {bin_dir}")
        print(f"  权限: {'可读' if os.access(bin_dir, os.R_OK) else '不可读'}")
        print(f"  内容: {list(bin_dir.iterdir())}")
    else:
        print(f"✗ bin目录不存在: {bin_dir}")
        
    if config_dir.exists():
        print(f"✓ config目录存在: {config_dir}")
        print(f"  权限: {'可读' if os.access(config_dir, os.R_OK) else '不可读'}")
        print(f"  内容: {list(config_dir.iterdir())}")
    else:
        print(f"✗ config目录不存在: {config_dir}")

if __name__ == "__main__":
    main()
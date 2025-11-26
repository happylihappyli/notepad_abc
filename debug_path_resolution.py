#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入分析路径解析问题
"""

import os
import sys

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')

def analyze_file_structure():
    """分析项目文件结构，确定正确的相对路径"""
    print("项目文件结构分析")
    print("=" * 50)
    
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # 查找关键文件
    vertical_switcher_path = None
    categories_json_path = None
    
    for root, dirs, files in os.walk(current_dir):
        if 'VerticalFileSwitcher.cpp' in files:
            vertical_switcher_path = os.path.join(root, 'VerticalFileSwitcher.cpp')
            print(f"找到VerticalFileSwitcher.cpp: {vertical_switcher_path}")
        
        if 'categories.json' in files:
            categories_json_path = os.path.join(root, 'categories.json')
            print(f"找到categories.json: {categories_json_path}")
    
    if vertical_switcher_path and categories_json_path:
        print(f"\n分析相对路径:")
        print(f"从: {os.path.dirname(vertical_switcher_path)}")
        print(f"到: {os.path.dirname(categories_json_path)}")
        
        # 计算相对路径
        src_dir = os.path.dirname(vertical_switcher_path)
        target_dir = os.path.dirname(categories_json_path)
        
        rel_path = os.path.relpath(target_dir, src_dir)
        print(f"相对路径: {rel_path}")
        print(f"配置文件路径: {os.path.join(rel_path, 'categories.json')}")
        
        # 检查".."符号的实际含义
        print(f"\n'..'符号分析:")
        print(f"src_dir: {src_dir}")
        print(f"src_dir的父目录: {os.path.dirname(src_dir)}")
        
        # 测试不同的路径方案
        print(f"\n测试不同的路径方案:")
        
        # 方案1: 使用src_dir的父目录（PowerEditor目录）
        powereditor_dir = os.path.dirname(src_dir)
        proposed_path1 = os.path.join(powereditor_dir, 'bin', 'categories.json')
        print(f"方案1 (PowerEditor/bin/categories.json): {proposed_path1}")
        print(f"  文件存在: {os.path.exists(proposed_path1)}")
        
        # 方案2: 使用当前目录的bin目录
        proposed_path2 = os.path.join(current_dir, 'bin', 'categories.json')
        print(f"方案2 (当前目录/bin/categories.json): {proposed_path2}")
        print(f"  文件存在: {os.path.exists(proposed_path2)}")
        
        # 方案3: 基于exe位置的常见路径
        print(f"\n方案3分析 - exe位置假设:")
        exe_locations = [
            os.path.join(current_dir, 'PowerEditor', 'bin'),
            os.path.join(current_dir, 'PowerEditor', 'bin64'),
            current_dir
        ]
        
        for exe_dir in exe_locations:
            config_path = os.path.join(exe_dir, '..', 'bin', 'categories.json')
            config_path = os.path.normpath(config_path)
            print(f"  exe位置: {exe_dir}")
            print(f"  解析路径: {config_path}")
            print(f"  文件存在: {os.path.exists(config_path)}")
        
        return vertical_switcher_path, categories_json_path
    
    return None, None

def test_exe_based_path_resolution():
    """测试基于exe位置的路径解析"""
    print(f"\n\n基于exe位置的路径解析测试")
    print("=" * 60)
    
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # Notepad++项目中exe通常在以下位置：
    exe_locations = [
        os.path.join(current_dir, 'PowerEditor', 'bin'),
        os.path.join(current_dir, 'PowerEditor', 'bin64'),
        current_dir
    ]
    
    test_configs = [
        ("..\\bin\\categories.json", "原始配置路径"),
        ("..\\\\bin\\\\categories.json", "双反斜杠版本"),
        ("..\\categories.json", "简化路径"),
        ("bin\\categories.json", "直接bin目录路径")
    ]
    
    for exe_dir in exe_locations:
        print(f"\n假设exe位置: {exe_dir}")
        if not os.path.exists(exe_dir):
            print("  ✗ 目录不存在")
            continue
        
        for config_path, description in test_configs:
            print(f"\n  {description}: {config_path}")
            
            # 组合路径
            full_path = os.path.join(exe_dir, config_path)
            full_path = os.path.normpath(full_path)
            print(f"    解析结果: {full_path}")
            print(f"    文件存在: {os.path.exists(full_path)}")
            
            if os.path.exists(full_path):
                print(f"    ✓ 找到有效配置文件")
                try:
                    import json
                    with open(full_path, 'rb') as f:
                        content = f.read()
                    if content[:3] == b'\xEF\xBB\xBF':
                        content = content[3:]
                    data = json.loads(content.decode('utf-8'))
                    print(f"    ✓ JSON有效，包含 {len(data.get('categories', []))} 个分类")
                except Exception as e:
                    print(f"    ✗ JSON解析失败: {e}")

if __name__ == "__main__":
    analyze_file_structure()
    test_exe_based_path_resolution()
    
    print(f"\n\n结论:")
    print(f"问题分析：'..\\\\bin\\\\categories.json'应该相对于exe位置解析")
    print(f"当前代码中使用GetCurrentDirectory()是错误的")
    print(f"应该使用GetModuleFileName()获取exe路径，然后相对于exe路径解析")
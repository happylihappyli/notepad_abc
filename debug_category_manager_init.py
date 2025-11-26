#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整模拟CategoryManager初始化过程的调试脚本
"""

import json
import os
import sys
from pathlib import Path
import re

def simulate_normalize_path(path, current_dir):
    """模拟CategoryManager的normalizePath方法"""
    print(f"  normalizePath输入: '{path}'")
    print(f"  当前目录: '{current_dir}'")
    
    if not path:
        return path
    
    normalized = path.replace('/', '\\')
    print(f"  标准化分隔符后: '{normalized}'")
    
    # 检查是否是相对路径
    if ':' not in normalized:
        print(f"  检测为相对路径")
        # 移除当前目录路径末尾的反斜杠（如果存在）
        dir_str = current_dir.rstrip('\\')
        
        # 组合路径
        normalized = dir_str + '\\' + normalized
        print(f"  转换为绝对路径: '{normalized}'")
    
    return normalized

def simulate_ensure_config_directory(config_path):
    """模拟CategoryManager的ensureConfigDirectory方法"""
    print(f"  ensureConfigDirectory输入: '{config_path}'")
    
    # 从路径中提取目录
    last_backslash = config_path.rfind('\\')
    last_forward_slash = config_path.rfind('/')
    last_separator = max(last_backslash, last_forward_slash)
    
    if last_separator != -1:
        directory = config_path[:last_separator]
        print(f"  提取的目录: '{directory}'")
        
        # 检查目录是否存在
        if os.path.exists(directory):
            print(f"  ✓ 目录已存在: {directory}")
        else:
            print(f"  ✗ 目录不存在: {directory}")
    else:
        print(f"  ✗ 无法从路径中提取目录: {config_path}")
    
    # 检查配置文件是否存在
    if os.path.exists(config_path):
        print(f"  ✓ 配置文件存在: {config_path}")
        return True
    else:
        print(f"  ✗ 配置文件不存在: {config_path}")
        return False

def simulate_load_config(config_path):
    """模拟CategoryManager的loadConfig方法"""
    print(f"  loadConfig输入: '{config_path}'")
    
    if not os.path.exists(config_path):
        print(f"  ✗ 文件不存在: {config_path}")
        return False
    
    try:
        # 模拟文件打开
        print(f"  ✓ 成功打开文件: {config_path}")
        
        # 模拟文件大小检查
        file_size = os.path.getsize(config_path)
        print(f"  文件大小: {file_size} 字节")
        
        if file_size == 0:
            print(f"  ✗ 文件为空")
            return False
        
        # 模拟文件内容读取
        with open(config_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        print(f"  读取到文件内容长度: {len(content)} 字符")
        
        # 检查BOM标记
        with open(config_path, 'rb') as f:
            first_bytes = f.read(3)
            if first_bytes == b'\\xef\\xbb\\xbf':
                print(f"  检测到UTF-8 BOM标记")
            else:
                print(f"  未检测到UTF-8 BOM标记")
        
        # 模拟JSON解析
        try:
            data = json.loads(content)
            print(f"  ✓ JSON解析成功")
            
            # 检查JSON结构
            if isinstance(data, dict):
                print(f"  JSON是对象类型，包含 {len(data)} 个键")
                
                if "categories" in data:
                    categories = data["categories"]
                    if isinstance(categories, list):
                        print(f"  ✓ categories是数组类型，大小: {len(categories)}")
                        for i, cat in enumerate(categories):
                            if isinstance(cat, dict):
                                name = cat.get("name", "未知")
                                id_val = cat.get("id", "未知")
                                print(f"    分类 {i+1}: {name} (ID: {id_val})")
                        return True, len(categories)
                    else:
                        print(f"  ✗ categories不是数组类型: {type(categories)}")
                        return False, 0
                else:
                    print(f"  ✗ JSON不包含categories键")
                    return False, 0
            else:
                print(f"  ✗ JSON不是对象类型: {type(data)}")
                return False, 0
                
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON解析错误: {e}")
            return False, 0
            
    except PermissionError:
        print(f"  ✗ 权限错误：无法读取文件")
        return False, 0
    except Exception as e:
        print(f"  ✗ 读取文件时发生错误: {e}")
        return False, 0

def simulate_category_manager_initialize(config_path):
    """模拟CategoryManager的完整初始化过程"""
    print(f"=== 模拟CategoryManager.initialize('{config_path}') ===")
    
    current_dir = str(Path(__file__).parent)
    
    # 第1步：设置配置路径
    m_config_path = config_path
    print(f"1. 设置m_configPath: '{m_config_path}'")
    
    # 第2步：路径标准化
    print(f"2. 开始路径标准化...")
    resolved_path = simulate_normalize_path(m_config_path, current_dir)
    
    if resolved_path != m_config_path:
        print(f"   路径已更新: '{m_config_path}' -> '{resolved_path}'")
        m_config_path = resolved_path
    else:
        print(f"   路径未改变")
    
    # 第3步：确保配置目录存在
    print(f"3. 确保配置目录存在...")
    dir_result = simulate_ensure_config_directory(m_config_path)
    
    # 第4步：加载配置
    print(f"4. 开始加载配置文件...")
    result = simulate_load_config(m_config_path)
    if isinstance(result, tuple):
        success, category_count = result
    else:
        success = result
        category_count = 0
    
    if success:
        print(f"   ✓ 配置加载成功，分类数量: {category_count}")
        return True, category_count
    else:
        print(f"   ✗ 配置加载失败，创建默认分类")
        return False, 0

def main():
    print("=== CategoryManager完整初始化过程模拟 ===")
    print(f"时间: {Path(__file__).stat().st_mtime}")
    print("-" * 60)
    
    # CategoryManager尝试的路径序列
    paths_to_test = [
        "..\\\\bin\\\\categories.json",     # WM_INITDIALOG中使用的路径
        "bin\\\\categories.json",           # 备用路径
        str(Path(__file__).parent / "bin" / "categories.json")  # 绝对路径
    ]
    
    for i, config_path in enumerate(paths_to_test, 1):
        print(f"\n{'='*60}")
        print(f"尝试路径 {i}: {config_path}")
        
        success, category_count = simulate_category_manager_initialize(config_path)
        
        if success and category_count > 0:
            print(f"\\n✓ 路径 {i} 成功加载分类数据！")
            print(f"  分类数量: {category_count}")
            break
        else:
            print(f"\\n✗ 路径 {i} 加载失败")
    else:
        print(f"\\n✗ 所有路径都无法加载分类数据")
    
    # 详细分析当前bin目录下的文件
    print(f"\\n{'='*60}")
    print("=== 当前bin目录分析 ===")
    
    bin_dir = Path(__file__).parent / "bin"
    categories_file = bin_dir / "categories.json"
    
    if categories_file.exists():
        print(f"✓ bin/categories.json 存在")
        
        # 详细文件分析
        file_size = categories_file.stat().st_size
        print(f"  文件大小: {file_size} 字节")
        
        # 读取文件头
        with open(categories_file, 'rb') as f:
            first_20_bytes = f.read(20)
        print(f"  文件头(hex): {first_20_bytes.hex()}")
        
        # 检查BOM
        with open(categories_file, 'rb') as f:
            bom = f.read(3)
        if bom == b'\\xef\\xbb\\xbf':
            print(f"  ✓ 包含UTF-8 BOM")
        else:
            print(f"  ✗ 不包含UTF-8 BOM")
        
        # 读取内容预览
        with open(categories_file, 'r', encoding='utf-8-sig') as f:
            content = f.read(200)
        print(f"  内容预览: {content[:100]}...")
        
        # 解析JSON
        try:
            data = json.loads(content)
            if "categories" in data and len(data["categories"]) == 5:
                print(f"  ✓ JSON格式正确，包含5个分类")
            else:
                print(f"  ✗ JSON格式不正确")
        except Exception as e:
            print(f"  ✗ JSON解析错误: {e}")

if __name__ == "__main__":
    main()
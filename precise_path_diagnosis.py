#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确诊断CategoryManager路径问题的脚本
"""

import os
import sys
from pathlib import Path

def check_current_directory():
    """检查当前工作目录"""
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查当前目录相对于项目根目录的位置
    project_root = Path(__file__).parent
    
    if Path(current_dir) == project_root:
        print("当前目录 = 项目根目录")
        return "project_root"
    elif Path(current_dir) == (project_root / "bin"):
        print("当前目录 = bin目录")
        return "bin_dir"
    else:
        print(f"当前目录 = 其他位置 (项目根目录: {project_root})")
        return "other"

def test_path_resolution():
    """测试不同路径的解析情况"""
    current_dir = check_current_directory()
    
    # 测试路径列表
    test_paths = [
        "..\\\\bin\\\\categories.json",
        "bin\\\\categories.json",
        "categories.json"
    ]
    
    project_root = Path(__file__).parent
    bin_dir = project_root / "bin"
    config_dir = project_root / "config"
    
    print(f"\\n=== 项目结构分析 ===")
    print(f"项目根目录: {project_root}")
    print(f"bin目录: {bin_dir}")
    print(f"config目录: {config_dir}")
    
    print(f"\\n=== 路径测试 ===")
    for path in test_paths:
        print(f"\\n测试路径: '{path}'")
        
        # 转换为绝对路径
        abs_path = project_root / path
        print(f"  相对于项目根目录: {abs_path}")
        
        # 检查文件是否存在
        if abs_path.exists():
            print(f"  ✓ 文件存在: {abs_path}")
            
            # 读取分类数量
            try:
                import json
                with open(abs_path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                
                if isinstance(data, dict) and "categories" in data:
                    categories = data["categories"]
                    if isinstance(categories, list):
                        print(f"  ✓ JSON格式正确，包含 {len(categories)} 个分类")
                        
                        # 显示分类详情
                        for i, cat in enumerate(categories):
                            if isinstance(cat, dict):
                                name = cat.get("name", "未知")
                                id_val = cat.get("id", "未知")
                                print(f"    {i+1}. {name} (ID: {id_val})")
                    else:
                        print(f"  ✗ categories不是数组类型: {type(categories)}")
                else:
                    print(f"  ✗ JSON格式错误或不包含categories")
                    
            except Exception as e:
                print(f"  ✗ 读取文件时发生错误: {e}")
        else:
            print(f"  ✗ 文件不存在: {abs_path}")

def simulate_normalize_path_with_current_dir(path, current_dir):
    """模拟CategoryManager的normalizePath方法，考虑实际工作目录"""
    print(f"\\n=== 模拟normalizePath (当前目录: {current_dir}) ===")
    print(f"输入路径: '{path}'")
    
    if not path:
        return path
    
    # 标准化路径分隔符
    normalized = path.replace('/', '\\\\')
    print(f"标准化分隔符后: '{normalized}'")
    
    # 检查是否是相对路径
    if ':' not in normalized:
        print(f"检测为相对路径")
        
        # 获取当前目录的字符串形式
        current_dir_str = str(current_dir)
        if not current_dir_str.endswith('\\\\'):
            current_dir_str += '\\\\'
        
        # 组合路径
        combined = current_dir_str + normalized
        print(f"组合路径: '{combined}'")
        
        # 处理..符号
        import os
        try:
            # 使用os.path.normpath来正确处理..符号
            final_path = os.path.normpath(combined)
            print(f"处理..符号后: '{final_path}'")
            return final_path
        except Exception as e:
            print(f"处理..符号时出错: {e}")
            return combined
    
    return normalized

def main():
    print("=== 精确诊断CategoryManager路径问题 ===")
    print(f"时间: {Path(__file__).stat().st_mtime}")
    print("-" * 60)
    
    # 测试当前工作目录
    current_location = check_current_directory()
    
    # 测试路径解析
    test_path_resolution()
    
    # 模拟normalizePath
    print(f"\\n=== 模拟CategoryManager路径处理 ===")
    
    current_dir = os.getcwd()
    
    test_paths = [
        "..\\\\bin\\\\categories.json",
        "bin\\\\categories.json"
    ]
    
    for path in test_paths:
        resolved = simulate_normalize_path_with_current_dir(path, current_dir)
        print(f"路径 '{path}' -> '{resolved}'")
        
        # 检查解析后的路径是否存在
        if os.path.exists(resolved):
            print(f"  ✓ 解析后的路径存在: {resolved}")
        else:
            print(f"  ✗ 解析后的路径不存在: {resolved}")
    
    # 建议解决方案
    print(f"\\n=== 解决方案建议 ===")
    
    project_root = Path(__file__).parent
    correct_path = project_root / "bin" / "categories.json"
    
    print(f"正确的配置文件路径应该是: {correct_path}")
    print(f"该文件存在: {correct_path.exists()}")
    
    if correct_path.exists():
        print("\\n✓ 发现正确的配置文件，问题在于路径解析")
        print("建议：修复CategoryManager的normalizePath方法，正确处理'..'符号")
    else:
        print("\\n✗ 正确配置文件不存在，需要创建")

if __name__ == "__main__":
    main()
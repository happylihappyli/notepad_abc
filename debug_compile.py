#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确查找编译错误位置
"""

import os
import re

def find_line_1040_issues():
    """检查第1040行周围的问题"""
    file_path = "PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher.cpp"
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        print(f"文件总行数: {len(lines)}")
        print("\n=== 第1035-1050行内容 ===")
        for i in range(1034, min(1050, len(lines))):
            line_num = i + 1
            content = lines[i].rstrip()
            print(f"{line_num}: {content}")
            
            # 检查可能的类型错误
            if '=' in content and 'order' in content:
                print(f"    >>> 检查赋值语句: {content}")
                if 'wstring' in content or 'std::wstring' in content:
                    print(f"    >>> 可能存在wstring类型问题")
        
        print("\n=== 搜索所有包含'order'的赋值语句 ===")
        for i, line in enumerate(lines):
            if 'order' in line and '=' in line:
                print(f"第{i+1}行: {line.strip()}")
                
    except Exception as e:
        print(f"处理文件时出错: {e}")

if __name__ == "__main__":
    find_line_1040_issues()
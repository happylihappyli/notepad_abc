#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为C++文件添加UTF-8 BOM编码
"""

import os

def add_utf8_bom(file_path):
    """为文件添加UTF-8 BOM"""
    try:
        # 读取文件内容（使用UTF-8编码）
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 写入文件，添加UTF-8 BOM
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(content)
            
        print(f"已为文件添加UTF-8 BOM: {file_path}")
        return True
        
    except Exception as e:
        print(f"处理文件时出错: {file_path}, 错误: {e}")
        return False

if __name__ == "__main__":
    # 要处理的文件
    target_file = "PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher.cpp"
    
    if os.path.exists(target_file):
        add_utf8_bom(target_file)
    else:
        print(f"文件不存在: {target_file}")
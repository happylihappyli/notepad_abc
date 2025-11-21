#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def search_doclist_in_xml(file_path):
    """在XML文件中搜索与文档列表相关的配置"""
    print(f"正在搜索文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 搜索DocList相关的内容
        doclist_patterns = [
            r'<DocList[\s\S]*?</DocList>',
            r'DocList',
            r'Document\s+List',
            r'DocumentList',
            r'FS_SETTINGS',
            r'FS_ROOT',
            r'File\s+Switcher',
            r'FilesList'
        ]
        
        found_anything = False
        for pattern in doclist_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"找到匹配 '{pattern}' 的内容:")
                for match in matches[:5]:  # 只显示前5个匹配
                    print(f"  - {match}")
                if len(matches) > 5:
                    print(f"  ... 还有 {len(matches) - 5} 个匹配")
                found_anything = True
                print()
        
        if not found_anything:
            print("未找到任何与文档列表相关的内容")
            
    except Exception as e:
        print(f"读取文件时出错: {e}")

if __name__ == "__main__":
    chinese_file = r"E:\GitHub3\notepad_abc\PowerEditor\installer\nativeLang\chineseSimplified.xml"
    english_file = r"E:\GitHub3\notepad_abc\PowerEditor\installer\nativeLang\english.xml"
    
    print("=" * 60)
    print("搜索中文本地化文件中的文档列表配置")
    print("=" * 60)
    search_doclist_in_xml(chinese_file)
    
    print("\n" + "=" * 60)
    print("搜索英文本地化文件中的文档列表配置")
    print("=" * 60)
    search_doclist_in_xml(english_file)
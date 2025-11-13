#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细检查配置文件
"""

import os
import xml.etree.ElementTree as ET

def check_config_detail():
    """详细检查配置文件"""
    config_path = os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml")
    
    if not os.path.exists(config_path):
        print("✗ 配置文件不存在")
        return False
    
    print(f"详细检查配置文件: {config_path}")
    
    try:
        # 读取原始内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n=== 原始内容检查 ===")
        
        # 查找documentList设置
        if 'documentList=' in content:
            print("✓ 在原始内容中找到documentList设置")
            
            # 查找所有包含documentList的行
            import re
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'documentList=' in line:
                    print(f"  第{i+1}行: {line.strip()}")
        else:
            print("✗ 在原始内容中未找到documentList设置")
        
        # XML解析检查
        print("\n=== XML解析检查 ===")
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # 查找所有GUIConfig元素
        guiconfigs = []
        for elem in root.iter('GUIConfig'):
            guiconfigs.append(elem)
        
        print(f"找到 {len(guiconfigs)} 个GUIConfig元素")
        
        # 检查每个GUIConfig元素
        for i, elem in enumerate(guiconfigs):
            name = elem.get('name', '')
            document_list = elem.get('documentList')
            
            print(f"\nGUIConfig {i+1}:")
            print(f"  name属性: '{name}'")
            print(f"  documentList属性: '{document_list}'")
            
            # 显示所有属性
            if elem.attrib:
                print(f"  所有属性: {elem.attrib}")
        
        # 专门查找空的name属性GUIConfig
        print("\n=== 查找空的name属性GUIConfig ===")
        for elem in root.iter('GUIConfig'):
            name = elem.get('name', '')
            if name == '':
                print("✓ 找到空的name属性GUIConfig")
                document_list = elem.get('documentList')
                print(f"  documentList属性: '{document_list}'")
                print(f"  所有属性: {elem.attrib}")
                break
        else:
            print("✗ 未找到空的name属性GUIConfig")
        
        return True
        
    except Exception as e:
        print(f"✗ 检查配置文件失败: {e}")
        return False

if __name__ == "__main__":
    print("详细检查配置文件")
    print("=" * 60)
    
    check_config_detail()
    
    print("\n=== 检查完成 ===")
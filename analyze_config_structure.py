#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析配置文件结构
"""

import os
import xml.etree.ElementTree as ET

def analyze_config_structure():
    """分析配置文件结构"""
    config_path = os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml")
    
    if not os.path.exists(config_path):
        print("✗ 配置文件不存在")
        return False
    
    print(f"分析配置文件: {config_path}")
    
    try:
        # 读取配置文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n=== 配置文件内容摘要 ===")
        print(f"文件大小: {len(content)} 字节")
        
        # 检查关键元素
        if '<GUIConfig' in content:
            print("✓ 找到GUIConfig标签")
            
            # 查找所有GUIConfig标签
            import re
            guiconfigs = re.findall(r'<GUIConfig[^>]*>', content)
            print(f"找到 {len(guiconfigs)} 个GUIConfig标签")
            
            for i, tag in enumerate(guiconfigs[:10]):  # 只显示前10个
                print(f"  {i+1}. {tag}")
        else:
            print("✗ 未找到GUIConfig标签")
        
        # 检查documentList设置
        if 'documentList=' in content:
            print("✓ 找到documentList设置")
            
            # 查找documentList设置
            doclist_matches = re.findall(r'documentList="[^"]*"', content)
            for match in doclist_matches:
                print(f"  {match}")
        else:
            print("✗ 未找到documentList设置")
        
        # 检查DockingManager
        if '<DockingManager' in content:
            print("✓ 找到DockingManager标签")
        else:
            print("✗ 未找到DockingManager标签")
        
        # 检查Plugin标签
        if '<Plugin' in content:
            print("✓ 找到Plugin标签")
            
            # 查找所有Plugin标签
            plugins = re.findall(r'<Plugin[^>]*pluginName="[^"]*"[^>]*>', content)
            print(f"找到 {len(plugins)} 个Plugin标签")
            
            for plugin in plugins[:5]:  # 只显示前5个
                print(f"  {plugin}")
        else:
            print("✗ 未找到Plugin标签")
        
        # 使用XML解析检查结构
        print("\n=== XML解析结构 ===")
        try:
            tree = ET.parse(config_path)
            root = tree.getroot()
            
            print(f"根元素: {root.tag}")
            
            # 遍历所有元素
            for elem in root.iter():
                if elem.tag in ['GUIConfig', 'DockingManager', 'Plugin']:
                    print(f"元素: {elem.tag}")
                    if elem.attrib:
                        print(f"  属性: {elem.attrib}")
                    
                    # 如果是GUIConfig，检查name属性
                    if elem.tag == 'GUIConfig':
                        name = elem.get('name', '')
                        if name == '':
                            print("  找到空的name属性GUIConfig")
                            document_list = elem.get('documentList')
                            if document_list:
                                print(f"  documentList: {document_list}")
                            else:
                                print("  未找到documentList属性")
        
        except Exception as e:
            print(f"XML解析错误: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ 分析配置文件失败: {e}")
        return False

if __name__ == "__main__":
    print("分析配置文件结构")
    print("=" * 60)
    
    analyze_config_structure()
    
    print("\n=== 分析完成 ===")
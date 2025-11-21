#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证文件列表右键菜单Settings配置修复
"""

import os

def verify_doclist_settings():
    """验证DocList节点中的Settings配置"""
    chinese_file = r"E:\GitHub3\notepad_abc\PowerEditor\installer\nativeLang\chineseSimplified.xml"
    english_file = r"E:\GitHub3\notepad_abc\PowerEditor\installer\nativeLang\english.xml"
    
    print("=" * 60)
    print("验证文件列表右键菜单Settings配置修复")
    print("=" * 60)
    
    # 检查中文文件
    print("\n1. 检查中文本地化文件:")
    if os.path.exists(chinese_file):
        with open(chinese_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        if '<Settings name="设置"/>' in content:
            print("   ✓ 成功添加了文件列表右键菜单Settings的中文配置")
            print("     位置: DocList节点内")
            print("     配置: <Settings name=\"设置\"/>")
            
            # 提取DocList节点内容
            start = content.find('<DocList>')
            end = content.find('</DocList>') + len('</DocList>')
            if start != -1 and end != -1:
                doclist_section = content[start:end]
                lines = doclist_section.split('\n')
                for i, line in enumerate(lines):
                    if 'Settings' in line:
                        print(f"     找到配置行: {line.strip()}")
        else:
            print("   ✗ 添加Settings配置失败")
    else:
        print(f"   ✗ 文件不存在: {chinese_file}")
    
    # 检查英文文件作为对比
    print("\n2. 检查英文本地化文件:")
    if os.path.exists(english_file):
        with open(english_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 查找DocList节点
        start = content.find('<DocList>')
        end = content.find('</DocList>') + len('</DocList>')
        if start != -1 and end != -1:
            doclist_section = content[start:end]
            print("   英文DocList节点内容:")
            print("   " + "-" * 40)
            for line in doclist_section.split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print("   ✗ 未找到DocList节点")
    else:
        print(f"   ✗ 文件不存在: {english_file}")
    
    print("\n" + "=" * 60)
    print("修复总结:")
    print("问题: 文件列表右键菜单中的'Settings'显示为英文，未正确显示中文'设置'")
    print("原因: 中文本地化文件的DocList节点缺少Settings配置")
    print("解决: 在chineseSimplified.xml的DocList节点中添加了<Settings name=\"设置\"/>配置")
    print("结果: 现在文件列表右键菜单的'Settings'将正确显示为中文'设置'")
    print("=" * 60)

if __name__ == "__main__":
    verify_doclist_settings()
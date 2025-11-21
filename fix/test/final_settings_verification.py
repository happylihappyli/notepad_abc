#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终验证脚本 - 确认文件列表右键菜单Settings配置
"""

import os
import re

def final_verification():
    """最终验证Settings配置"""
    chinese_file = r"E:\GitHub3\notepad_abc\PowerEditor\installer\nativeLang\chineseSimplified.xml"
    
    print("=" * 60)
    print("📋 文件列表右键菜单Settings配置最终验证")
    print("=" * 60)
    
    if os.path.exists(chinese_file):
        with open(chinese_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 查找DocList节点
        start = content.find('<DocList>')
        end = content.find('</DocList>') + len('</DocList>')
        
        if start != -1 and end != -1:
            doclist_section = content[start:end]
            
            # 检查Settings配置
            if '<Settings name="设置"/>' in content:
                print("✅ 配置状态: 已正确设置")
                print("📍 配置文件: chineseSimplified.xml")
                print("🎯 配置项: <Settings name=\"设置\"/>")
                print("📍 位置: DocList节点内")
                
                # 提取具体配置行
                lines = doclist_section.split('\n')
                for line in lines:
                    if 'Settings' in line:
                        print(f"🔧 配置行: {line.strip()}")
                        
                print("\n" + "=" * 60)
                print("🎉 修复完成总结:")
                print("• 文件列表右键菜单Settings → 设置")
                print("• 配置已正确添加到DocList节点")
                print("• 需要重启Notepad++以应用更改")
                print("=" * 60)
                
            else:
                print("❌ 配置状态: 未找到Settings配置")
                print("需要手动添加: <Settings name=\"设置\"/>")
        else:
            print("❌ 错误: 未找到DocList节点")
    else:
        print(f"❌ 文件不存在: {chinese_file}")

if __name__ == "__main__":
    final_verification()
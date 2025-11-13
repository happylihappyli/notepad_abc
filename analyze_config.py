#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析配置文件内容，检查文档列表配置
"""

import os
import xml.etree.ElementTree as ET

def analyze_config_file():
    """分析配置文件内容"""
    config_path = os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml")
    
    if not os.path.exists(config_path):
        print("✗ 配置文件不存在")
        return
    
    print(f"分析配置文件: {config_path}")
    print("=" * 60)
    
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # 查找DockingManager配置
        docking_manager = None
        for elem in root.iter():
            if elem.tag == "GUIConfig" and elem.get("name") == "DockingManager":
                docking_manager = elem
                break
        
        if docking_manager is None:
            print("✗ 未找到DockingManager配置")
            return
        
        print("✓ 找到DockingManager配置")
        
        # 检查PluginDlg配置
        plugin_dlgs = docking_manager.findall(".//PluginDlg")
        print(f"\n找到 {len(plugin_dlgs)} 个PluginDlg配置:")
        
        for i, plugin in enumerate(plugin_dlgs):
            plugin_name = plugin.get("pluginName", "")
            plugin_id = plugin.get("id", "")
            is_visible = plugin.get("isVisible", "no")
            curr = plugin.get("curr", "")
            prev = plugin.get("prev", "")
            
            print(f"\n插件 {i+1}:")
            print(f"  名称: {plugin_name}")
            print(f"  ID: {plugin_id}")
            print(f"  可见性: {is_visible}")
            print(f"  当前容器: {curr}")
            print(f"  上一个容器: {prev}")
            
            # 检查是否是文档列表
            if plugin_id == "44084":  # IDM_VIEW_DOCLIST的值
                print("  ✓ 这是文档列表配置")
                if is_visible == "yes":
                    print("  ✓ 文档列表配置为可见")
                else:
                    print("  ✗ 文档列表配置为不可见")
            else:
                print("  ✗ 这不是文档列表配置")
        
        # 检查是否缺少文档列表配置
        doclist_found = any(plugin.get("id") == "44084" for plugin in plugin_dlgs)
        
        if not doclist_found:
            print("\n✗ 配置文件中缺少文档列表配置")
            print("需要添加以下配置:")
            print('  <PluginDlg pluginName="Notepad++::InternalFunction" id="44084" curr="0" prev="-1" isVisible="yes" />')
        else:
            print("\n✓ 配置文件中包含文档列表配置")
        
        # 显示完整的DockingManager配置
        print("\n完整的DockingManager配置:")
        print(ET.tostring(docking_manager, encoding='unicode'))
        
    except Exception as e:
        print(f"✗ 分析配置文件失败: {e}")

def check_idm_view_doclist_value():
    """检查IDM_VIEW_DOCLIST的值"""
    print("\n=== 检查IDM_VIEW_DOCLIST的值 ===")
    
    # 在代码中搜索IDM_VIEW_DOCLIST的定义
    import subprocess
    
    try:
        result = subprocess.run([
            'powershell', '-Command', 
            'Get-Content "E:\GitHub3\notepad_abc\PowerEditor\src\resource.h" | Select-String "IDM_VIEW_DOCLIST"'
        ], capture_output=True, text=True, cwd='E:\GitHub3\notepad_abc')
        
        if result.returncode == 0 and result.stdout:
            print("找到IDM_VIEW_DOCLIST定义:")
            print(result.stdout)
        else:
            print("在resource.h中未找到IDM_VIEW_DOCLIST定义")
            
            # 尝试在其他文件中搜索
            result2 = subprocess.run([
                'powershell', '-Command', 
                'Get-ChildItem -Path "E:\GitHub3\notepad_abc" -Recurse -Include *.h,*.cpp | Select-String "IDM_VIEW_DOCLIST" | Select-Object -First 5'
            ], capture_output=True, text=True, cwd='E:\GitHub3\notepad_abc')
            
            if result2.returncode == 0 and result2.stdout:
                print("在其他文件中找到IDM_VIEW_DOCLIST:")
                print(result2.stdout)
            else:
                print("未找到IDM_VIEW_DOCLIST定义")
                
    except Exception as e:
        print(f"搜索失败: {e}")

if __name__ == "__main__":
    print("分析配置文件内容")
    print("=" * 60)
    
    # 分析配置文件
    analyze_config_file()
    
    # 检查IDM_VIEW_DOCLIST的值
    check_idm_view_doclist_value()
    
    print("\n=== 分析完成 ===")
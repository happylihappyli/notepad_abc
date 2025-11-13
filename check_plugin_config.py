#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查插件配置结构
"""

import os
import xml.etree.ElementTree as ET

def check_plugin_config():
    """检查插件配置结构"""
    config_path = os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml")
    
    if not os.path.exists(config_path):
        print("✗ 配置文件不存在")
        return False
    
    print(f"检查插件配置: {config_path}")
    
    try:
        # 读取原始内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n=== 查找所有Plugin配置 ===")
        
        # 查找所有Plugin标签
        import re
        plugins = re.findall(r'<Plugin[^>]*>', content)
        print(f"找到 {len(plugins)} 个Plugin标签")
        
        for i, plugin in enumerate(plugins):
            print(f"\nPlugin {i+1}:")
            print(f"  {plugin}")
            
            # 提取pluginName属性
            plugin_name_match = re.search(r'pluginName="([^"]*)"', plugin)
            if plugin_name_match:
                plugin_name = plugin_name_match.group(1)
                print(f"  pluginName: {plugin_name}")
            
            # 提取internalID属性
            internal_id_match = re.search(r'internalID="([^"]*)"', plugin)
            if internal_id_match:
                internal_id = internal_id_match.group(1)
                print(f"  internalID: {internal_id}")
        
        # XML解析检查
        print("\n=== XML解析检查 ===")
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # 查找DockingManager
        docking_manager = root.find('.//DockingManager')
        if docking_manager:
            print("✓ 找到DockingManager")
            
            # 查找所有Plugin元素
            plugins_xml = docking_manager.findall('.//Plugin')
            print(f"XML解析找到 {len(plugins_xml)} 个Plugin元素")
            
            for i, plugin in enumerate(plugins_xml):
                print(f"\nPlugin {i+1}:")
                print(f"  所有属性: {plugin.attrib}")
        else:
            print("✗ 未找到DockingManager")
        
        return True
        
    except Exception as e:
        print(f"✗ 检查插件配置失败: {e}")
        return False

if __name__ == "__main__":
    print("检查插件配置结构")
    print("=" * 60)
    
    check_plugin_config()
    
    print("\n=== 检查完成 ===")
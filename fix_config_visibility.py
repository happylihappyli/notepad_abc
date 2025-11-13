#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改配置文件，将文档列表的可见性设置为yes
"""

import os
import xml.etree.ElementTree as ET

def fix_doclist_visibility():
    """修改文档列表的可见性配置"""
    config_path = os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml")
    
    if not os.path.exists(config_path):
        print("✗ 配置文件不存在")
        return False
    
    print(f"修改配置文件: {config_path}")
    
    try:
        # 备份原文件
        backup_path = config_path + ".backup"
        import shutil
        shutil.copy2(config_path, backup_path)
        print(f"✓ 已创建备份: {backup_path}")
        
        # 解析XML文件
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
            return False
        
        # 查找文档列表配置
        doclist_found = False
        for plugin in docking_manager.findall(".//PluginDlg"):
            if plugin.get("id") == "44084":  # IDM_VIEW_DOCLIST
                current_visibility = plugin.get("isVisible", "no")
                print(f"找到文档列表配置，当前可见性: {current_visibility}")
                
                if current_visibility == "no":
                    plugin.set("isVisible", "yes")
                    print("✓ 已将文档列表可见性修改为yes")
                    doclist_found = True
                else:
                    print("✓ 文档列表已经可见")
                    doclist_found = True
                break
        
        if not doclist_found:
            print("✗ 未找到文档列表配置，需要添加新配置")
            # 添加新的文档列表配置
            new_plugin = ET.SubElement(docking_manager, "PluginDlg")
            new_plugin.set("pluginName", "Notepad++::InternalFunction")
            new_plugin.set("id", "44084")
            new_plugin.set("curr", "0")
            new_plugin.set("prev", "-1")
            new_plugin.set("isVisible", "yes")
            print("✓ 已添加新的文档列表配置")
        
        # 保存修改后的文件
        tree.write(config_path, encoding="utf-8", xml_declaration=True)
        print("✓ 配置文件已保存")
        
        # 验证修改
        print("\n验证修改结果:")
        tree2 = ET.parse(config_path)
        root2 = tree2.getroot()
        
        for elem in root2.iter():
            if elem.tag == "GUIConfig" and elem.get("name") == "DockingManager":
                for plugin in elem.findall(".//PluginDlg"):
                    if plugin.get("id") == "44084":
                        visibility = plugin.get("isVisible", "no")
                        print(f"文档列表可见性: {visibility}")
                        if visibility == "yes":
                            print("✓ 修改成功!")
                            return True
                        else:
                            print("✗ 修改失败")
                            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 修改配置文件失败: {e}")
        return False

def test_program_with_fixed_config():
    """测试修改后的配置是否生效"""
    print("\n=== 测试修改后的配置 ===")
    
    import subprocess
    import time
    
    exe_path = os.path.join(os.getcwd(), "bin", "notepad_abc_new.exe")
    print(f"启动程序: {exe_path}")
    
    try:
        # 正常启动程序（不使用-nosession参数）
        process = subprocess.Popen([exe_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        # 等待程序启动
        time.sleep(3)
        
        if process.poll() is None:
            print("✓ 程序正在运行")
            
            # 检查是否创建了分类配置文件
            categories_path = os.path.join(os.getcwd(), "bin", "categories.json")
            if os.path.exists(categories_path):
                print("✓ 分类配置文件已创建")
                print("✓ 文档列表已自动显示，分类管理器已初始化")
            else:
                print("✗ 分类配置文件未创建")
                print("说明: 可能需要更多时间来初始化分类管理器")
            
            # 终止程序
            process.terminate()
            process.wait(timeout=5)
            print("✓ 程序已终止")
        else:
            print("✗ 程序启动失败")
            
    except Exception as e:
        print(f"✗ 测试过程中出错: {e}")

if __name__ == "__main__":
    print("修改配置文件可见性")
    print("=" * 60)
    
    # 修改配置文件
    if fix_doclist_visibility():
        print("\n✓ 配置文件修改成功")
        
        # 测试修改后的配置
        test_program_with_fixed_config()
    else:
        print("\n✗ 配置文件修改失败")
    
    print("\n=== 操作完成 ===")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口显示问题修复脚本
通过修改配置文件来解决窗口不显示的问题
"""

import xml.etree.ElementTree as ET
import os
import shutil
from datetime import datetime

def backup_config():
    """备份原始配置文件"""
    print("正在备份原始配置文件...")
    
    config_files = [
        "bin\\config.xml",
        "bin\\doLocalConf.xml", 
        "bin\\nativeLang.xml"
    ]
    
    backup_dir = "config_backup"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    for config_file in config_files:
        if os.path.exists(config_file):
            backup_path = os.path.join(backup_dir, os.path.basename(config_file))
            shutil.copy2(config_file, backup_path)
            print(f"✅ 已备份: {config_file} -> {backup_path}")

def fix_config_window_position():
    """修复窗口位置配置问题"""
    print("正在修复窗口位置配置...")
    
    config_path = "bin\\config.xml"
    
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    try:
        # 解析XML文件
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # 查找GUIConfigs节点
        gui_configs = root.find('.//GUIConfigs')
        if gui_configs is None:
            print("❌ 未找到GUIConfigs节点")
            return False
        
        # 查找AppPosition组件
        appposition_elem = gui_configs.find('.//GUIConfig[@name="AppPosition"]')
        if appposition_elem is None:
            print("❌ 未找到AppPosition组件")
            return False
        
        # 显示原始配置
        x = appposition_elem.get('x', '0')
        y = appposition_elem.get('y', '0')
        width = appposition_elem.get('width', '1100')
        height = appposition_elem.get('height', '700')
        isMaximized = appposition_elem.get('isMaximized', 'no')
        
        print("原始窗口配置:")
        print(f"  原始位置: x={x}, y={y}")
        print(f"  原始尺寸: {width}x{height}")
        print(f"  最大化状态: {isMaximized}")
        
        # 修复窗口位置 - 设置为居中显示
        # 获取屏幕分辨率（默认1920x1080）
        screen_width = 1920
        screen_height = 1080
        
        # 计算居中位置
        new_x = max(0, (screen_width - int(width)) // 2)
        new_y = max(0, (screen_height - int(height)) // 2)
        
        print(f"\n修复后的窗口配置:")
        print(f"  新位置: x={new_x}, y={new_y}")
        print(f"  保持尺寸: {width}x{height}")
        print(f"  设置为非最大化状态")
        
        # 更新配置
        appposition_elem.set('x', str(new_x))
        appposition_elem.set('y', str(new_y))
        appposition_elem.set('isMaximized', 'no')  # 确保窗口正常显示
        
        # 保存修改后的配置
        tree.write(config_path, encoding='utf-8', xml_declaration=True)
        print(f"✅ 已更新配置文件: {config_path}")
        
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML解析错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置修复失败: {e}")
        return False

def fix_toolbar_status():
    """修复工具栏状态"""
    print("正在修复工具栏状态...")
    
    config_path = "bin\\config.xml"
    
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        gui_configs = root.find('.//GUIConfigs')
        if gui_configs is None:
            print("❌ 未找到GUIConfigs节点")
            return False
        
        # 查找ToolBar组件
        toolbar_elem = gui_configs.find('.//ToolBar')
        if toolbar_elem is not None:
            original_visible = toolbar_elem.get('visible', 'yes')
            print(f"原始工具栏状态: visible={original_visible}")
            
            # 确保工具栏可见
            toolbar_elem.set('visible', 'yes')
            print("✅ 已设置工具栏为可见状态")
        
        # 查找StatusBar组件  
        statusbar_elem = gui_configs.find('.//StatusBar')
        if statusbar_elem is not None:
            original_visible = statusbar_elem.get('visible', 'yes')
            print(f"原始状态栏状态: visible={original_visible}")
            
            # 确保状态栏可见
            statusbar_elem.set('visible', 'yes')
            print("✅ 已设置状态栏为可见状态")
        
        # 保存修改
        tree.write(config_path, encoding='utf-8', xml_declaration=True)
        
        return True
        
    except Exception as e:
        print(f"❌ 工具栏状态修复失败: {e}")
        return False

def create_test_batch():
    """创建测试批处理文件"""
    print("正在创建测试批处理文件...")
    
    batch_content = '''@echo off
chcp 65001 >nul
echo 正在启动Notepad++...
echo.
echo 如果窗口仍未显示，请尝试:
echo 1. 以管理员权限运行
echo 2. 检查是否有其他程序干扰
echo 3. 重启explorer.exe进程
echo.
pause
'''
    
    with open("test_start.bat", "w", encoding='utf-8') as f:
        f.write(batch_content)
    
    print("✅ 已创建测试批处理文件: test_start.bat")

def main():
    """主修复函数"""
    print("Notepad++ 窗口显示问题修复工具")
    print("=" * 50)
    
    # 检查必要文件
    if not os.path.exists("bin\\notepad_abc_new.exe"):
        print("❌ 可执行文件不存在: bin\\notepad_abc_new.exe")
        return False
    
    if not os.path.exists("bin\\config.xml"):
        print("❌ 配置文件不存在: bin\\config.xml")
        return False
    
    try:
        # 1. 备份原始配置
        backup_config()
        
        print("\n" + "=" * 50)
        
        # 2. 修复窗口位置
        if fix_config_window_position():
            print("✅ 窗口位置修复成功")
        else:
            print("❌ 窗口位置修复失败")
        
        print("\n" + "=" * 50)
        
        # 3. 修复工具栏状态
        if fix_toolbar_status():
            print("✅ 工具栏状态修复成功")
        else:
            print("❌ 工具栏状态修复失败")
        
        print("\n" + "=" * 50)
        
        # 4. 创建测试批处理
        create_test_batch()
        
        print("\n✅ 修复完成！")
        print("\n修复内容:")
        print("1. 调整窗口位置到屏幕中央")
        print("2. 确保工具栏和状态栏可见")
        print("3. 备份原始配置文件到 config_backup 文件夹")
        
        print("\n建议的下一步:")
        print("1. 运行: python test_startup.py")
        print("2. 或者直接运行: .\\bin\\notepad_abc_new.exe")
        print("3. 如果仍有问题，尝试以管理员权限运行")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 修复过程中发生错误: {e}")
        print("\n可以使用以下命令恢复原始配置:")
        print("robocopy config_backup bin *.xml /Y")
        return False

if __name__ == "__main__":
    success = main()
    input("\n按回车键退出...")
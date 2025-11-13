#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试程序启动时是否创建配置文件
"""

import os
import time
import subprocess
import tempfile

def find_config_files():
    """查找可能的配置文件位置"""
    config_locations = [
        os.path.join(os.getcwd(), "config.xml"),
        os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml"),
        os.path.join(os.getenv("APPDATA"), "notepad_abc", "config.xml"),
        os.path.join(os.getenv("LOCALAPPDATA"), "Notepad++", "config.xml"),
        os.path.join(os.getenv("LOCALAPPDATA"), "notepad_abc", "config.xml"),
    ]
    
    print("=== 检查配置文件位置 ===")
    for location in config_locations:
        if os.path.exists(location):
            print(f"✓ 找到配置文件: {location}")
            # 读取文件内容检查是否包含文档列表配置
            try:
                with open(location, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "IDM_VIEW_DOCLIST" in content or "Document List" in content:
                        print("  ✓ 配置文件包含文档列表配置")
                    else:
                        print("  ✗ 配置文件不包含文档列表配置")
                return location
            except Exception as e:
                print(f"  ✗ 读取配置文件失败: {e}")
        else:
            print(f"✗ 配置文件不存在: {location}")
    
    return None

def test_program_startup():
    """测试程序启动并检查配置文件创建"""
    print("\n=== 启动程序测试 ===")
    
    # 先检查启动前是否有配置文件
    config_before = find_config_files()
    
    # 启动程序
    exe_path = os.path.join(os.getcwd(), "bin", "notepad_abc_new.exe")
    print(f"启动程序: {exe_path}")
    
    try:
        # 使用-nosession参数启动
        process = subprocess.Popen([exe_path, "-nosession"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        # 等待程序启动
        time.sleep(3)
        
        # 检查程序是否在运行
        if process.poll() is None:
            print("✓ 程序正在运行")
            
            # 等待一段时间让程序可能创建配置文件
            time.sleep(2)
            
            # 检查是否创建了配置文件
            config_after = find_config_files()
            
            if config_after and (not config_before or config_after != config_before):
                print("✓ 程序创建了新的配置文件")
            else:
                print("✗ 程序没有创建新的配置文件")
            
            # 终止程序
            process.terminate()
            process.wait(timeout=5)
            print("✓ 程序已终止")
        else:
            print("✗ 程序启动失败")
            
    except Exception as e:
        print(f"✗ 测试过程中出错: {e}")

def check_existing_config_content():
    """检查现有配置文件的内容"""
    print("\n=== 检查现有配置文件内容 ===")
    
    config_locations = [
        os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml"),
        os.path.join(os.getenv("APPDATA"), "notepad_abc", "config.xml"),
        os.path.join(os.getenv("LOCALAPPDATA"), "Notepad++", "config.xml"),
        os.path.join(os.getenv("LOCALAPPDATA"), "notepad_abc", "config.xml"),
    ]
    
    for location in config_locations:
        if os.path.exists(location):
            print(f"\n检查配置文件: {location}")
            try:
                with open(location, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 检查关键配置项
                    checks = [
                        ("IDM_VIEW_DOCLIST", "文档列表配置"),
                        ("PluginDlg", "插件对话框配置"),
                        ("DockingManager", "停靠管理器配置"),
                        ("isVisible", "可见性配置"),
                    ]
                    
                    for keyword, description in checks:
                        if keyword in content:
                            print(f"  ✓ 包含{description}")
                        else:
                            print(f"  ✗ 不包含{description}")
                    
                    # 显示部分内容
                    print("\n配置文件片段:")
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "PluginDlg" in line or "DockingManager" in line:
                            start = max(0, i-2)
                            end = min(len(lines), i+3)
                            for j in range(start, end):
                                print(f"  {j+1}: {lines[j]}")
                            break
                            
            except Exception as e:
                print(f"  ✗ 读取配置文件失败: {e}")

if __name__ == "__main__":
    print("测试程序配置文件创建")
    print("=" * 50)
    
    # 检查现有配置文件
    check_existing_config_content()
    
    # 测试程序启动
    test_program_startup()
    
    print("\n=== 测试完成 ===")
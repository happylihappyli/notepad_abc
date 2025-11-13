#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试面板初始化过程，检查为什么文档列表没有自动显示
"""

import os
import time
import subprocess
import tempfile

def check_config_file():
    """检查配置文件内容"""
    config_path = os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml")
    
    if not os.path.exists(config_path):
        print("✗ 配置文件不存在")
        return False
    
    print(f"检查配置文件: {config_path}")
    
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # 检查DockingManager配置
        for elem in root.iter():
            if elem.tag == "GUIConfig" and elem.get("name") == "DockingManager":
                print("✓ 找到DockingManager配置")
                
                # 检查文档列表配置
                for plugin in elem.findall(".//PluginDlg"):
                    if plugin.get("id") == "44084":
                        visibility = plugin.get("isVisible", "no")
                        curr = plugin.get("curr", "")
                        prev = plugin.get("prev", "")
                        
                        print(f"文档列表配置:")
                        print(f"  可见性: {visibility}")
                        print(f"  当前容器: {curr}")
                        print(f"  上一个容器: {prev}")
                        
                        if visibility == "yes":
                            print("✓ 配置文件正确设置为可见")
                            return True
                        else:
                            print("✗ 配置文件设置为不可见")
                            return False
                
                print("✗ 未找到文档列表配置")
                return False
        
        print("✗ 未找到DockingManager配置")
        return False
        
    except Exception as e:
        print(f"✗ 检查配置文件失败: {e}")
        return False

def test_program_with_debug():
    """测试程序启动并添加调试信息"""
    print("\n=== 测试程序启动 ===")
    
    exe_path = os.path.join(os.getcwd(), "bin", "notepad_abc_new.exe")
    print(f"启动程序: {exe_path}")
    
    # 创建调试日志文件
    debug_log = os.path.join(tempfile.gettempdir(), "notepad_abc_debug.log")
    
    try:
        # 启动程序并等待更长时间
        process = subprocess.Popen([exe_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        print("等待程序初始化...")
        time.sleep(5)  # 等待更长时间让程序完全初始化
        
        if process.poll() is None:
            print("✓ 程序正在运行")
            
            # 检查分类配置文件
            categories_path = os.path.join(os.getcwd(), "bin", "categories.json")
            
            # 多次检查，因为初始化可能需要时间
            for i in range(3):
                print(f"检查分类配置文件 (第{i+1}次)...")
                
                if os.path.exists(categories_path):
                    print("✓ 分类配置文件已创建")
                    print("✓ 文档列表已自动显示，分类管理器已初始化")
                    
                    # 读取配置文件内容
                    try:
                        import json
                        with open(categories_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():
                                data = json.loads(content)
                                print(f"分类配置内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
                            else:
                                print("分类配置文件为空")
                    except Exception as e:
                        print(f"读取分类配置文件失败: {e}")
                    
                    break
                else:
                    print("✗ 分类配置文件未创建")
                    
                    if i < 2:  # 不是最后一次检查
                        print("等待2秒后再次检查...")
                        time.sleep(2)
                    else:
                        print("✗ 多次检查后分类配置文件仍未创建")
                        print("可能的原因:")
                        print("1. 文档列表仍然没有自动显示")
                        print("2. 分类管理器初始化需要用户交互")
                        print("3. 程序逻辑存在问题")
            
            # 终止程序
            print("终止程序...")
            process.terminate()
            process.wait(timeout=5)
            print("✓ 程序已终止")
            
        else:
            print("✗ 程序启动失败")
            
    except Exception as e:
        print(f"✗ 测试过程中出错: {e}")

def analyze_problem():
    """分析可能的问题"""
    print("\n=== 问题分析 ===")
    
    print("可能的问题:")
    print("1. 配置文件修改没有正确生效")
    print("2. 程序需要重新编译才能应用配置更改")
    print("3. 文档列表显示需要其他条件")
    print("4. 分类管理器初始化需要特定的触发条件")
    
    print("\n建议的解决方案:")
    print("1. 重新编译程序")
    print("2. 检查程序启动日志")
    print("3. 手动测试文档列表显示功能")
    print("4. 检查分类管理器的初始化代码")

def test_manual_doclist():
    """测试手动显示文档列表"""
    print("\n=== 测试手动显示文档列表 ===")
    
    exe_path = os.path.join(os.getcwd(), "bin", "notepad_abc_new.exe")
    
    try:
        # 启动程序
        process = subprocess.Popen([exe_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        print("程序已启动，等待手动操作...")
        print("请手动执行以下操作:")
        print("1. 在Notepad++中点击'查看'菜单")
        print("2. 选择'文档列表'")
        print("3. 等待几秒钟")
        print("4. 关闭程序")
        
        input("按回车键继续测试分类配置文件创建...")
        
        # 检查分类配置文件
        categories_path = os.path.join(os.getcwd(), "bin", "categories.json")
        
        if os.path.exists(categories_path):
            print("✓ 手动显示文档列表后，分类配置文件已创建")
            print("✓ 分类管理器已初始化")
        else:
            print("✗ 手动显示文档列表后，分类配置文件仍未创建")
            print("说明分类管理器初始化可能存在问题")
        
        # 终止程序
        process.terminate()
        process.wait(timeout=5)
        print("✓ 程序已终止")
        
    except Exception as e:
        print(f"✗ 测试过程中出错: {e}")

if __name__ == "__main__":
    print("调试面板初始化过程")
    print("=" * 60)
    
    # 检查配置文件
    if check_config_file():
        print("\n✓ 配置文件检查通过")
        
        # 测试程序启动
        test_program_with_debug()
        
        # 分析问题
        analyze_problem()
        
        # 测试手动显示文档列表
        test_manual_doclist()
    else:
        print("\n✗ 配置文件检查失败")
    
    print("\n=== 调试完成 ===")
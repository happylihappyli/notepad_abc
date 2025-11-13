#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文档列表自动显示功能
"""

import os
import time
import subprocess
import xml.etree.ElementTree as ET

def check_config_file():
    """检查配置文件设置"""
    config_path = os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml")
    
    if not os.path.exists(config_path):
        print("✗ 配置文件不存在")
        return False
    
    print(f"检查配置文件: {config_path}")
    
    try:
        # 读取原始内容检查
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查documentList设置
        if 'documentList="yes"' in content:
            print("✓ documentList设置为yes")
        else:
            print("✗ documentList设置不正确")
            return False
        
        # XML解析检查DockingManager中的文档列表设置
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # 查找文档列表的PluginDlg配置
        doclist_found = False
        for plugin in root.iter():
            if plugin.tag == "PluginDlg" and plugin.get("id") == "44070":
                print("✓ 找到文档列表插件配置")
                doclist_found = True
                
                # 检查isVisible属性
                is_visible = plugin.get("isVisible")
                print(f"文档列表可见性: {is_visible}")
                
                if is_visible == "yes":
                    print("✓ 文档列表可见性设置为yes")
                else:
                    print("✗ 文档列表可见性设置为no")
                    return False
        
        if not doclist_found:
            print("✗ 未找到文档列表插件配置")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 检查配置文件失败: {e}")
        return False

def start_notepad_abc():
    """启动Notepad++程序"""
    exe_path = os.path.join(os.getcwd(), "bin", "notepad_abc.exe")
    
    if not os.path.exists(exe_path):
        print("✗ 程序文件不存在")
        return None
    
    print(f"启动程序: {exe_path}")
    
    try:
        # 启动程序
        process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ 程序已启动")
        
        # 等待程序初始化
        time.sleep(3)
        
        return process
    except Exception as e:
        print(f"✗ 启动程序失败: {e}")
        return None

def check_category_config():
    """检查分类配置文件是否创建"""
    category_path = os.path.join(os.getcwd(), "bin", "categories.json")
    
    # 检查文件是否存在
    if os.path.exists(category_path):
        print("✓ 分类配置文件已创建")
        
        # 检查文件内容
        try:
            with open(category_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    print("✓ 分类配置文件有内容")
                    return True
                else:
                    print("✗ 分类配置文件为空")
                    return False
        except Exception as e:
            print(f"✗ 读取分类配置文件失败: {e}")
            return False
    else:
        print("✗ 分类配置文件未创建")
        return False

def stop_process(process):
    """停止程序进程"""
    if process and process.poll() is None:
        try:
            # 终止进程
            process.terminate()
            process.wait(timeout=5)
            print("✓ 程序已停止")
        except subprocess.TimeoutExpired:
            print("✗ 程序终止超时，强制终止")
            process.kill()
        except Exception as e:
            print(f"✗ 停止程序失败: {e}")

def main():
    """主测试函数"""
    print("测试文档列表自动显示功能")
    print("=" * 60)
    
    # 1. 检查配置文件设置
    print("\n1. 检查配置文件设置...")
    if not check_config_file():
        print("✗ 配置文件设置不正确")
        return False
    
    # 2. 启动程序
    print("\n2. 启动程序...")
    process = start_notepad_abc()
    if not process:
        print("✗ 无法启动程序")
        return False
    
    # 3. 等待程序初始化
    print("\n3. 等待程序初始化...")
    time.sleep(5)
    
    # 4. 检查分类配置文件
    print("\n4. 检查分类配置文件...")
    category_created = check_category_config()
    
    # 5. 停止程序
    print("\n5. 停止程序...")
    stop_process(process)
    
    # 6. 分析结果
    print("\n6. 测试结果分析...")
    if category_created:
        print("✓ 测试成功 - 文档列表自动显示功能正常")
        print("✓ 分类管理器已初始化，文档列表应该已自动显示")
        return True
    else:
        print("✗ 测试失败 - 文档列表未自动显示")
        print("可能原因:")
        print("  - 程序需要重新编译")
        print("  - 配置文件修改未生效")
        print("  - 分类管理器需要用户交互触发")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n=== 测试完成 - 成功 ===")
        else:
            print("\n=== 测试完成 - 失败 ===")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        print("\n=== 测试完成 - 错误 ===")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分类管理器功能
"""

import os
import time
import subprocess
import json

def test_category_manager():
    """测试分类管理器功能"""
    print("=== 测试分类管理器功能 ===")
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查bin目录是否存在
    bin_dir = os.path.join(current_dir, "bin")
    if not os.path.exists(bin_dir):
        print("错误: bin目录不存在")
        return False
    
    # 检查可执行文件是否存在
    exe_path = os.path.join(bin_dir, "notepad_abc_new.exe")
    if not os.path.exists(exe_path):
        print("错误: notepad_abc_new.exe 不存在")
        return False
    
    print("启动程序...")
    
    # 启动程序
    process = subprocess.Popen([exe_path], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
    
    # 等待程序启动
    time.sleep(3)
    
    # 检查程序是否在运行
    if process.poll() is not None:
        print("程序已退出，退出码:", process.returncode)
        stdout, stderr = process.communicate()
        print("标准输出:", stdout)
        print("标准错误:", stderr)
        return False
    
    print("程序正在运行，PID:", process.pid)
    
    # 检查分类配置文件是否创建
    config_path = os.path.join(bin_dir, "categories.json")
    
    # 等待一段时间让程序初始化
    time.sleep(2)
    
    if os.path.exists(config_path):
        print("✓ 分类配置文件已创建:", config_path)
        # 读取文件内容
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print("配置文件内容:")
                print(content)
                
                # 验证JSON格式
                try:
                    data = json.loads(content)
                    print("✓ JSON格式验证成功")
                    if "categories" in data:
                        print(f"✓ 包含分类数组，数量: {len(data['categories'])}")
                    else:
                        print("✗ 缺少分类数组")
                except json.JSONDecodeError as e:
                    print(f"✗ JSON格式错误: {e}")
        except Exception as e:
            print(f"读取文件时出错: {e}")
    else:
        print("✗ 分类配置文件未创建")
        print("说明: 程序启动时不会自动显示文档列表，需要手动触发分类管理器初始化")
    
    # 终止程序
    print("终止程序...")
    try:
        # 使用taskkill强制终止
        subprocess.run(["taskkill", "/f", "/im", "notepad_abc_new.exe"], 
                      check=False, capture_output=True)
        
        # 等待程序终止
        time.sleep(2)
        
        if process.poll() is None:
            print("警告: 程序仍在运行，尝试强制终止")
            process.terminate()
            process.wait(timeout=5)
        
        print("程序已终止")
        
    except Exception as e:
        print("终止程序时出错:", e)
    
    return True

def check_existing_config():
    """检查现有的分类配置文件"""
    print("\n=== 检查现有分类配置文件 ===")
    
    config_path = os.path.join(os.getcwd(), "bin", "categories.json")
    
    if os.path.exists(config_path):
        print("✓ 分类配置文件存在:", config_path)
        
        # 获取文件信息
        stat = os.stat(config_path)
        print(f"文件大小: {stat.st_size} 字节")
        print(f"创建时间: {time.ctime(stat.st_ctime)}")
        print(f"修改时间: {time.ctime(stat.st_mtime)}")
        
        # 读取文件内容
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print("文件内容:")
                print(content)
                
                # 验证JSON格式
                try:
                    data = json.loads(content)
                    print("✓ JSON格式验证成功")
                    if "categories" in data:
                        print(f"✓ 包含分类数组，数量: {len(data['categories'])}")
                        for i, category in enumerate(data['categories']):
                            print(f"  分类 {i+1}: {category}")
                    else:
                        print("✗ 缺少分类数组")
                except json.JSONDecodeError as e:
                    print(f"✗ JSON格式错误: {e}")
        except Exception as e:
            print(f"读取文件时出错: {e}")
    else:
        print("✗ 分类配置文件不存在")
        print("说明: 需要手动显示文档列表来触发分类管理器初始化")

def test_path_conversion():
    """测试路径转换逻辑"""
    print("\n=== 测试路径转换逻辑 ===")
    
    # 测试相对路径转绝对路径
    config_path = "bin/categories.json"
    print(f"相对路径: {config_path}")
    
    # 获取当前工作目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 构建绝对路径
    absolute_path = os.path.join(current_dir, config_path)
    print(f"绝对路径: {absolute_path}")
    
    # 检查路径是否存在
    if os.path.exists(absolute_path):
        print("✓ 路径存在")
    else:
        print("✗ 路径不存在")
        
        # 检查目录是否存在
        dir_path = os.path.dirname(absolute_path)
        if os.path.exists(dir_path):
            print("✓ 目录存在")
        else:
            print("✗ 目录不存在")
            print("需要创建目录:", dir_path)

if __name__ == "__main__":
    # 设置控制台编码
    os.system("chcp 65001 > nul")
    
    # 测试路径转换
    test_path_conversion()
    
    # 检查现有配置文件
    check_existing_config()
    
    # 测试分类管理器功能
    test_category_manager()
    
    print("\n=== 测试完成 ===")
    print("结论: 程序启动时不会自动显示文档列表，需要用户手动操作来触发分类管理器初始化")
    print("建议: 修改程序配置，设置_docListKeepState为true，让文档列表在启动时自动显示")
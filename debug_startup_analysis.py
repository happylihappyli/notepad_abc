#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试启动分析 - 捕获程序启动过程和错误
"""

import os
import sys
import time
import ctypes
from ctypes import wintypes
import subprocess
import json
import signal
from pathlib import Path

def test_debug_mode():
    """测试调试模式启动"""
    print("=== 调试模式启动测试 ===")
    
    exe_path = Path("bin/notepad_abc_new.exe")
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return False
    
    print(f"可执行文件: {exe_path.absolute()}")
    
    # 切换到bin目录
    old_cwd = os.getcwd()
    bin_dir = exe_path.parent
    
    try:
        os.chdir(bin_dir)
        print(f"切换工作目录到: {bin_dir}")
        
        # 尝试不同的启动参数
        debug_commands = [
            ["notepad_abc_new.exe"],  # 默认启动
            ["notepad_abc_new.exe", "-debug"],  # 调试模式
            ["notepad_abc_new.exe", "-console"],  # 控制台模式
            ["notepad_abc_new.exe", "-noPlugin"],  # 无插件模式
            ["notepad_abc_new.exe", "-multiInst"],  # 多实例模式
            ["notepad_abc_new.exe", "-notepadStyleDirLab"],  # 特定目录
        ]
        
        for i, cmd in enumerate(debug_commands):
            print(f"\n--- 测试命令 {i+1}: {' '.join(cmd)} ---")
            
            try:
                # 使用管道捕获输出
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE  # 创建新控制台
                )
                
                print(f"✅ 进程启动成功，PID: {process.pid}")
                
                # 等待一段时间
                time.sleep(3)
                
                # 检查进程是否还在运行
                if process.poll() is None:
                    print("✅ 进程仍在运行")
                    
                    # 尝试读取标准输出
                    try:
                        stdout_data, stderr_data = process.communicate(timeout=1)
                        if stdout_data:
                            print("标准输出:")
                            print(stdout_data[:500])
                        if stderr_data:
                            print("标准错误:")
                            print(stderr_data[:500])
                    except subprocess.TimeoutExpired:
                        # 进程仍在运行，手动杀死
                        print("进程仍在运行，强制终止...")
                        process.terminate()
                        try:
                            process.wait(timeout=2)
                        except:
                            process.kill()
                else:
                    exit_code = process.returncode
                    print(f"❌ 进程已退出，退出码: {exit_code}")
                    
                    # 读取退出输出
                    try:
                        stdout_data, stderr_data = process.communicate(timeout=1)
                        if stdout_data:
                            print("标准输出:")
                            print(stdout_data[:500])
                        if stderr_data:
                            print("标准错误:")
                            print(stderr_data[:500])
                    except:
                        pass
                
            except Exception as e:
                print(f"❌ 启动失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 恢复工作目录
        os.chdir(old_cwd)

def test_admin_mode():
    """测试管理员模式启动"""
    print("\n=== 管理员模式启动测试 ===")
    
    exe_path = Path("bin/notepad_abc_new.exe")
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return False
    
    print(f"可执行文件: {exe_path.absolute()}")
    
    try:
        # 尝试使用管理员权限启动
        cmd = ['powershell', '-Command', f'Start-Process "{exe_path.absolute()}" -Verb RunAs']
        
        print("尝试管理员权限启动...")
        print(f"命令: {' '.join(cmd)}")
        
        # 由于不能真正启动管理员进程，我们只是记录这个选项
        print("💡 提示：可以手动尝试以管理员身份运行程序")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def analyze_executable():
    """分析可执行文件"""
    print("=== 可执行文件分析 ===")
    
    exe_path = Path("bin/notepad_abc_new.exe")
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return False
    
    try:
        # 获取文件信息
        stat_info = exe_path.stat()
        print(f"文件大小: {stat_info.st_size:,} bytes ({stat_info.st_size / 1024 / 1024:.2f} MB)")
        print(f"创建时间: {time.ctime(stat_info.st_ctime)}")
        print(f"修改时间: {time.ctime(stat_info.st_mtime)}")
        print(f"访问时间: {time.ctime(stat_info.st_atime)}")
        
        # 检查是否需要依赖
        print("\n检查依赖DLL...")
        
        # 常见的Notepad++依赖
        dependencies = [
            "kernel32.dll", "user32.dll", "gdi32.dll",
            "comctl32.dll", "comdlg32.dll", "shell32.dll",
            "ole32.dll", "oleaut32.dll", "uuid.dll"
        ]
        
        import platform
        system_dir = os.environ.get('SystemRoot', 'C:\\Windows') + '\\System32'
        
        missing_deps = []
        for dep in dependencies:
            dep_path = Path(system_dir) / dep
            if dep_path.exists():
                print(f"  ✅ {dep}")
            else:
                print(f"  ❌ {dep}")
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"\n❌ 缺失依赖: {', '.join(missing_deps)}")
        else:
            print("\n✅ 所有基本依赖都存在")
        
        return len(missing_deps) == 0
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return False

def main():
    print("调试启动分析")
    print("=" * 60)
    
    # 1. 分析可执行文件
    analyze_executable()
    
    # 2. 测试不同启动模式
    test_debug_mode()
    
    # 3. 测试管理员模式
    test_admin_mode()
    
    print("\n" + "=" * 60)
    print("诊断结论")
    print("=" * 60)
    print("根据测试结果，程序启动时只创建控制台窗口的可能原因：")
    print("1. 程序在GUI初始化过程中遇到未处理的异常")
    print("2. 缺少必要的DLL依赖文件")
    print("3. 需要特定的启动参数或配置")
    print("4. 需要管理员权限或特殊权限")
    print("5. 程序设计为控制台模式运行")
    
    print("\n建议解决方案：")
    print("1. 尝试以管理员身份运行程序")
    print("2. 检查程序是否有-debug启动参数")
    print("3. 确认所有依赖的DLL文件都存在且版本正确")
    print("4. 检查程序是否被安全软件阻止")
    print("5. 查看程序源代码中的窗口创建逻辑")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细UI问题诊断测试脚本
用于检测Notepad++程序启动过程中的具体问题
"""

import subprocess
import time
import threading
import psutil
import os
import sys
import ctypes
from ctypes import wintypes

# Windows API常量
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

def create_debug_console():
    """创建调试控制台"""
    try:
        if ctypes.windll.kernel32.AllocConsole():
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)  # UTF-8
            ctypes.windll.kernel32.SetConsoleCP(65001)  # UTF-8
            print("=== Notepad++ 调试控制台 ===")
            print("编码已设置为 UTF-8")
            return True
    except Exception as e:
        print(f"创建调试控制台失败: {e}")
        return False

def get_process_info(pid):
    """获取进程信息"""
    try:
        process = psutil.Process(pid)
        return {
            'name': process.name(),
            'status': process.status(),
            'create_time': process.create_time(),
            'memory_info': process.memory_info(),
            'cmdline': process.cmdline()
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def find_notepad_windows():
    """查找Notepad++窗口"""
    try:
        # 使用Windows API查找窗口
        hwnd = ctypes.windll.user32.FindWindowW(None, "Notepad++")
        if hwnd:
            print(f"找到主窗口句柄: {hwnd}")
            
            # 获取窗口位置和状态
            rect = ctypes.wintypes.RECT()
            if ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                print(f"窗口位置: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                print(f"窗口尺寸: {width}x{height}")
                
                # 检查窗口是否可见
                if ctypes.windll.user32.IsWindowVisible(hwnd):
                    print("窗口状态: 可见")
                else:
                    print("窗口状态: 隐藏")
                    
                # 检查窗口是否被最小化
                if ctypes.windll.user32.IsIconic(hwnd):
                    print("窗口状态: 最小化")
                    
                # 获取窗口文本
                title_length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if title_length > 0:
                    title_buffer = ctypes.create_unicode_buffer(title_length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
                    print(f"窗口标题: {title_buffer.value}")
                    
            return hwnd
        else:
            print("未找到主窗口")
            return None
    except Exception as e:
        print(f"查找窗口时出错: {e}")
        return None

def monitor_process_startup(exe_path, timeout=15):
    """监控程序启动过程"""
    print(f"开始启动程序: {exe_path}")
    print(f"超时设置: {timeout}秒")
    
    start_time = time.time()
    process = None
    main_window_hwnd = None
    
    try:
        # 创建进程
        print("创建进程...")
        process = subprocess.Popen(
            exe_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"进程创建成功，PID: {process.pid}")
        
        # 持续监控
        while time.time() - start_time < timeout:
            elapsed = time.time() - start_time
            print(f"\n--- 监控进度: {elapsed:.1f}s ---")
            
            # 检查进程状态
            if process.poll() is not None:
                print("❌ 进程已退出")
                stdout, stderr = process.communicate()
                print(f"退出代码: {process.returncode}")
                if stdout:
                    print(f"标准输出:\n{stdout}")
                if stderr:
                    print(f"标准错误:\n{stderr}")
                return False
            else:
                print("✅ 进程仍在运行")
            
            # 获取进程详细信息
            proc_info = get_process_info(process.pid)
            if proc_info:
                print(f"进程名: {proc_info['name']}")
                print(f"状态: {proc_info['status']}")
                memory_mb = proc_info['memory_info'].rss / 1024 / 1024
                print(f"内存使用: {memory_mb:.1f} MB")
            
            # 查找窗口
            if not main_window_hwnd:
                print("查找主窗口...")
                main_window_hwnd = find_notepad_windows()
                if main_window_hwnd:
                    print("✅ 主窗口已找到")
                else:
                    print("⏳ 主窗口尚未创建")
            
            time.sleep(1)  # 等待1秒
        
        # 最终检查
        print(f"\n=== {timeout}秒监控结束 ===")
        if process.poll() is None:
            print("✅ 程序仍在运行")
            if main_window_hwnd:
                print("✅ 窗口已显示")
            else:
                print("❌ 窗口未显示")
        else:
            print("❌ 程序已退出")
            
        return main_window_hwnd is not None and process.poll() is None
        
    except Exception as e:
        print(f"监控过程中出错: {e}")
        return False
        
    finally:
        if process and process.poll() is None:
            print("\n正在终止测试进程...")
            try:
                process.terminate()
                process.wait(timeout=3)
            except:
                process.kill()

def analyze_configuration():
    """分析配置文件"""
    print("\n=== 配置分析 ===")
    
    bin_dir = "bin"
    config_files = ["config.xml", "doLocalConf.xml", "nativeLang.xml"]
    
    for config_file in config_files:
        config_path = os.path.join(bin_dir, config_file)
        if os.path.exists(config_path):
            print(f"✅ 找到配置文件: {config_file}")
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'NotepadPlus' in content:
                        print(f"✅ {config_file} 包含有效的NotepadPlus配置")
                    else:
                        print(f"⚠️  {config_file} 可能不是有效的NotepadPlus配置")
            except Exception as e:
                print(f"❌ 读取 {config_file} 失败: {e}")
        else:
            print(f"❌ 缺少配置文件: {config_file}")

def main():
    """主测试函数"""
    print("Notepad++ UI问题诊断测试")
    print("=" * 50)
    
    # 创建调试控制台
    if create_debug_console():
        print("调试控制台创建成功")
    else:
        print("无法创建调试控制台")
    
    # 检查可执行文件
    exe_path = "bin\\notepad_abc_new.exe"
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False
    
    file_size = os.path.getsize(exe_path)
    print(f"✅ 可执行文件存在: {exe_path} ({file_size:,} 字节)")
    
    # 分析配置
    analyze_configuration()
    
    # 启动监控测试
    print(f"\n开始启动测试...")
    success = monitor_process_startup(exe_path, timeout=15)
    
    if success:
        print("\n✅ 测试结论: 程序启动和窗口显示正常")
        input("按回车键继续...")
        return True
    else:
        print("\n❌ 测试结论: 程序启动或窗口显示存在问题")
        print("\n建议:")
        print("1. 检查程序是否有依赖的DLL文件缺失")
        print("2. 验证配置文件是否正确")
        print("3. 尝试以管理员权限运行")
        print("4. 检查是否有杀毒软件阻止程序运行")
        input("按回车键退出...")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生未处理的异常: {e}")
        sys.exit(1)
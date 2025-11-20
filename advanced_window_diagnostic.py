#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级窗口诊断脚本
深度分析notepad_abc程序窗口创建失败的原因
"""

import subprocess
import time
import ctypes
from ctypes import wintypes
import threading
import sys
import os
import json

def check_system_resources():
    """检查系统资源状态"""
    print("=== 系统资源检查 ===")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"总内存: {memory.total // (1024**3)} GB")
        print(f"可用内存: {memory.available // (1024**3)} GB ({memory.percent}% 使用)")
        
        disk = psutil.disk_usage('.')
        print(f"磁盘使用: {disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB")
        
        process_count = len(psutil.pids())
        print(f"运行进程数: {process_count}")
    except ImportError:
        print("psutil不可用，跳过系统资源检查")

def analyze_processes():
    """分析当前运行的进程"""
    print("\n=== 进程分析 ===")
    
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True, encoding='utf-8')
        lines = result.stdout.split('\n')
        
        notepad_processes = [line for line in lines if 'notepad' in line.lower()]
        
        print(f"找到 {len(notepad_processes)} 个notepad相关进程:")
        for proc in notepad_processes:
            print(f"  {proc}")
            
    except Exception as e:
        print(f"进程分析失败: {e}")

def check_dll_files():
    """检查DLL文件"""
    print("\n=== DLL文件检查 ===")
    
    bin_dir = "bin"
    if os.path.exists(bin_dir):
        print(f"检查 {bin_dir} 目录:")
        dll_files = [f for f in os.listdir(bin_dir) if f.endswith('.dll')]
        print(f"找到 {len(dll_files)} 个DLL文件:")
        for dll in dll_files:
            print(f"  {dll}")
    else:
        print(f"bin目录不存在: {bin_dir}")

def monitor_process_startup():
    """监控程序启动过程"""
    print("\n=== 程序启动监控 ===")
    
    exe_path = "bin\\notepad_abc_new.exe"
    
    if not os.path.exists(exe_path):
        print(f"可执行文件不存在: {exe_path}")
        return
    
    try:
        # 启动程序
        print(f"启动程序: {exe_path}")
        process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        pid = process.pid
        print(f"进程已启动，PID: {pid}")
        
        # 监控5秒
        for i in range(5):
            time.sleep(1)
            
            # 检查进程是否还在运行
            poll_result = process.poll()
            if poll_result is not None:
                print(f"第{i+1}秒: 进程已退出，返回码={poll_result}")
                
                # 获取错误信息
                try:
                    stderr_output, stdout_output = process.communicate(timeout=1)
                    if stderr_output:
                        print(f"错误输出: {stderr_output}")
                    if stdout_output:
                        print(f"标准输出: {stdout_output}")
                except:
                    print("无法获取退出信息")
                break
            else:
                print(f"第{i+1}秒: 进程仍在运行")
        
        # 终止进程
        print("终止测试进程...")
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            
    except Exception as e:
        print(f"启动监控失败: {e}")

def check_window_creation():
    """检查窗口创建情况"""
    print("\n=== 窗口创建检查 ===")
    
    # 枚举所有窗口
    user32 = ctypes.windll.user32
    windows_info = []
    
    def enum_windows_callback(hwnd, lParam):
        windows = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_int)).contents
        
        # 获取窗口类名
        class_name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_name, 256)
        
        # 获取窗口标题
        window_text = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, window_text, 256)
        
        windows_info.append({
            'hwnd': hwnd,
            'class_name': class_name.value,
            'window_text': window_text.value,
            'is_visible': user32.IsWindowVisible(hwnd)
        })
        
        return True
    
    try:
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.POINTER(ctypes.c_int))
        EnumWindowsProc = EnumWindowsProc(enum_windows_callback)
        
        windows_count = ctypes.c_int()
        user32.EnumWindows(EnumWindowsProc, ctypes.byref(windows_count))
        
        print(f"总共找到 {len(windows_info)} 个窗口")
        
        # 查找可能的notepad++窗口
        notepad_windows = []
        for win in windows_info:
            class_name_lower = win['class_name'].lower()
            window_text_lower = win['window_text'].lower()
            
            if any(keyword in class_name_lower for keyword in ['notepad', 'npp', 'notepad_plus']):
                notepad_windows.append(win)
            elif any(keyword in window_text_lower for keyword in ['notepad', 'notepad++', 'npp']):
                notepad_windows.append(win)
        
        if notepad_windows:
            print(f"找到 {len(notepad_windows)} 个可能的notepad++窗口:")
            for i, win in enumerate(notepad_windows):
                visibility = "可见" if win['is_visible'] else "隐藏"
                print(f"  {i+1}. 类名: {win['class_name']}")
                print(f"     标题: {win['window_text'][:50]}")
                print(f"     状态: {visibility}")
        else:
            print("未找到notepad++相关窗口")
            
    except Exception as e:
        print(f"窗口检查失败: {e}")

def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 基本功能测试 ===")
    
    # 测试是否能启动简单的Windows程序
    try:
        print("测试记事本程序...")
        notepad_process = subprocess.Popen(['notepad'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        
        # 检查记事本是否启动
        poll_result = notepad_process.poll()
        if poll_result is None:
            print("✅ 记事本程序可以正常启动")
            
            # 尝试关闭记事本
            notepad_process.terminate()
            notepad_process.wait(timeout=2)
            print("✅ 记事本程序可以正常关闭")
        else:
            print("❌ 记事本程序启动失败")
            
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")

def main():
    """主诊断函数"""
    print("开始高级窗口诊断")
    print("=" * 50)
    
    # 关闭可能运行的程序
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'notepad_abc_new.exe'], 
                      capture_output=True, text=True)
        time.sleep(1)
    except:
        pass
    
    # 执行各项检查
    check_system_resources()
    analyze_processes()
    check_dll_files()
    test_basic_functionality()
    check_window_creation()
    monitor_process_startup()
    
    print("\n" + "=" * 50)
    print("高级诊断完成")

if __name__ == "__main__":
    main()
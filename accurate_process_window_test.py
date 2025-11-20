#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确进程窗口测试 - 通过进程查找窗口
"""

import os
import sys
import time
import ctypes
from ctypes import wintypes
import subprocess
import json
import psutil
from pathlib import Path

# Windows API函数定义
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def find_windows_by_process(pid):
    """根据进程PID查找该进程的所有窗口"""
    process_windows = []
    
    def enum_window_proc(hwnd, lParam):
        # 获取创建窗口的进程ID
        process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        
        # 如果窗口属于指定进程
        if process_id.value == pid:
            title_buffer = ctypes.create_unicode_buffer(512)
            title_length = user32.GetWindowTextW(hwnd, title_buffer, 512)
            
            class_buffer = ctypes.create_unicode_buffer(256)
            class_length = user32.GetClassNameW(hwnd, class_buffer, 256)
            
            is_visible = bool(user32.IsWindowVisible(hwnd))
            is_enabled = bool(user32.IsWindowEnabled(hwnd))
            window_style = user32.GetWindowLongW(hwnd, -16)
            
            window_info = {
                "hwnd": hwnd,
                "title": title_buffer.value if title_length > 0 else "",
                "class_name": class_buffer.value if class_length > 0 else "",
                "is_visible": is_visible,
                "is_enabled": is_enabled,
                "window_style": window_style,
                "process_id": process_id.value
            }
            
            process_windows.append(window_info)
        
        return True
    
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))
    enum_proc = EnumWindowsProc(enum_window_proc)
    
    user32.EnumWindows(enum_proc, 0)
    return process_windows

def analyze_process_comprehensive(pid):
    """全面分析进程信息"""
    try:
        process = psutil.Process(pid)
        
        info = {
            "pid": pid,
            "name": process.name(),
            "exe": process.exe(),
            "cmdline": process.cmdline(),
            "status": process.status(),
            "create_time": process.create_time(),
            "memory_info": process.memory_info(),
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads(),
            "parent_pid": process.ppid()
        }
        
        # 查找进程的所有窗口
        windows = find_windows_by_process(pid)
        info["windows"] = windows
        
        return info
        
    except Exception as e:
        return {"error": str(e), "pid": pid}

def test_notepad_abc_startup():
    """测试notepad_abc启动"""
    print("=== notepad_abc启动测试 ===")
    
    exe_path = Path("bin/notepad_abc_new.exe")
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return False
    
    print(f"可执行文件: {exe_path.absolute()}")
    print(f"文件大小: {exe_path.stat().st_size} bytes")
    
    # 切换到bin目录
    old_cwd = os.getcwd()
    bin_dir = exe_path.parent
    
    try:
        os.chdir(bin_dir)
        print(f"切换工作目录到: {bin_dir}")
        
        # 检查已有相关进程
        print("检查已有notepad_abc进程...")
        existing_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if 'notepad' in proc.info['name'].lower() and 'notepad_abc' in proc.info['name'].lower():
                    existing_processes.append(proc.info)
            except:
                pass
        
        print(f"已有notepad_abc进程: {len(existing_processes)}")
        for proc in existing_processes:
            print(f"  PID: {proc['pid']}, Name: {proc['name']}")
        
        # 启动程序
        print("启动程序...")
        process = subprocess.Popen(
            ["notepad_abc_new.exe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ 进程已启动，PID: {process.pid}")
        
        # 等待程序初始化
        print("等待程序初始化...")
        time.sleep(5)
        
        # 全面分析进程
        print("分析进程信息...")
        process_info = analyze_process_comprehensive(process.pid)
        
        print(f"进程名称: {process_info.get('name', 'Unknown')}")
        print(f"执行文件: {process_info.get('exe', 'Unknown')}")
        print(f"命令行: {process_info.get('cmdline', [])}")
        print(f"状态: {process_info.get('status', 'Unknown')}")
        print(f"内存使用: {process_info.get('memory_info', {}).rss / 1024 / 1024:.1f} MB")
        print(f"线程数: {process_info.get('num_threads', 0)}")
        
        # 分析进程窗口
        windows = process_info.get('windows', [])
        print(f"\n进程的窗口数量: {len(windows)}")
        
        if windows:
            print("进程窗口详情:")
            for i, window in enumerate(windows):
                print(f"  窗口 {i+1}:")
                print(f"    标题: '{window['title']}'")
                print(f"    类名: '{window['class_name']}'")
                print(f"    可见: {window['is_visible']}")
                print(f"    启用: {window['is_enabled']}")
                print(f"    句柄: {window['hwnd']}")
                print(f"    样式: 0x{window['window_style']:08x}")
                
                # 检查是否可能是主窗口
                is_main_window = (
                    window['title'] and  # 有标题
                    'console' not in window['class_name'].lower() and  # 不是控制台
                    ('dialog' not in window['class_name'].lower()) and  # 不是对话框
                    (window['window_style'] & 0x10000000)  # 可见
                )
                print(f"    可能是主窗口: {is_main_window}")
            
            # 检查是否有非控制台窗口
            non_console_windows = [w for w in windows if 'console' not in w['class_name'].lower()]
            return len(non_console_windows) > 0
        
        else:
            print("❌ 进程未创建任何窗口")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 恢复工作目录
        os.chdir(old_cwd)
        
        # 终止进程
        try:
            if process and process.poll() is None:
                process.terminate()
                process.wait(timeout=3)
        except:
            try:
                process.kill()
            except:
                pass

def main():
    print("精确进程窗口测试")
    print("=" * 60)
    
    success = test_notepad_abc_startup()
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    
    if success:
        print("✅ notepad_abc进程成功创建了窗口")
    else:
        print("❌ notepad_abc进程未创建有效窗口")
        print("\n分析:")
        print("- 程序可能只创建了控制台窗口，没有GUI主窗口")
        print("- 程序可能遇到了未处理的异常")
        print("- 程序可能需要特定的初始化环境")
    
    return success

if __name__ == "__main__":
    main()
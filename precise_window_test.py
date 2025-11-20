#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确窗口测试 - 专门查找Notepad++主窗口
"""

import os
import sys
import time
import ctypes
from ctypes import wintypes
import subprocess
import json
from pathlib import Path

# Windows API函数定义
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def find_specific_notepad_windows():
    """专门查找Notepad++相关窗口"""
    all_windows = []
    
    def enum_window_proc(hwnd, lParam):
        # 获取窗口信息
        title_buffer = ctypes.create_unicode_buffer(512)
        title_length = user32.GetWindowTextW(hwnd, title_buffer, 512)
        
        class_buffer = ctypes.create_unicode_buffer(256)
        class_length = user32.GetClassNameW(hwnd, class_buffer, 256)
        
        # 获取窗口状态
        is_visible = bool(user32.IsWindowVisible(hwnd))
        is_enabled = bool(user32.IsWindowEnabled(hwnd))
        
        # 获取窗口样式
        window_style = user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
        extended_style = user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE
        
        window_info = {
            "hwnd": hwnd,
            "title": title_buffer.value if title_length > 0 else "",
            "class_name": class_buffer.value if class_length > 0 else "",
            "is_visible": is_visible,
            "is_enabled": is_enabled,
            "window_style": window_style,
            "extended_style": extended_style
        }
        
        all_windows.append(window_info)
        
        return True  # 继续枚举
    
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))
    enum_proc = EnumWindowsProc(enum_window_proc)
    
    user32.EnumWindows(enum_proc, 0)
    
    # 过滤出Notepad++相关的窗口
    notepad_windows = []
    console_windows = []
    other_windows = []
    
    for window in all_windows:
        title_lower = window['title'].lower()
        class_lower = window['class_name'].lower()
        
        # 检查是否是Notepad++主窗口
        if ("notepad++" in title_lower or 
            "notepad++" in class_lower or
            "notepad_abc" in title_lower or
            ("window" in class_lower and "notepad" in class_lower)):
            notepad_windows.append(window)
        
        # 检查控制台窗口
        elif ("consolewindowclass" in class_lower and 
              ("notepad" in title_lower.lower() or "调试控制台" in title_lower)):
            console_windows.append(window)
        
        # 收集其他可能相关的窗口
        elif (window['title'] and (window['is_visible'] or window['is_enabled']) and
              ("notepad" in title_lower or "notepad" in class_lower)):
            other_windows.append(window)
    
    return notepad_windows, console_windows, other_windows, all_windows

def test_precise_window_detection():
    """精确的窗口检测测试"""
    print("=== 精确窗口检测测试 ===")
    
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
        
        # 检查已有进程
        print("检查已有进程...")
        existing_notepad_windows, existing_console_windows, existing_other, all_existing = find_specific_notepad_windows()
        print(f"已有Notepad主窗口: {len(existing_notepad_windows)}")
        print(f"已有控制台窗口: {len(existing_console_windows)}")
        
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
        
        # 检查窗口
        print("检查窗口...")
        notepad_windows, console_windows, other_windows, all_windows = find_specific_notepad_windows()
        
        print(f"总窗口数: {len(all_windows)}")
        print(f"Notepad主窗口: {len(notepad_windows)}")
        print(f"控制台窗口: {len(console_windows)}")
        print(f"其他相关窗口: {len(other_windows)}")
        
        # 显示详细信息
        if notepad_windows:
            print("✅ 找到Notepad++主窗口:")
            for i, window in enumerate(notepad_windows):
                print(f"  窗口 {i+1}:")
                print(f"    标题: '{window['title']}'")
                print(f"    类名: '{window['class_name']}'")
                print(f"    可见: {window['is_visible']}")
                print(f"    启用: {window['is_enabled']}")
                print(f"    句柄: {window['hwnd']}")
                print(f"    样式: 0x{window['window_style']:08x}")
                
                # 检查是否是真正的应用窗口（非对话框或控制台）
                is_app_window = (
                    window['window_style'] & 0x10000000  # WS_VISIBLE
                    and not window['window_style'] & 0x80000000  # 非WS_OVERLAPPED
                    and not ("console" in window['class_name'].lower())
                )
                
                print(f"    可能是应用窗口: {is_app_window}")
            
            return True
        
        elif console_windows:
            print("⚠️ 只找到控制台窗口:")
            for i, window in enumerate(console_windows):
                print(f"  控制台 {i+1}:")
                print(f"    标题: '{window['title']}'")
                print(f"    类名: '{window['class_name']}'")
                print(f"    可见: {window['is_visible']}")
                print(f"    启用: {window['is_enabled']}")
                print(f"    句柄: {window['hwnd']}")
            
            print("结论: 程序启动了但可能未创建主窗口")
            return False
        
        else:
            print("❌ 未找到任何Notepad++相关窗口")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 恢复工作目录
        os.chdir(old_cwd)
        
        # 尝试终止进程
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
    print("精确窗口检测测试")
    print("=" * 60)
    
    success = test_precise_window_detection()
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    
    if success:
        print("✅ 程序成功创建了Notepad++主窗口")
    else:
        print("❌ 程序未创建主窗口，可能存在初始化问题")
        print("\n可能的原因:")
        print("1. 程序在窗口创建前遇到了异常")
        print("2. 配置文件格式错误导致初始化失败")
        print("3. 依赖的DLL文件缺失或不兼容")
        print("4. 程序需要在特定的工作目录运行")
    
    return success

if __name__ == "__main__":
    main()
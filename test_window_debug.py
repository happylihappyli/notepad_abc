#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import win32gui
import win32api
import win32con
import os

def find_notepad_windows():
    """查找Notepad++相关窗口"""
    windows = []
    
    def enum_windows_callback(hwnd, param):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            if window_text or class_name:
                print(f"窗口句柄: {hwnd}, 标题: '{window_text}', 类名: '{class_name}'")
                if 'notepad' in window_text.lower() or 'notepad' in class_name.lower():
                    windows.append((hwnd, window_text, class_name))
        return True
    
    win32gui.EnumWindows(enum_windows_callback, None)
    return windows

def main():
    print("=== 程序窗口检测和调试测试 ===")
    print()
    
    # 1. 查找Notepad++窗口
    print("1. 查找Notepad++相关窗口:")
    windows = find_notepad_windows()
    print(f"找到 {len(windows)} 个相关窗口")
    
    for hwnd, title, class_name in windows:
        print(f"   - 句柄: {hwnd}, 标题: '{title}', 类名: '{class_name}'")
    
    print()
    
    # 2. 检查调试日志文件
    print("2. 检查调试日志文件:")
    log_file = "npp_debug.log"
    if os.path.exists(log_file):
        size = os.path.getsize(log_file)
        print(f"日志文件存在，大小: {size} 字节")
        if size > 0:
            print("最近几行日志:")
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:
                        print(f"   {line.strip()}")
            except Exception as e:
                print(f"   读取日志出错: {e}")
    else:
        print("调试日志文件不存在")
    
    print()
    
    # 3. 手动触发调试输出（如果能找到设置对话框）
    print("3. 手动测试调试功能:")
    print("如果程序正在运行，现在你可以:")
    print("   a) 在垂直文件切换器中右键点击")
    print("   b) 点击'setting'菜单项")
    print("   c) 观察是否有调试日志生成")
    print()
    
    # 4. 实时监控调试日志
    print("4. 开始实时监控调试日志...")
    print("等待5秒，然后检查日志文件变化")
    
    if os.path.exists(log_file):
        initial_size = os.path.getsize(log_file)
        print(f"初始日志大小: {initial_size} 字节")
        
        # 等待并检查文件变化
        for i in range(5):
            time.sleep(1)
            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                if current_size > initial_size:
                    print(f"检测到日志文件变化! 新大小: {current_size} 字节")
                    break
                else:
                    print(f"等待中... ({i+1}/5)")
            else:
                print("日志文件消失")
                break
    else:
        print("日志文件不存在，等待生成...")
        for i in range(5):
            time.sleep(1)
            if os.path.exists(log_file):
                print(f"日志文件已生成!")
                break
            print(f"等待中... ({i+1}/5)")

if __name__ == "__main__":
    main()
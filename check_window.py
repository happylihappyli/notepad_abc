#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查notepad_abc程序是否创建了GUI窗口
"""

import subprocess
import time
import sys
import os
import ctypes
from ctypes import wintypes

def main():
    print("启动notepad_abc并检查GUI窗口...")
    
    exe_path = "bin\\notepad_abc_new.exe"
    if not os.path.exists(exe_path):
        print(f"错误：找不到可执行文件 {exe_path}")
        return 1
    
    try:
        # 启动进程
        proc = subprocess.Popen(
            [exe_path], 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"进程已启动，PID: {proc.pid}")
        
        # 等待程序初始化
        print("等待程序初始化...")
        time.sleep(8)
        
        # 使用Windows API检查窗口
        user32 = ctypes.windll.user32
        
        # 查找Notepad++窗口
        def enum_windows_callback(hwnd, lParam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    title = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, title, length + 1)
                    class_name = ctypes.create_unicode_buffer(256)
                    user32.GetClassNameW(hwnd, class_name, 256)
                    lParam.append((hwnd, title.value, class_name.value))
            return True
        
        windows = []
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))
        callback = EnumWindowsProc(enum_windows_callback)
        user32.EnumWindows(callback, ctypes.byref(ctypes.c_int()))
        
        print("\n找到的可见窗口:")
        notepad_windows = []
        for hwnd, title, class_name in windows:
            print(f"  窗口句柄: 0x{hwnd:X}")
            print(f"  标题: '{title}'")
            print(f"  类名: '{class_name}'")
            print("  ---")
            
            # 检查是否是Notepad++窗口
            if "Notepad++" in title or class_name == "Notepad++" or "notepad" in title.lower():
                notepad_windows.append((hwnd, title, class_name))
        
        if notepad_windows:
            print(f"\n✅ 找到 {len(notepad_windows)} 个Notepad++相关窗口!")
            for hwnd, title, class_name in notepad_windows:
                print(f"  GUI窗口: '{title}' (类名: {class_name}, 句柄: 0x{hwnd:X})")
                
                # 检查窗口状态
                rect = ctypes.wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                print(f"  窗口位置: ({rect.left}, {rect.top}) 到 ({rect.right}, {rect.bottom})")
                print(f"  窗口宽度: {rect.right - rect.left}, 高度: {rect.bottom - rect.top}")
                
                # 检查是否最小化
                if user32.IsIconic(hwnd):
                    print("  状态: 最小化")
                else:
                    print("  状态: 正常显示")
        else:
            print("\n❌ 没有找到Notepad++ GUI窗口!")
            
            # 检查控制台窗口
            print("\n检查控制台窗口:")
            for hwnd, title, class_name in windows:
                if "console" in class_name.lower() or "cmd" in title.lower():
                    print(f"  控制台窗口: '{title}' (类名: {class_name})")
        
        # 继续观察一段时间
        print("\n继续观察5秒...")
        time.sleep(5)
        
        # 检查进程状态
        if proc.poll() is None:
            print("进程仍在运行")
        else:
            print("进程已退出")
            
    except Exception as e:
        print(f"运行程序时出错: {e}")
        return 1
    
    print("\n检查完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())
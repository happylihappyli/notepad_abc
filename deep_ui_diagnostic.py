#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
深度诊断程序无窗口显示问题
专门检查窗口创建和消息循环问题
"""

import ctypes
from ctypes import wintypes
import subprocess
import time
import threading
import sys

# Windows API 结构体
class WNDCLASSEX(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("style", wintypes.UINT),
        ("lpfnWndProc", ctypes.CFUNCTYPE(ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HANDLE),
        ("hIcon", wintypes.HANDLE),
        ("hCursor", wintypes.HANDLE),
        ("hBrush", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm", wintypes.HANDLE)
    ]

def enum_windows_proc(hwnd, lParam):
    """窗口枚举回调函数"""
    windows = lParam
    class_name = ctypes.create_unicode_buffer(256)
    window_text = ctypes.create_unicode_buffer(256)
    
    # 获取窗口类名
    GetClassNameW = ctypes.windll.user32.GetClassNameW
    GetClassNameW(hwnd, class_name, 256)
    
    # 获取窗口标题
    GetWindowTextW = ctypes.windll.user32.GetWindowTextW
    GetWindowTextW(hwnd, window_text, 256)
    
    windows.append({
        'hwnd': hwnd,
        'class_name': class_name.value,
        'window_text': window_text.value,
        'is_visible': ctypes.windll.user32.IsWindowVisible(hwnd)
    })
    
    return True  # 继续枚举

def deep_window_diagnostic():
    """深度窗口诊断"""
    print("=== 深度窗口诊断 ===")
    
    # 获取所有窗口
    user32 = ctypes.windll.user32
    windows = []
    
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.POINTER(ctypes.c_int))
    EnumWindowsProc = EnumWindowsProc(enum_windows_proc)
    
    user32.EnumWindows(EnumWindowsProc, ctypes.pointer(ctypes.c_int(len(windows))))
    
    # 查找可能的notepad++窗口
    notepad_like_windows = []
    for win in windows:
        class_name = win['class_name'].lower()
        window_text = win['window_text'].lower()
        
        # 查找notepad++相关的窗口类名或标题
        if any(keyword in class_name for keyword in ['notepad', 'npp', 'notepad_plus']):
            notepad_like_windows.append(win)
            print(f"找到notepad++类窗口: {win}")
        elif any(keyword in window_text for keyword in ['notepad', 'notepad++', 'npp']):
            notepad_like_windows.append(win)
            print(f"找到notepad++标题窗口: {win}")
    
    if notepad_like_windows:
        print(f"\n✅ 找到 {len(notepad_like_windows)} 个可能的notepad++窗口")
        for i, win in enumerate(notepad_like_windows):
            print(f"窗口 {i+1}: 类名='{win['class_name']}', 标题='{win['window_text']}', 可见={win['is_visible']}")
    else:
        print("\n❌ 未找到任何notepad++相关窗口")
    
    # 检查所有可见的顶级窗口
    visible_windows = [win for win in windows if win['is_visible']]
    print(f"\n总共有 {len(visible_windows)} 个可见窗口")
    
    # 检查进程状态
    print("\n=== 检查进程状态 ===")
    
    # 查找运行的notepad_abc进程
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq notepad_abc_new.exe'], 
                              capture_output=True, text=True, encoding='utf-8')
        print("notepad_abc进程状态:")
        print(result.stdout)
    except:
        print("无法获取进程列表")

def test_window_forcing():
    """测试强制显示窗口"""
    print("\n=== 强制显示窗口测试 ===")
    
    # 启动程序并尝试强制显示窗口
    exe_path = "bin\\notepad_abc_new.exe"
    
    try:
        process = subprocess.Popen([exe_path])
        print(f"已启动程序，PID: {process.pid}")
        
        # 等待2秒让窗口创建
        time.sleep(2)
        
        # 枚举窗口并查找可能的notepad++窗口
        user32 = ctypes.windll.user32
        windows = []
        
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.POINTER(ctypes.c_int))
        EnumWindowsProc = EnumWindowsProc(enum_windows_proc)
        
        user32.EnumWindows(EnumWindowsProc, ctypes.pointer(ctypes.c_int(len(windows))))
        
        # 查找窗口并尝试显示
        found_window = None
        for win in windows:
            if any(keyword in win['class_name'].lower() for keyword in ['notepad', 'npp', 'notepad_plus']):
                found_window = win
                break
        
        if found_window:
            print(f"找到窗口: {found_window}")
            
            # 尝试强制显示窗口
            ShowWindow = user32.ShowWindow
            SW_RESTORE = 9
            SW_SHOW = 5
            WM_SHOWWINDOW = 24
            
            print("尝试显示窗口...")
            ShowWindow(found_window['hwnd'], SW_RESTORE)
            time.sleep(0.5)
            ShowWindow(found_window['hwnd'], SW_SHOW)
            time.sleep(0.5)
            
            # 尝试激活窗口
            SetForegroundWindow = user32.SetForegroundWindow
            SetForegroundWindow(found_window['hwnd'])
            
            print("已尝试强制显示和激活窗口")
            
        else:
            print("未找到notepad++窗口")
        
        # 等待一下看效果
        time.sleep(2)
        
        # 终止进程
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"强制显示测试失败: {e}")

def check_gdi_issues():
    """检查GDI相关问题"""
    print("\n=== 检查GDI问题 ===")
    
    try:
        # 检查GDI对象数量
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq notepad_abc_new.exe', '/FO', 'CSV'], 
                              capture_output=True, text=True, encoding='utf-8')
        print("当前进程信息:")
        print(result.stdout)
        
        # 检查是否有其他相关进程
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq *notepad*'], 
                              capture_output=True, text=True, encoding='utf-8')
        print("所有notepad相关进程:")
        print(result.stdout)
        
    except Exception as e:
        print(f"GDI检查失败: {e}")

if __name__ == "__main__":
    print("开始深度窗口诊断")
    
    # 关闭可能运行的程序
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'notepad_abc_new.exe'], 
                      capture_output=True, text=True)
    except:
        pass
    
    time.sleep(1)
    
    # 执行诊断
    deep_window_diagnostic()
    test_window_forcing()
    check_gdi_issues()
    
    print("\n=== 诊断完成 ===")
    input("按回车键退出...")
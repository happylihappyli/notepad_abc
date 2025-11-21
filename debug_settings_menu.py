#!/usr/bin/env python
# -*- coding: utf-8 -*-

import win32gui
import win32api
import win32con
import time
import threading

def find_notepad_windows():
    """查找所有与notepad相关的窗口"""
    windows = []
    
    def enum_windows_callback(hwnd, param):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text and ("notepad" in window_text.lower() or "abc" in window_text.lower()):
                windows.append((hwnd, window_text))
        return True
    
    win32gui.EnumWindows(enum_windows_callback, None)
    return windows

def monitor_window_messages(hwnd):
    """监控窗口消息（简单版本）"""
    def message_loop():
        try:
            # 监听WM_COMMAND消息
            def win_proc(hwnd, msg, wParam, lParam):
                if msg == win32con.WM_COMMAND:
                    print(f"收到WM_COMMAND消息: wParam={wParam}, lParam={lParam}")
                    # 检查是否是IDM_SETTINGS_VFS命令
                    if wParam == 3100:  # IDM_SETTINGS_VFS的值
                        print("检测到IDM_SETTINGS_VFS命令!")
                    
                    # 检查是否是标准设置命令
                    if wParam == 100:  # 可能的IDM_SETTING_PREFERENCE值
                        print("检测到标准设置命令!")
                        
                # 继续默认消息处理
                return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)
            
            print(f"开始监控窗口: {win32gui.GetWindowText(hwnd)} (句柄: {hwnd})")
            
            # 注册一个简单的窗口类来监听消息（这个方法比较复杂）
            print("请手动点击设置菜单，观察控制台输出...")
            
        except Exception as e:
            print(f"监控出错: {e}")
    
    # 在后台运行消息监控
    thread = threading.Thread(target=message_loop)
    thread.daemon = True
    thread.start()
    return thread

def main():
    print("=== Notepad_abc设置菜单调试工具 ===")
    print("1. 查找所有相关窗口...")
    
    windows = find_notepad_windows()
    if not windows:
        print("未找到notepad_abc窗口，请确保程序正在运行!")
        return
    
    print(f"找到 {len(windows)} 个相关窗口:")
    for i, (hwnd, title) in enumerate(windows):
        print(f"  {i+1}. {title} (句柄: {hwnd})")
    
    # 监控主窗口
    main_hwnd = None
    for hwnd, title in windows:
        if "notepad_abc" in title.lower():
            main_hwnd = hwnd
            break
    
    if main_hwnd:
        print(f"\n2. 监控主窗口: {win32gui.GetWindowText(main_hwnd)}")
        monitor_window_messages(main_hwnd)
    else:
        print("\n2. 未找到主窗口...")
    
    print("\n3. 请执行以下步骤进行测试:")
    print("   - 点击垂直文件切换器面板")
    print("   - 右键点击以显示右键菜单")
    print("   - 点击'设置'选项")
    print("   - 观察上述控制台输出")
    print("\n4. 按Ctrl+C退出...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n调试结束!")

if __name__ == "__main__":
    main()
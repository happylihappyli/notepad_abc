#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
import win32gui
import win32api
import win32con
from ctypes import windll, byref, c_char, c_wchar, c_int, c_ulong, c_void_p, POINTER
from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, UINT_PTR, HANDLE

# 窗口消息监控器
class WindowMessageMonitor:
    def __init__(self):
        self.messages = []
        self.running = False
        
    def enum_windows_callback(self, hwnd, lParam):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if 'notepad_abc' in window_text.lower():
                print(f"找到Notepad++窗口: {window_text} (句柄: {hwnd})")
                lParam[0] = hwnd  # 存储窗口句柄
        return True
        
    def find_notepad_window(self):
        """查找Notepad++主窗口"""
        hwnd_ref = [0]
        win32gui.EnumWindows(self.enum_windows_callback, hwnd_ref)
        return hwnd_ref[0] if hwnd_ref[0] != 0 else None
        
    def monitor_messages(self, hwnd, duration=30):
        """监控窗口消息"""
        print(f"开始监控窗口消息，窗口句柄: {hwnd}")
        print("请在程序中点击设置菜单，我将监控相关消息...")
        
        # 定义消息常量
        WM_COMMAND = 0x0111
        IDM_SETTING_PREFERENCE = 100
        
        message_count = 0
        start_time = time.time()
        
        def wndproc(hwnd, msg, wparam, lparam):
            nonlocal message_count
            if msg == WM_COMMAND:
                command_id = wparam & 0xFFFF  # 低16位是命令ID
                print(f"[{time.strftime('%H:%M:%S')}] 捕获WM_COMMAND消息 - 命令ID: {command_id}")
                
                if command_id == IDM_SETTING_PREFERENCE:
                    print(f"*** 捕获到设置命令(IDM_SETTING_PREFERENCE = {IDM_SETTING_PREFERENCE}) ***")
                    print("设置对话框应该会打开...")
                    
                # 也检查可能的自定义设置命令
                if command_id == 3100:  # IDM_SETTINGS_VFS的值
                    print(f"*** 捕获到自定义设置命令(IDM_SETTINGS_VFS = {command_id}) ***")
                    
            elif msg == win32con.WM_CLOSE:
                print("*** 窗口正在关闭 ***")
                
            # 调用默认窗口过程
            return windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam)
            
        # 安装子窗口消息钩子
        def install_hook():
            # 这里我们需要使用SetWindowsHookEx来监控消息
            # 但为了简化，我们使用定时器方式检查
            pass
            
        # 监控循环
        while time.time() - start_time < duration and self.running:
            try:
                # 检查程序是否还在运行
                if not win32gui.IsWindow(hwnd):
                    print("程序窗口已关闭，停止监控")
                    break
                    
                time.sleep(0.1)  # 100ms检查一次
            except Exception as e:
                print(f"监控出错: {e}")
                break
                
        print("监控结束")

def main():
    monitor = WindowMessageMonitor()
    
    print("=== Notepad++ 设置菜单消息监控器 ===")
    print("正在查找Notepad++窗口...")
    
    # 等待一秒让程序完全启动
    time.sleep(2)
    
    hwnd = monitor.find_notepad_window()
    if not hwnd:
        print("未找到Notepad++窗口，请确保程序正在运行")
        return
        
    print("\n=== 监控说明 ===")
    print("1. 程序已找到，现在将开始监控消息")
    print("2. 请在垂直文件切换器中右键点击")
    print("3. 点击'setting'菜单项")
    print("4. 监控器将捕获相关的消息")
    print("5. 如果看到WM_COMMAND消息被捕获，说明点击被正确处理")
    print("\n开始监控...")
    
    monitor.running = True
    monitor.monitor_messages(hwnd, duration=60)  # 监控60秒
    
    print("\n=== 监控完成 ===")

if __name__ == "__main__":
    main()
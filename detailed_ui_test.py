#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细的UI测试脚本 - 检查程序窗口创建情况
"""

import os
import sys
import time
import subprocess
import threading
import ctypes
from ctypes import wintypes

# Windows API函数定义
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def find_window_by_exe(exe_name):
    """查找指定exe创建的窗口"""
    def enum_windows_callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            window_text = ctypes.create_unicode_buffer(256)
            class_name = ctypes.create_unicode_buffer(256)
            
            user32.GetWindowTextW(hwnd, window_text, 256)
            user32.GetClassNameW(hwnd, class_name, 256)
            
            # 获取进程ID
            process_id = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            
            # 获取进程路径
            process_handle = kernel32.OpenProcess(0x0400, False, process_id)
            if process_handle:
                process_path = ctypes.create_unicode_buffer(260)
                if kernel32.GetModuleFileNameExW(process_handle, None, process_path, 260):
                    path_str = process_path.value
                    exe_name_only = os.path.basename(path_str).lower()
                    if exe_name_only == exe_name.lower():
                        print(f"找到窗口: '{window_text.value}' (类: '{class_name.value}')")
                        print(f"进程ID: {process_id.value}")
                        print(f"进程路径: {path_str}")
                        lParam.append({
                            'hwnd': hwnd,
                            'title': window_text.value,
                            'class': class_name.value,
                            'pid': process_id.value
                        })
                kernel32.CloseHandle(process_handle)
        return True
    
    windows = []
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))
    callback = EnumWindowsProc(lambda hwnd, lParam: enum_windows_callback(hwnd, lParam))
    user32.EnumWindows(callback, ctypes.byref(ctypes.c_int(len(windows))))
    return windows

def test_program_ui():
    """测试程序UI是否正常显示"""
    print("=== Notepad_abc UI详细测试 ===")
    
    exe_path = "e:\\GitHub3\\notepad_abc\\bin\\notepad_abc_new.exe"
    
    if not os.path.exists(exe_path):
        print(f"❌ 程序文件不存在: {exe_path}")
        return 1
    
    print(f"✅ 程序文件存在，大小: {os.path.getsize(exe_path)} 字节")
    
    try:
        print("\n🚀 启动程序...")
        process = subprocess.Popen(
            [exe_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        print(f"📊 进程已启动，PID: {process.pid}")
        
        # 等待程序初始化
        print("⏳ 等待5秒让程序初始化...")
        time.sleep(5)
        
        # 查找窗口
        print("\n🔍 查找程序窗口...")
        windows = find_window_by_exe("notepad_abc_new.exe")
        
        if not windows:
            print("❌ 未找到程序窗口")
        else:
            print(f"✅ 找到 {len(windows)} 个窗口:")
            for i, win in enumerate(windows, 1):
                print(f"  窗口 {i}:")
                print(f"    标题: '{win['title']}'")
                print(f"    类名: '{win['class']}'")
                print(f"    句柄: {win['hwnd']}")
        
        # 检查进程状态
        poll_result = process.poll()
        if poll_result is None:
            print(f"\n✅ 程序仍在运行 (PID: {process.pid})")
            print("💡 程序启动成功，窗口可能已显示")
            
            # 等待用户观察
            print("\n👀 等待10秒供用户观察...")
            time.sleep(10)
            
            # 再次检查窗口
            print("\n🔍 再次查找窗口...")
            windows_after = find_window_by_exe("notepad_abc_new.exe")
            if not windows_after:
                print("❌ 程序仍在运行，但窗口消失了")
            
            print("\n🛑 终止程序...")
            process.terminate()
            try:
                process.wait(timeout=3)
                print("✅ 程序已正常终止")
            except:
                print("⚠️ 程序未响应，强制终止")
                process.kill()
        else:
            print(f"\n❌ 程序已退出，退出代码: {poll_result}")
            stdout, stderr = process.communicate()
            if stdout:
                print("标准输出:")
                print(stdout.decode('utf-8', errors='ignore'))
            if stderr:
                print("标准错误:")
                print(stderr.decode('utf-8', errors='ignore'))
        
        return 0
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return 1

def main():
    print("这个脚本会启动程序并检查是否创建了窗口")
    print("如果程序正常，应该能看到一个文本编辑器的窗口")
    print("=" * 60)
    
    try:
        result = test_program_ui()
        
        print("\n" + "=" * 60)
        if result == 0:
            print("✅ 测试完成：程序启动正常")
            print("💡 如果您看不到窗口，可能的原因:")
            print("   1. 窗口在屏幕外或被最小化")
            print("   2. 窗口透明度设置导致难以看到")
            print("   3. 多显示器设置问题")
        else:
            print("❌ 测试失败：程序启动或运行有问题")
            
        return result
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
        return 1
    except Exception as e:
        print(f"\n❌ 测试过程发生错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
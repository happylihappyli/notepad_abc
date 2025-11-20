#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
深度窗口注册和创建测试
检查RegisterClass和CreateWindowEx的详细错误信息
"""

import subprocess
import time
import ctypes
from ctypes import wintypes
import sys
import os

def test_basic_window_creation():
    """测试基本窗口创建功能"""
    print("=== 基本窗口创建测试 ===")
    
    # 测试Python能否创建简单窗口
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        print("✅ Tkinter窗口系统可用")
        root.destroy()
        return True
    except Exception as e:
        print(f"❌ Tkinter窗口系统测试失败: {e}")
        return False

def test_ctypes_window_api():
    """测试ctypes Windows API调用"""
    print("\n=== Windows API调用测试 ===")
    
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        # 测试GetLastError函数
        kernel32.GetLastError.restype = wintypes.DWORD
        error_code = kernel32.GetLastError()
        print(f"当前错误代码: {error_code}")
        
        # 测试注册窗口类
        class WNDCLASSEX(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("style", wintypes.UINT),
                ("lpfnWndProc", ctypes.c_void_p),
                ("cbClsExtra", wintypes.INT),
                ("cbWndExtra", wintypes.INT),
                ("hInstance", wintypes.HANDLE),
                ("hIcon", wintypes.HANDLE),
                ("hCursor", wintypes.HANDLE),
                ("hbrBackground", wintypes.HANDLE),
                ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR),
                ("hIconSm", wintypes.HANDLE),
            ]
        
        # 创建一个测试窗口类
        test_class_name = "TestWindowClass"
        
        wnd_class = WNDCLASSEX()
        wnd_class.cbSize = ctypes.sizeof(WNDCLASSEX)
        wnd_class.style = 0
        wnd_class.lpfnWndProc = user32.DefWindowProcW
        wnd_class.cbClsExtra = 0
        wnd_class.cbWndExtra = 0
        wnd_class.hInstance = kernel32.GetModuleHandleW(None)
        wnd_class.hIcon = None
        wnd_class.hCursor = user32.LoadCursorW(None, 32512)  # IDC_ARROW
        wnd_class.hbrBackground = user32.GetStockObject(5)   # WHITE_BRUSH
        wnd_class.lpszMenuName = None
        wnd_class.lpszClassName = test_class_name
        wnd_class.hIconSm = None
        
        # 尝试注册窗口类
        atom = user32.RegisterClassExW(ctypes.byref(wnd_class))
        if atom == 0:
            error_code = kernel32.GetLastError()
            print(f"❌ RegisterClassEx失败，错误代码: {error_code}")
            return False
        else:
            print("✅ 窗口类注册成功")
            
            # 尝试创建窗口
            hwnd = user32.CreateWindowExW(
                0,  # 扩展样式
                test_class_name,
                "Test Window",
                0x10000000,  # WS_OVERLAPPEDWINDOW
                100, 100, 400, 300,
                None,  # 父窗口
                None,  # 菜单
                kernel32.GetModuleHandleW(None),
                None   # lParam
            )
            
            if hwnd == 0:
                error_code = kernel32.GetLastError()
                print(f"❌ CreateWindowEx失败，错误代码: {error_code}")
                return False
            else:
                print("✅ 窗口创建成功")
                
                # 检查窗口是否可见
                visible = user32.IsWindowVisible(hwnd)
                print(f"窗口可见性: {'可见' if visible else '隐藏'}")
                
                # 获取窗口标题
                title_buffer = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, title_buffer, 256)
                print(f"窗口标题: {title_buffer.value}")
                
                # 销毁窗口
                user32.DestroyWindow(hwnd)
                print("✅ 窗口已销毁")
                
                # 取消注册窗口类
                user32.UnregisterClassW(test_class_name, kernel32.GetModuleHandleW(None))
                print("✅ 窗口类已取消注册")
                return True
                
    except Exception as e:
        print(f"❌ Windows API测试失败: {e}")
        return False

def check_environment_variables():
    """检查环境变量"""
    print("\n=== 环境变量检查 ===")
    
    important_vars = [
        "PATH", "WINDIR", "SYSTEMROOT", "USERPROFILE",
        "PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA", "APPDATA"
    ]
    
    for var in important_vars:
        value = os.environ.get(var, "未设置")
        print(f"{var}: {value[:100]}{'...' if len(value) > 100 else ''}")

def check_system_capabilities():
    """检查系统能力"""
    print("\n=== 系统能力检查 ===")
    
    try:
        user32 = ctypes.windll.user32
        
        # 检查DPI感知
        print(f"屏幕宽度: {user32.GetSystemMetrics(0)}")  # SM_CXSCREEN
        print(f"屏幕高度: {user32.GetSystemMetrics(1)}")  # SM_CYSCREEN
        print(f"显示器数量: {user32.GetSystemMetrics(80)}")  # SM_CMONITORS
        
        # 检查支持的窗口操作
        print("Windows API支持检查:")
        print(f"  CreateWindowExW: {'支持' if hasattr(user32, 'CreateWindowExW') else '不支持'}")
        print(f"  RegisterClassExW: {'支持' if hasattr(user32, 'RegisterClassExW') else '不支持'}")
        print(f"  ShowWindow: {'支持' if hasattr(user32, 'ShowWindow') else '不支持'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统能力检查失败: {e}")
        return False

def test_exe_dependencies():
    """测试可执行文件依赖"""
    print("\n=== 可执行文件依赖检查 ===")
    
    exe_path = "bin\\notepad_abc_new.exe"
    
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False
    
    # 检查文件大小
    file_size = os.path.getsize(exe_path)
    print(f"可执行文件大小: {file_size / 1024 / 1024:.2f} MB")
    
    # 尝试以不同方式运行程序
    print("尝试以不同方式启动程序...")
    
    # 方式1: 直接启动
    try:
        print("方式1: 直接启动")
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ 直接启动成功")
            process.terminate()
            try:
                process.wait(timeout=3)
            except:
                process.kill()
        else:
            print(f"❌ 直接启动失败，返回码: {process.poll()}")
            
    except Exception as e:
        print(f"❌ 直接启动异常: {e}")
    
    # 方式2: 使用CREATE_NEW_CONSOLE标志
    try:
        print("方式2: 带新控制台启动")
        process = subprocess.Popen([exe_path], 
                                 creationflags=subprocess.CREATE_NEW_CONSOLE,
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ 带新控制台启动成功")
            process.terminate()
            try:
                process.wait(timeout=3)
            except:
                process.kill()
        else:
            print(f"❌ 带新控制台启动失败，返回码: {process.poll()}")
            
    except Exception as e:
        print(f"❌ 带新控制台启动异常: {e}")

def main():
    """主测试函数"""
    print("开始深度窗口注册和创建测试")
    print("=" * 50)
    
    # 关闭可能运行的程序
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'notepad_abc_new.exe'], 
                      capture_output=True, text=True)
        time.sleep(1)
    except:
        pass
    
    # 执行各项测试
    check_environment_variables()
    check_system_capabilities()
    test_basic_window_creation()
    test_ctypes_window_api()
    test_exe_dependencies()
    
    print("\n" + "=" * 50)
    print("深度测试完成")

if __name__ == "__main__":
    main()
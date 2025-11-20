#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口显示问题深度诊断脚本
不依赖pywin32，直接分析进程状态和窗口创建过程
"""

import subprocess
import time
import threading
import psutil
import os
import sys
import ctypes
from ctypes import wintypes
import winreg

class WindowDiagnostic:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
    def find_process_windows(self, pid):
        """查找指定PID相关的窗口"""
        windows = []
        
        def enum_windows_proc(hwnd, lParam):
            windows_info = lParam
            try:
                # 获取窗口所属进程ID
                process_id = ctypes.wintypes.DWORD()
                thread_id = self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                
                if process_id.value == pid and self.user32.IsWindow(hwnd):
                    # 获取窗口信息
                    class_name = ctypes.create_unicode_buffer(256)
                    self.user32.GetClassNameW(hwnd, class_name, 256)
                    
                    title_length = self.user32.GetWindowTextLengthW(hwnd)
                    title = ""
                    if title_length > 0:
                        title_buffer = ctypes.create_unicode_buffer(title_length + 1)
                        self.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
                        title = title_buffer.value
                    
                    # 获取窗口位置
                    rect = ctypes.wintypes.RECT()
                    is_visible = self.user32.IsWindowVisible(hwnd)
                    is_minimized = self.user32.IsIconic(hwnd)
                    
                    window_info = {
                        'hwnd': hwnd,
                        'class_name': class_name.value,
                        'title': title,
                        'visible': bool(is_visible),
                        'minimized': bool(is_minimized),
                        'pid': process_id.value
                    }
                    
                    if self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                        window_info['rect'] = (rect.left, rect.top, rect.right, rect.bottom)
                    
                    windows_info.append(window_info)
            except Exception as e:
                pass
            
            return True
        
        try:
            self.user32.EnumWindows(enum_windows_proc, ctypes.py_object(windows))
        except Exception as e:
            print(f"枚举窗口失败: {e}")
        
        return windows
    
    def analyze_process_creation_flags(self, pid):
        """分析进程创建标志"""
        try:
            process = psutil.Process(pid)
            
            # 获取进程启动信息
            create_time = process.create_time()
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            num_threads = process.num_threads()
            
            print(f"进程分析:")
            print(f"  创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))}")
            print(f"  CPU使用率: {cpu_percent}%")
            print(f"  内存使用: {memory_info.rss / 1024 / 1024:.1f} MB")
            print(f"  线程数: {num_threads}")
            
            # 检查进程状态
            status = process.status()
            print(f"  进程状态: {status}")
            
            # 检查进程工作目录
            try:
                cwd = process.cwd()
                print(f"  工作目录: {cwd}")
            except:
                print("  工作目录: 无法获取")
            
            return True
        except Exception as e:
            print(f"分析进程失败: {e}")
            return False
    
    def check_environment_issues(self):
        """检查环境问题"""
        print("\n=== 环境检查 ===")
        
        # 检查显示器数量
        monitor_count = self.user32.GetSystemMetrics(0)  # SM_CMONITORS
        print(f"显示器数量: {monitor_count}")
        
        # 检查主屏幕尺寸
        screen_width = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        print(f"主屏幕分辨率: {screen_width}x{screen_height}")
        
        # 检查DPI设置
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Control Panel\Desktop") as key:
                dpi_value, _ = winreg.QueryValueEx(key, "LogPixels")
                print(f"DPI设置: {dpi_value} DPI")
        except:
            print("DPI设置: 无法获取")
        
        # 检查显示缩放
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Control Panel\Desktop\PerMonitorSettings") as key:
                scale_value, _ = winreg.QueryValueEx(key, "DpiValue")
                print(f"缩放设置: {scale_value}")
        except:
            print("缩放设置: 默认")
    
    def test_window_force_display(self, hwnd):
        """尝试强制显示窗口"""
        print("尝试强制显示窗口...")
        
        try:
            # 1. 恢复窗口（如果最小化）
            self.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            
            # 2. 显示窗口
            self.user32.ShowWindow(hwnd, 5)  # SW_SHOW
            
            # 3. 激活窗口
            self.user32.SetForegroundWindow(hwnd)
            
            # 4. 设置焦点
            self.user32.SetFocus(hwnd)
            
            # 5. 更新窗口
            self.user32.UpdateWindow(hwnd)
            
            # 6. 发送激活消息
            self.user32.SendMessageW(hwnd, 0x0006, 1, 0)  # WM_ACTIVATE
            
            print("✅ 窗口强制显示操作完成")
            return True
            
        except Exception as e:
            print(f"❌ 强制显示窗口失败: {e}")
            return False
    
    def run_comprehensive_test(self, exe_path):
        """运行综合测试"""
        print("Notepad++ 窗口显示问题深度诊断")
        print("=" * 60)
        
        if not os.path.exists(exe_path):
            print(f"❌ 可执行文件不存在: {exe_path}")
            return False
        
        # 环境检查
        self.check_environment_issues()
        
        # 启动进程
        print(f"\n=== 启动进程测试 ===")
        print(f"启动文件: {exe_path}")
        
        try:
            process = subprocess.Popen(
                exe_path,
                creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print(f"✅ 进程启动成功，PID: {process.pid}")
            
            # 分析进程
            self.analyze_process_creation_flags(process.pid)
            
            # 等待并查找窗口
            print(f"\n=== 窗口查找 ===")
            window_found = False
            
            for i in range(10):
                print(f"等待窗口创建 ({i+1}/10)...")
                time.sleep(1)
                
                windows = self.find_process_windows(process.pid)
                
                if windows:
                    print(f"✅ 找到 {len(windows)} 个窗口:")
                    for window in windows:
                        print(f"  窗口类名: {window['class_name']}")
                        print(f"  窗口标题: {window['title']}")
                        print(f"  可见性: {'可见' if window['visible'] else '隐藏'}")
                        print(f"  最小化: {'是' if window['minimized'] else '否'}")
                        if 'rect' in window:
                            rect = window['rect']
                            print(f"  位置: ({rect[0]}, {rect[1]}) 尺寸: {rect[2]-rect[0]}x{rect[3]-rect[1]}")
                        
                        # 尝试强制显示
                        if not window['visible'] and window['hwnd']:
                            print(f"  尝试强制显示窗口...")
                            self.test_window_force_display(window['hwnd'])
                        
                        time.sleep(0.5)  # 等待操作生效
                    
                    window_found = True
                    break
                else:
                    print(f"⏳ 未找到窗口...")
            
            # 最终检查
            if not window_found:
                print(f"\n=== 最终窗口检查 ===")
                windows = self.find_process_windows(process.pid)
                if windows:
                    print(f"最终找到 {len(windows)} 个窗口")
                    window_found = True
                else:
                    print("❌ 整个过程中未找到任何窗口")
            
            # 等待用户确认（可选）
            print(f"\n是否检查进程? (y/n): ", end="")
            if input().lower().startswith('y'):
                input("按回车键继续，进程将保持运行...")
            
            # 终止进程
            print("终止进程...")
            process.terminate()
            try:
                process.wait(timeout=3)
                print("✅ 进程正常终止")
            except:
                process.kill()
                print("⚠️  强制终止进程")
            
            return window_found
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False

def main():
    diagnostic = WindowDiagnostic()
    
    exe_path = "bin\\notepad_abc_new.exe"
    
    # 运行综合测试
    success = diagnostic.run_comprehensive_test(exe_path)
    
    print(f"\n=== 诊断结论 ===")
    if success:
        print("✅ 窗口能够创建，但可能存在显示问题")
        print("建议:")
        print("1. 检查窗口是否被其他窗口遮挡")
        print("2. 尝试移动窗口到不同位置")
        print("3. 检查多显示器设置")
        print("4. 重启资源管理器")
    else:
        print("❌ 窗口创建失败，可能存在以下问题:")
        print("1. DLL依赖缺失")
        print("2. 权限不足")
        print("3. 显卡驱动问题")
        print("4. 系统兼容性问题")
        print("5. 杀毒软件阻止")

if __name__ == "__main__":
    main()
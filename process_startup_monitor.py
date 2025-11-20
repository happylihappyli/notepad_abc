#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
程序启动和异常监控
监控notepad_abc程序的完整启动流程和可能的异常退出
"""

import subprocess
import time
import threading
import psutil
import os
import sys
import ctypes
from ctypes import wintypes

def monitor_process_lifecycle(exe_path, timeout=10):
    """监控进程生命周期"""
    print("=== 进程生命周期监控 ===")
    
    try:
        # 启动进程
        print(f"启动程序: {exe_path}")
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 bufsize=1,
                                 universal_newlines=True)
        
        pid = process.pid
        print(f"进程PID: {pid}")
        
        # 创建进程对象进行监控
        try:
            psutil_process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            print("❌ 进程启动后立即退出")
            return
        
        # 监控进程状态变化
        start_time = time.time()
        last_memory = 0
        
        while time.time() - start_time < timeout:
            try:
                # 检查进程状态
                if psutil_process.is_running():
                    cpu_percent = psutil_process.cpu_percent()
                    memory_info = psutil_process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    
                    # 获取进程详细信息
                    create_time = psutil_process.create_time()
                    status = psutil_process.status()
                    num_threads = psutil_process.num_threads()
                    
                    print(f"时间: {time.time() - start_time:.1f}s, "
                          f"内存: {memory_mb:.1f}MB, "
                          f"CPU: {cpu_percent:.1f}%, "
                          f"状态: {status}, "
                          f"线程: {num_threads}")
                    
                    # 检查内存变化
                    if memory_mb > last_memory + 1:
                        print(f"  📈 内存增加: {memory_mb:.1f}MB (增加 {memory_mb - last_memory:.1f}MB)")
                        last_memory = memory_mb
                    elif memory_mb < last_memory - 1:
                        print(f"  📉 内存减少: {memory_mb:.1f}MB (减少 {last_memory - memory_mb:.1f}MB)")
                        last_memory = memory_mb
                    
                    # 检查异常状态
                    if status == 'zombie':
                        print("  ⚠️  进程变为僵尸状态")
                        break
                        
                else:
                    print("❌ 进程已退出")
                    break
                    
                time.sleep(0.5)
                
            except psutil.NoSuchProcess:
                print("❌ 进程已不存在")
                break
            except Exception as e:
                print(f"❌ 监控异常: {e}")
                break
        
        # 终止进程
        print("终止测试进程...")
        try:
            process.terminate()
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            
        return True
        
    except Exception as e:
        print(f"❌ 生命周期监控失败: {e}")
        return False

def check_window_creation_timing():
    """检查窗口创建时机"""
    print("\n=== 窗口创建时机检查 ===")
    
    exe_path = "bin\\notepad_abc_new.exe"
    
    try:
        # 启动程序
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        pid = process.pid
        print(f"进程PID: {pid}")
        
        # 在不同时间点检查窗口
        for check_time in [0.5, 1.0, 2.0, 3.0, 5.0]:
            time.sleep(check_time - (time.time() - (start_time := time.time())))
            
            if process.poll() is not None:
                print(f"❌ 程序在 {check_time}s 前已退出")
                break
            
            # 查找窗口
            windows_found = []
            user32 = ctypes.windll.user32
            
            def enum_windows_callback(hwnd, lParam):
                windows = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_int)).contents
                
                # 获取窗口类名
                class_name = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_name, 256)
                
                # 获取窗口标题
                window_text = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, window_text, 256)
                
                # 检查是否包含"Notepad++"
                if "Notepad++" in class_name.value or "Notepad++" in window_text.value:
                    windows.append({
                        'hwnd': hwnd,
                        'class_name': class_name.value,
                        'window_text': window_text.value
                    })
                
                return True
            
            try:
                EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.POINTER(ctypes.c_int))
                EnumWindowsProc = EnumWindowsProc(enum_windows_callback)
                
                windows_info = []
                user32.EnumWindows(EnumWindowsProc, ctypes.byref(windows_info))
                
                if windows_info:
                    print(f"✅ {check_time}s: 找到 {len(windows_info)} 个Notepad++窗口")
                    for window in windows_info:
                        print(f"   - 类名: {window['class_name']}")
                        print(f"   - 标题: {window['window_text'][:50]}")
                else:
                    print(f"⏳ {check_time}s: 未找到Notepad++窗口")
                    
            except Exception as e:
                print(f"❌ {check_time}s: 窗口检查异常: {e}")
        
        # 清理
        process.terminate()
        try:
            process.wait(timeout=3)
        except:
            process.kill()
            
    except Exception as e:
        print(f"❌ 窗口创建时机检查失败: {e}")

def check_exception_details():
    """检查异常详情"""
    print("\n=== 异常详情检查 ===")
    
    exe_path = "bin\\notepad_abc_new.exe"
    
    try:
        # 启动进程并捕获异常输出
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 等待进程运行一段时间
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ 程序仍在运行，检查输出...")
            
            # 获取输出
            try:
                stdout, stderr = process.communicate(timeout=1)
                
                if stdout:
                    print("标准输出:")
                    print(stdout)
                if stderr:
                    print("错误输出:")
                    print(stderr)
                    
            except subprocess.TimeoutExpired:
                print("程序仍在运行，输出不可用")
                process.terminate()
        else:
            print(f"❌ 程序已退出，返回码: {process.poll()}")
            
            # 获取退出信息
            try:
                stdout, stderr = process.communicate(timeout=1)
                
                if stdout:
                    print("标准输出:")
                    print(stdout)
                if stderr:
                    print("错误输出:")
                    print(stderr)
                    
            except subprocess.TimeoutExpired:
                print("无法获取退出信息")
                
        # 确保进程被终止
        try:
            process.wait(timeout=1)
        except:
            process.kill()
            
    except Exception as e:
        print(f"❌ 异常详情检查失败: {e}")

def main():
    """主监控函数"""
    print("开始程序启动和异常监控")
    print("=" * 50)
    
    exe_path = "bin\\notepad_abc_new.exe"
    
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return
    
    # 关闭可能运行的程序
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'notepad_abc_new.exe'], 
                      capture_output=True, text=True)
        time.sleep(1)
    except:
        pass
    
    # 执行监控测试
    monitor_process_lifecycle(exe_path, timeout=8)
    check_window_creation_timing()
    check_exception_details()
    
    print("\n" + "=" * 50)
    print("监控完成")

if __name__ == "__main__":
    main()
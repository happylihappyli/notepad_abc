#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细启动诊断脚本 - 深度分析程序启动问题
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

def get_process_creation_time(pid):
    """获取进程创建时间"""
    try:
        process_handle = kernel32.OpenProcess(0x0400, False, pid)  # PROCESS_QUERY_INFORMATION
        if process_handle:
            creation_time = wintypes.FILETIME()
            exit_time = wintypes.FILETIME()
            kernel_time = wintypes.FILETIME()
            user_time = wintypes.FILETIME()
            
            if kernel32.GetProcessTimes(process_handle, 
                                      ctypes.byref(creation_time),
                                      ctypes.byref(exit_time),
                                      ctypes.byref(kernel_time),
                                      ctypes.byref(user_time)):
                # 将FILETIME转换为Python时间
                # FILETIME是100纳秒单位从1601年1月1日开始
                import datetime
                epoch_start = datetime.datetime(1601, 1, 1)
                creation_timestamp = (creation_time.dwHighDateTime << 32) + creation_time.dwLowDateTime
                creation_datetime = epoch_start + datetime.timedelta(microseconds=creation_timestamp / 10)
                kernel32.CloseHandle(process_handle)
                return creation_datetime
            kernel32.CloseHandle(process_handle)
    except Exception as e:
        pass
    return None

def check_console_output(pid):
    """检查控制台输出"""
    try:
        # 尝试从标准输出读取
        import psutil
        process = psutil.Process(pid)
        
        # 尝试读取标准输出和标准错误
        stdout_data = ""
        stderr_data = ""
        
        try:
            # 这在Windows上可能不起作用，但值得一试
            stdout_data = process.stdout.read() if hasattr(process, 'stdout') else ""
        except:
            pass
            
        try:
            stderr_data = process.stderr.read() if hasattr(process, 'stderr') else ""
        except:
            pass
            
        return stdout_data, stderr_data
    except:
        return "", ""

def analyze_process_details(pid):
    """分析进程详细信息"""
    process_info = {}
    
    try:
        import psutil
        process = psutil.Process(pid)
        
        # 基本信息
        process_info["pid"] = pid
        process_info["name"] = process.name()
        process_info["status"] = process.status()
        process_info["create_time"] = process.create_time()
        process_info["cmdline"] = process.cmdline()
        
        # 内存信息
        memory_info = process.memory_info()
        process_info["memory"] = {
            "rss": memory_info.rss,  # 常驻内存
            "vms": memory_info.vms,  # 虚拟内存
        }
        
        # CPU信息
        try:
            process_info["cpu_percent"] = process.cpu_percent(interval=1)
        except:
            process_info["cpu_percent"] = 0
        
        # 线程信息
        try:
            process_info["num_threads"] = process.num_threads()
        except:
            process_info["num_threads"] = 0
        
        # 文件描述符（Windows上通常无效）
        try:
            process_info["num_handles"] = process.num_handles()
        except:
            process_info["num_handles"] = "N/A"
            
    except Exception as e:
        process_info["error"] = str(e)
    
    return process_info

def find_all_windows():
    """查找所有窗口"""
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
    
    return all_windows

def check_important_files():
    """检查重要文件"""
    important_files = [
        # 配置文件
        "config.xml",
        "nativeLang.xml",
        "shortcuts.xml", 
        "stylers.xml",
        "contextMenu.xml",
        "doLocalConf.xml",
        
        # 目录
        "themes",
        "plugins",
        
        # 可执行文件相关
        "bin/notepad_abc_new.exe",
        
        # 可能的DLL依赖
        "bin/bin",
    ]
    
    file_status = {}
    
    for item in important_files:
        path = Path(item)
        if path.exists():
            if path.is_file():
                file_status[item] = {"exists": True, "type": "file", "size": path.stat().st_size}
            else:
                file_status[item] = {"exists": True, "type": "directory"}
        else:
            file_status[item] = {"exists": False}
    
    return file_status

def test_minimal_startup():
    """测试最小化启动"""
    print("=== 最小化启动测试 ===")
    
    exe_path = Path("bin/notepad_abc_new.exe")
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return None
    
    print(f"可执行文件: {exe_path}")
    print(f"文件大小: {exe_path.stat().st_size} bytes")
    
    try:
        # 启动程序
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW | subprocess.STARTF_USESTDHANDLES
        startupinfo.wShowWindow = 0  # SW_HIDE
        
        process = subprocess.Popen(
            [str(exe_path)],
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"✅ 进程已启动，PID: {process.pid}")
        
        # 等待一段时间让程序初始化
        print("等待程序初始化...")
        time.sleep(3)
        
        # 分析进程
        process_info = analyze_process_details(process.pid)
        print(f"进程信息:")
        print(f"  状态: {process_info.get('status', 'Unknown')}")
        print(f"  内存使用: {process_info.get('memory', {}).get('rss', 0) / 1024 / 1024:.1f} MB")
        print(f"  线程数: {process_info.get('num_threads', 0)}")
        
        # 检查窗口
        print("检查窗口...")
        all_windows = find_all_windows()
        notepad_windows = [w for w in all_windows if "Notepad" in w.get('title', '') or "Notepad" in w.get('class_name', '')]
        
        print(f"总窗口数: {len(all_windows)}")
        print(f"Notepad相关窗口: {len(notepad_windows)}")
        
        if notepad_windows:
            print("找到的Notepad窗口:")
            for window in notepad_windows:
                print(f"  标题: '{window['title']}'")
                print(f"  类名: '{window['class_name']}'")
                print(f"  可见: {window['is_visible']}")
                print(f"  启用: {window['is_enabled']}")
        else:
            print("未找到Notepad窗口")
            print("所有窗口概览:")
            for window in all_windows[:5]:  # 只显示前5个窗口
                if window['title'] or 'class' in window['class_name'].lower():
                    print(f"  '{window['title']}' / {window['class_name']} (可见: {window['is_visible']})")
        
        # 尝试读取控制台输出
        try:
            stdout_data, stderr_data = process.communicate(timeout=5)
            if stdout_data:
                print("标准输出:")
                print(stdout_data[:1000])  # 限制输出长度
            if stderr_data:
                print("标准错误:")
                print(stderr_data[:1000])
        except subprocess.TimeoutExpired:
            print("程序仍在运行，强制终止...")
            process.terminate()
            try:
                process.wait(timeout=3)
            except:
                process.kill()
        
        return process_info
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return None

def main():
    print("详细启动诊断")
    print("=" * 60)
    
    # 1. 检查文件
    print("1. 检查重要文件")
    files_status = check_important_files()
    missing_files = [k for k, v in files_status.items() if not v.get('exists', False)]
    if missing_files:
        print(f"❌ 缺失文件/目录: {', '.join(missing_files)}")
    else:
        print("✅ 所有重要文件都存在")
    print()
    
    # 2. 最小化启动测试
    process_info = test_minimal_startup()
    
    # 3. 生成诊断报告
    print("\n" + "=" * 60)
    print("诊断报告")
    print("=" * 60)
    
    report = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "working_directory": os.getcwd(),
        "files_status": files_status,
        "process_info": process_info,
        "missing_files": missing_files
    }
    
    try:
        with open("detailed_diagnostic_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("详细报告已保存到: detailed_diagnostic_report.json")
    except Exception as e:
        print(f"保存报告失败: {e}")
    
    print("\n根据诊断结果，程序启动但窗口不显示的原因可能是:")
    print("1. 程序在初始化过程中遇到了未处理的异常")
    print("2. 窗口创建但被立即隐藏或最小化")
    print("3. 程序依赖的DLL文件缺失或版本不兼容")
    print("4. 程序需要管理员权限或其他特殊权限")
    
    return len(missing_files) == 0 and process_info is not None

if __name__ == "__main__":
    main()
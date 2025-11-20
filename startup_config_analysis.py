#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动配置分析脚本 - 检查notepad_abc项目的启动配置和窗口显示问题
"""

import os
import sys
import time
import ctypes
from ctypes import wintypes
import subprocess
import json
import shutil
from pathlib import Path

# Windows API函数定义
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), 
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [("length", wintypes.UINT), ("flags", wintypes.UINT),
                ("showCmd", wintypes.UINT), ("ptMinPosition", POINT),
                ("ptMaxPosition", POINT), ("rcNormalPosition", RECT)]

def check_config_files():
    """检查配置文件是否存在和配置状态"""
    config_analysis = {
        "config_files": {},
        "total_files": 0,
        "missing_files": []
    }
    
    config_dir = Path("config")
    
    # 检查重要的配置文件
    important_files = [
        "config.xml",
        "nativeLang.xml", 
        "shortcuts.xml",
        "stylers.xml",
        "themes/theme.xml",
        "plugins/config.ini"
    ]
    
    for config_file in important_files:
        config_path = config_dir / config_file
        full_path = config_path.resolve()
        
        if full_path.exists():
            file_size = full_path.stat().st_size
            config_analysis["config_files"][config_file] = {
                "exists": True,
                "size": file_size,
                "last_modified": full_path.stat().st_mtime
            }
        else:
            config_analysis["config_files"][config_file] = {
                "exists": False
            }
            config_analysis["missing_files"].append(config_file)
        
        config_analysis["total_files"] += 1
    
    return config_analysis

def analyze_window_state(hwnd):
    """分析窗口状态"""
    window_info = {}
    
    try:
        # 获取窗口标题
        title_length = user32.GetWindowTextLengthW(hwnd)
        if title_length > 0:
            title_buffer = ctypes.create_unicode_buffer(title_length + 1)
            user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
            window_info["title"] = title_buffer.value
        else:
            window_info["title"] = ""
        
        # 获取窗口类名
        class_name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_name, 256)
        window_info["class_name"] = class_name.value
        
        # 检查窗口是否可见
        window_info["is_visible"] = bool(user32.IsWindowVisible(hwnd))
        
        # 获取窗口位置和大小
        placement = WINDOWPLACEMENT()
        placement.length = ctypes.sizeof(WINDOWPLACEMENT)
        
        if user32.GetWindowPlacement(hwnd, ctypes.byref(placement)):
            window_info["show_command"] = placement.showCmd
            window_info["normal_position"] = {
                "left": placement.rcNormalPosition.left,
                "top": placement.rcNormalPosition.top,
                "right": placement.rcNormalPosition.right,
                "bottom": placement.rcNormalPosition.bottom
            }
        
        # 获取实际窗口矩形
        rect = RECT()
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            window_info["actual_rect"] = {
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom
            }
        
        # 检查窗口是否被最小化
        window_info["is_minimized"] = bool(user32.IsIconic(hwnd))
        
        # 检查窗口是否被最大化
        window_info["is_maximized"] = bool(user32.IsZoomed(hwnd))
        
    except Exception as e:
        window_info["error"] = str(e)
    
    return window_info

def find_notepad_windows():
    """查找Notepad++窗口"""
    notepad_windows = []
    
    def enum_window_proc(hwnd, lParam):
        # 检查是否包含"Notepad"或"Notepad++"在标题中
        title_buffer = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, title_buffer, 512)
        title = title_buffer.value
        
        if "Notepad" in title:
            class_buffer = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buffer, 256)
            class_name = class_buffer.value
            
            if "Notepad" in class_name:
                window_info = analyze_window_state(hwnd)
                window_info["hwnd"] = hwnd
                notepad_windows.append(window_info)
        
        return True  # 继续枚举
    
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))
    enum_proc = EnumWindowsProc(enum_window_proc)
    
    user32.EnumWindows(enum_proc, 0)
    
    return notepad_windows

def start_process_monitoring():
    """启动进程监控"""
    executable = Path("bin/notepad_abc_new.exe")
    
    if not executable.exists():
        executable = Path("notepad_abc_new.exe")
    
    if not executable.exists():
        return {"error": "可执行文件不存在"}
    
    print(f"启动进程监控: {executable}")
    
    # 启动进程
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 1  # SW_NORMAL
        
        process = subprocess.Popen(
            [str(executable)],
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"进程已启动，PID: {process.pid}")
        
        # 等待3秒让窗口有机会创建
        time.sleep(3)
        
        # 查找窗口
        windows = find_notepad_windows()
        
        # 等待额外2秒
        time.sleep(2)
        
        # 检查进程状态
        try:
            process_status = process.poll()
            if process_status is None:
                process_state = "运行中"
                # 强制终止进程
                process.terminate()
                process.wait(timeout=5)
            else:
                process_state = f"已退出 (代码: {process_status})"
        except Exception as e:
            process_state = f"检查失败: {str(e)}"
        
        return {
            "process_id": process.pid,
            "process_state": process_state,
            "windows_found": len(windows),
            "windows": windows
        }
        
    except Exception as e:
        return {"error": f"启动失败: {str(e)}"}

def analyze_directory_permissions():
    """分析目录权限"""
    permission_analysis = {}
    
    important_dirs = [
        ".",
        "config",
        "bin",
        "themes"
    ]
    
    for directory in important_dirs:
        try:
            dir_path = Path(directory)
            if dir_path.exists():
                # 检查读权限
                can_read = os.access(directory, os.R_OK)
                can_write = os.access(directory, os.W_OK)
                can_execute = os.access(directory, os.X_OK)
                
                # 尝试创建临时文件
                temp_file = None
                temp_error = None
                try:
                    temp_file = os.path.join(directory, "temp_test.tmp")
                    with open(temp_file, "w") as f:
                        f.write("test")
                    os.remove(temp_file)
                    can_create = True
                except Exception as e:
                    can_create = False
                    temp_error = str(e)
                
                permission_analysis[directory] = {
                    "exists": True,
                    "can_read": can_read,
                    "can_write": can_write,
                    "can_execute": can_execute,
                    "can_create_files": can_create,
                    "error": temp_error
                }
            else:
                permission_analysis[directory] = {
                    "exists": False,
                    "can_read": False,
                    "can_write": False,
                    "can_execute": False,
                    "can_create_files": False
                }
        except Exception as e:
            permission_analysis[directory] = {
                "error": str(e)
            }
    
    return permission_analysis

def main():
    print("=== Notepad_ABC 启动配置分析 ===")
    print(f"工作目录: {os.getcwd()}")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 配置文件分析
    print("1. 配置文件分析")
    config_analysis = check_config_files()
    print(f"   检查了 {config_analysis['total_files']} 个配置文件")
    if config_analysis['missing_files']:
        print(f"   缺失文件: {', '.join(config_analysis['missing_files'])}")
    else:
        print("   所有重要配置文件都存在")
    print()
    
    # 2. 目录权限分析
    print("2. 目录权限分析")
    permission_analysis = analyze_directory_permissions()
    for directory, perms in permission_analysis.items():
        if "error" in perms:
            print(f"   {directory}: 错误 - {perms['error']}")
        elif not perms.get("exists", False):
            print(f"   {directory}: 目录不存在")
        else:
            status = []
            if perms.get("can_read"): status.append("读")
            if perms.get("can_write"): status.append("写")
            if perms.get("can_execute"): status.append("执行")
            if perms.get("can_create_files"): status.append("创建文件")
            print(f"   {directory}: {'/'.join(status) if status else '无权限'}")
    print()
    
    # 3. 进程启动和窗口分析
    print("3. 进程启动和窗口分析")
    try:
        process_info = start_process_monitoring()
        
        if "error" in process_info:
            print(f"   进程启动失败: {process_info['error']}")
        else:
            print(f"   进程PID: {process_info['process_id']}")
            print(f"   进程状态: {process_info['process_state']}")
            print(f"   发现窗口数: {process_info['windows_found']}")
            
            if process_info['windows']:
                print("   窗口详情:")
                for i, window in enumerate(process_info['windows'], 1):
                    print(f"     窗口 {i}:")
                    print(f"       标题: {window.get('title', 'N/A')}")
                    print(f"       类名: {window.get('class_name', 'N/A')}")
                    print(f"       句柄: {window.get('hwnd', 'N/A')}")
                    print(f"       可见: {window.get('is_visible', 'N/A')}")
                    print(f"       最小化: {window.get('is_minimized', 'N/A')}")
                    print(f"       最大化: {window.get('is_maximized', 'N/A')}")
                    
                    if "actual_rect" in window:
                        rect = window["actual_rect"]
                        print(f"       位置: ({rect['left']}, {rect['top']}) - ({rect['right']}, {rect['bottom']})")
                        width = rect['right'] - rect['left']
                        height = rect['bottom'] - rect['top']
                        print(f"       大小: {width}x{height}")
                    print()
            else:
                print("   没有发现Notepad++窗口")
    except Exception as e:
        print(f"   进程分析出错: {str(e)}")
    
    print()
    print("=== 分析完成 ===")
    
    # 生成详细报告
    report = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "working_directory": os.getcwd(),
        "config_analysis": config_analysis,
        "permission_analysis": permission_analysis,
        "process_analysis": process_info if 'process_info' in locals() else {"error": "未执行"}
    }
    
    try:
        with open("startup_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("详细报告已保存到: startup_analysis_report.json")
    except Exception as e:
        print(f"保存报告失败: {str(e)}")

if __name__ == "__main__":
    main()
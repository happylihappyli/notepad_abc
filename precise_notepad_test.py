#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确的notepad_abc窗口检测测试
"""

import os
import sys
import time
import subprocess
import psutil
import win32api
import win32con
import win32gui
import win32process

def fix_utf8_environment():
    """设置UTF-8编码环境"""
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul')
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def find_notepad_abc_processes():
    """查找所有notepad_abc相关进程"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            pinfo = proc.info
            if pinfo['name'] and 'notepad' in pinfo['name'].lower():
                processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def find_windows_by_process(hwnd, window_list):
    """回调函数：按进程查找窗口"""
    if win32gui.IsWindowVisible(hwnd):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        window_title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        
        # 检查窗口类型
        is_console = 'Console' in class_name or 'ConsoleWindowClass' in class_name
        is_main_window = any(term in window_title for term in ['Notepad++', 'notepad', 'text', 'editor']) and not is_console
        
        if is_main_window:
            window_list.append({
                'hwnd': hwnd,
                'title': window_title,
                'class': class_name,
                'pid': pid,
                'type': 'main'
            })
        elif is_console:
            window_list.append({
                'hwnd': hwnd,
                'title': window_title,
                'class': class_name,
                'pid': pid,
                'type': 'console'
            })

def test_precise_notepad_detection():
    """精确检测notepad_abc窗口"""
    print("=== 精确notepad_abc窗口检测 ===")
    
    exe_path = os.path.join(os.getcwd(), "bin", "notepad_abc_new.exe")
    
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False
    
    # 获取启动前的进程列表
    initial_processes = find_notepad_abc_processes()
    initial_pids = {p['pid'] for p in initial_processes}
    print(f"启动前相关进程: {len(initial_pids)}")
    
    # 启动进程
    try:
        print("启动notepad_abc...")
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        print(f"✅ 进程启动成功，PID: {process.pid}")
        
        # 等待窗口创建
        time.sleep(5)
        
        # 获取启动后的进程列表
        current_processes = find_notepad_abc_processes()
        new_processes = [p for p in current_processes if p['pid'] not in initial_pids]
        
        if new_processes:
            print(f"✅ 发现新进程: {len(new_processes)}")
            for proc in new_processes:
                print(f"   PID: {proc['pid']}, Name: {proc['name']}, Exe: {proc['exe']}")
        else:
            print("❌ 未发现新进程")
            return False
        
        # 枚举所有窗口
        all_windows = []
        win32gui.EnumWindows(find_windows_by_process, all_windows)
        
        # 过滤出当前进程的窗口
        notepad_windows = [w for w in all_windows if w['pid'] == process.pid]
        
        if notepad_windows:
            print(f"✅ 找到 {len(notepad_windows)} 个相关窗口:")
            for w in notepad_windows:
                print(f"   类型: {w['type']}")
                print(f"   标题: {w['title']}")
                print(f"   类名: {w['class']}")
                print(f"   PID: {w['pid']}")
                print(f"   句柄: {w['hwnd']}")
                print()
            
            # 检查是否有主窗口
            main_windows = [w for w in notepad_windows if w['type'] == 'main']
            if main_windows:
                print("✅ 成功创建主窗口！")
                return True
            else:
                print("❌ 只创建了控制台窗口，无主窗口")
                return False
        else:
            print("❌ 未找到相关窗口")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False
    finally:
        # 清理进程
        try:
            os.system(f"taskkill /PID {process.pid} /F > nul")
            print("✅ 进程已清理")
        except:
            pass

def check_process_status():
    """检查进程状态"""
    print("=== 进程状态检查 ===")
    
    processes = find_notepad_abc_processes()
    
    for proc_info in processes:
        try:
            proc = psutil.Process(proc_info['pid'])
            
            # 获取进程信息
            memory_info = proc.memory_info()
            cpu_percent = proc.cpu_percent()
            create_time = proc.create_time()
            status = proc.status()
            
            print(f"进程信息:")
            print(f"   PID: {proc_info['pid']}")
            print(f"   名称: {proc_info['name']}")
            print(f"   路径: {proc_info['exe']}")
            print(f"   状态: {status}")
            print(f"   内存: {memory_info.rss / 1024 / 1024:.1f} MB")
            print(f"   CPU: {cpu_percent:.1f}%")
            print(f"   创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))}")
            print()
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"无法获取进程 {proc_info['pid']} 的详细信息: {e}")

def main():
    """主函数"""
    print("============================================================")
    print("精确的notepad_abc窗口检测")
    print("============================================================")
    
    fix_utf8_environment()
    
    # 检查当前进程状态
    check_process_status()
    
    # 测试精确窗口检测
    result = test_precise_notepad_detection()
    
    print("\n============================================================")
    print("测试结果")
    print("============================================================")
    
    if result:
        print("✅ 成功！程序能够正常创建GUI窗口")
    else:
        print("❌ 失败！程序只创建控制台窗口，无法创建GUI主窗口")
        print("\n问题分析:")
        print("1. 程序启动成功但GUI初始化失败")
        print("2. 窗口注册过程可能出错")
        print("3. 主题或样式加载可能阻塞窗口创建")
        print("4. 插件系统可能阻止GUI初始化")
        print("\n建议解决方案:")
        print("1. 检查Windows事件查看器的应用程序日志")
        print("2. 使用Process Monitor监控文件访问")
        print("3. 尝试在安全模式下启动(禁用插件)")
        print("4. 检查主题文件和图标资源")

if __name__ == "__main__":
    main()
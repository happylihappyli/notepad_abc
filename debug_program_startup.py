#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import time
import os
import threading
from datetime import datetime

def monitor_process_startup():
    """监控程序启动过程"""
    exe_path = "bin\\notepad_abc.exe"
    
    print("=== 程序启动调试器 ===")
    print(f"程序路径: {os.path.abspath(exe_path)}")
    
    # 1. 检查文件是否存在
    if not os.path.exists(exe_path):
        print("❌ 程序文件不存在！")
        return
    
    file_size = os.path.getsize(exe_path)
    print(f"✅ 程序文件存在，大小: {file_size:,} 字节")
    
    # 2. 尝试直接运行程序并监控输出
    print("\n=== 尝试启动程序 ===")
    
    try:
        # 使用subprocess.PIPE捕获输出
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"✅ 程序启动成功，PID: {process.pid}")
        
        # 监控进程5秒
        for i in range(10):
            time.sleep(0.5)
            poll_result = process.poll()
            
            if poll_result is None:
                print(f"🟢 程序正在运行 ({i*0.5:.1f}s)")
            else:
                print(f"🔴 程序已退出，退出码: {poll_result}")
                
                # 读取输出
                try:
                    stdout, stderr = process.communicate(timeout=2)
                    if stdout:
                        print(f"\n📄 标准输出:")
                        print(stdout)
                    if stderr:
                        print(f"\n❌ 错误输出:")
                        print(stderr)
                except:
                    pass
                break
        else:
            print("⏰ 5秒后程序仍在运行")
            process.terminate()
            try:
                process.wait(timeout=3)
            except:
                process.kill()
                
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        
        # 尝试检查依赖项
        print("\n=== 检查程序依赖 ===")
        try:
            # 尝试用depends.exe或类似工具检查
            print("请检查程序是否缺少必要的DLL文件")
        except:
            pass

def check_existing_processes():
    """检查现有的notepad进程"""
    import psutil
    
    print("\n=== 检查现有进程 ===")
    
    notepad_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'notepad' in proc.info['name'].lower():
                notepad_processes.append(proc.info)
        except:
            pass
    
    if notepad_processes:
        print(f"找到 {len(notepad_processes)} 个相关进程:")
        for proc in notepad_processes:
            print(f"  PID: {proc['pid']}, 名称: {proc['name']}")
            if proc['cmdline']:
                print(f"    命令行: {' '.join(proc['cmdline'])}")
    else:
        print("未找到相关进程")

def main():
    monitor_process_startup()
    check_existing_processes()
    
    print("\n=== 建议的操作 ===")
    print("1. 如果程序无法启动，检查是否有缺失的DLL文件")
    print("2. 尝试在命令行中运行程序查看详细错误信息")
    print("3. 检查Windows事件日志")
    print("4. 确保有足够的权限运行程序")

if __name__ == "__main__":
    main()
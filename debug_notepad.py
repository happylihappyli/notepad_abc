#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试notepad_abc程序的简单测试脚本
"""

import subprocess
import time
import sys
import os

def main():
    print("正在启动notepad_abc程序进行调试...")
    
    # 运行程序
    exe_path = "bin\\notepad_abc_new.exe"
    if not os.path.exists(exe_path):
        print(f"错误：找不到可执行文件 {exe_path}")
        return 1
    
    try:
        # 启动进程
        proc = subprocess.Popen(
            [exe_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"进程已启动，PID: {proc.pid}")
        
        # 等待程序初始化
        time.sleep(5)
        
        # 检查进程是否还在运行
        if proc.poll() is None:
            print("进程仍在运行")
            
            # 尝试获取一些基本信息
            try:
                import psutil
                p = psutil.Process(proc.pid)
                print(f"内存使用: {p.memory_info().rss} bytes")
                print(f"创建时间: {p.create_time()}")
            except ImportError:
                print("psutil不可用，跳过进程信息获取")
            except Exception as e:
                print(f"获取进程信息时出错: {e}")
            
            # 等待一段时间，看是否有错误输出
            try:
                stdout, stderr = proc.communicate(timeout=3)
                if stdout:
                    print("标准输出:")
                    print(stdout)
                if stderr:
                    print("标准错误:")
                    print(stderr)
            except subprocess.TimeoutExpired:
                print("程序仍在运行，没有输出")
                proc.terminate()
                try:
                    stdout, stderr = proc.communicate(timeout=2)
                    if stdout:
                        print("终止时的标准输出:")
                        print(stdout)
                    if stderr:
                        print("终止时的标准错误:")
                        print(stderr)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    print("强制终止进程")
        else:
            print("进程已退出")
            stdout, stderr = proc.communicate()
            if stdout:
                print("标准输出:")
                print(stdout)
            if stderr:
                print("标准错误:")
                print(stderr)
                
    except Exception as e:
        print(f"运行程序时出错: {e}")
        return 1
    
    print("调试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试notepad_abc.exe是否能够正常启动
"""

import os
import sys
import time
import subprocess

def main():
    print("测试notepad_abc.exe是否能够正常启动")
    print("=" * 50)
    
    exe_path = os.path.join(os.path.dirname(__file__), "bin", "notepad_abc.exe")
    
    if not os.path.exists(exe_path):
        print(f"错误: 可执行文件不存在: {exe_path}")
        return 1
    
    print(f"可执行文件存在: {exe_path}")
    print(f"文件大小: {os.path.getsize(exe_path)} 字节")
    
    # 尝试启动程序
    try:
        print("尝试启动程序...")
        process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待一段时间让程序启动
        time.sleep(3)
        
        # 检查进程是否仍在运行
        if process.poll() is None:
            print("程序已成功启动并正在运行")
            # 终止进程
            process.terminate()
            return 0
        else:
            print("程序启动失败或已退出")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"标准输出: {stdout.decode('utf-8', errors='ignore')}")
            if stderr:
                print(f"标准错误: {stderr.decode('utf-8', errors='ignore')}")
            return 1
    except Exception as e:
        print(f"启动程序时发生异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
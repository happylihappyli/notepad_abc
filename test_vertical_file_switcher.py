#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试VerticalFileSwitcher是否正常工作
"""

import os
import sys
import time
import subprocess

def is_process_running(process_name):
    """检查指定名称的进程是否在运行"""
    try:
        # 使用tasklist命令检查进程
        result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name}'], 
                              capture_output=True, text=True)
        return process_name in result.stdout
    except:
        return False

def main():
    print("测试VerticalFileSwitcher是否正常工作")
    print("=" * 50)
    
    # 检查notepad_abc.exe是否在运行
    if not is_process_running('notepad_abc.exe'):
        print("错误: notepad_abc.exe未运行")
        return 1
    
    print("notepad_abc.exe正在运行")
    
    # 等待几秒钟，让程序完全启动
    print("等待程序完全启动...")
    time.sleep(3)
    
    # 检查错误日志
    error_log_path = os.path.join(os.path.dirname(__file__), "error.txt")
    if os.path.exists(error_log_path):
        with open(error_log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "StaticDialog::create" in content:
                print("警告: 错误日志中仍然包含'StaticDialog::create'")
                print("最近的错误内容:")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "StaticDialog::create" in line:
                        start = max(0, i-5)
                        end = min(len(lines), i+6)
                        for j in range(start, end):
                            print(f"{j}: {lines[j]}")
                        break
                return 1
            else:
                print("错误日志中未找到'StaticDialog::create'")
    else:
        print("未找到错误日志文件")
    
    print("测试完成: VerticalFileSwitcher似乎正常工作")
    return 0

if __name__ == "__main__":
    sys.exit(main())
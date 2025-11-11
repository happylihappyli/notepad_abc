#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文档列表功能是否正常工作
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
    print("测试文档列表功能是否正常工作")
    print("=" * 50)
    
    # 检查notepad_abc.exe是否在运行
    if not is_process_running('notepad_abc.exe'):
        print("错误: notepad_abc.exe未运行")
        print("请先启动notepad_abc.exe")
        return 1
    
    print("notepad_abc.exe正在运行")
    
    # 检查错误日志
    error_log_path = os.path.join(os.path.dirname(__file__), "error", "2.txt")
    if os.path.exists(error_log_path):
        with open(error_log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "CreateDialogParam() return NULL" in content:
                print("警告: 错误日志中仍然包含'CreateDialogParam() return NULL'")
                print("最近的错误内容:")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "CreateDialogParam() return NULL" in line:
                        start = max(0, i-5)
                        end = min(len(lines), i+6)
                        for j in range(start, end):
                            print(f"{j}: {lines[j]}")
                        break
                return 1
            else:
                print("错误日志中未找到'CreateDialogParam() return NULL'")
    else:
        print("未找到错误日志文件")
    
    # 检查主错误日志
    main_error_log_path = os.path.join(os.path.dirname(__file__), "bin", "error.txt")
    if os.path.exists(main_error_log_path):
        with open(main_error_log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "CreateDialogParam() return NULL" in content:
                print("警告: 主错误日志中包含'CreateDialogParam() return NULL'")
                return 1
            else:
                print("主错误日志中未找到'CreateDialogParam() return NULL'")
    
    print("测试完成: 文档列表功能似乎正常工作")
    return 0

if __name__ == "__main__":
    sys.exit(main())
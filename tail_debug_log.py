#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import threading
from datetime import datetime

def tail_debug_log():
    """实时监控npp_debug.log文件"""
    log_file = "npp_debug.log"
    print(f"=== 监控调试日志文件: {log_file} ===")
    print("等待程序生成调试日志...")
    print("请在程序中点击设置菜单，观察日志输出:")
    print("-" * 60)
    
    # 检查文件是否存在
    if not os.path.exists(log_file):
        print(f"日志文件 {log_file} 不存在，程序可能尚未启动或未生成调试日志")
        return
        
    # 获取文件初始大小
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, 2)  # 移动到文件末尾
        last_size = f.tell()
    
    print(f"当前日志文件大小: {last_size} 字节")
    
    # 监控循环
    while True:
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_size)
                    new_lines = f.readlines()
                    
                    for line in new_lines:
                        line = line.strip()
                        if line:
                            # 高亮显示相关的调试信息
                            if '设置命令被触发' in line or 'popupMenuCmd' in line or '设置对话框' in line or 'IDM_SETTING_PREFERENCE' in line:
                                print(f"*** {datetime.now().strftime('%H:%M:%S')} *** {line}")
                            else:
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
                    
                    if new_lines:
                        last_size = f.tell()
                        
            time.sleep(0.5)  # 每500ms检查一次
            
        except KeyboardInterrupt:
            print("\n监控已停止")
            break
        except Exception as e:
            print(f"监控出错: {e}")
            time.sleep(1)

def main():
    print("=== Notepad++ 设置菜单调试日志监控器 ===")
    print()
    print("使用方法:")
    print("1. 先启动Notepad++程序")
    print("2. 在垂直文件切换器中右键点击")
    print("3. 点击'setting'菜单项")
    print("4. 观察下方调试日志输出")
    print()
    print("我将监控以下关键日志:")
    print("- '设置命令被触发' - 点击设置菜单被检测到")
    print("- '已发送标准设置对话框打开消息' - 发送消息到主程序")
    print("- '设置对话框' 相关日志 - 设置对话框的创建/显示")
    print()
    print("开始监控...")
    print("-" * 60)
    
    tail_debug_log()

if __name__ == "__main__":
    main()
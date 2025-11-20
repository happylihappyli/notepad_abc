#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字体大小标签修复效果
检查"字体大小"标签后是否还有额外的文字信息
"""

import os
import sys
import time
import subprocess
import psutil
import signal

def kill_process_tree(pid):
    """终止进程树"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.terminate()
        parent.terminate()
        
        # 等待进程结束
        gone, alive = psutil.wait_procs([parent], timeout=3)
        for p in alive:
            p.kill()
        return True
    except:
        return False

def test_font_size_label_fix():
    """测试字体大小标签修复"""
    print("=" * 60)
    print("测试字体大小标签修复效果")
    print("=" * 60)
    
    # 启动程序
    exe_path = r"bin\notepad_abc.exe"
    if not os.path.exists(exe_path):
        print(f"错误：可执行文件不存在 - {exe_path}")
        return False
    
    print(f"启动程序: {exe_path}")
    
    try:
        # 启动程序
        process = subprocess.Popen(
            exe_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        pid = process.pid
        print(f"程序已启动，PID: {pid}")
        
        # 等待程序启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        try:
            if psutil.pid_exists(pid):
                print(f"✓ 程序正在运行 (PID: {pid})")
                
                # 检查程序句柄
                try:
                    proc = psutil.Process(pid)
                    print(f"  - 进程名: {proc.name()}")
                    print(f"  - 状态: {proc.status()}")
                except:
                    pass
                
                print("\n请手动检查以下内容：")
                print("1. 打开垂直文件切换器（点击左侧的文件列表图标）")
                print("2. 观察'字体大小:'标签是否正常显示")
                print("3. 检查'字体大小:'标签后面是否还有额外的文字信息")
                print("4. 测试字体大小下拉框功能是否正常")
                
                print("\n程序将保持运行60秒，请在此期间进行手动测试...")
                time.sleep(60)
                
            else:
                print("✗ 程序未启动或已退出")
                return False
                
        except psutil.NoSuchProcess:
            print("✗ 进程不存在")
            return False
            
    except Exception as e:
        print(f"错误：启动程序时发生异常 - {e}")
        return False
    
    finally:
        # 终止程序
        print("\n正在终止程序...")
        try:
            kill_process_tree(pid)
            print("✓ 程序已终止")
        except:
            try:
                os.kill(pid, signal.SIGTERM)
                print("✓ 程序已终止")
            except:
                print("✗ 终止程序失败")
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_font_size_label_fix()
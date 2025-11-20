#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试修复后的程序是否有基本的UI响应
"""

import subprocess
import time
import ctypes
from ctypes import wintypes
import threading
import sys

def test_process_lifecycle():
    """测试程序的生命周期"""
    exe_path = "bin\\notepad_abc_new.exe"
    
    print(f"=== 测试程序生命周期 ===")
    print(f"启动程序: {exe_path}")
    
    try:
        # 启动程序
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        print(f"进程已启动，PID: {process.pid}")
        
        # 等待3秒
        print("等待3秒...")
        time.sleep(3)
        
        # 检查进程是否还在运行
        poll_result = process.poll()
        print(f"进程状态检查: poll() 返回 {poll_result}")
        
        if poll_result is None:
            print("✅ 进程仍在运行")
            
            # 尝试获取进程输出
            try:
                # 非阻塞读取输出
                import select
                if select.select([process.stderr], [], [], 0)[0]:
                    error_output = process.stderr.read()
                    if error_output:
                        print(f"错误输出: {error_output}")
                else:
                    print("无错误输出")
                    
                if select.select([process.stdout], [], [], 0)[0]:
                    stdout_output = process.stdout.read()
                    if stdout_output:
                        print(f"标准输出: {stdout_output}")
                    else:
                        print("无标准输出")
            except:
                print("无法读取进程输出")
                
        else:
            print(f"❌ 进程已退出，返回码: {poll_result}")
            
            # 获取错误信息
            try:
                stderr_output, stdout_output = process.communicate(timeout=1)
                if stderr_output:
                    print(f"错误信息: {stderr_output}")
                if stdout_output:
                    print(f"输出信息: {stdout_output}")
            except:
                print("无法获取退出信息")
        
        # 终止进程
        print("终止测试进程...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            
        print("测试完成")
        
    except Exception as e:
        print(f"❌ 启动程序失败: {e}")
        return False
    
    return True

def test_with_detailed_logging():
    """使用详细日志测试"""
    exe_path = "bin\\notepad_abc_new.exe"
    
    print(f"\n=== 详细日志测试 ===")
    
    # 创建详细的启动日志
    log_file = "startup_debug.log"
    
    try:
        # 使用重定向启动程序
        with open(log_file, 'w', encoding='utf-8') as log:
            process = subprocess.Popen(
                [exe_path],
                stdout=log,
                stderr=log,
                text=True,
                encoding='utf-8'
            )
            
            print(f"程序已启动，PID: {process.pid}")
            
            # 等待5秒
            for i in range(5):
                time.sleep(1)
                poll_result = process.poll()
                if poll_result is not None:
                    print(f"程序在第{i+1}秒时退出，返回码: {poll_result}")
                    break
                else:
                    print(f"第{i+1}秒：程序仍在运行...")
            
            # 终止进程
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        
        # 读取日志文件
        print(f"\n读取日志文件: {log_file}")
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            if log_content:
                print("日志内容:")
                print(log_content)
            else:
                print("日志文件为空")
                
    except Exception as e:
        print(f"详细测试失败: {e}")

if __name__ == "__main__":
    print("开始程序UI修复验证测试")
    
    # 测试生命周期
    test_process_lifecycle()
    
    # 详细日志测试
    test_with_detailed_logging()
    
    input("\n按回车键退出...")
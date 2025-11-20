#!/usr/bin/env python3
"""
简单GUI窗口测试脚本
"""
import subprocess
import time
import psutil
import os

def check_process_exists():
    """检查进程是否存在"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            if 'notepad_abc_new' in proc.info['name'].lower():
                return proc
        return None
    except:
        return None

def main():
    print("=== 简单GUI窗口测试 ===")
    
    # 启动程序
    print("启动notepad_abc_new.exe...")
    exe_path = os.path.abspath("bin\\notepad_abc_new.exe")
    
    if not os.path.exists(exe_path):
        print(f"❌ 找不到可执行文件: {exe_path}")
        return
    
    print(f"可执行文件路径: {exe_path}")
    
    # 启动进程
    process = subprocess.Popen(
        [exe_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False  # 使用二进制模式避免编码问题
    )
    
    print(f"进程启动成功，PID: {process.pid}")
    
    # 等待一下让程序初始化
    time.sleep(3)
    
    # 检查进程是否还在运行
    proc = psutil.Process(process.pid)
    try:
        print(f"进程状态: {proc.status()}")
        print(f"内存使用: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
        print(f"CPU使用率: {proc.cpu_percent():.1f}%")
        
        # 获取命令行
        try:
            cmdline = proc.cmdline()
            print(f"命令行: {' '.join(cmdline)}")
        except:
            pass
            
    except psutil.NoSuchProcess:
        print("❌ 进程已经退出")
        # 获取错误输出
        try:
            stdout, stderr = process.communicate(timeout=1)
            if stdout:
                print("标准输出:")
                print(stdout.decode('utf-8', errors='ignore'))
            if stderr:
                print("错误输出:")
                print(stderr.decode('utf-8', errors='ignore'))
        except:
            pass
        return
    
    # 再等待一下观察
    print("\n等待5秒观察进程行为...")
    time.sleep(5)
    
    # 最终检查
    try:
        proc = psutil.Process(process.pid)
        print(f"最终检查 - 进程仍在运行，PID: {process.pid}")
        print(f"当前内存使用: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
        
        if proc.memory_info().rss > 10 * 1024 * 1024:  # 大于10MB
            print("✅ 程序已正常启动并占用合理内存")
            print("⚠️  但GUI窗口未显示，可能存在以下问题：")
            print("   1. 窗口创建但被隐藏或最小化")
            print("   2. 窗口在屏幕外创建")
            print("   3. 窗口创建失败但程序继续运行")
        else:
            print("❌ 程序内存使用过低，可能初始化失败")
            
    except psutil.NoSuchProcess:
        print("❌ 进程已退出")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
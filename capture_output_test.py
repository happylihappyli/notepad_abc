#!/usr/bin/env python3
"""
捕获程序输出和错误信息测试脚本
"""
import subprocess
import time
import os

def main():
    print("=== 捕获程序输出测试 ===")
    
    exe_path = os.path.abspath("bin\\notepad_abc_new.exe")
    print(f"可执行文件路径: {exe_path}")
    
    if not os.path.exists(exe_path):
        print(f"❌ 找不到可执行文件: {exe_path}")
        return
    
    print("启动程序并捕获输出...")
    
    try:
        # 启动进程并等待
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"进程启动成功，PID: {process.pid}")
        
        # 等待进程退出或超时
        try:
            stdout, stderr = process.communicate(timeout=10)
            print(f"\n进程退出码: {process.returncode}")
            
            if stdout:
                print("\n=== 标准输出 ===")
                print(stdout)
            
            if stderr:
                print("\n=== 错误输出 ===")
                print(stderr)
                
        except subprocess.TimeoutExpired:
            print("\n进程运行10秒仍未退出")
            process.kill()
            try:
                stdout, stderr = process.communicate(timeout=2)
                if stdout:
                    print("\n=== 标准输出 ===")
                    print(stdout)
                if stderr:
                    print("\n=== 错误输出 ===")
                    print(stderr)
            except:
                pass
            
    except Exception as e:
        print(f"启动失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
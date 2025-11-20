#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的UI测试 - 直接运行程序并观察
"""

import subprocess
import time
import sys
import os

def main():
    print("=== 简单UI测试 ===")
    print("这个测试会:")
    print("1. 启动notepad_abc_new.exe")
    print("2. 等待5秒")  
    print("3. 检查程序状态")
    print("4. 显示结果")
    print("=" * 40)
    
    exe_path = "e:\\GitHub3\\notepad_abc\\bin\\notepad_abc_new.exe"
    
    if not os.path.exists(exe_path):
        print("❌ 程序文件不存在")
        return 1
    
    print(f"✅ 程序文件存在: {os.path.getsize(exe_path)} 字节")
    
    try:
        print("\n🚀 启动程序...")
        # 启动程序，不创建新控制台
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"📊 进程PID: {process.pid}")
        
        # 等待程序
        print("⏳ 等待5秒...")
        time.sleep(5)
        
        # 检查进程状态
        status = process.poll()
        if status is None:
            print("✅ 程序仍在运行")
            print("💡 如果您看不到窗口，请检查:")
            print("   - 任务管理器中是否有notepad_abc_new.exe进程")
            print("   - 窗口是否在屏幕外或被其他窗口遮挡")
            print("   - 尝试按Alt+Tab切换窗口")
            
            # 再等5秒看是否有变化
            print("\n⏳ 再等待5秒...")
            time.sleep(5)
            
            final_status = process.poll()
            if final_status is None:
                print("✅ 程序持续运行正常")
            else:
                print(f"⚠️ 程序退出了，退出代码: {final_status}")
            
            # 终止程序
            print("\n🛑 终止程序...")
            process.terminate()
            try:
                process.wait(timeout=2)
                print("✅ 程序已终止")
            except:
                print("⚠️ 强制终止程序")
                process.kill()
                
        else:
            print(f"❌ 程序已退出，退出代码: {status}")
            # 获取输出
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stdout:
                    print("标准输出:")
                    print(stdout)
                if stderr:
                    print("标准错误:")
                    print(stderr)
            except:
                pass
        
        return 0
        
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(1)
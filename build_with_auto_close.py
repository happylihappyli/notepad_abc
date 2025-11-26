#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能编译脚本 - 自动关闭程序后编译
自动检测并关闭notepad_abc相关进程，然后执行scons编译
"""

import subprocess
import sys
import os
import time
import psutil
from datetime import datetime

def log_message(message):
    """输出带时间戳的日志信息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def find_and_kill_processes(process_names):
    """查找并关闭指定的进程"""
    killed_processes = []
    
    for process_name in process_names:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    killed_processes.append(f"{process_name} (PID: {proc.info['pid']})")
                    log_message(f"关闭进程: {process_name} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    
    # 等待进程退出
    if killed_processes:
        time.sleep(2)
        
        # 检查是否还有残留进程
        for process_name in process_names:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == process_name.lower():
                        proc.kill()  # 强制杀死
                        log_message(f"强制关闭进程: {process_name} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
    
    return killed_processes

def run_scons_compile():
    """执行scons编译"""
    log_message("开始执行scons编译...")
    
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        # 执行scons编译
        result = subprocess.run(
            ['scons'],
            cwd=os.getcwd(),
            env=env,
            encoding='utf-8',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 输出编译结果
        if result.stdout:
            print("编译输出:")
            print(result.stdout)
        
        if result.stderr:
            print("编译错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            log_message("✅ 编译成功完成!")
            return True
        else:
            log_message(f"❌ 编译失败，退出码: {result.returncode}")
            return False
            
    except Exception as e:
        log_message(f"❌ 执行scons编译时发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    log_message("🚀 智能编译脚本启动")
    log_message(f"当前工作目录: {os.getcwd()}")
    
    # 要关闭的进程列表
    target_processes = [
        'notepad_abc.exe',
        'notepad++.exe',  # 可能的旧版本进程名
        'npp.exe'         # 可能的缩写
    ]
    
    # 检查并关闭目标进程
    log_message("🔍 检查并关闭相关进程...")
    killed_processes = find_and_kill_processes(target_processes)
    
    if killed_processes:
        log_message(f"✅ 已关闭 {len(killed_processes)} 个进程")
        for proc in killed_processes:
            log_message(f"   - {proc}")
    else:
        log_message("ℹ️ 没有发现运行中的目标程序")
    
    # 等待一秒确保文件释放
    time.sleep(1)
    
    # 执行编译
    compile_success = run_scons_compile()
    
    if compile_success:
        log_message("🎉 整个编译流程完成!")
        
        # 检查生成的可执行文件
        exe_path = os.path.join("bin", "notepad_abc.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            log_message(f"📁 生成文件: {exe_path} ({file_size:.2f} MB)")
        else:
            log_message("⚠️ 警告: 未找到生成的可执行文件")
    else:
        log_message("💥 编译流程失败")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("⏹️ 用户中断编译流程")
        sys.exit(1)
    except Exception as e:
        log_message(f"💥 脚本执行发生未预期错误: {str(e)}")
        sys.exit(1)
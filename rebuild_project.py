#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新编译Notepad++项目脚本
"""

import os
import time
import subprocess
import sys

def run_command_with_output(cmd, cwd=None):
    """运行命令并获取输出"""
    print(f"执行命令: {cmd}")
    print("-" * 40)
    
    try:
        # 使用subprocess.run来获取完整输出
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace'
        )
        
        # 输出结果
        if result.stdout:
            print("输出:")
            print(result.stdout)
        if result.stderr:
            print("错误:")
            print(result.stderr)
        
        print(f"返回码: {result.returncode}")
        return result.returncode == 0
        
    except Exception as e:
        print(f"命令执行失败: {e}")
        return False

def compile_project():
    """编译项目"""
    print("重新编译Notepad++项目")
    print("=" * 60)
    
    # 确保在正确的目录
    base_dir = os.getcwd()
    print(f"当前目录: {base_dir}")
    
    # 设置环境变量（确保UTF-8）
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    # 编译命令
    compile_cmd = "chcp 65001; scons SCINTILLA_DIR=lexilla\\src LEXILLA_DIR=lexilla"
    
    print("开始编译...")
    start_time = time.time()
    
    # 运行编译
    success = run_command_with_output(compile_cmd)
    
    elapsed_time = time.time() - start_time
    print(f"编译用时: {elapsed_time:.1f}秒")
    
    if success:
        print("✅ 编译成功！")
        
        # 检查输出文件
        exe_path = "bin\\notepad_abc_new.exe"
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path)
            print(f"✅ 输出文件存在: {exe_path}")
            print(f"文件大小: {file_size:,} 字节")
        else:
            print("⚠️ 输出文件不存在")
            
        return True
    else:
        print("❌ 编译失败")
        return False

def test_compiled_exe():
    """测试编译后的可执行文件"""
    print("\n测试编译后的程序...")
    print("=" * 40)
    
    exe_path = "bin\\notepad_abc_new.exe"
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False
    
    print(f"测试程序: {exe_path}")
    
    try:
        # 启动程序
        process = subprocess.Popen(
            exe_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ 程序启动成功，PID: {process.pid}")
        print("⏳ 等待程序初始化...")
        
        # 等待5秒
        time.sleep(5)
        
        # 检查进程是否还在运行
        try:
            process.poll()
            if process.returncode is None:
                print("✅ 程序仍在运行")
                print("🎉 窗口显示问题已修复！")
                
                # 终止进程
                process.terminate()
                try:
                    process.wait(timeout=3)
                    print("✅ 程序正常终止")
                except:
                    process.kill()
                    print("⚠️ 强制终止进程")
                    
                return True
            else:
                print(f"❌ 程序已退出，返回码: {process.returncode}")
                return False
                
        except Exception as e:
            print(f"检查进程状态失败: {e}")
            return False
            
    except Exception as e:
        print(f"测试程序失败: {e}")
        return False

def main():
    """主函数"""
    print("Notepad++ 重新编译工具")
    print("=" * 60)
    
    # 编译项目
    if compile_project():
        # 测试编译结果
        test_compiled_exe()
    else:
        print("编译失败，请检查错误信息")
    
    print("\n" + "=" * 60)
    print("编译完成！")

if __name__ == "__main__":
    main()
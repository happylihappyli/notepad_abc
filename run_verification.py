#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动测试脚本：以管理员权限运行notepad_abc.exe
"""

import os
import sys
import subprocess
import ctypes
import time
from pathlib import Path

def run_as_admin():
    """检查是否以管理员权限运行，如果不是则尝试提权"""
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin:
            # 请求管理员权限重新运行
            script = sys.argv[0]
            params = ' '.join([script] + sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1)
            return False
        return True
    except Exception as e:
        print(f"检查管理员权限时出错: {str(e)}")
        return False

def main():
    print("====== Notepad++ 文档列表修复测试 ======")
    print("正在准备运行程序...")
    
    # 检查管理员权限
    if not run_as_admin():
        print("已请求管理员权限，请在弹出的对话框中确认")
        sys.exit(0)
    
    # 设置工作目录
    base_dir = Path(r"E:\GitHub3\notepad_abc")
    bin_dir = base_dir / "bin"
    exe_path = bin_dir / "notepad_abc.exe"
    
    # 检查可执行文件是否存在
    if not os.path.exists(exe_path):
        print(f"错误: 找不到可执行文件 {exe_path}")
        return
    
    print(f"找到可执行文件: {exe_path}")
    print(f"文件大小: {os.path.getsize(exe_path) / 1024:.1f} KB")
    print("\n修复信息:")
    print("1. ✓ VerticalFileSwitcher构造函数已修改为使用-1作为资源ID")
    print("2. ✓ 使用CreateWindowEx直接创建对话框，避免依赖资源文件")
    print("3. ✓ 资源ID已正确定义")
    print("\n运行验证要点:")
    print("- 检查程序启动时是否不再出现'找不到映像文件不包含资源区域'错误")
    print("- 检查工具栏按钮是否正确显示图标")
    print("- 测试文档列表功能是否正常工作")
    print("\n正在启动程序...")
    
    try:
        # 切换到bin目录并运行程序
        os.chdir(bin_dir)
        
        # 使用subprocess运行程序
        process = subprocess.Popen(
            [str(exe_path)],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("\n程序已启动，请观察是否有错误提示。")
        print("按Ctrl+C可以终止此脚本，但不会关闭程序。")
        
        # 等待程序退出
        try:
            stdout, stderr = process.communicate()
            if stdout:
                print("\n程序输出:")
                print(stdout)
            if stderr:
                print("\n错误输出:")
                print(stderr)
            
            if process.returncode == 0:
                print("\n程序正常退出。")
            else:
                print(f"\n程序以退出码 {process.returncode} 退出。")
        except KeyboardInterrupt:
            print("\n脚本已终止，但程序可能仍在运行。")
            process.kill()
    
    except Exception as e:
        print(f"\n启动程序时出错: {str(e)}")
    
    print("\n测试完成。请手动确认程序是否正常运行。")

if __name__ == "__main__":
    main()
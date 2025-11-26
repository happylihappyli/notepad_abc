#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notepad++ 简化编译脚本
专注于解决分类文件读取问题
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def ensure_utf8():
    """确保UTF-8编码"""
    if sys.platform.startswith('win'):
        os.system('chcp 65001 > nul')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def kill_running_processes():
    """终止运行中的notepad_abc进程"""
    print("检查并终止正在运行的notepad_abc进程...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'notepad_abc.exe'], 
                      capture_output=True, text=True)
        time.sleep(2)
        print("进程终止检查完成")
    except:
        print("没有运行的notepad_abc进程")

def compile_with_msbuild():
    """使用MSBuild编译项目"""
    print("开始编译时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 查找Visual Studio 2022
    vs_installer_path = r"D:\Code\VS2022\Community"
    msbuild_path = os.path.join(vs_installer_path, "MSBuild", "Current", "Bin", "MSBuild.exe")
    
    if not os.path.exists(msbuild_path):
        # 尝试其他可能的路径
        possible_paths = [
            r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe",
            r"C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe",
            r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                msbuild_path = path
                break
        else:
            print("错误: 无法找到MSBuild.exe")
            return False
    
    print(f"使用MSBuild: {msbuild_path}")
    
    # 查找项目文件
    project_files = []
    for root, dirs, files in os.walk("PowerEditor"):
        for file in files:
            if file.endswith(('.vcxproj', '.sln')):
                project_files.append(os.path.join(root, file))
    
    if not project_files:
        print("错误: 未找到项目文件")
        return False
    
    print(f"找到项目文件: {project_files}")
    
    # 编译配置
    build_configs = [
        "/p:Configuration=Release",
        "/p:Platform=x64",
        "/m",  # 并行编译
        "/v:minimal"  # 详细输出
    ]
    
    success = True
    for project in project_files:
        print(f"编译项目: {project}")
        cmd = [msbuild_path, project] + build_configs
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=300)
            if result.returncode == 0:
                print(f"✓ {project} 编译成功")
            else:
                print(f"✗ {project} 编译失败")
                print("错误输出:")
                print(result.stderr)
                success = False
        except subprocess.TimeoutExpired:
            print(f"✗ {project} 编译超时")
            success = False
        except Exception as e:
            print(f"✗ {project} 编译异常: {str(e)}")
            success = False
    
    print("编译结束时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return success

def main():
    """主函数"""
    ensure_utf8()
    kill_running_processes()
    
    print("=== 简化编译脚本 - 修复分类文件读取问题 ===")
    
    # 检查是否在正确目录
    if not os.path.exists("PowerEditor"):
        print("错误: 请在项目根目录运行此脚本")
        return False
    
    # 创建必要的目录
    for dir_name in ['bin', 'obj']:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"创建目录: {dir_name}")
    
    # 编译项目
    success = compile_with_msbuild()
    
    if success:
        print("\n🎉 编译成功!")
        print("现在可以测试分类文件读取功能")
        
        # 检查生成的exe文件
        exe_files = []
        for root, dirs, files in os.walk("bin"):
            for file in files:
                if file.endswith('.exe'):
                    exe_files.append(os.path.join(root, file))
        
        if exe_files:
            print(f"生成的exe文件: {exe_files}")
    else:
        print("\n❌ 编译失败")
        print("请检查错误信息并重试")
    
    return success

if __name__ == "__main__":
    main()
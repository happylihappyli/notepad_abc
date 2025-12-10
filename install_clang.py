#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装Clang编译器的Python脚本
"""

import os
import sys
import urllib.request
import zipfile
import subprocess
import shutil
from pathlib import Path

def ensure_utf8_print():
    """确保Python输出使用UTF-8编码"""
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        os.system('chcp 65001 > nul')

def download_clang():
    """下载Clang编译器"""
    print("正在下载Clang编译器...")
    
    # Clang 17.0.6 Windows 64位版本
    clang_url = "https://github.com/llvm/llvm-project/releases/download/llvmorg-17.0.6/LLVM-17.0.6-win64.exe"
    installer_path = "LLVM-17.0.6-win64.exe"
    
    try:
        # 下载安装程序
        urllib.request.urlretrieve(clang_url, installer_path)
        print(f"✅ 下载完成: {installer_path}")
        return installer_path
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None

def install_clang(installer_path):
    """安装Clang编译器"""
    print("正在安装Clang编译器...")
    
    # 安装到D:\Code\LLVM目录
    install_dir = r"D:\Code\LLVM"
    
    try:
        # 创建安装目录
        os.makedirs(install_dir, exist_ok=True)
        
        # 静默安装Clang
        cmd = f"{installer_path} /S /D={install_dir}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Clang安装完成: {install_dir}")
            return install_dir
        else:
            print(f"❌ 安装失败: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ 安装过程中出错: {e}")
        return None

def add_to_path(clang_path):
    """将Clang添加到系统PATH"""
    print("正在配置环境变量...")
    
    bin_path = os.path.join(clang_path, "bin")
    
    try:
        # 获取当前PATH
        current_path = os.environ.get('PATH', '')
        
        # 如果PATH中还没有Clang路径，则添加
        if bin_path not in current_path:
            new_path = f"{bin_path};{current_path}"
            
            # 设置当前进程的PATH
            os.environ['PATH'] = new_path
            
            # 写入到用户环境变量（需要管理员权限）
            try:
                subprocess.run([
                    'setx', 'PATH', new_path, '/M'
                ], shell=True, capture_output=True)
                print("✅ 已添加到系统PATH（需要重启生效）")
            except:
                print("⚠️  需要管理员权限才能永久修改PATH，当前仅临时生效")
        else:
            print("✅ Clang已在PATH中")
            
        return bin_path
    except Exception as e:
        print(f"❌ 配置环境变量失败: {e}")
        return None

def verify_clang_installation():
    """验证Clang安装"""
    print("验证Clang安装...")
    
    try:
        # 检查clang版本
        result = subprocess.run(['clang', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Clang安装验证成功:")
            print(result.stdout)
            return True
        else:
            print("❌ Clang安装验证失败")
            return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def create_clang_config():
    """创建Clang配置文件"""
    print("创建Clang配置文件...")
    
    config_content = """# Clang编译器配置
# 使用Clang编译Notepad++项目

# 基本编译选项
-std=c++20
-fms-extensions
-fms-compatibility
-municode

# 警告选项
-Wall
-Wextra
-Wpedantic

# 禁用特定警告（减少编译错误）
-Wno-microsoft-cast
-Wno-microsoft-enum-value
-Wno-deprecated-declarations
-Wno-unknown-pragmas
-Wno-unused-function
-Wno-unused-variable
-Wno-format
-Wno-sign-compare
-Wno-switch
-Wno-reorder
-Wno-overloaded-virtual
-Wno-invalid-offsetof
-Wno-unreachable-code
-Wno-uninitialized
-Wno-non-virtual-dtor
-Wno-old-style-cast
-Wno-return-type

# 优化选项
-O2
-flto

# 调试选项
-g
-fdiagnostics-absolute-paths

# 其他选项
-fexceptions
-frtti
-fuse-ld=lld
"""
    
    try:
        with open('clang_config.txt', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ Clang配置文件已创建: clang_config.txt")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False

def main():
    """主函数"""
    ensure_utf8_print()
    
    print("=" * 50)
    print("Clang编译器安装脚本")
    print("=" * 50)
    
    # 检查是否已安装Clang
    print("检查当前Clang安装状态...")
    try:
        result = subprocess.run(['clang', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Clang已安装:")
            print(result.stdout)
            print("无需重新安装")
            return
    except:
        pass
    
    # 下载Clang
    installer_path = download_clang()
    if not installer_path:
        print("❌ 下载失败，无法继续安装")
        return
    
    # 安装Clang
    clang_path = install_clang(installer_path)
    if not clang_path:
        print("❌ 安装失败")
        return
    
    # 添加到PATH
    bin_path = add_to_path(clang_path)
    if not bin_path:
        print("⚠️  环境变量配置失败，但安装已完成")
    
    # 验证安装
    if verify_clang_installation():
        print("✅ Clang安装成功！")
    else:
        print("⚠️  Clang安装可能有问题，请手动验证")
    
    # 创建配置文件
    create_clang_config()
    
    print("\n" + "=" * 50)
    print("安装完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
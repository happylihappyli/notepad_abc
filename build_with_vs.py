#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Visual Studio编译器直接构建程序
"""

import os
import subprocess
import sys

def setup_vs_environment():
    """设置Visual Studio环境"""
    print("设置Visual Studio环境...")
    
    # Visual Studio 2022路径
    vs_path = r"D:\Code\VS2022\Community\VC\Auxiliary\Build\vcvars64.bat"
    
    if not os.path.exists(vs_path):
        print(f"错误: Visual Studio路径不存在: {vs_path}")
        return False
    
    # 运行vcvars64.bat来设置环境
    try:
        # 创建一个临时的批处理文件来设置环境并运行我们的命令
        temp_bat = "setup_vs_env.bat"
        with open(temp_bat, 'w') as f:
            f.write(f'@echo off\n')
            f.write(f'call "{vs_path}"\n')
            f.write(f'set > vs_env.txt\n')
        
        result = subprocess.run(temp_bat, shell=True, capture_output=True, text=True)
        os.remove(temp_bat)
        
        if os.path.exists("vs_env.txt"):
            # 读取环境变量
            with open("vs_env.txt", 'r') as f:
                env_lines = f.readlines()
            os.remove("vs_env.txt")
            
            # 设置环境变量
            for line in env_lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
            
            print("✓ Visual Studio环境设置成功")
            return True
        else:
            print("✗ 无法设置Visual Studio环境")
            return False
            
    except Exception as e:
        print(f"✗ 设置Visual Studio环境时出错: {e}")
        return False

def compile_single_file():
    """尝试编译单个文件来测试编译器"""
    print("\n测试编译器...")
    
    # 创建一个简单的测试文件
    test_file = "test_compile.cpp"
    with open(test_file, 'w') as f:
        f.write("""
#include <iostream>
int main() {
    std::cout << "Hello from Visual Studio compiler!" << std::endl;
    return 0;
}
""")
    
    try:
        # 尝试编译
        result = subprocess.run(
            f'cl.exe /nologo /EHsc "{test_file}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ 编译器测试成功")
            
            # 运行编译的程序
            if os.path.exists("test_compile.exe"):
                run_result = subprocess.run("test_compile.exe", capture_output=True, text=True)
                print(f"程序输出: {run_result.stdout.strip()}")
                
                # 清理
                os.remove("test_compile.exe")
                os.remove("test_compile.obj")
            
            os.remove(test_file)
            return True
        else:
            print(f"✗ 编译器测试失败: {result.stderr}")
            os.remove(test_file)
            return False
            
    except Exception as e:
        print(f"✗ 编译器测试出错: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def check_current_exe():
    """检查当前的可执行文件"""
    print("\n检查当前的可执行文件...")
    
    exe_path = os.path.join("bin", "notepad_abc.exe")
    
    if not os.path.exists(exe_path):
        print("✗ 可执行文件不存在")
        return False
    
    # 检查文件大小
    size = os.path.getsize(exe_path)
    print(f"文件大小: {size} 字节")
    
    # 检查是否是有效的PE文件
    try:
        with open(exe_path, 'rb') as f:
            # 检查MZ签名
            header = f.read(2)
            if header == b'MZ':
                print("✓ 有效的DOS签名")
                
                # 检查PE偏移
                f.seek(0x3C)
                pe_offset_bytes = f.read(4)
                pe_offset = int.from_bytes(pe_offset_bytes, 'little')
                print(f"PE头偏移: 0x{pe_offset:X}")
                
                # 检查PE签名
                f.seek(pe_offset)
                pe_sig = f.read(4)
                expected_sig = b'PE\\x00\\x00'
                
                if pe_sig == expected_sig:
                    print("✓ 有效的PE签名")
                    return True
                else:
                    print(f"✗ 无效的PE签名: {pe_sig.hex()} (期望: {expected_sig.hex()})")
                    return False
            else:
                print(f"✗ 无效的DOS签名: {header.hex()}")
                return False
                
    except Exception as e:
        print(f"✗ 文件检查错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("Visual Studio直接构建测试")
    print("=" * 60)
    
    # 检查当前目录
    print(f"当前目录: {os.getcwd()}")
    
    # 检查当前的可执行文件
    current_ok = check_current_exe()
    
    if not current_ok:
        print("\n当前可执行文件有问题，尝试使用Visual Studio重新构建...")
        
        # 设置Visual Studio环境
        if setup_vs_environment():
            # 测试编译器
            if compile_single_file():
                print("\n✓ Visual Studio编译器工作正常")
                print("建议: 当前的SCons构建可能有问题，需要修复构建脚本")
            else:
                print("\n✗ Visual Studio编译器测试失败")
        else:
            print("\n✗ 无法设置Visual Studio环境")
    else:
        print("\n✓ 当前可执行文件正常")
        print("建议: 程序文件结构正常，DLL重定向问题可能已解决")
        print("请尝试手动双击notepad_abc.exe文件启动")
    
    print("\n" + "=" * 60)
    print("构建测试完成")
    print("=" * 60)
    
    # 播放语音提示
    try:
        import pyttsx3
        engine = pyttsx3.init()
        if current_ok:
            engine.say("程序文件检查正常，请手动测试")
        else:
            engine.say("程序文件有问题，需要修复构建脚本")
        engine.runAndWait()
    except:
        print("语音提示不可用")

if __name__ == "__main__":
    main()
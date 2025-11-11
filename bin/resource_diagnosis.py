#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源文件诊断脚本
专门用于诊断文档列表和函数列表功能相关的资源文件问题
"""

import os
import sys
import subprocess
import re

def check_resource_files():
    """检查资源文件状态"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("🔍 资源文件诊断报告")
    print("=" * 60)
    
    # 检查关键资源文件
    resource_files = [
        ("VerticalFileSwitcher.rc", "PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher.rc"),
        ("VerticalFileSwitcher_rc.h", "PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher_rc.h"),
        ("Notepad_plus.rc", "PowerEditor/src/Notepad_plus.rc"),
    ]
    
    for file_name, rel_path in resource_files:
        file_path = os.path.join(base_dir, rel_path)
        if os.path.exists(file_path):
            print(f"✅ {file_name} 存在: {file_path}")
            
            # 检查文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if file_name == "VerticalFileSwitcher.rc":
                    if "IDD_DOCLIST" in content:
                        print("  ✅ 包含IDD_DOCLIST资源定义")
                    else:
                        print("  ❌ 不包含IDD_DOCLIST资源定义")
                        
                elif file_name == "VerticalFileSwitcher_rc.h":
                    if "#define\tIDD_DOCLIST" in content or "#define IDD_DOCLIST" in content:
                        print("  ✅ 包含IDD_DOCLIST宏定义")
                    else:
                        print("  ❌ 不包含IDD_DOCLIST宏定义")
                        
            except Exception as e:
                print(f"  ⚠️  无法读取文件内容: {e}")
        else:
            print(f"❌ {file_name} 不存在: {file_path}")
    
    print()

def check_scons_config():
    """检查SCons构建配置"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("🔧 SCons构建配置检查")
    print("=" * 60)
    
    scons_files = ["SConscript", "SConstruct"]
    
    for scons_file in scons_files:
        file_path = os.path.join(base_dir, scons_file)
        if os.path.exists(file_path):
            print(f"✅ {scons_file} 存在")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含VerticalFileSwitcher资源文件
                if "VerticalFileSwitcher.rc" in content:
                    print("  ✅ 包含VerticalFileSwitcher.rc资源文件引用")
                else:
                    print("  ❌ 不包含VerticalFileSwitcher.rc资源文件引用")
                    
                # 检查资源文件列表
                rc_pattern = r'rc_files\s*=\s*\[([^\]]+)\]'
                match = re.search(rc_pattern, content, re.DOTALL)
                if match:
                    rc_list = match.group(1)
                    print("  📋 资源文件列表:")
                    for line in rc_list.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#') and 'rc' in line:
                            print(f"    - {line.strip(',')}")
                            
            except Exception as e:
                print(f"  ⚠️  无法读取文件内容: {e}")
        else:
            print(f"❌ {scons_file} 不存在")
    
    print()

def check_executable_resources():
    """检查可执行文件中的资源"""
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notepad_abc_new.exe")
    
    print("📦 可执行文件资源检查")
    print("=" * 60)
    
    if os.path.exists(exe_path):
        print(f"✅ 可执行文件存在: {exe_path}")
        print(f"📏 文件大小: {os.path.getsize(exe_path):,} 字节")
        
        # 使用Windows资源工具检查资源
        try:
            # 尝试使用Resource Hacker或类似工具检查资源
            result = subprocess.run([
                "powershell", "-Command", 
                f"Get-Content -Path '{exe_path}' -Encoding Byte -TotalCount 100 | Format-Hex"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # 检查PE文件签名
                if "MZ" in result.stdout:
                    print("  ✅ PE文件签名有效 (MZ)")
                else:
                    print("  ❌ 不是有效的PE文件")
            
        except Exception as e:
            print(f"  ⚠️  无法检查可执行文件: {e}")
            
    else:
        print(f"❌ 可执行文件不存在: {exe_path}")
    
    print()

def check_error_logs():
    """检查错误日志"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    error_dir = os.path.join(base_dir, "error")
    
    print("📋 错误日志检查")
    print("=" * 60)
    
    if os.path.exists(error_dir):
        print(f"✅ 错误日志目录存在: {error_dir}")
        
        for i in range(1, 4):
            error_file = os.path.join(error_dir, f"{i}.txt")
            if os.path.exists(error_file):
                print(f"\n📄 错误日志 {i}.txt:")
                try:
                    with open(error_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content.strip():
                        print(f"  内容: {content.strip()}")
                        
                        # 分析常见错误
                        if "CreateDialogParam" in content:
                            print("  🔍 检测到CreateDialogParam错误 - 资源加载失败")
                        if "找不到映像文件" in content:
                            print("  🔍 检测到资源文件缺失错误")
                        if "LoadIcon" in content:
                            print("  🔍 检测到图标加载错误")
                            
                    else:
                        print("  空文件")
                        
                except Exception as e:
                    print(f"  ⚠️  无法读取错误日志: {e}")
            else:
                print(f"❌ 错误日志 {i}.txt 不存在")
    else:
        print(f"❌ 错误日志目录不存在: {error_dir}")
    
    print()

def generate_recommendations():
    """生成修复建议"""
    print("💡 修复建议")
    print("=" * 60)
    
    print("1. 检查SConscript文件中的资源文件列表")
    print("   - 确保包含VerticalFileSwitcher.rc")
    print("   - 确保资源文件路径正确")
    
    print("\n2. 重新编译程序")
    print("   - 清理obj目录")
    print("   - 重新运行scons构建")
    
    print("\n3. 验证资源编译")
    print("   - 检查编译过程中是否有资源编译错误")
    print("   - 确保资源编译器正常工作")
    
    print("\n4. 测试功能")
    print("   - 启动程序后测试文档列表功能")
    print("   - 检查是否有新的错误日志")

def main():
    """主函数"""
    print("🐭 文档列表功能资源诊断工具")
    print("=" * 60)
    print()
    
    check_resource_files()
    check_scons_config()
    check_executable_resources()
    check_error_logs()
    generate_recommendations()
    
    print("✅ 诊断完成")

if __name__ == "__main__":
    main()
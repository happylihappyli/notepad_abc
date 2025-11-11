#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档列表和函数列表功能诊断脚本
用于诊断面板不显示的问题
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_executable():
    """检查可执行文件是否存在和状态"""
    exe_path = Path("notepad_abc_new.exe")
    
    print("🔍 检查可执行文件")
    print("-" * 40)
    
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return False
    
    print(f"✅ 可执行文件存在: {exe_path}")
    print(f"📏 文件大小: {exe_path.stat().st_size} 字节")
    
    # 检查文件是否可执行
    try:
        with open(exe_path, 'rb') as f:
            header = f.read(2)
            if header == b'MZ':
                print("✅ 有效的Windows可执行文件")
            else:
                print("❌ 不是有效的Windows可执行文件")
                return False
    except Exception as e:
        print(f"❌ 无法读取文件: {e}")
        return False
    
    return True

def check_process_running():
    """检查Notepad++ ABC进程是否在运行"""
    print("\n🔍 检查进程状态")
    print("-" * 40)
    
    # 使用tasklist命令检查进程
    try:
        result = subprocess.run(['tasklist', '/fi', 'imagename eq notepad*.exe'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if "notepad" in result.stdout.lower() and "信息:" not in result.stdout:
            print("✅ 找到Notepad++相关进程:")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "notepad" in line.lower() and ".exe" in line:
                    print(f"  - {line.strip()}")
            return True
        else:
            print("❌ 未找到Notepad++相关进程")
            return False
    except Exception as e:
        print(f"❌ 检查进程时出错: {e}")
        return False

def check_resource_files():
    """检查必要的资源文件"""
    print("\n🔍 检查资源文件")
    print("-" * 40)
    
    # 检查关键资源文件
    resource_files = [
        "../PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher.rc",
        "../PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher_rc.h",
        "../PowerEditor/src/WinControls/FunctionList/functionListPanel.rc",
        "../PowerEditor/src/WinControls/FunctionList/functionListPanel_rc.h"
    ]
    
    all_resources_exist = True
    for resource_file in resource_files:
        file_path = Path(resource_file)
        if file_path.exists():
            print(f"✅ {resource_file}")
        else:
            print(f"❌ {resource_file} - 文件不存在")
            all_resources_exist = False
    
    return all_resources_exist

def check_config_files():
    """检查配置文件"""
    print("\n🔍 检查配置文件")
    print("-" * 40)
    
    config_files = [
        "../SConscript",
        "../SConstruct",
        "../PowerEditor/src/Notepad_plus.cpp",
        "../PowerEditor/src/NppCommands.cpp"
    ]
    
    all_configs_exist = True
    for config_file in config_files:
        file_path = Path(config_file)
        if file_path.exists():
            print(f"✅ {config_file}")
        else:
            print(f"❌ {config_file} - 文件不存在")
            all_configs_exist = False
    
    return all_configs_exist

def check_error_logs():
    """检查错误日志"""
    print("\n🔍 检查错误日志")
    print("-" * 40)
    
    error_files = [
        "error.log",
        "detailed_error.log",
        "npp_debug.log",
        "../error/1.txt",
        "../error/2.txt",
        "../error/3.txt"
    ]
    
    errors_found = False
    for error_file in error_files:
        file_path = Path(error_file)
        if file_path.exists():
            print(f"⚠️  {error_file} - 存在错误日志")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if "CreateDialogParam" in content:
                        print("    ❌ 包含CreateDialogParam错误")
                        errors_found = True
                    if "NULL" in content:
                        print("    ⚠️  包含NULL错误")
                        errors_found = True
                    if "资源" in content:
                        print("    ⚠️  包含资源相关错误")
                        errors_found = True
            except Exception as e:
                print(f"    ❌ 无法读取文件: {e}")
        else:
            print(f"✅ {error_file} - 无错误日志")
    
    return errors_found

def check_build_artifacts():
    """检查构建产物"""
    print("\n🔍 检查构建产物")
    print("-" * 40)
    
    artifacts = [
        "../obj/PowerEditor/src/com_stub.obj",
        "../obj/PowerEditor/src/CustomFileDialog.obj",
        "../obj/PowerEditor/src/Notepad_plus.obj",
        "../obj/PowerEditor/src/NppCommands.obj"
    ]
    
    all_artifacts_exist = True
    for artifact in artifacts:
        file_path = Path(artifact)
        if file_path.exists():
            print(f"✅ {artifact}")
        else:
            print(f"❌ {artifact} - 文件不存在")
            all_artifacts_exist = False
    
    return all_artifacts_exist

def generate_diagnosis_report():
    """生成诊断报告"""
    print("\n📊 诊断报告")
    print("=" * 50)
    
    # 执行各项检查
    exe_ok = check_executable()
    process_ok = check_process_running()
    resources_ok = check_resource_files()
    configs_ok = check_config_files()
    errors_found = check_error_logs()
    artifacts_ok = check_build_artifacts()
    
    print("\n📋 诊断结果总结")
    print("-" * 50)
    
    issues = []
    
    if not exe_ok:
        issues.append("❌ 可执行文件问题")
    
    if not process_ok:
        issues.append("❌ 进程未运行")
    
    if not resources_ok:
        issues.append("❌ 资源文件缺失")
    
    if not configs_ok:
        issues.append("❌ 配置文件缺失")
    
    if errors_found:
        issues.append("❌ 发现错误日志")
    
    if not artifacts_ok:
        issues.append("❌ 构建产物不完整")
    
    if not issues:
        print("✅ 所有检查通过，程序应该正常工作")
        print("\n💡 建议:")
        print("  - 使用鼠标操作记录器记录具体操作")
        print("  - 检查程序是否以管理员权限运行")
        print("  - 尝试重新启动程序")
    else:
        print("⚠️  发现以下问题:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n🔧 修复建议:")
        if "资源文件缺失" in issues:
            print("  - 检查资源文件是否在正确位置")
            print("  - 重新编译程序确保资源被正确嵌入")
        
        if "发现错误日志" in issues:
            print("  - 查看详细错误日志文件")
            print("  - 检查CreateDialogParam相关错误")
        
        if "构建产物不完整" in issues:
            print("  - 重新运行scons编译")
            print("  - 检查编译过程中是否有错误")
    
    print("\n📝 下一步操作:")
    print("  1. 运行鼠标操作记录器: python mouse_operation_logger.py")
    print("  2. 启动Notepad++ ABC程序")
    print("  3. 尝试点击'视图->文档列表'和'视图->函数列表'")
    print("  4. 查看生成的日志文件分析问题")

def main():
    """主函数"""
    print("文档列表和函数列表功能诊断工具")
    print("=" * 50)
    
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"工作目录: {os.getcwd()}")
    
    # 生成诊断报告
    generate_diagnosis_report()

if __name__ == "__main__":
    main()
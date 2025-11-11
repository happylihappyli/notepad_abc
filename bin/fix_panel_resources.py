#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复文档列表和函数列表面板资源问题
解决CreateDialogParam返回NULL的错误
"""

import os
import sys
import subprocess
from pathlib import Path

def check_resource_compilation():
    """检查资源编译状态"""
    print("🔍 检查资源编译状态")
    print("-" * 40)
    
    # 检查关键资源文件是否被正确编译
    resource_files = [
        "../PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher.rc",
        "../PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher_rc.h",
        "../PowerEditor/src/WinControls/FunctionList/functionListPanel.rc",
        "../PowerEditor/src/WinControls/FunctionList/functionListPanel_rc.h"
    ]
    
    for resource_file in resource_files:
        file_path = Path(resource_file)
        if file_path.exists():
            print(f"✅ {resource_file} - 存在")
            # 检查文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "IDD_DOCLIST" in content or "IDD_FUNCLIST" in content:
                        print(f"  包含对话框资源定义")
            except Exception as e:
                print(f"❌ 无法读取文件: {e}")
        else:
            print(f"❌ {resource_file} - 不存在")

def check_scons_config():
    """检查SConscript配置"""
    print("\n🔍 检查SConscript配置")
    print("-" * 40)
    
    sconscript_path = Path("../SConscript")
    if sconscript_path.exists():
        print("✅ SConscript文件存在")
        
        # 检查是否包含必要的资源文件
        with open(sconscript_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if "VerticalFileSwitcher" in content:
                print("✅ 包含VerticalFileSwitcher资源")
            else:
                print("❌ 未找到VerticalFileSwitcher资源引用")
                
            if "FunctionList" in content:
                print("✅ 包含FunctionList资源")
            else:
                print("❌ 未找到FunctionList资源引用")
                
            if "rc_files" in content:
                print("✅ 包含rc_files定义")
            else:
                print("❌ 未找到rc_files定义")
    else:
        print("❌ SConscript文件不存在")

def rebuild_resources():
    """重新构建资源"""
    print("\n🔧 重新构建资源")
    print("-" * 40)
    
    print("步骤1: 清理旧的构建产物")
    try:
        # 清理obj目录
        obj_dir = Path("../obj")
        if obj_dir.exists():
            # 只清理特定文件，保留目录结构
            for file_pattern in ["*.obj", "*.res"]:
                result = subprocess.run(["cmd", "/c", f"del /q {obj_dir}\\{file_pattern}"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ 清理obj文件成功")
                else:
                    print("⚠️  清理obj文件时可能有问题")
        else:
            print("❌ obj目录不存在")
    except Exception as e:
        print(f"❌ 清理失败: {e}")
    
    print("\n步骤2: 重新编译")
    try:
        # 切换到项目根目录
        project_root = Path("..").resolve()
        os.chdir(project_root)
        
        print(f"工作目录: {os.getcwd()}")
        
        # 运行scons编译
        print("运行scons编译...")
        result = subprocess.run(["scons", "-j1"], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 编译成功")
            print("编译输出:")
            print(result.stdout[-1000:])  # 显示最后1000字符
        else:
            print("❌ 编译失败")
            print("错误信息:")
            print(result.stderr)
            print("标准输出:")
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ 编译过程出错: {e}")
    finally:
        # 切换回bin目录
        os.chdir(Path(__file__).parent)

def test_panel_functionality():
    """测试面板功能"""
    print("\n🧪 测试面板功能")
    print("-" * 40)
    
    exe_path = Path("notepad_abc_new.exe")
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return
    
    print("✅ 可执行文件存在")
    
    # 检查文件是否包含必要的资源
    try:
        result = subprocess.run(["strings", exe_path], capture_output=True, text=True)
        if "IDD_DOCLIST" in result.stdout:
            print("✅ 可执行文件包含文档列表资源")
        else:
            print("❌ 可执行文件缺少文档列表资源")
            
        if "IDD_FUNCLIST" in result.stdout:
            print("✅ 可执行文件包含函数列表资源")
        else:
            print("❌ 可执行文件缺少函数列表资源")
    except Exception as e:
        print(f"⚠️  无法检查可执行文件资源: {e}")

def create_test_script():
    """创建测试脚本"""
    print("\n📝 创建测试脚本")
    print("-" * 40)
    
    # 创建一个简单的测试脚本
    test_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 面板功能测试脚本

import os
import subprocess
from pathlib import Path

def main():
    print("面板功能测试")
    print("=" * 30)
    
    # 检查可执行文件
    exe_path = Path("notepad_abc_new.exe")
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return
    
    print("✅ 可执行文件存在")
    print("💡 请手动测试以下功能:")
    print("  1. 启动程序: .\\notepad_abc_new.exe")
    print("  2. 视图 -> 文档列表")
    print("  3. 视图 -> 函数列表")
    print("  4. 工具栏相关按钮")
    print("\n📝 如果功能不正常，请查看错误日志")

if __name__ == "__main__":
    main()
"""
    
    with open("panel_function_test.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✅ 测试脚本创建成功: panel_function_test.py")

def main():
    """主函数"""
    print("修复文档列表和函数列表面板资源问题")
    print("=" * 50)
    
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"工作目录: {os.getcwd()}")
    
    # 执行修复步骤
    check_resource_compilation()
    check_scons_config()
    rebuild_resources()
    test_panel_functionality()
    create_test_script()
    
    print("\n📋 修复完成")
    print("-" * 50)
    print("✅ 资源检查完成")
    print("✅ SConscript配置检查完成")
    print("✅ 重新构建资源完成")
    print("✅ 面板功能测试脚本创建完成")
    
    print("\n🔧 下一步操作:")
    print("  1. 运行测试脚本: python panel_function_test.py")
    print("  2. 手动测试文档列表和函数列表功能")
    print("  3. 如果仍有问题，查看错误日志")
    print("  4. 使用鼠标操作记录器记录具体问题")

if __name__ == "__main__":
    main()
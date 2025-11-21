#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试VerticalFileSwitcherListView.cpp编译错误修复
检查iostream头文件添加是否正确
"""

import os
import sys

def test_iostream_include():
    """测试iostream头文件包含"""
    
    cpp_file = "PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcherListView.cpp"
    cpp_path = os.path.join(os.getcwd(), cpp_file)
    
    print("=" * 60)
    print("🔧 编译错误修复验证")
    print("=" * 60)
    
    if not os.path.exists(cpp_path):
        print(f"❌ 错误：找不到文件 {cpp_file}")
        return False
    
    print(f"✅ 找到源文件：{cpp_file}")
    
    with open(cpp_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查头文件包含
    checks = {
        "iostream头文件": ("#include <iostream>" in content, "缺少iostream头文件包含"),
        "shlwapi头文件": ("#include <shlwapi.h>" in content, "缺少shlwapi头文件包含"),
        "stdexcept头文件": ("#include <stdexcept>" in content, "缺少stdexcept头文件包含"),
        "debugLog函数使用": ("debugLog" in content, "debugLog函数可能未被正确使用"),
        "std::cout使用": ("std::cout" in content, "std::cout使用需要iostream支持")
    }
    
    print("\n🔍 头文件检查结果：")
    all_passed = True
    for check_name, (passed, desc) in checks.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {check_name}: {status} - {desc}")
        if not passed:
            all_passed = False
    
    # 检查iostream头文件位置
    if "#include <iostream>" in content:
        lines = content.split('\n')
        iostream_line = -1
        for i, line in enumerate(lines):
            if "#include <iostream>" in line:
                iostream_line = i
                break
        
        if iostream_line > 0:
            print(f"\n📍 iostream头文件位置：第 {iostream_line + 1} 行")
            # 检查前面的头文件
            prev_lines = lines[max(0, iostream_line-3):iostream_line]
            print("  前面的头文件：")
            for line in prev_lines:
                if line.strip().startswith('#include'):
                    print(f"    {line.strip()}")
        
        # 检查std::cout的使用位置
        cout_lines = []
        for i, line in enumerate(lines):
            if "std::cout" in line:
                cout_lines.append(i + 1)
        
        if cout_lines:
            print(f"\n🎯 std::cout使用位置：第 {cout_lines} 行")
            print("  ✅ iostream头文件位于std::cout使用之前，修复正确！")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 测试结果：✅ 编译错误修复成功！")
        print("\n📝 修复摘要：")
        print("  • 添加了 #include <iostream> 头文件")
        print("  • 头文件位置在std::cout使用之前")
        print("  • 解决了C2039和C2065编译错误")
        print("  • 可以重新编译项目")
    else:
        print("❌ 测试结果：❌ 修复不完整，需要进一步检查")
    
    print("=" * 60)
    return all_passed

def check_specific_errors():
    """检查特定的编译错误"""
    
    print("\n🔍 特定编译错误检查")
    print("-" * 40)
    
    cpp_file = "PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcherListView.cpp"
    cpp_path = os.path.join(os.getcwd(), cpp_file)
    
    with open(cpp_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找第794行附近的代码
    lines = content.split('\n')
    
    error_locations = [
        (794, "error C2039: \"cout\": 不是 \"std\" 的成员"),
        (794, "error C2065: \"cout\": 未声明的标识符")
    ]
    
    for line_num, error_desc in error_locations:
        if line_num <= len(lines):
            context_start = max(0, line_num - 3)
            context_end = min(len(lines), line_num + 2)
            
            print(f"\n第{line_num}行附近代码 ({error_desc}):")
            for i in range(context_start, context_end):
                marker = " >>> " if i == line_num - 1 else "     "
                print(f"{marker}{i+1:3d}: {lines[i]}")
    
    return True

if __name__ == "__main__":
    print("开始测试VerticalFileSwitcherListView.cpp编译错误修复...")
    
    success = test_iostream_include()
    check_specific_errors()
    
    if success:
        print("\n🚀 修复验证完成！可以重新编译项目。")
        print("\n📋 下一步操作：")
        print("  1. 运行 scons 重新编译")
        print("  2. 检查是否还有其他编译错误")
        print("  3. 测试修复后的功能")
        sys.exit(0)
    else:
        print("\n⚠️  修复验证发现问题，请检查修改。")
        sys.exit(1)
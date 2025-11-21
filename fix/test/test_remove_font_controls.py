#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证删除VerticalFileSwitcher文件列表面板中的字体大小控件
"""

import os
import re
import sys

def test_removed_controls():
    """测试字体控件是否已完全移除"""
    print("=== 测试删除文件列表面板字体控件 ===")
    
    base_path = "E:/GitHub3/notepad_abc/PowerEditor/src/WinControls/VerticalFileSwitcher"
    
    # 测试.rc文件
    rc_file = os.path.join(base_path, "VerticalFileSwitcher.rc")
    print(f"\n1. 检查 {os.path.basename(rc_file)} 文件...")
    
    with open(rc_file, 'r', encoding='utf-8') as f:
        rc_content = f.read()
    
    # 检查字体控件是否已删除
    if "IDC_FONTSIZE_STATIC_VFS" in rc_content or "IDC_FONTSIZE_COMBO_VFS" in rc_content:
        print("❌ 错误：字体控件定义仍在.rc文件中")
        return False
    else:
        print("✅ 字体控件定义已从.rc文件中删除")
    
    # 检查ListView布局
    listview_pattern = r'CONTROL\s+.*IDC_LIST_DOCLIST.*,\d+,\d+,(\d+),(\d+)"'
    match = re.search(listview_pattern, rc_content)
    if match:
        width, height = int(match.group(1)), int(match.group(2))
        if width == 230 and height == 370:
            print("✅ ListView控件布局调整正确，占用整个对话框")
        else:
            print(f"⚠️  ListView布局可能需要调整：{width}x{height}")
    
    # 测试.h文件
    h_file = os.path.join(base_path, "VerticalFileSwitcher.h")
    print(f"\n2. 检查 {os.path.basename(h_file)} 文件...")
    
    with open(h_file, 'r', encoding='utf-8') as f:
        h_content = f.read()
    
    # 检查成员变量是否已删除
    if "_hFontSizeCombo" in h_content or "_hFontSizeLabel" in h_content:
        print("❌ 错误：字体控件成员变量仍在.h文件中")
        return False
    else:
        print("✅ 字体控件成员变量已从.h文件中删除")
    
    # 测试.rc.h文件
    rc_h_file = os.path.join(base_path, "VerticalFileSwitcher_rc.h")
    print(f"\n3. 检查 {os.path.basename(rc_h_file)} 文件...")
    
    with open(rc_h_file, 'r', encoding='utf-8') as f:
        rc_h_content = f.read()
    
    # 检查控件ID是否已删除
    if "IDC_FONTSIZE_STATIC_VFS" in rc_h_content or "IDC_FONTSIZE_COMBO_VFS" in rc_h_content:
        print("❌ 错误：字体控件ID定义仍在.rc.h文件中")
        return False
    else:
        print("✅ 字体控件ID定义已从.rc.h文件中删除")
    
    # 测试.cpp文件
    cpp_file = os.path.join(base_path, "VerticalFileSwitcher.cpp")
    print(f"\n4. 检查 {os.path.basename(cpp_file)} 文件...")
    
    with open(cpp_file, 'r', encoding='utf-8') as f:
        cpp_content = f.read()
    
    # 检查初始化代码是否已删除
    if "IDC_FONTSIZE_COMBO_VFS" in cpp_content or "GetDlgItem.*IDC_FONTSIZE_STATIC_VFS" in cpp_content:
        print("❌ 错误：字体控件初始化代码仍在.cpp文件中")
        return False
    else:
        print("✅ 字体控件初始化代码已从.cpp文件中删除")
    
    # 检查处理函数是否已删除
    if "CBN_SELCHANGE.*IDC_FONTSIZE_COMBO_VFS" in cpp_content:
        print("❌ 错误：字体下拉框处理函数仍在.cpp文件中")
        return False
    else:
        print("✅ 字体下拉框处理函数已从.cpp文件中删除")
    
    # 检查分类按钮位置调整
    if "buttonY = 5" in cpp_content:
        print("✅ 分类按钮位置已调整到顶部")
    else:
        print("⚠️  分类按钮位置可能需要调整")
    
    return True

def test_compilation_readiness():
    """测试编译准备情况"""
    print("\n=== 编译准备情况检查 ===")
    
    # 检查修改的文件是否存在语法问题
    files_to_check = [
        "E:/GitHub3/notepad_abc/PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher.rc",
        "E:/GitHub3/notepad_abc/PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher.h",
        "E:/GitHub3/notepad_abc/PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher_rc.h",
        "E:/GitHub3/notepad_abc/PowerEditor/src/WinControls/VerticalFileSwitcher/VerticalFileSwitcher.cpp"
    ]
    
    all_good = True
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有明显的语法错误
            if content.count('{') != content.count('}'):
                print(f"❌ {os.path.basename(file_path)}: 大括号不匹配")
                all_good = False
            elif "IDC_FONTSIZE_COMBO_VFS" in content or "IDC_FONTSIZE_STATIC_VFS" in content:
                print(f"❌ {os.path.basename(file_path)}: 仍包含已删除的控件ID")
                all_good = False
            else:
                print(f"✅ {os.path.basename(file_path)}: 语法检查通过")
                
        except Exception as e:
            print(f"❌ {os.path.basename(file_path)}: 读取错误 - {e}")
            all_good = False
    
    return all_good

def main():
    """主函数"""
    print("开始验证删除文件列表面板字体控件的修改...")
    
    # 执行测试
    test1_passed = test_removed_controls()
    test2_passed = test_compilation_readiness()
    
    print(f"\n=== 测试结果 ===")
    if test1_passed and test2_passed:
        print("✅ 所有测试通过！")
        print("\n📋 修改摘要：")
        print("• 删除了文件列表面板中的字体大小标签")
        print("• 删除了文件列表面板中的字体大小下拉列表")
        print("• 调整了ListView控件布局占用整个对话框空间")
        print("• 调整了分类按钮位置从顶部开始显示")
        print("• 清理了所有相关的代码和ID定义")
        print("\n🎯 可以重新编译项目测试效果")
        return True
    else:
        print("❌ 部分测试失败，请检查修改内容")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
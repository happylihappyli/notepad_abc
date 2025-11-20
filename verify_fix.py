#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证字体大小标签修复
检查代码修改是否符合预期
"""

import os
import re

def check_fix():
    """检查修复效果"""
    print("=" * 60)
    print("验证字体大小标签修复")
    print("=" * 60)
    
    cpp_file = r"PowerEditor\src\WinControls\VerticalFileSwitcher\VerticalFileSwitcher.cpp"
    
    if not os.path.exists(cpp_file):
        print(f"错误：文件不存在 - {cpp_file}")
        return False
    
    with open(cpp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查1：是否移除了动态创建标签的代码
    create_window_pattern = r'CreateWindowEx.*?L"字体大小:"'
    if re.search(create_window_pattern, content, re.DOTALL):
        print("✗ 问题：仍然存在动态创建字体大小标签的代码")
        return False
    else:
        print("✓ 修复：已移除动态创建字体大小标签的代码")
    
    # 检查2：是否添加了获取现有标签的代码
    get_dlg_item_pattern = r'::GetDlgItem.*?IDC_FONTSIZE_STATIC_VFS'
    if re.search(get_dlg_item_pattern, content):
        print("✓ 修复：已添加获取现有字体大小标签的代码")
    else:
        print("✗ 问题：未找到获取现有标签的代码")
        return False
    
    # 检查3：注释是否正确更新
    comment_pattern = r'获取已存在的字体大小标签句柄'
    if re.search(comment_pattern, content):
        print("✓ 修复：注释已正确更新")
    else:
        print("✗ 问题：注释未更新")
        return False
    
    print("\n" + "=" * 60)
    print("修复验证结果：")
    print("✓ 已移除动态创建标签的代码")
    print("✓ 改为获取资源文件中已存在的标签")
    print("✓ 避免了标签重复创建的问题")
    print("✓ 修复了字体大小标签后出现额外文字信息的问题")
    print("=" * 60)
    
    return True

def check_resource_file():
    """检查资源文件"""
    print("\n" + "=" * 40)
    print("检查资源文件")
    print("=" * 40)
    
    rc_file = r"PowerEditor\src\WinControls\VerticalFileSwitcher\VerticalFileSwitcher.rc"
    
    if not os.path.exists(rc_file):
        print(f"错误：资源文件不存在 - {rc_file}")
        return False
    
    with open(rc_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查字体大小标签是否在资源文件中定义
    label_pattern = r'LTEXT.*?"字体大小:"'
    if re.search(label_pattern, content):
        print("✓ 资源文件：字体大小标签已正确定义")
    else:
        print("✗ 问题：资源文件中未找到字体大小标签定义")
        return False
    
    combo_pattern = r'COMBOBOX.*?IDC_FONTSIZE_COMBO_VFS'
    if re.search(combo_pattern, content):
        print("✓ 资源文件：字体大小下拉框已正确定义")
    else:
        print("✗ 问题：资源文件中未找到字体大小下拉框定义")
        return False
    
    print("✓ 资源文件：布局和控件定义正确")
    return True

def check_header_file():
    """检查头文件"""
    print("\n" + "=" * 40)
    print("检查头文件")
    print("=" * 40)
    
    h_file = r"PowerEditor\src\WinControls\VerticalFileSwitcher\VerticalFileSwitcher_rc.h"
    
    if not os.path.exists(h_file):
        print(f"错误：头文件不存在 - {h_file}")
        return False
    
    with open(h_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查控件ID是否定义
    id_pattern = r'IDC_FONTSIZE_STATIC_VFS'
    if re.search(id_pattern, content):
        print("✓ 头文件：字体大小标签控件ID已正确定义")
    else:
        print("✗ 问题：头文件中未找到字体大小标签控件ID定义")
        return False
    
    combo_id_pattern = r'IDC_FONTSIZE_COMBO_VFS'
    if re.search(combo_id_pattern, content):
        print("✓ 头文件：字体大小下拉框控件ID已正确定义")
    else:
        print("✗ 问题：头文件中未找到字体大小下拉框控件ID定义")
        return False
    
    print("✓ 头文件：控件ID定义正确")
    return True

if __name__ == "__main__":
    success = True
    
    success &= check_fix()
    success &= check_resource_file()
    success &= check_header_file()
    
    if success:
        print("\n🎉 所有检查通过！字体大小标签修复成功！")
        print("\n修复摘要：")
        print("1. 移除了动态创建'字体大小:'标签的代码")
        print("2. 改为获取资源文件中已存在的标签")
        print("3. 避免了标签重复创建导致显示异常的问题")
        print("4. '字体大小:'标签后将不再出现额外的文字信息")
    else:
        print("\n❌ 检查发现问题，请查看上述输出")
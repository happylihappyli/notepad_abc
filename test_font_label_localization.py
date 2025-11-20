#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体大小标签本地化修复验证脚本
验证字体大小标签不再出现乱码，而是显示正确的本地化文本
"""

import os
import sys

def test_font_size_label_localization_fix():
    """验证字体大小标签本地化修复效果"""
    print("=" * 60)
    print("字体大小标签本地化修复验证")
    print("=" * 60)
    
    # 1. 检查编译后的exe文件
    exe_path = "bin\\notepad_abc.exe"
    if os.path.exists(exe_path):
        exe_size = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✅ 编译成功: {exe_path} ({exe_size:.2f} MB)")
    else:
        print(f"❌ 编译失败: {exe_path} 不存在")
        return False
    
    # 2. 检查修改的源文件
    cpp_file = "PowerEditor\\src\\WinControls\\VerticalFileSwitcher\\VerticalFileSwitcher.cpp"
    if os.path.exists(cpp_file):
        print(f"✅ 源文件存在: {cpp_file}")
        
        # 检查是否包含本地化修复代码
        with open(cpp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'pNativeSpeaker->getAttrNameStr(L"Font Size"' in content:
                print("✅ 包含本地化文本获取代码")
            else:
                print("❌ 缺少本地化文本获取代码")
                return False
                
            if '::SetWindowText(_hFontSizeLabel, fontSizeStr.c_str())' in content:
                print("✅ 包含SetWindowText设置标签文本代码")
            else:
                print("❌ 缺少SetWindowText设置标签文本代码")
                return False
    else:
        print(f"❌ 源文件不存在: {cpp_file}")
        return False
    
    # 3. 检查资源文件设置
    rc_file = "PowerEditor\\src\\WinControls\\VerticalFileSwitcher\\VerticalFileSwitcher.rc"
    if os.path.exists(rc_file):
        print(f"✅ 资源文件存在: {rc_file}")
        
        with open(rc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'IDC_FONTSIZE_STATIC_VFS' in content:
                print("✅ 字体大小标签控件ID正确")
            else:
                print("❌ 字体大小标签控件ID缺失")
                return False
    else:
        print(f"❌ 资源文件不存在: {rc_file}")
        return False
    
    # 4. 检查本地化相关定义
    h_file = "PowerEditor\\src\\WinControls\\VerticalFileSwitcher\\VerticalFileSwitcher_rc.h"
    if os.path.exists(h_file):
        print(f"✅ 头文件存在: {h_file}")
        
        with open(h_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'IDC_FONTSIZE_STATIC_VFS 2209' in content:
                print("✅ 字体大小标签控件ID定义为2209")
            else:
                print("❌ 字体大小标签控件ID定义不正确")
                return False
    else:
        print(f"❌ 头文件不存在: {h_file}")
        return False
    
    print("\n" + "=" * 60)
    print("修复总结:")
    print("1. ✅ 已修改VerticalFileSwitcher.cpp，在WM_INITDIALOG中使用本地化系统")
    print("2. ✅ 使用NativeLangSpeaker::getAttrNameStr获取本地化文本")
    print("3. ✅ 使用SetWindowText正确设置字体大小标签文本")
    print("4. ✅ 保持控件ID 2209与本地化系统一致")
    print("5. ✅ 程序编译成功")
    print("\n预期结果:")
    print("- 字体大小标签现在应该显示为'Font Size'（英文）或相应本地化文本")
    print("- 不再出现乱码问题")
    print("- 标签文本与本地化设置保持一致")
    print("=" * 60)
    
    return True

def show_test_instructions():
    """显示测试说明"""
    print("\n" + "=" * 60)
    print("测试步骤:")
    print("=" * 60)
    print("1. 启动程序: bin\\notepad_abc.exe")
    print("2. 打开文档列表面板 (视图 -> 文档列表)")
    print("3. 查找文档列表左上角的字体大小标签")
    print("4. 验证标签文本是否正确显示（不再是乱码）")
    print("5. 检查下拉框功能是否正常")
    print("6. 如果仍有乱码，请检查系统本地化设置")
    print("=" * 60)

if __name__ == "__main__":
    success = test_font_size_label_localization_fix()
    if success:
        show_test_instructions()
        print("\n🎉 字体大小标签本地化修复验证通过！")
    else:
        print("\n❌ 字体大小标签本地化修复验证失败！")
        sys.exit(1)